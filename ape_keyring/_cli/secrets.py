from typing import List

import click
from ape.cli import ape_cli_context

from ape_keyring._secrets import Scope, get_secret_manager
from ape_keyring.args import scope_option, secret_argument


@click.group()
def secrets():
    """Manage secrets"""


@secrets.command("list")
@ape_cli_context()
def _list(cli_ctx):
    """List secrets"""

    secret_manager = get_secret_manager(cli_ctx.project_manager.path)

    if not secret_manager.secrets_exist:
        cli_ctx.logger.warning("No secrets found.")
        return

    def output_secret_list(header: str, secret_keys: List[str]) -> bool:
        if not secret_keys:
            return False

        click.echo(f"{header}:")
        for key in secret_keys:
            click.echo(f"  {key}")

        return True

    did_output = output_secret_list("Global secrets", secret_manager.global_keys)
    if did_output and secret_manager.project_keys:
        click.echo()

    output_secret_list("Project secrets", secret_manager.project_keys)


@secrets.command(name="set")
@secret_argument()
@ape_cli_context()
@scope_option()
def _set(cli_ctx, secret, scope):
    """Add or replace a secret"""
    value = click.prompt(f"Enter the secret value for '{secret}'", hide_input=True)
    secret_manager = get_secret_manager(cli_ctx.project_manager.path)
    secret_manager.store_secret(secret, value, scope=scope)
    cli_ctx.logger.success(f"Secret '{secret}' has been set.")


@secrets.command()
@ape_cli_context()
@secret_argument()
@scope_option()
def delete(cli_ctx, secret, scope):
    """Remove a secret"""

    secret_manager = get_secret_manager(cli_ctx.project_manager.path)
    did_delete = secret_manager.delete_secret(secret, scope=scope)
    if not did_delete:
        # Try to delete project secret
        if secret_manager.get_secret(secret, scope=Scope.PROJECT):
            do_delete = click.confirm(f"Delete project-scoped secret '{secret}'?")
            if do_delete:
                did_delete = secret_manager.delete_secret(secret, scope=scope.PROJECT)
        else:
            project_output = (
                f"(project={secret_manager.project_name})" if scope == Scope.PROJECT else ""
            )
            message = f"Failed to delete secret '{secret}'"
            if project_output:
                message = f"{message} {project_output}"
            cli_ctx.logger.warning(f"{message}.")

    if did_delete:
        message = f"Secret '{secret}' "
        if secret_manager.project_name:
            message = f"{message}(project={secret_manager.project_name}) "
        message = f"{message}has been unset."

        cli_ctx.logger.success(message)
