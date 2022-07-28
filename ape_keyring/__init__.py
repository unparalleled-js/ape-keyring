from pathlib import Path

import ape.plugins

from ._secrets import Scope, get_secret_manager
from .accounts import KeyringAccount, KeyringAccountContainer
from .config import KeyringConfig


@ape.plugins.register(ape.plugins.Config)
def config_class():
    return KeyringConfig


@ape.plugins.register(ape.plugins.AccountPlugin)
def account_types():
    return KeyringAccountContainer, KeyringAccount


# Sync environment variables if configured to do so.
secret_manager = get_secret_manager(Path.cwd())
secret_manager.set_environment_variables()

__all__ = ["Scope", "secret_manager"]
