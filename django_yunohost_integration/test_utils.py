import base64
from typing import Optional

import requests
from packaging.version import Version


def generate_basic_auth(username, password):
    basic_auth = f'{username}:{password}'
    basic_auth_creds = bytes(basic_auth, encoding='utf-8')
    creds = str(base64.b64encode(basic_auth_creds), encoding='utf-8')
    return f'basic {creds}'


def get_github_version_tag(github_project_url: str) -> Optional[Version]:
    """
    Returns the last non-prerelease Version objects from github tags.
    """
    assert github_project_url.startswith(
        'https://github.com/'
    ), f'No Github Project url: {github_project_url!r}'

    api_url = github_project_url.replace('github.com', 'api.github.com/repos')
    tags = requests.get(f'{api_url}/tags').json()
    for tag in tags:
        version_str = tag['name']
        ver_obj = Version(version_str)
        if ver_obj.base_version and not ver_obj.is_prerelease:
            return ver_obj

    raise AssertionError(
        f'No version found from github tags: {api_url} (check: {github_project_url})'
    )


def assert_project_version(current_version: str, github_project_url: str) -> None:
    """
    Check that current version is the last version from Github tags.
    """
    current_ver_obj = Version(current_version)
    github_ver = get_github_version_tag(github_project_url=github_project_url)
    assert github_ver == current_ver_obj, (
        f'Current version from {github_project_url} is: {github_ver}'
        f' but current package version is: {current_ver_obj}'
    )
