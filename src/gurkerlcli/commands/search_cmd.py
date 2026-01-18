"""Product search commands."""

import json
from decimal import Decimal

import click
from rich.table import Table

from ..client import GurkerlClient
from ..config import Config
from ..exceptions import GurkerlError
from ..models import SearchResult
from ..utils.formatting import print_error, console


def _create_search_client(debug: bool = False) -> GurkerlClient:
    """Create a client for search without PHPSESSION cookie.

    PHPSESSION cookie causes search to return cached results instead of
    actual search results. See: https://github.com/pasogott/gurkerlcli/issues/1
    """
    from ..config import Session

    session = Config.load_session()
    if not session:
        from ..exceptions import AuthenticationError

        raise AuthenticationError(
            "Not authenticated. Please run 'gurkerlcli login' first."
        )

    # Filter out PHPSESSION cookie
    filtered_cookies = {k: v for k, v in session.cookies.items() if k != "PHPSESSION"}

    # Create new session with filtered cookies
    filtered_session = Session(
        cookies=filtered_cookies,
        user_email=session.user_email,
        created_at=session.created_at,
        expires_at=session.expires_at,
    )

    return GurkerlClient(session=filtered_session, debug=debug)


def _format_search_table(results: list[SearchResult]) -> Table:
    """Format search results as a table."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Brand", style="cyan")
    table.add_column("Amount")
    table.add_column("Price", justify="right", style="green")
    table.add_column("Per Unit", justify="right", style="dim")

    for result in results:
        per_unit = (
            f"€ {result.price_per_unit:.2f}/{result.unit}"
            if result.price_per_unit
            else ""
        )
        table.add_row(
            str(result.id),
            result.name,
            result.brand or "",
            result.textual_amount,
            result.price_display,
            per_unit,
        )

    return table


@click.command(name="search")
@click.argument("query")
@click.option("--limit", default=20, help="Maximum number of results")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--debug", is_flag=True, help="Enable debug output")
def search(query: str, limit: int, output_json: bool, debug: bool) -> None:
    """Search for products.

    Examples:
        gurkerlcli search "bio milch"
        gurkerlcli search "äpfel" --limit 10
        gurkerlcli search "brot" --json
    """
    try:
        with _create_search_client(debug=debug) as client:
            # Search via autocomplete endpoint
            response = client.get(
                "/services/frontend-service/autocomplete",
                params={
                    "search": query,
                    "referer": "whisperer",
                    "companyId": "1",
                },
            )

            # Get product IDs from autocomplete response
            product_ids = []
            if "productIds" in response:
                product_ids = [str(pid) for pid in response["productIds"][:limit]]

            if not product_ids:
                print_error(f"No products found for '{query}'")
                return

            # Build params for products endpoint (multiple products params)
            products_params = [("products", pid) for pid in product_ids]

            # Get full product details
            products_response = client.get(
                "/api/v1/products",
                params=products_params,
            )

            # Get prices for products
            prices_response = client.get(
                "/api/v1/products/prices",
                params=products_params,
            )

            # Build price lookup by product ID
            prices_by_id = {}
            if isinstance(prices_response, list):
                for price_item in prices_response:
                    pid = price_item.get("productId")
                    if pid:
                        prices_by_id[pid] = price_item

            # Parse product list response
            if isinstance(products_response, list):
                products_data = products_response
            elif isinstance(products_response, dict):
                products_data = products_response.get("products", [])
            else:
                products_data = []

            if not products_data:
                print_error(f"No product details found for '{query}'")
                return

            # Convert to SearchResult models
            results = []
            for item in products_data[:limit]:
                try:
                    pid = item.get("id")
                    price_data = prices_by_id.get(pid, {})

                    # Extract price info
                    price = None
                    price_per_unit = None
                    currency = "EUR"

                    if "price" in price_data:
                        price = Decimal(str(price_data["price"]["amount"]))
                        currency = price_data["price"].get("currency", "EUR")
                    if "pricePerUnit" in price_data:
                        price_per_unit = Decimal(
                            str(price_data["pricePerUnit"]["amount"])
                        )

                    result = SearchResult(
                        id=pid,
                        name=item.get("name", ""),
                        slug=item.get("slug", ""),
                        brand=item.get("brand"),
                        unit=item.get("unit", ""),
                        textualAmount=item.get("textualAmount", ""),
                        images=item.get("images", []),
                        price=price,
                        price_per_unit=price_per_unit,
                        currency=currency,
                    )
                    results.append(result)
                except Exception as e:
                    if debug:
                        print_error(f"Failed to parse product: {e}")
                        import traceback

                        traceback.print_exc()
                    continue

            if not results:
                print_error(f"No valid products found for '{query}'")
                return

            # Output
            if output_json:
                click.echo(
                    json.dumps([r.model_dump(mode="json") for r in results], indent=2)
                )
            else:
                table = _format_search_table(results)
                console.print(table)
                console.print(f"\n[dim]Found {len(results)} products[/dim]")

    except GurkerlError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Search failed: {e}")
        if debug:
            raise
        raise click.Abort()
