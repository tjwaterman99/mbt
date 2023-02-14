from argparse import Namespace
from dbt.task.build import BuildTask
from dbt.task.list import ListTask
from dbt.contracts.results import RunExecutionResult
from dbt.graph.selector_spec import SelectionUnion, SelectionCriteria
from dbt.lib import get_dbt_config as _get_dbt_config
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


# TODO: figure out how we add the target in here
def get_deferrable_args(select=None, selector_name=None, exclude=None, defer=False):
    ns = Namespace()
    ns.selector_name = selector_name
    ns.select = select
    ns.exclude = exclude
    ns.defer = defer
    ns.single_threaded = False
    ns.state = None
    ns.resource_types = None
    ns.models = None
    ns.output = 'path'
    return ns


class DeferredBuildTask(BuildTask):
    # TODO: overwrite to pull the manifest from GitHub
    # def _get_deferred_manifest():
    #     pass
    pass


class DeferredListTask(ListTask):
    pass


class Dbt:
    """
    Service for interacting with dbt
    """

    def __init__(self):
        self.config = get_dbt_config()

    def build(self, selector_name=None, select=None, exclude=None, defer=None) -> RunExecutionResult:
        args = get_deferrable_args(selector_name=selector_name, select=select, exclude=exclude, defer=defer)
        task = DeferredBuildTask(args, self.config)
        return task.run()

    def list(self, selector_name=None, select=None, exclude=None, defer=None) -> RunExecutionResult:
        args = get_deferrable_args(selector_name=selector_name, select=select, exclude=exclude, defer=defer)
        task = DeferredListTask(args, self.config)
        return task.run()
