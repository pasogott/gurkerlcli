---
name: gurkerlcli
description: >
  CLI for gurkerl.at online grocery shopping (Austria). Search products, manage
  shopping cart, view order history. Use when user mentions "gurkerl", "grocery
  shopping", "warenkorb", "bestellen", or Austrian online shopping.
---

# gurkerlcli

Command-line interface for gurkerl.at online grocery shopping (Austria).

## Trigger Words

- "gurkerl"
- "grocery shopping"
- "warenkorb"
- "einkaufen"
- "bestellen"
- "shopping cart"
- "online supermarket"

## Prerequisites

- macOS/Linux (keyring support)
- Python 3.12+
- UV package manager
- gurkerl.at account

## Setup

```bash
# Navigate to project
cd /Users/pascal/projects/gurkerlcli

# Install dependencies
uv sync

# Login to gurkerl.at
uv run gurkerlcli auth login
```

## Usage

### Authentication

```bash
# Login
gurkerlcli auth login
gurkerlcli auth login --email user@example.com

# Check auth status
gurkerlcli auth whoami

# Logout
gurkerlcli auth logout
```

### Product Search

```bash
# Search products
gurkerlcli search "bio milch"
gurkerlcli search "äpfel" --limit 10

# JSON output
gurkerlcli search "brot" --json
```

### Shopping Cart

```bash
# View cart
gurkerlcli cart list
gurkerlcli cart

# Add product
gurkerlcli cart add 12345
gurkerlcli cart add 12345 --quantity 3

# Remove product
gurkerlcli cart remove 12345

# Clear cart
gurkerlcli cart clear
gurkerlcli cart clear --force  # Skip confirmation
```

### Order History

```bash
# List orders
gurkerlcli orders list
gurkerlcli orders list --limit 20

# Show order details
gurkerlcli orders show G-123456

# JSON output
gurkerlcli orders list --json
```

## Global Options

- `-h, --help` - Show help
- `--version` - Show version
- `--debug` - Enable debug output (for most commands)
- `--json` - Output as JSON (for data commands)

## Configuration

### Session Storage
- Location: `~/.config/gurkerlcli/session.json`
- Session expires after 7 days
- Credentials stored in system keyring (macOS Keychain)

### Cache Directory
- Location: `~/.config/gurkerlcli/cache/`

## API Details

Uses gurkerl.at internal API (reverse-engineered, no official documentation):

- `/services/frontend-service/login` - Authentication
- `/services/frontend-service/autocomplete-suggestion` - Product search
- `/api/v1/cart` - Shopping cart
- `/api/v1/products/*` - Product details
- `/services/frontend-service/v2/user-profile/orders` - Order history

⚠️ **Note**: This is an unofficial API client. Endpoints may change without notice.

## Limitations

- No checkout/payment via CLI (requires web browser)
- No delivery time scheduling via CLI
- Rate limiting may apply
- CAPTCHA/bot detection possible

## Error Handling

The CLI provides clear error messages:

- `401` - Authentication failed (re-login required)
- `404` - Resource not found
- `429` - Rate limit exceeded
- Network errors - Connection failures

Use `--debug` flag for detailed error information.

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest tests/ -v

# Lint
uv run ruff check src/

# Format
uv run ruff format src/
```

## Examples for Claude

```bash
# User: "Add bio milk to my gurkerl cart"
gurkerlcli search "bio milch" --limit 5
# Review results, then:
gurkerlcli cart add <product_id> --quantity 2

# User: "What's in my shopping cart?"
gurkerlcli cart list

# User: "Show my last gurkerl orders"
gurkerlcli orders list --limit 5

# User: "Clear my cart"
gurkerlcli cart clear
```

## Troubleshooting

### Authentication Errors
```bash
# Clear session and re-login
gurkerlcli auth logout
gurkerlcli auth login
```

### Debug Mode
```bash
# Enable debug output for troubleshooting
gurkerlcli --debug search "test"
gurkerlcli cart list --debug
```

### Session Expired
```bash
# Check session status
gurkerlcli auth whoami

# Re-login if expired
gurkerlcli auth login
```

## Output Modes

### Human-friendly (default)
- Rich tables and panels
- Colors and formatting
- Progress indicators

### Machine-readable
```bash
# JSON output for scripting
gurkerlcli search "milch" --json | jq '.[] | .name'
gurkerlcli orders list --json | jq '.[0].order_number'
```

## Exit Codes

- `0` - Success
- `1` - General error
- `130` - Interrupted (Ctrl-C)

## Future Features

Planned enhancements:
- Shopping list management
- Product favorites
- Order repeat (add previous order to cart)
- Obsidian integration for shopping lists
- Delivery time slot selection

## Related Skills

- `obsidian-gtd` - For shopping list integration
- `gmail-gtd` - For order confirmation emails
