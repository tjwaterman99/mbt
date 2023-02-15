from conftest import Project
import os


def test_cache_homedir(project: Project):
    assert os.path.exists(project.cache.path)


def test_cache_inserts(project: Project, manifest):
    project.cache.set('a', data=manifest)
    data = project.cache.get('a')
    assert data == manifest
