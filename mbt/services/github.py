from dbt.contracts.graph.manifest import WritableManifest
from mbt.config import Config


config = Config()


class GitHub:

    def __init__(self, token=None):
        self.token = token or config.github_token

    def get_latest_manifest(repo=None, branch=None, workflow=None) -> WritableManifest:
        pass
