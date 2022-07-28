# ape-keyring

Store secrets and manage accounts for `ape` using [keyring](https://pypi.org/project/keyring/).

## Dependencies

* [python3](https://www.python.org/downloads) version 3.7.2 or greater, python3-dev

## Installation

### via `pip`

You can install the latest release via [`pip`](https://pypi.org/project/pip/):

```bash
pip install ape-keyring
```

### via `setuptools`

You can clone the repository and use [`setuptools`](https://github.com/pypa/setuptools) for the most up-to-date version:

```bash
git clone https://github.com/ApeWorX/ape-keyring.git
cd ape_keyring
python3 setup.py install
```

## Quick Usage

Add accounts to keyring:

```bash
ape keyring import keyring_dev_0
```

and then when it prompts you, input your private key.

To add secrets to keyring:

```bash
ape keyring set WEB3_API_KEY
```

and then when it prompts you, input the value to your secret.

Optionally, scope your secrets to the active project.

```bah
ape keyring set DEPLOYMENT_SECRET --scope project 
```

To enable your secrets to become environment variables at runtime,
use the `ape-config.yaml` option `set_env_vars`:

```yaml
keyring:
  set_env_vars: true
```

## License

This project is licensed under the [Apache 2.0](LICENSE).
