import tempfile
from pathlib import Path

import ape
import keyring.backend
import pytest
from ape._cli import cli as root_cli
from click.testing import CliRunner

from ape_keyring._secrets import get_secret_manager
from ape_keyring.storage import SecretStorage
from ape_keyring.testing import MockBackend

TEMP_DATA_FOLDER = Path(tempfile.mkdtemp()).resolve()
PROJECT_DIRECTORY = Path(__file__).parent


@pytest.fixture(scope="session", autouse=True)
def secret_manager():
    storage = SecretStorage("secrets", data_folder=TEMP_DATA_FOLDER)
    return get_secret_manager(PROJECT_DIRECTORY, storage)


@pytest.fixture(scope="session")
def config():
    return ape.config


@pytest.fixture(scope="session", autouse=True)
def from_tests_directory(config):
    with config.using_project(PROJECT_DIRECTORY):
        yield


@pytest.fixture(autouse=True)
def mock_keyring_backend():
    keyring.set_keyring(MockBackend())


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli():
    return root_cli


@pytest.fixture
def test_account():
    return ape.accounts.test_accounts[0]
