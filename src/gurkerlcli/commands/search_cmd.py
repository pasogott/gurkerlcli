"""Product search commands."""

import json

import click

from ..client import GurkerlClient
from ..config import Config
from ..exceptions import GurkerlError
from ..models import Product
from ..utils.formatting import format_product_table, print_error, console


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
    filtered_cookies = {
        k: v for k, v in session.cookies.items() if k != "PHPSESSION"
    }

    # Create new session with filtered cookies
    filtered_session = Session(
        cookies=filtered_cookies,
        user_email=session.user_email,
        created_at=session.created_at,
        expires_at=session.expires_at,
    )

    return GurkerlClient(session=filtered_session, debug=debug)


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
                "/services/frontend-service/autocomplete-suggestion",
                params={"q": query},
            )

            # Get product IDs from autocomplete
            product_ids = []
            if "productIds" in response:
                # Direct product IDs list
                product_ids = [str(pid) for pid in response["productIds"][:limit]]
            elif "products" in response:
                product_ids = [str(p.get("id")) for p in response["products"][:limit]]
            elif "data" in response and "products" in response["data"]:
                product_ids = [
                    str(p.get("id")) for p in response["data"]["products"][:limit]
                ]

            if not product_ids:
                print_error(f"No products found for '{query}'")
                return

            # Get full product details
            products_response = client.get(
                "/api/v1/products/card",
                params={
                    "products": product_ids,
                    "categoryType": "normal",
                },
            )

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

            # Convert to Product models
            products = []
            for item in products_data[:limit]:
                try:
                    product = Product(**item)
                    products.append(product)
                except Exception as e:
                    if debug:
                        print_error(f"Failed to parse product: {e}")
                        import traceback

                        traceback.print_exc()
                    continue

            if not products:
                print_error(f"No valid products found for '{query}'")
                return

            # Output
            if output_json:
                click.echo(
                    json.dumps([p.model_dump(mode="json") for p in products], indent=2)
                )
            else:
                table = format_product_table(products)
                console.print(table)
                console.print(f"\n[dim]Found {len(products)} products[/dim]")

    except GurkerlError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Search failed: {e}")
        if debug:
            raise
        raise click.Abort()
