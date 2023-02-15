import sys
from argparse import Namespace
from dbt.task.build import BuildTask
from dbt.task.list import ListTask
from dbt.contracts.results import RunExecutionResult
from dbt.graph.selector_spec import SelectionUnion, SelectionCriteria
from dbt.lib import get_dbt_config as _get_dbt_config
from dbt.main import parse_args, log_manager, adapter_management
from dbt.config.profile import read_user_config
from dbt.config.runtime import RuntimeConfig
from dbt.profiler import profiler
import dbt.flags as flags
import dbt

from mbt.config import Config


config = Config()


def get_dbt_args(command: str, cls=None, project_dir=None, **kwargs) -> Namespace:
    """
    Generate and monkeypatch the Namespace produced by dbt's ArgParser
    for a command
    """

    default_args = parse_args([command])
    for k, v in kwargs.items():
        setattr(default_args, k, v)

    if cls:
        default_args.cls = cls
    if project_dir:
        default_args.project_dir = project_dir

    return default_args


def get_dbt_config(args=None) -> RuntimeConfig:
    """
    Generate and monkeypatch a dbt config from a set of dbt args.
    """

    dbt_config = _get_dbt_config(project_dir=args.project_dir, args=args)
    dbt_config.get_default_selector_name = lambda: 'changed'
    dbt_config.selectors['changed'] = get_autodefer_selector()
    return dbt_config


# TODO: implement the git service to identify changed files on the branch (via Merge Base?)
def get_autodefer_selector():
    """
    Generate a dbt selector for autodeferring.
    """

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
    return auto_defer_selector


def run_dbt(args):
    """
    Runs dbt from a given set of args.
    """

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


class DeferredBuildTask(BuildTask):

    def __init__(self, args, config):
        super().__init__(args, config=get_dbt_config(args=args))

    def _get_deferred_manifest(self):
        # Call this from the function instead
        from mbt.services.github import GitHub
        artifacts = GitHub().artifacts()
        return artifacts


class DeferredListTask(ListTask):
    
    def __init__(self, args, config):
        super().__init__(args, config=get_dbt_config(args=args))


class Dbt:
    """
    Service for interacting with dbt
    """

    def __init__(self, project_dir=None):
        self.project_dir = project_dir

    def call(self, args):
        if self.project_dir:
            args.project_dir = self.project_dir
        return run_dbt(args)

    def build(self, **kwargs) -> RunExecutionResult:
        args = get_dbt_args('build', cls=DeferredBuildTask, **kwargs)
        return self.call(args)

    # TODO: can have an optional "quiet" arg here to just return the list
    # of nodes. From that list we can select other details about the model such as
    # its tests, or its schema + name, in order to retrieve the quality checks
    def list(self, **kwargs) -> RunExecutionResult:
        args = get_dbt_args('list', cls=DeferredListTask, **kwargs)
        return self.call(args)
