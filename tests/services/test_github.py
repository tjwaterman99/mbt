from mbt.services.github import GitHub


def test_github_artifacts(project):
    gh = GitHub()
    assert gh.artifacts().metadata.dbt_version is not None
