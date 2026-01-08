"""Rich formatting helpers."""

from __future__ import annotations

from decimal import Decimal

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models import Cart, Order, Product

console = Console()


def format_price(price: Decimal) -> str:
    """Format price as EUR currency."""
    return f"€{price:.2f}"


def format_stock_status(in_stock: bool) -> str:
    """Format stock status with color."""
    return "[green]✓[/green]" if in_stock else "[red]✗[/red]"


def format_product_table(products: list[Product]) -> Table:
    """Create a Rich table for products."""
    table = Table(title="Products")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Price", justify="right")
    table.add_column("Unit")
    table.add_column("Stock", justify="center")

    for product in products:
        table.add_row(
            product.id,
            product.name,
            format_price(product.price),
            product.unit or "-",
            format_stock_status(product.in_stock),
        )

    return table


def format_cart_table(cart: Cart) -> Table:
    """Create a Rich table for cart."""
    table = Table(title=f"🛒 Shopping Cart (Cart ID: {cart.cart_id})")
    table.add_column("Product", style="bold")
    table.add_column("Brand", style="dim")
    table.add_column("Qty", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Subtotal", justify="right")

    for item in cart.items:
        # Format price with discount indicator
        price_str = format_price(item.price)
        if item.has_discount and item.original_price:
            price_str = f"[red]{format_price(item.original_price)}[/red] → [green]{price_str}[/green]"

        table.add_row(
            item.name,
            item.brand or "-",
            f"{item.quantity}x {item.textual_amount}",
            price_str,
            format_price(item.subtotal),
        )

    # Add separator and totals
    if cart.items:
        table.add_section()

        # Show savings if any
        if cart.total_savings > 0:
            table.add_row(
                "",
                "",
                "",
                "[green]Savings:[/green]",
                f"[green]-{format_price(cart.total_savings)}[/green]",
            )

        table.add_row(
            "",
            "",
            "",
            "[bold]Total:[/bold]",
            f"[bold]{format_price(cart.total)}[/bold]",
        )

    return table


def format_order_table(orders: list[Order]) -> Table:
    """Create a Rich table for orders."""
    table = Table(title="Order History")
    table.add_column("Order #", style="dim")
    table.add_column("Date")
    table.add_column("Status")
    table.add_column("Total", justify="right")

    for order in orders:
        status_color = "green" if order.status.lower() == "delivered" else "yellow"
        table.add_row(
            order.order_number,
            order.date.strftime("%Y-%m-%d"),
            f"[{status_color}]{order.status}[/{status_color}]",
            format_price(order.total),
        )

    return table


def format_order_panel(order: Order) -> Panel:
    """Create a Rich panel for order details."""
    lines = [
        f"[bold]Order Number:[/bold] {order.order_number}",
        f"[bold]Date:[/bold] {order.date.strftime('%Y-%m-%d %H:%M')}",
        f"[bold]Status:[/bold] {order.status}",
        f"[bold]Total:[/bold] {format_price(order.total)}",
        "",
        "[bold]Items:[/bold]",
    ]

    for item in order.items:
        lines.append(
            f"  • {item.product.name} ({item.quantity}x) - {format_price(item.subtotal)}"
        )

    return Panel("\n".join(lines), title=f"Order {order.order_number}", expand=False)


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]✗[/red] {message}", style="red")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")
