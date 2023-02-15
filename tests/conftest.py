import os
from distutils.dir_util import copy_tree
from shutil import rmtree
from pathlib import Path
from dataclasses import dataclass
from dbt.contracts.graph.manifest import WritableManifest
from pytest import fixture
from sqlite3 import Connection as SqliteConnection, Row
from mbt.services.dbt import Dbt
from mbt.services.github import GitHub
from mbt.cache import Cache
from mbt.config import Config


@dataclass
class Project:
    path: Path
    dbt: Dbt
    db: SqliteConnection
    github: GitHub
    cache: Cache

    def query(self, sql):
        conn = self.db
        conn.row_factory = Row
        resp = conn.execute(sql).fetchall()
        return resp

    def table_names(self):
        resp = self.query('select distinct name as name from sqlite_master')
        return [r['name'] for r in resp]


@fixture
def fixtures_dir():
    return Path(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures'))


@fixture
def manifest(fixtures_dir: Path):
    manifest_path = fixtures_dir.absolute() / 'manifest.json'
    manifest = WritableManifest.read_and_check_versions(str(manifest_path))
    return manifest


@fixture
def project(monkeypatch, manifest, fixtures_dir: Path, tmp_path: Path) -> Project:
    fixtures_path = fixtures_dir.absolute() / 'test_project'
    project_path = tmp_path.absolute() / 'test_project'
    homedir = tmp_path.absolute() / '.mbt'
    config = Config(homedir=homedir)
    cache = Cache(path=config.cache_path)
    github = GitHub()
    
    monkeypatch.setattr('mbt.services.github.GitHub.get_latest_manifest', lambda self: manifest)

    copy_tree(str(fixtures_path), str(project_path))

    try:
        rmtree(project_path / 'logs')
    except FileNotFoundError:
        pass

    try:
        rmtree(project_path / 'target')
    except FileNotFoundError:
        pass

    monkeypatch.setenv('MBT_DATABASE_PATH', str(project_path / 'db.sqlite'))
    monkeypatch.setenv('MBT_SCHEMA_DIRECTORY', str(project_path / 'dbs'))

    db = SqliteConnection(os.getenv('MBT_DATABASE_PATH'))

    return Project(
        path=project_path,
        dbt=Dbt(project_dir=str(project_path)),
        db=db,
        github=github,
        cache=cache
    )
