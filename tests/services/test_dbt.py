from pytest import fixture
from mbt.services.dbt import Dbt
from conftest import Project


def test_config(project: Project):
    assert project.dbt.config.project_name == 'test_project'
    assert 'changed' in project.dbt.config.selectors


def test_dbt_build(project: Project):
    resp = project.dbt.build()
    assert len(resp) > 0


def test_dbt_list(project: Project):
    resp = project.dbt.list()
    assert len(resp) > 0
