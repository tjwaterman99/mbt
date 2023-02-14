import sys
from argparse import Namespace
from dbt.task.build import BuildTask
from dbt.task.list import ListTask
from dbt.contracts.results import RunExecutionResult
from dbt.graph.selector_spec import SelectionUnion, SelectionCriteria
from dbt.lib import get_dbt_config as _get_dbt_config
from dbt.main import parse_args, log_manager, adapter_management
from dbt.config.profile import read_user_config
from dbt.profiler import profiler
import dbt.flags as flags
import dbt

from mbt.config import Config


config = Config()

auto_defer_selector = dict(
    name='changed',
    description='Automatically detect changed models',
    default=True,
    definition=SelectionUnion(
        components=[
            SelectionCriteria.selection_criteria_from_dict(raw=None, dct=dict(
                method='path',
                value='models/example/my_first_dbt_model.sql'
            )),
            # SelectionCriteria.selection_criteria_from_dict(raw=None, dct=dict(
            #     method='path',
            #     value='models/example/my_second_dbt_model.sql'
            # ))
        ]
    )
)


def get_dbt_config():
    dbt_config = _get_dbt_config(project_dir=config.dbt_project_dir)
    dbt_config.get_default_selector_name = lambda: 'changed'
    dbt_config.selectors['changed'] = auto_defer_selector
    return dbt_config


class DeferredBuildTask(BuildTask):

    def __init__(self, args, config):
        super().__init__(args, config=get_dbt_config())

    # TODO: overwrite to pull the manifest from GitHub
    # def _get_deferred_manifest():
    #     pass


# TODO: This is not actually deferring to use the default selector.
class DeferredListTask(ListTask):
    pass


class Dbt:
    """
    Service for interacting with dbt
    """

    def __init__(self):
        self.config = get_dbt_config()

    # This just copies the handle_and_check method of dbt.main
    def call(self, args):
        args.project_dir = config.dbt_project_dir
        
        with log_manager.applicationbound():
            parsed = args

            # Set flags from args, user config, and env vars
            user_config = read_user_config(flags.PROFILES_DIR)  # This is read again later
            flags.set_from_args(parsed, user_config)
            dbt.tracking.initialize_from_flags()
            # Set log_format from flags
            parsed.cls.set_log_format()

            # we've parsed the args and set the flags - we can now decide if we're debug or not
            if flags.DEBUG:
                log_manager.set_debug()

            profiler_enabled = False

            if parsed.record_timing_info:
                profiler_enabled = True

            with profiler(enable=profiler_enabled, outfile=parsed.record_timing_info):

                with adapter_management():

                    # task, res = run_from_args(parsed)
                    task = parsed.cls.from_args(args=parsed)
                    res = task.run()
                    success = task.interpret_results(res)

                return res, success

    def build(self, selector_name=None, select=None, exclude=None, defer=None) -> RunExecutionResult:
        args = parse_args(['build'] + sys.argv[2:])
        args.cls = DeferredBuildTask
        args.selector_name = selector_name
        args.select = select
        args.exclude = exclude
        args.defer = defer
        return self.call(args)

    def list(self, selector_name=None, select=None, exclude=None, defer=None) -> RunExecutionResult:
        args = parse_args(['list'] + sys.argv[2:])
        args.cls = DeferredListTask
        args.selector_name = selector_name
        args.select = select
        args.exclude = exclude
        args.defer = defer
        return self.call(args)
