import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import keyring
from ape.logging import logger
from keyring.errors import PasswordDeleteError

SERVICE_NAME = "ape-keyring"
ACCOUNTS_TRACKER_KEY = "ape-keyring-accounts"
SECRETS_TRACKER_KEY = "ape-keyring-secrets"


class SecretStorage:
    def __init__(self, tracker_key: str, data_folder: Optional[Path] = None):
        """
        Initialize a new base-storage class.

        Args:
            tracker_key (str): The key-name for storing a comma-separated list
              of items tracked.
            data_folder (Optional[Path]): The path to the plugin's data.
              If given ``None``, defaults to  ``Path.home() / ".ape" / "keyring"``.
              Defaults to ``None``.
        """

        self._tracker_key = tracker_key
        self._data_folder = data_folder or Path.home() / ".ape" / "keyring"

    def __iter__(self):
        for key in self.keys:
            secret = self.get_secret(key)
            if secret:
                yield key, secret

    @property
    def data_file_path(self) -> Path:
        return self._data_folder / "data.json"

    @property
    def plugin_data(self) -> Dict:
        if self.data_file_path.is_file():
            return json.loads(self.data_file_path.read_text())

        return {}

    @property
    def keys(self) -> List[str]:
        """
        A list of stored item keys. Each key can unlock a secret.

        Returns:
            List[str]
        """

        return self.plugin_data.get(self._tracker_key, [])

    def get_secret(self, key: str) -> Optional[str]:
        """
        Get a secret.

        Args:
            key (str): The key for the secret, such as an account alias
              or environment variable name.

        Returns:
            str: The secret value from the OS secure-storage.
        """
        if key not in self.keys:
            return None

        return _get_secret(key)

    def store_secret(self, key: str, secret: str):
        """
        Add a new item to be tracked.

        Args:
            key (str): The new key for the item.
            secret (str): The value of the secret to store.
        """

        if key not in self.keys:
            self._track([*self.keys, key])

        _set_secret(key, secret)

    def delete_secret(self, key: str):
        if key in self.keys:
            self._track([k for k in self.keys if k != key])

        return _delete_secret(key)

    def delete_all(self):
        for key in self.keys:
            _delete_secret(key)

    def _track(self, new_keys: List[str]):
        self._store_public_data(self._tracker_key, new_keys)

    def _store_public_data(self, key: str, value: Any):
        self._data_folder.mkdir(exist_ok=True, parents=True)
        data = {**dict(self.plugin_data), key: value}
        if self.data_file_path.exists():
            self.data_file_path.unlink()

        self.data_file_path.write_text(json.dumps(data))


account_storage = SecretStorage(ACCOUNTS_TRACKER_KEY)
"""A storage class for storing account private-keys."""

secret_storage = SecretStorage(SECRETS_TRACKER_KEY)
"""A storage class for storing secrets."""


def _get_secret(key: str) -> Optional[str]:
    try:
        return keyring.get_password(SERVICE_NAME, key)
    except KeyError:
        return None


def _set_secret(key: str, secret: str):
    if not key or not secret:
        return

    keyring.set_password(SERVICE_NAME, key, secret)


def _delete_secret(key: str):
    if not key:
        return False

    try:
        keyring.delete_password(SERVICE_NAME, key)
        return True
    except (PasswordDeleteError, AssertionError) as err:
        logger.debug(err)
        return False
