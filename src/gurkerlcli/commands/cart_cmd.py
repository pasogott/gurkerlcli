"""Shopping cart commands."""

import json

import click

from ..client import GurkerlClient
from ..exceptions import GurkerlError
from ..models import Cart, CartResponseDTO
from ..utils.formatting import (
    format_cart_table,
    print_error,
    print_info,
    print_success,
    console,
)


@click.group(name="cart")
def cart_group() -> None:
    """Shopping cart management."""
    pass


@cart_group.command(name="list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--debug", is_flag=True, help="Enable debug output")
def list_cart(output_json: bool, debug: bool) -> None:
    """Show shopping cart contents.

    Examples:
        gurkerlcli cart list
        gurkerlcli cart list --json
    """
    try:
        with GurkerlClient.from_config(debug=debug) as client:
            response = client.get(
                "/services/frontend-service/v2/cart-review/check-cart"
            )

            # Parse response using Pydantic models
            cart_response = CartResponseDTO(**response)
            cart = Cart.from_response(cart_response)

            if output_json:
                click.echo(json.dumps(cart.model_dump(mode="json"), indent=2))
            else:
                if not cart.items:
                    print_info("🛒 Cart is empty")
                    return

                table = format_cart_table(cart)
                console.print(table)

                # Show order minimum if not met
                if not cart.submit_condition_passed:
                    remaining = cart.minimal_order_price - cart.total
                    console.print(
                        f"\n[yellow]⚠️  Minimum order: €{cart.minimal_order_price:.2f} "
                        f"(€{remaining:.2f} remaining)[/yellow]"
                    )

    except GurkerlError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Failed to load cart: {e}")
        if debug:
            raise
        raise click.Abort()


@cart_group.command(name="add")
@click.argument("product_id")
@click.option("--quantity", "-q", default=1, help="Quantity to add")
@click.option("--debug", is_flag=True, help="Enable debug output")
def add_to_cart(product_id: str, quantity: int, debug: bool) -> None:
    """Add product to cart.

    Examples:
        gurkerlcli cart add 12345
        gurkerlcli cart add 12345 --quantity 3
    """
    try:
        with GurkerlClient.from_config(debug=debug) as client:
            # First get current cart to find orderFieldId if item exists
            cart_response = client.get(
                "/services/frontend-service/v2/cart-review/check-cart"
            )
            cart_data = CartResponseDTO(**cart_response)

            # Check if item already in cart
            existing_item = cart_data.data.items.get(product_id)
            if existing_item:
                # Update existing item
                new_quantity = existing_item.quantity + quantity
                client.post(
                    f"/services/frontend-service/v2/cart-review/item/{existing_item.orderFieldId}",
                    json={"quantity": new_quantity},
                )
                product_name = existing_item.productName
                print_success(
                    f"✓ Updated {product_name} ({existing_item.quantity} → {new_quantity})"
                )
            else:
                # Add new item via cart/item endpoint
                client.post(
                    "/api/v1/cart/item",
                    json={"amount": quantity, "productId": int(product_id)},
                )

                # Re-fetch cart to get product name
                updated_response = client.get(
                    "/services/frontend-service/v2/cart-review/check-cart"
                )
                updated_cart = CartResponseDTO(**updated_response)
                item = updated_cart.data.items.get(product_id)
                product_name = item.productName if item else f"Product {product_id}"
                print_success(f"✓ Added {product_name} ({quantity}x) to cart")

    except GurkerlError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Failed to add to cart: {e}")
        if debug:
            raise
        raise click.Abort()


@cart_group.command(name="remove")
@click.argument("product_id")
@click.option("--debug", is_flag=True, help="Enable debug output")
def remove_from_cart(product_id: str, debug: bool) -> None:
    """Remove product from cart.

    Examples:
        gurkerlcli cart remove 12345
    """
    try:
        with GurkerlClient.from_config(debug=debug) as client:
            # Get current cart to find orderFieldId
            cart_response = client.get(
                "/services/frontend-service/v2/cart-review/check-cart"
            )
            cart_data = CartResponseDTO(**cart_response)

            # Find item in cart
            item = cart_data.data.items.get(product_id)
            if not item:
                print_error(f"Product {product_id} not in cart")
                raise click.Abort()

            # Remove item via DELETE
            client.delete(
                f"/services/frontend-service/v2/cart-review/item/{item.orderFieldId}",
            )
            print_success(f"✓ Removed {item.productName} from cart")

    except GurkerlError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Failed to remove from cart: {e}")
        if debug:
            raise
        raise click.Abort()


@cart_group.command(name="clear")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
@click.option("--debug", is_flag=True, help="Enable debug output")
def clear_cart(force: bool, debug: bool) -> None:
    """Clear all items from cart.

    Examples:
        gurkerlcli cart clear
        gurkerlcli cart clear --force
    """
    if not force:
        if not click.confirm("Are you sure you want to clear the cart?"):
            print_info("Cart clear cancelled")
            return

    try:
        with GurkerlClient.from_config(debug=debug) as client:
            # Get current cart
            cart_response = client.get(
                "/services/frontend-service/v2/cart-review/check-cart"
            )
            cart_data = CartResponseDTO(**cart_response)

            # Remove all items via DELETE
            for item in cart_data.data.items.values():
                client.delete(
                    f"/services/frontend-service/v2/cart-review/item/{item.orderFieldId}",
                )

            print_success(f"✓ Cleared {len(cart_data.data.items)} items from cart")

    except GurkerlError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Failed to clear cart: {e}")
        if debug:
            raise
        raise click.Abort()


# Add shortcut: 'gurkerlcli cart' defaults to 'gurkerlcli cart list'
@cart_group.command(name="show", hidden=True)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--debug", is_flag=True, help="Enable debug output")
def show_cart(output_json: bool, debug: bool) -> None:
    """Alias for 'cart list'."""
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(list_cart, ["--json"] if output_json else [])
    click.echo(result.output, nl=False)
