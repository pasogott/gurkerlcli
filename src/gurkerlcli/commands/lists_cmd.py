"""Shopping lists commands."""

from __future__ import annotations

import json

import click
from rich.console import Console
from rich.table import Table

from gurkerlcli.client import GurkerlClient
from gurkerlcli.models import ShoppingList
from gurkerlcli.utils.formatting import print_error, print_success, print_info

console = Console()


@click.group(name="lists")
def lists_cmd() -> None:
    """Manage shopping lists."""
    pass


@lists_cmd.command(name="list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--debug", is_flag=True, help="Enable debug output")
def list_lists(output_json: bool, debug: bool) -> None:
    """List all shopping lists."""
    try:
        with GurkerlClient.from_config(debug=debug) as client:
            # Get shopping lists component
            response = client.get("/api/v1/components/shopping-lists")

            list_ids = response.get("shoppingLists", [])
            if not list_ids:
                print_info("No shopping lists found")
                return

            # Get details for each list
            lists = []
            for list_id in list_ids:
                try:
                    detail_response = client.get(f"/api/v2/shopping-lists/id/{list_id}")
                    shopping_list = ShoppingList(**detail_response)
                    lists.append(shopping_list)
                except Exception as e:
                    if debug:
                        print_error(f"Failed to fetch list {list_id}: {e}")
                    continue

            if not lists:
                print_error("No valid shopping lists found")
                return

            # Output
            if output_json:
                click.echo(
                    json.dumps([lst.model_dump(mode="json") for lst in lists], indent=2)
                )
            else:
                table = Table(title="Shopping Lists", show_header=True)
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Type", style="blue")
                table.add_column("Items", justify="right", style="yellow")
                table.add_column("Shared", justify="center")

                for lst in lists:
                    table.add_row(
                        str(lst.id),
                        lst.name,
                        lst.type,
                        str(len(lst.products)),
                        "✓" if lst.shared else "✗",
                    )

                console.print(table)
                console.print(f"\n[dim]Found {len(lists)} shopping lists[/dim]")

    except Exception as e:
        print_error(f"Failed to list shopping lists: {e}")
        if debug:
            raise


@lists_cmd.command(name="create")
@click.argument("name")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--debug", is_flag=True, help="Enable debug output")
def create_list(name: str, output_json: bool, debug: bool) -> None:
    """Create a new shopping list."""
    try:
        with GurkerlClient.from_config(debug=debug) as client:
            response = client.post(
                "/api/v1/shopping-lists",
                params={"source": "Shopping Lists"},
                json={"name": name},
            )

            list_id = response.get("id")
            if not list_id:
                print_error("Failed to create shopping list")
                return

            # Get full details
            detail_response = client.get(f"/api/v2/shopping-lists/id/{list_id}")
            shopping_list = ShoppingList(**detail_response)

            if output_json:
                click.echo(json.dumps(shopping_list.model_dump(mode="json"), indent=2))
            else:
                print_success(
                    f"Created shopping list '{shopping_list.name}' (ID: {shopping_list.id})"
                )

    except Exception as e:
        print_error(f"Failed to create shopping list: {e}")
        if debug:
            raise


@lists_cmd.command(name="show")
@click.argument("list_id", type=int)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--debug", is_flag=True, help="Enable debug output")
def show_list(list_id: int, output_json: bool, debug: bool) -> None:
    """Show shopping list details."""
    try:
        with GurkerlClient.from_config(debug=debug) as client:
            response = client.get(f"/api/v2/shopping-lists/id/{list_id}")
            shopping_list = ShoppingList(**response)

            if output_json:
                click.echo(json.dumps(shopping_list.model_dump(mode="json"), indent=2))
            else:
                console.print(
                    f"[bold cyan]Shopping List: {shopping_list.name}[/bold cyan]"
                )
                console.print(f"ID: {shopping_list.id}")
                console.print(f"Type: {shopping_list.type}")
                console.print(f"Shared: {'Yes' if shopping_list.shared else 'No'}")
                console.print(f"Read-only: {'Yes' if shopping_list.readOnly else 'No'}")

                if shopping_list.products:
                    console.print(
                        f"\n[bold]Products ({len(shopping_list.products)}):[/bold]"
                    )
                    table = Table(show_header=True)
                    table.add_column("Product ID", style="cyan")
                    table.add_column("Amount", justify="right", style="yellow")
                    table.add_column("Status", justify="center")

                    for product in shopping_list.products:
                        table.add_row(
                            str(product.productId),
                            str(product.amount),
                            "✓" if product.checked else "○",
                        )
                    console.print(table)
                else:
                    console.print("\n[dim]No products in list[/dim]")

    except Exception as e:
        print_error(f"Failed to show shopping list: {e}")
        if debug:
            raise


@lists_cmd.command(name="delete")
@click.argument("list_id", type=int)
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.confirmation_option(prompt="Are you sure you want to delete this shopping list?")
def delete_list(list_id: int, debug: bool) -> None:
    """Delete a shopping list."""
    try:
        with GurkerlClient.from_config(debug=debug) as client:
            client.delete(f"/api/v1/shopping-lists/{list_id}")
            print_success(f"Deleted shopping list {list_id}")

    except Exception as e:
        print_error(f"Failed to delete shopping list: {e}")
        if debug:
            raise
