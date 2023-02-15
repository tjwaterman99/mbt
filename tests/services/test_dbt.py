from pytest import fixture
from dbt.task.build import BuildTask
from mbt.services.dbt import Dbt, get_dbt_args, get_dbt_config
from conftest import Project


def test_get_dbt_args():
    args = get_dbt_args('build')
    assert args.cls == BuildTask


    args = get_dbt_args('build', selector='test')
    assert args.selector == 'test'


def test_dbt_call(project: Project):
    resp, success = project.dbt.call('build')
    assert success
    assert 'test_my_first_dbt_model' in project.table_names()
    assert 'test_my_second_dbt_model' in project.table_names()
    assert len(project.table_names()) == 2


def test_dbt_build(project: Project):
    resp, success = project.dbt.build()
    assert success
    assert len(resp) > 0


def test_dbt_list(project: Project):
    resp, success = project.dbt.list()
    assert success
    assert len(resp) > 0


def test_dbt_build_prod_with_target(project: Project):
    resp, success = project.dbt.build(target='test')
    assert success
    assert len(resp) > 0