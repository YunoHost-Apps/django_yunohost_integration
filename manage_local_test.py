#!.venv/bin/python3

"""
    Call the "manage.py" from the local test environment.
    Just copy&paste this file to your real Yunohost package.
"""

from django_yunohost_integration.local_test import run_local_test_manage


if __name__ == '__main__':
    run_local_test_manage(
        extra_env={'ENV_TYPE': 'local'},
        extra_replacements={
            '__PATH__': 'app_path',  # Simulate installation into "/app_path/" !
        },
    )
