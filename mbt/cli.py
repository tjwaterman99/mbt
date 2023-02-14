import json
import click
from dbt import version as dbt_version
from mbt.services.dbt import Dbt


@click.group()
def cli():
    """
    mbt - helpers for working with dbt
    """

    pass


@cli.command()
def version():
    """
    Print version information
    """

    print("0.1.0")


@cli.command()
def debug():
    """
    Print debug information
    """

    dbt = Dbt()

    data = {
        'version': '0.1.0',
        'dbt': {
            'version': str(dbt_version.get_installed_version()),
            'project_dir': dbt.config.project_root,
            'profile': dbt.config.profile_name
        }
    }

    print(json.dumps(data))


@cli.command()
@click.option('--selector', help="The named selector to use")
def list(selector):
    """
    Print all changed models
    """

    dbt = Dbt()
    resp = dbt.list(selector=selector)


@cli.command()
@click.option('--target', '-t', help="The target to build against")
def build(target):
    """
    Run all changed Models, Tests, Seeds, and Snapshots in DAG order
    """

    dbt = Dbt()
    resp = dbt.build(target=target)