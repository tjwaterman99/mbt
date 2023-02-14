import os


class Config:
    def __init__(self, dbt_project_dir=None):
        self.dbt_project_dir = dbt_project_dir or os.getenv('DBT_PROJECT_DIR')
