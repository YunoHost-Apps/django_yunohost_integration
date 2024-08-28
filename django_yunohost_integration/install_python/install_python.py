#!/usr/bin/env python3

"""
    Setup Python Interpreter
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This script downloads, builds and installs a Python interpreter, but:
    - only if the required version is not already installed
    - only if the required version is not already built

    Download Python source code from official Python FTP server.
    Download only over verified HTTPS connection.
    Verify the download with the GPG signature, if gpg is available.

    Has a CLI interface e.g.:

        $ python install_python.py --help

    Defaults to Python 3.11 and ~/.local/ as prefix.
"""
from __future__ import annotations

import argparse
import hashlib
import logging
import os
import re
import shlex
import shutil
import ssl
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path


assert sys.version_info >= (3, 9), f'Python version {sys.version_info} is too old!'


DEFAULT_MAJOR_VERSION = '3.11'
PY_FTP_INDEX_URL = 'https://www.python.org/ftp/python/'


GPG_KEY_IDS = {
    # from: https://www.python.org/downloads/
    #
    # Thomas Wouters (3.12.x and 3.13.x source files and tags) (key id: A821E680E5FA6305):
    '3.13': '7169605F62C751356D054A26A821E680E5FA6305',
    '3.12': '7169605F62C751356D054A26A821E680E5FA6305',
    #
    # Pablo Galindo Salgado (3.10.x and 3.11.x source files and tags) (key id: 64E628F8D684696D):
    '3.11': 'A035C8C19219BA821ECEA86B64E628F8D684696D',
    '3.10': 'A035C8C19219BA821ECEA86B64E628F8D684696D',
}

# https://docs.python.org/3/using/configure.html#cmdoption-prefix
DEFAULT_INSTALL_PREFIX = '/usr/local'

TEMP_PREFIX = 'setup_python_'

logger = logging.getLogger(__name__)


class TemporaryDirectory:
    """tempfile.TemporaryDirectory in Python 3.9 has no "delete", yet."""

    def __init__(self, prefix, delete: bool):
        self.prefix = prefix
        self.delete = delete

    def __enter__(self) -> Path:
        self.temp_path = Path(tempfile.mkdtemp(prefix=self.prefix))
        return self.temp_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.delete:
            shutil.rmtree(self.temp_path, ignore_errors=True)
        if exc_type:
            return False


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(
        url=url,
        context=ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH),
    ) as response:
        return response.read()


def get_html_page(url) -> str:
    logger.debug(f'Getting HTML page from {url}')
    html = fetch(url).decode('utf-8')
    assert html, 'Failed to get Python FTP index page'
    return html


def extract_versions(*, html, major_version) -> list[str]:
    pattern = rf'href="({re.escape(major_version)}\.[0-9]+)'
    logger.debug(f'Extracting versions with pattern: {pattern}')
    versions = re.findall(pattern, html)
    versions.sort(reverse=True)
    logger.debug(f'Extracted versions: {versions}')
    return versions


def get_latest_versions(*, html, major_version) -> str:
    latest_versions = extract_versions(html=html, major_version=major_version)[0]
    logger.info(f'Latest version of Python {major_version}: {latest_versions}')
    return latest_versions


def run(args, **kwargs):
    logger.debug(f'Running: {shlex.join(str(arg) for arg in args)} ({kwargs=})')
    return subprocess.run(args, **kwargs)


def run_build_step(args, *, step: str, cwd: Path) -> None:
    with tempfile.NamedTemporaryFile(prefix=f'{TEMP_PREFIX}_{step}_', suffix='.txt', delete=False) as temp_file:
        logger.info(f'Running: {shlex.join(str(arg) for arg in args)}... Output in {temp_file.name}')
        try:
            subprocess.run(args, stdout=temp_file, stderr=temp_file, check=True, cwd=cwd)
        except subprocess.SubprocessError as err:
            logger.error(f'Failed to run {step} step: {err}')
            run(['tail', temp_file.name])
            raise


def get_python_version(python_bin) -> str:
    logger.debug(f'Check {python_bin} version')
    full_version = run([python_bin, '--version'], capture_output=True, text=True).stdout.split()[1]
    logger.info(f'{python_bin} version: {full_version}')
    return full_version


def download2temp(*, temp_path: Path, base_url: str, filename: str) -> Path:
    url = f'{base_url}/{filename}'
    dst_path = temp_path / filename
    logger.info(f'Downloading {url} into {dst_path}...')
    dst_path.write_bytes(fetch(url))
    logger.info(f'Downloaded {filename} is {dst_path.stat().st_size} Bytes')
    return dst_path


def verify_download(*, major_version: str, tar_file_path: Path, asc_file_path: Path):
    hash_obj = hashlib.sha256(tar_file_path.read_bytes())
    logger.info(f'Downloaded sha256: {hash_obj.hexdigest()}')

    if gpg_bin := shutil.which('gpg'):
        logger.debug(f'Verifying signature with {gpg_bin}...')
        assert major_version in GPG_KEY_IDS, f'No GPG key ID for Python {major_version}'
        gpg_key_id = GPG_KEY_IDS[major_version]
        run([gpg_bin, '--keyserver', 'hkps://keys.openpgp.org', '--recv-keys', gpg_key_id], check=True)
        run([gpg_bin, '--verify', asc_file_path, tar_file_path], check=True)
        run(['gpgconf', '--kill', 'all'], check=True)
    else:
        logger.warning('No GPG verification possible! (gpg not found)')


def install_python(
    major_version: str,
    *,
    write_check: bool = True,
    delete_temp: bool = True,
) -> Path:
    logger.info(f'Installing Python {major_version} interpreter.')

    # Check system Python version
    for try_version in (major_version, '3'):
        filename = f'python{try_version}'
        logger.debug(f'Checking {filename}...')
        if python3bin := shutil.which(filename):
            if get_python_version(python3bin).startswith(major_version):
                logger.info('Python version already installed')
                return Path(python3bin)

    # Get latest full version number of Python from Python FTP:
    py_required_version = get_latest_versions(
        html=get_html_page(PY_FTP_INDEX_URL),
        major_version=major_version,
    )

    local_bin_path = Path(DEFAULT_INSTALL_PREFIX) / 'bin'

    # Check existing built version of Python in /usr/local/bin
    local_python_path = local_bin_path / f'python{major_version}'
    if local_python_path.exists() and get_python_version(local_python_path) == py_required_version:
        logger.info('Local Python is up to date')
        return local_python_path

    # Before we start building Python, check if we have write permissions:
    if write_check and not os.access(local_bin_path, os.W_OK):
        raise PermissionError(f'No write permission to {local_bin_path} (Hint: Call with "sudo" ?!)')

    # Download, build and Setup Python
    with TemporaryDirectory(prefix=TEMP_PREFIX, delete=delete_temp) as temp_path:
        base_url = f'https://www.python.org/ftp/python/{py_required_version}'

        tar_filename = f'Python-{py_required_version}.tar.xz'
        asc_filename = f'{tar_filename}.asc'
        asc_file_path = download2temp(
            temp_path=temp_path,
            base_url=base_url,
            filename=asc_filename,
        )
        tar_file_path = download2temp(
            temp_path=temp_path,
            base_url=base_url,
            filename=tar_filename,
        )
        verify_download(
            major_version=major_version,
            tar_file_path=tar_file_path,
            asc_file_path=asc_file_path,
        )

        tar_bin = shutil.which('tar')
        logger.debug(f'Extracting {tar_file_path} with ...')
        run([tar_bin, 'xf', tar_file_path], check=True, cwd=temp_path)
        extracted_dir = temp_path / f'Python-{py_required_version}'

        logger.info(f'Building Python {py_required_version} (may take a while)...')

        run_build_step(
            ['./configure', '--enable-optimizations'],
            step='configure',
            cwd=extracted_dir,
        )
        run_build_step(
            ['make', f'-j{os.cpu_count()}'],
            step='make',
            cwd=extracted_dir,
        )
        run_build_step(
            ['make', 'altinstall'],
            step='install',
            cwd=extracted_dir,
        )

    logger.info(f'Python {py_required_version} installed to {local_python_path}')

    local_python_version = get_python_version(local_python_path)
    assert local_python_version == py_required_version, f'{local_python_version} is not {py_required_version}'

    return local_python_path


def main() -> Path:
    parser = argparse.ArgumentParser(
        description='Setup Python Interpreter',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        'major_version',
        nargs=argparse.OPTIONAL,
        default=DEFAULT_MAJOR_VERSION,
        choices=sorted(GPG_KEY_IDS.keys()),
        help='Specify the Python version',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='count',
        default=0,
        help='Increase verbosity level (can be used multiple times, e.g.: -vv)',
    )
    parser.add_argument(
        '--skip-temp-deletion',
        action='store_true',
        help='Skip deletion of temporary files created during build steps',
    )
    parser.add_argument(
        '--skip-write-check',
        action='store_true',
        help='Skip the test for write permission to /usr/local/bin',
    )
    args = parser.parse_args()
    verbose2level = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    logging.basicConfig(
        level=verbose2level.get(args.verbose, logging.DEBUG),
        format='%(levelname)9s %(message)s',
        stream=sys.stderr,
    )
    logger.debug(f'Arguments: {args}')
    return install_python(
        major_version=args.major_version,
        write_check=not args.skip_write_check,
        delete_temp=not args.skip_temp_deletion,
    )


if __name__ == '__main__':
    python_path = main()
    print(python_path)
