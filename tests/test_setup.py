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


def test_dbt_build_passes(project: Project):
    resp = project.dbt.build()
    assert resp.success == True
    assert resp.summary.num_errors == 0
    assert project.query('select * from my_first_dbt_model')[0]["id"] == 1


# TODO: make sure the build command always writes into a fresh database
# and check that the database is getting the relevant tables populated.
# We can add a method to the `project` object for querying the dbs