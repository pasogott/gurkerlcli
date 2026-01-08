# gurkerlcli 🥒

Command-line interface for [gurkerl.at](https://gurkerl.at) online grocery shopping (Austria).

> ✅ **Working Features**: Login, Product Search, Shopping Lists, Shopping Cart  
> ⏳ **Coming Soon**: Orders, Checkout

## Features

- 🔐 **Authentication** - Secure login with macOS Keychain ✅
- 🔍 **Product Search** - Search the product catalog ✅
- 📝 **Shopping Lists** - Create and manage shopping lists ✅
- 🛒 **Shopping Cart** - Add, remove, and view cart items ✅
- 📦 **Order History** - View past orders ⏳
- 💻 **CLI-first** - Human-friendly interface with JSON output for scripting
- 🎨 **Rich formatting** - Beautiful tables and colors

## Installation

```bash
# Via Homebrew (recommended)
brew tap pasogott/tap
brew install gurkerlcli

# Or via UV
git clone https://github.com/pasogott/gurkerlcli.git
cd gurkerlcli
uv sync
```

## Quick Start

```bash
# 1. Login
gurkerlcli auth login

# 2. Search for products
gurkerlcli search "bio milch"

# 3. Create shopping list
gurkerlcli lists create "Wochenende"

# 4. Show lists
gurkerlcli lists list
```

## Usage

### Authentication ✅

```bash
# Login
gurkerlcli auth login

# Check status
gurkerlcli auth whoami

# Logout
gurkerlcli auth logout
```

### Search Products ✅

```bash
# Basic search
gurkerlcli search "bio milch" --limit 5

# JSON output for scripting
gurkerlcli search "äpfel" --json | jq '.[0]'
```

### Shopping Lists ✅

```bash
# List all shopping lists
gurkerlcli lists list

# Create new list
gurkerlcli lists create "Wochenende Grillen"

# Show list details
gurkerlcli lists show 12345

# JSON output
gurkerlcli lists list --json
```

### Shopping Cart ✅

```bash
# View cart
gurkerlcli cart list

# Add product to cart
gurkerlcli cart add 4659 --quantity 2

# Remove product from cart
gurkerlcli cart remove 4659

# Clear entire cart
gurkerlcli cart clear --force

# JSON output
gurkerlcli cart list --json
```

### Order History ⏳ (Coming Soon)

```bash
# Will be available soon:
gurkerlcli orders list
gurkerlcli orders show G-123456
```

## Configuration

### Session Storage

- **Session**: `~/.config/gurkerlcli/session.json` (expires after 7 days)
- **Credentials**: macOS Keychain (secure)

### Debug Mode

```bash
# Enable debug output
gurkerlcli search "test" --debug
gurkerlcli lists list --debug
```

## Examples

### Scripting

```bash
# Find cheapest bio milk
gurkerlcli search "bio milch" --json | jq 'sort_by(.price) | .[0]'

# Export shopping lists
gurkerlcli lists list --json > my_lists.json

# Search and filter
gurkerlcli search "bio" --json | jq '.[] | select(.price < 5)'
```

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

## API Endpoints (Verified ✅)

```
✅ POST /services/frontend-service/login
✅ GET  /services/frontend-service/user
✅ GET  /services/frontend-service/autocomplete-suggestion
✅ GET  /api/v1/products/card
✅ GET  /api/v1/components/shopping-lists
✅ GET  /api/v2/shopping-lists/id/{id}
✅ POST /api/v1/shopping-lists
✅ GET  /services/frontend-service/v2/cart-review/check-cart
✅ PUT  /services/frontend-service/v2/cart-review/item/{orderFieldId}
⏳ GET  /services/frontend-service/v2/user-profile/orders
```

## Limitations

⚠️ **Unofficial API Client**

- No official API documentation
- Endpoints may change without notice
- No checkout/payment via CLI
- Rate limiting may apply
- Use responsibly!

## Troubleshooting

### Session Expired

```bash
gurkerlcli auth logout
gurkerlcli auth login
```

### Debug Mode

```bash
gurkerlcli --debug search "test"
```

## License

MIT License - see LICENSE file

## Disclaimer

Unofficial tool, not affiliated with gurkerl.at or REWE International AG. Use at your own risk.

## Support

- 🐛 Issues: [GitHub Issues](https://github.com/pasogott/gurkerlcli/issues)
- 📖 Docs: [GitHub Wiki](https://github.com/pasogott/gurkerlcli/wiki)
