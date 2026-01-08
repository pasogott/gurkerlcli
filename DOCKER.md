# Docker Usage

## Using gurkerlcli in Docker

Since Docker containers don't have access to macOS Keychain, use environment variables:

### Docker Run

```bash
docker run --rm \
  -e GURKERL_EMAIL=your-email@example.com \
  -e GURKERL_PASSWORD=your-password \
  your-image \
  gurkerlcli search "bio milch"
```

### Docker Compose

```yaml
version: '3.8'

services:
  gurkerlcli:
    image: your-image
    environment:
      - GURKERL_EMAIL=${GURKERL_EMAIL}
      - GURKERL_PASSWORD=${GURKERL_PASSWORD}
    command: gurkerlcli cart list --json
```

Create a `.env` file (don't commit!):

```bash
GURKERL_EMAIL=your-email@example.com
GURKERL_PASSWORD=your-password
```

### GitHub Actions / CI

```yaml
name: Check Cart

on:
  schedule:
    - cron: '0 8 * * *'  # Daily at 8 AM

jobs:
  check-cart:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install gurkerlcli
        run: |
          pip install uv
          uv tool install gurkerlcli
      
      - name: Check cart
        env:
          GURKERL_EMAIL: ${{ secrets.GURKERL_EMAIL }}
          GURKERL_PASSWORD: ${{ secrets.GURKERL_PASSWORD }}
        run: |
          gurkerlcli cart list --json > cart.json
          cat cart.json
```

## Security Notes

⚠️ **Never commit `.env` files or hardcode credentials!**

- ✅ Use GitHub Secrets for CI/CD
- ✅ Use Docker secrets for production
- ✅ Use `.env.local` for local development
- ❌ Don't commit `.env` to Git (already in `.gitignore`)

## Building Docker Image

```dockerfile
FROM python:3.12-slim

# Install uv
RUN pip install uv

# Install gurkerlcli
RUN uv tool install gurkerlcli

# Set working directory
WORKDIR /app

# Default command
CMD ["gurkerlcli", "--help"]
```

Build and run:

```bash
docker build -t gurkerlcli .

docker run --rm \
  -e GURKERL_EMAIL=user@example.com \
  -e GURKERL_PASSWORD=password \
  gurkerlcli cart list
```
