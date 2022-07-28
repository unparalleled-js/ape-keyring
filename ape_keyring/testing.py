from keyring.backend import KeyringBackend

from ape_keyring.storage import ACCOUNTS_TRACKER_KEY, SECRETS_TRACKER_KEY, SERVICE_NAME


def _require_ape(service_name: str, msg: str):
    if service_name != SERVICE_NAME:
        raise AssertionError(msg)


class MockBackend(KeyringBackend):
    _storage = {ACCOUNTS_TRACKER_KEY: "", SECRETS_TRACKER_KEY: ""}

    def set_password(self, servicename, username, password):
        _require_ape(servicename, "Saving non-ape secret.")
        self._storage[username] = password

    def get_password(self, servicename, username):
        _require_ape(servicename, "Requesting non-ape secret.")
        return self._storage[username]

    def delete_password(self, servicename, username):
        _require_ape(servicename, "Deleting non-ape secret.")

        if username not in self._storage:
            raise AssertionError(f"Deleting non-stored username '{username}'.")

        del self._storage[username]
