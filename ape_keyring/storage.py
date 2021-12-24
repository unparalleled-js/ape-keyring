from typing import List, Optional

import keyring
from ape.logging import logger
from keyring.errors import PasswordDeleteError

SERVICE_NAME = "ape-keyring"
ACCOUNTS_TRACKER_KEY = "ape-keyring-aliases"
ENVIRONMENT_VARIABLES_TRACKER_KEY = "ape-keyring-env-vars"


class SecretStorage:
    def __init__(self, tracker_key: str):
        """
        Initialize a new base-storage class.

        Args:
            tracker_key (str): The key-name for storing a comma-separated list
              of items tracked.
        """

        self._tracker_key = tracker_key

    @property
    def keys_str(self) -> str:
        """
        A stored, comma-separated list of items. This is for knowing which items
        we have stored.

        Returns:
            str
        """

        return _get_secret(self._tracker_key) or ""

    @property
    def keys(self) -> List[str]:
        """
        A list of stored item keys. Each key can unlock a secret.

        Returns:
            List[str]
        """

        return list(set([k for k in self.keys_str.split(",") if k]))

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
            new_keys_str = f"{self.keys_str},{key}" if self.keys_str else key
            _set_secret(self._tracker_key, new_keys_str)

        _set_secret(key, secret)

    def delete_secret(self, key: str):
        if key in self.keys:
            new_keys_str = ",".join([k for k in self.keys if k != key])
            _set_secret(self._tracker_key, new_keys_str)

        _delete_secret(key)

    def delete_all(self):
        for key in self.keys:
            _delete_secret(key)

        _delete_secret(self._tracker_key)


account_storage = SecretStorage(ACCOUNTS_TRACKER_KEY)
"""A storage class for storing account private-keys."""

environment_variable_storage = SecretStorage(ENVIRONMENT_VARIABLES_TRACKER_KEY)
"""A storage class for storing environment variables."""


def _get_secret(key: str) -> str:
    return keyring.get_password(SERVICE_NAME, key)


def _set_secret(key: str, secret: str):
    keyring.set_password(SERVICE_NAME, key, secret)


def _delete_secret(key: str):
    try:
        keyring.delete_password(SERVICE_NAME, key)
    except PasswordDeleteError:
        logger.debug(f"Failed to delete '{key}' - it does not exist.")
        return
