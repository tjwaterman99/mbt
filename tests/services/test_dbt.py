from pytest import fixture
from mbt.services.dbt import Dbt


@fixture
def dbt() -> Dbt:
    return Dbt()


def test_config(dbt: Dbt):
    assert dbt.config.project_name == 'test_project'
    assert 'changed' in dbt.config.selectors


def test_dbt_build(dbt: Dbt):
    resp = dbt.build()
    assert len(resp) > 0


def test_dbt_list(dbt: Dbt):
    resp = dbt.list()
    assert len(resp) > 0
