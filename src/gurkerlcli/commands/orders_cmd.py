"""Order history commands."""

import json
from datetime import datetime

import click

from ..client import GurkerlClient
from ..exceptions import GurkerlError
from ..models import Order, CartItem, Product
from ..utils.formatting import (
    format_order_panel,
    format_order_table,
    print_error,
    print_info,
    console,
)


@click.group(name="orders")
def orders_group() -> None:
    """Order history management."""
    pass


@orders_group.command(name="list")
@click.option("--limit", default=10, help="Maximum number of orders")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--debug", is_flag=True, help="Enable debug output")
def list_orders(limit: int, output_json: bool, debug: bool) -> None:
    """Show order history.

    Examples:
        gurkerlcli orders list
        gurkerlcli orders list --limit 20
        gurkerlcli orders list --json
    """
    try:
        with GurkerlClient.from_config(debug=debug) as client:
            response = client.get(
                "/services/frontend-service/v2/user-profile/orders",
                params={"limit": limit},
            )

            # Parse orders (adapt based on actual API structure)
            orders_data = response.get("orders", [])
            if not orders_data:
                print_info("No orders found")
                return

            # Convert to models
            orders = []
            for order_data in orders_data:
                try:
                    order = Order(
                        id=str(order_data.get("id", "")),
                        order_number=order_data.get("orderNumber", ""),
                        date=datetime.fromisoformat(
                            order_data.get("date", datetime.now().isoformat())
                        ),
                        status=order_data.get("status", "Unknown"),
                        total=order_data.get("total", 0),
                        items=[],  # Items loaded separately in 'show' command
                    )
                    orders.append(order)
                except Exception as e:
                    if debug:
                        print_error(f"Failed to parse order: {e}")
                    continue

            if not orders:
                print_info("No valid orders found")
                return

            if output_json:
                click.echo(
                    json.dumps([o.model_dump(mode="json") for o in orders], indent=2)
                )
            else:
                table = format_order_table(orders)
                console.print(table)
                console.print(f"\n[dim]Showing {len(orders)} orders[/dim]")

    except GurkerlError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Failed to load orders: {e}")
        if debug:
            raise
        raise click.Abort()


@orders_group.command(name="show")
@click.argument("order_number")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--debug", is_flag=True, help="Enable debug output")
def show_order(order_number: str, output_json: bool, debug: bool) -> None:
    """Show order details.

    Examples:
        gurkerlcli orders show G-123456
    """
    try:
        with GurkerlClient.from_config(debug=debug) as client:
            response = client.get(
                f"/services/frontend-service/v2/orders/{order_number}"
            )

            # Parse order details
            items_data = response.get("items", [])
            items = []
            for item_data in items_data:
                try:
                    product = Product(
                        id=str(item_data.get("productId", "")),
                        name=item_data.get("name", "Unknown"),
                        price=item_data.get("price", 0),
                        unit=item_data.get("unit"),
                    )
                    cart_item = CartItem(
                        product=product,
                        quantity=item_data.get("quantity", 1),
                        subtotal=item_data.get("subtotal", product.price),
                    )
                    items.append(cart_item)
                except Exception as e:
                    if debug:
                        print_error(f"Failed to parse order item: {e}")
                    continue

            order = Order(
                id=str(response.get("id", "")),
                order_number=order_number,
                date=datetime.fromisoformat(
                    response.get("date", datetime.now().isoformat())
                ),
                status=response.get("status", "Unknown"),
                total=response.get("total", 0),
                items=items,
            )

            if output_json:
                click.echo(json.dumps(order.model_dump(mode="json"), indent=2))
            else:
                panel = format_order_panel(order)
                console.print(panel)

    except GurkerlError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Failed to load order: {e}")
        if debug:
            raise
        raise click.Abort()
