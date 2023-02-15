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
    assert len(project.table_names()) == 0
    resp, success = project.dbt.call('build')
    assert success
    assert 'test_my_first_dbt_model' in project.table_names()
    assert 'test_my_second_dbt_model' in project.table_names()
    assert len(project.table_names()) == 2


def test_dbt_build(project: Project):
    resp, success = project.dbt.build()
    assert success
    assert 'test_my_first_dbt_model' in project.table_names()
    assert len(project.table_names()) == 1


def test_dbt_list(project: Project):
    resp, success = project.dbt.list()
    assert success
    assert len(resp) > 0


def test_dbt_build_with_prod_target(project: Project):
    resp, success = project.dbt.build(target='prod')
    assert success
    assert 'prod_my_first_dbt_model' in project.table_names()
    assert len(project.table_names()) == 1
    

def test_dbt_build_with_select(project: Project):
    resp, success = project.dbt.build(select='my_first_dbt_model')
    assert success
    assert 'test_my_first_dbt_model' in project.table_names()
    assert len(project.table_names()) == 1
