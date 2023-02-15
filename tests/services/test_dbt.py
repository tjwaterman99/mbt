from pytest import fixture
from dbt.task.build import BuildTask
from mbt.services.dbt import Dbt, get_dbt_args, get_dbt_config
from conftest import Project


def test_get_dbt_args():
    args = get_dbt_args('build')
    assert args.cls == BuildTask


    args = get_dbt_args('build', selector='test')
    assert args.selector == 'test'


def test_dbt_build(project: Project):
    resp, success = project.dbt.build()
    assert success
    assert len(resp) > 0


def test_dbt_list(project: Project):
    resp, success = project.dbt.list()
    assert success
    assert len(resp) > 0
