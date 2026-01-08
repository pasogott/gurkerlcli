"""Main CLI entry point."""

import click

from . import __version__
from .commands.auth_cmd import auth_group
from .commands.cart_cmd import cart_group
from .commands.lists_cmd import lists_cmd
from .commands.orders_cmd import orders_group
from .commands.search_cmd import search


@click.group()
@click.version_option(version=__version__, prog_name="gurkerlcli")
@click.help_option("-h", "--help")
def cli() -> None:
    """gurkerlcli - CLI for gurkerl.at online grocery shopping.

    \b
    Examples:
        # Login
        gurkerlcli auth login

        # Search products
        gurkerlcli search "bio milch"

        # Add to cart
        gurkerlcli cart add 12345 --quantity 2

        # View cart
        gurkerlcli cart list

        # View orders
        gurkerlcli orders list

    \b
    Documentation:
        https://github.com/yourusername/gurkerlcli

    \b
    Support:
        For issues and feature requests, visit:
        https://github.com/yourusername/gurkerlcli/issues
    """
    pass


# Register command groups
cli.add_command(auth_group)
cli.add_command(cart_group)
cli.add_command(lists_cmd)
cli.add_command(orders_group)

# Register standalone commands
cli.add_command(search)


if __name__ == "__main__":
    cli()
