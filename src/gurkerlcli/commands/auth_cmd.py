"""Authentication commands."""

import os
from pathlib import Path

import click

from ..auth import AuthManager
from ..config import Config
from ..exceptions import AuthenticationError
from ..utils.formatting import print_error, print_info, print_success, console


@click.group(name="auth")
def auth_group() -> None:
    """Authentication commands."""
    pass


@auth_group.command(name="login")
@click.option("--email", prompt=True, help="Email address")
@click.option("--password", prompt=True, hide_input=True, help="Password")
def login(email: str, password: str) -> None:
    """Login to gurkerl.at.

    Examples:
        gurkerlcli auth login
        gurkerlcli auth login --email user@example.com
    """
    try:
        with click.progressbar(
            length=1, label="Logging in", show_eta=False
        ) as progress:
            session = AuthManager.login(email, password)
            progress.update(1)

        print_success(f"Logged in as {email}")
        if session.expires_at:
            print_info(f"Session expires: {session.expires_at.strftime('%Y-%m-%d')}")

        # Check if using .env file and show warning
        dotenv_path = Path.cwd() / ".env"
        if dotenv_path.exists() and os.getenv("GURKERL_PASSWORD"):
            console.print("\n[yellow]⚠️  Using credentials from .env file.[/yellow]")
            console.print(
                "[dim]   On macOS, credentials are stored in Keychain for better security.[/dim]"
            )

    except AuthenticationError as e:
        print_error(str(e))
        raise click.Abort()
    except Exception as e:
        print_error(f"Login failed: {e}")
        raise click.Abort()


@auth_group.command(name="logout")
def logout() -> None:
    """Logout and clear session.

    Examples:
        gurkerlcli auth logout
    """
    AuthManager.logout()
    print_success("Logged out")


@auth_group.command(name="whoami")
def whoami() -> None:
    """Show current authentication status.

    Examples:
        gurkerlcli auth whoami
    """
    session = Config.load_session()
    if not session:
        print_info("Not logged in. Run 'gurkerlcli auth login' to login.")
        return

    if session.is_expired():
        print_info("Session expired. Please login again.")
        Config.clear_session()
        return

    print_success(f"Logged in as {session.user_email}")
    print_info(f"Session created: {session.created_at.strftime('%Y-%m-%d %H:%M')}")
    if session.expires_at:
        print_info(f"Session expires: {session.expires_at.strftime('%Y-%m-%d %H:%M')}")
