sudo apt update
sudo apt install sqlite3
pipx install poetry
poetry install
alias build="poetry run dbt build --project-dir /workspaces/mbt/tests/fixtures/test_project"