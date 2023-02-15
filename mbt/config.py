import os


class Config:
    def __init__(self, dbt_project_dir=None, github_token=None, homedir=None):
        self.dbt_project_dir = dbt_project_dir or os.getenv('DBT_PROJECT_DIR')
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.homedir = os.path.join(os.path.expanduser('~'), '.mbt')
        self.cache_path = os.path.join(self.homedir, 'cache.sqlite')

        if not os.path.exists(self.homedir):
            os.makedirs(self.homedir)