import os
from distutils.dir_util import copy_tree
from shutil import rmtree
from pathlib import Path
from dataclasses import dataclass
from unittest.mock import patch
from typing import Any
from pytest import fixture
from dbt.main import handle_and_check


@dataclass
class DbtResult:
    res: Any
    success: Any
    stdout: str


def process_stdout_mock(stdout_mock):
    return '\n'.join([''.join(args[0]) for args, kwargs in stdout_mock.call_args_list])


class Dbt:
    def __init__(self, project_dir=None):
        self.project_dir = project_dir or os.getcwd()

    def call(self, command):
        with patch('builtins.print') as stdout_mock:
            default_flags = ['--no-use-colors']
            default_flags.extend(command)
            # TODO: instead of using handle_and_check directly, we should create our own
            # service to call dbt
            res, success = handle_and_check(default_flags)
            return DbtResult(
                stdout=process_stdout_mock(stdout_mock), 
                res=res, 
                success=success
            )

    def debug(self, *args):
        command = ['debug', '--project-dir', self.project_dir]
        command.extend(args)
        return self.call(command)


@dataclass
class Project:
    path: Path
    dbt: Dbt


@fixture
def fixtures_dir():
    return Path(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures'))


@fixture
def project(fixtures_dir: Path, tmp_path: Path) -> Project:
    project_path = fixtures_dir.absolute() / 'test_project'
    
    try:
        rmtree(project_path / 'logs')
    except FileNotFoundError:
        pass

    try:
        rmtree(project_path / 'target')
    except FileNotFoundError:
        pass

    copy_tree(fixtures_dir.absolute(), str(tmp_path.absolute()))
    
    return Project(
        path=project_path,
        dbt=Dbt(project_dir=str(project_path.absolute()))
    )
