import os

import pytest

from ape_keyring import Scope, secret_manager
from ape_keyring.config import KeyringConfig

GLOBAL_SECRET_KEY = "__GLOBAL_TEST_SECRET__"
PROJECT_SECRET_KEY = "__PROJECT_TEST_SECRET__"
GLOBAL_SECRET_VALUE = "test-global-secret-value"
PROJECT_SECRET_VALUE = "test-project-secret-value"

key_value_and_scope = pytest.mark.parametrize(
    "key,value,scope",
    [
        (GLOBAL_SECRET_KEY, GLOBAL_SECRET_VALUE, Scope.GLOBAL.value),
        (PROJECT_SECRET_KEY, PROJECT_SECRET_VALUE, Scope.PROJECT.value),
    ],
)


def clean():
    if GLOBAL_SECRET_KEY in secret_manager.global_keys:
        secret_manager.delete_secret(GLOBAL_SECRET_KEY)
    if PROJECT_SECRET_KEY in secret_manager.project_keys:
        secret_manager.delete_secret(PROJECT_SECRET_KEY)


@pytest.fixture(autouse=True)
def auto_clean():
    clean()
    yield
    clean()


@pytest.fixture
def temp_global_secret():
    if GLOBAL_SECRET_KEY not in secret_manager.global_keys:
        secret_manager.store_secret(GLOBAL_SECRET_KEY, GLOBAL_SECRET_VALUE, scope=Scope.GLOBAL)


@pytest.fixture
def temp_project_secret():
    if PROJECT_SECRET_KEY not in secret_manager.project_keys:
        secret_manager.store_secret(PROJECT_SECRET_KEY, PROJECT_SECRET_VALUE, scope=Scope.PROJECT)


@pytest.fixture
def temp_secrets(temp_global_secret, temp_project_secret):
    yield


@key_value_and_scope
def test_set(cli, runner, key, value, scope):
    result = runner.invoke(cli, ["keyring", "secrets", "set", key, "--scope", scope], input=value)
    assert result.exit_code == 0, result.output

    keys = (
        secret_manager.project_keys if scope == Scope.PROJECT.value else secret_manager.global_keys
    )
    opposite = [k for k in [GLOBAL_SECRET_KEY, PROJECT_SECRET_KEY] if k != key][0]
    assert key in keys
    assert opposite not in keys


@pytest.mark.parametrize("key", (GLOBAL_SECRET_KEY, PROJECT_SECRET_KEY))
def test_list(cli, runner, temp_secrets, key):
    result = runner.invoke(cli, ["keyring", "secrets", "list"])
    assert key in result.output


@key_value_and_scope
def test_delete(cli, runner, temp_secrets, key, value, scope):
    _ = value
    result = runner.invoke(cli, ["keyring", "secrets", "delete", key, "--scope", scope])
    assert result.exit_code == 0, result.output

    result = runner.invoke(cli, ["keyring", "secrets", "list"])
    assert key not in result.output


def test_config(config):
    plugin_config = config.get_config("keyring")
    assert isinstance(plugin_config, KeyringConfig)
    assert plugin_config.set_env_vars is True


@key_value_and_scope
def test_secrets_in_env(temp_secrets, key, value, scope):
    secret_manager.store_secret(key, value, scope=scope)
    assert os.environ.get(key) == value
    secret_manager.delete_secret(key, scope=scope)
    assert not os.environ.get(key)
