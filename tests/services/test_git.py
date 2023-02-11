from mbt.services.git import Git


def test_git_init():
    git = Git()
    assert git is not None