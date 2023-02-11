from git import Git as GitPy


class Git:
    def __init__(self):
        self._git = GitPy()