import os


class Config:
    def __init__(self, dbt_project_dir=None, github_token=None):
        self.dbt_project_dir = dbt_project_dir or os.getenv('DBT_PROJECT_DIR')
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
