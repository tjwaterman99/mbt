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


def test_github_manifest_patch(manifest, project: Project):
    assert project.github.get_latest_manifest() == manifest


def test_dbt_project_table_names(project: Project):
    project.query('create table sometable (a int)')
    table_names = project.table_names()
    assert 'sometable' in table_names
    assert len(table_names) == 1
    

# TODO: make sure the build command always writes into a fresh database
# and check that the database is getting the relevant tables populated.
# We can add a method to the `project` object for querying the dbs
