from click.testing import CliRunner
from conftest import Project
import os


def test_fixtures_dir_has_dbt_project(fixtures_dir):
    assert 'test_project' in os.listdir(fixtures_dir)


def test_dbt_project_exists(project: Project):
    assert project.path.exists()


def test_dbt_project_dir_is_clean(project: Project):
    files = list(p.name for p in project.path.iterdir())
    assert 'dbt_project.yml' in files
    assert 'profiles.yml' in files
    assert 'logs' not in files
    assert 'target' not in files


def test_dbt_debug_passes(project: Project):
    resp = project.dbt.debug()
    assert resp.success == True
    assert 'All checks passed!' in resp.stdout
