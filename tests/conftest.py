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


@dataclass
class DbtResult:
    res: Any
    success: Any
    stdout: str
    summary: EndOfRunSummary


def process_stdout_mock(stdout_mock):
    return '\n'.join([''.join(args[0]) for args, kwargs in stdout_mock.call_args_list])


def process_run_summary(event_manager_mock):
    messages = [args[0] for args, kwargs in event_manager_mock.call_args_list]
    summary_events = [m for m in messages if type(m) == EndOfRunSummary]
    if summary_events:
        return summary_events[0] 





class Dbt:
    def __init__(self, project_dir=None):
        self.project_dir = project_dir or os.getcwd()

    def call(self, command):
        with patch('builtins.print') as stdout_mock:
            with patch('dbt.events.eventmgr.EventManager.fire_event') as event_manager_mock:
                default_flags = ['--no-use-colors']
                default_flags.extend(command)
                # TODO: instead of using handle_and_check directly, we should create our own
                # service to call dbt
                res, success = handle_and_check(default_flags)
                return DbtResult(
                    stdout=process_stdout_mock(stdout_mock),
                    summary=process_run_summary(event_manager_mock),
                    res=res, 
                    success=success
                )

    def debug(self, *args):
        command = ['debug', '--project-dir', self.project_dir]
        command.extend(args)
        return self.call(command)

    def build(self, *args):
        command = ['build', '--project-dir', self.project_dir]
        command.extend(args)
        return self.call(command)



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
        dbt=Dbt(project_dir=str(project_path.absolute())),
        db=db
    )
