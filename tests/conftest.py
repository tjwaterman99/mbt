import os
from distutils.dir_util import copy_tree
from shutil import rmtree
from pathlib import Path
from dataclasses import dataclass
from unittest.mock import patch
from typing import Any
from pytest import fixture
from dbt.main import handle_and_check
from dbt.events.types import EndOfRunSummary
from sqlite3 import Connection as SqliteConnection, Row
from mbt.services.dbt import Dbt
import dbt.logger


@dataclass
class Project:
    path: Path
    dbt: Dbt
    db: SqliteConnection

    def query(self, sql):
        conn = self.db
        conn.row_factory = Row
        resp = conn.execute(sql).fetchall()
        return resp


@fixture
def fixtures_dir():
    return Path(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures'))


@fixture
def project(monkeypatch, fixtures_dir: Path, tmp_path: Path) -> Project:
    fixtures_path = fixtures_dir.absolute() / 'test_project'
    project_path = tmp_path.absolute() / 'test_project'

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
        dbt=Dbt(),
        db=db
    )
