"""Authentication management."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import keyring
from dotenv import load_dotenv

from .config import Config, Session
from .exceptions import AuthenticationError

KEYRING_SERVICE = "gurkerlcli"

# Load .env file if it exists
dotenv_path = Path.cwd() / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)


class AuthManager:
    """Manage authentication and sessions."""

    @staticmethod
    def login(email: str, password: str) -> Session:
        """Login to gurkerl.at and create session."""
        # Store credentials in keyring for future use (if available)
        try:
            keyring.set_password(KEYRING_SERVICE, email, password)
        except Exception:
            # Keyring not available - credentials will need to be in .env or env vars
            pass

        # Make login request
        client = httpx.Client(
            base_url="https://www.gurkerl.at",
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "gurkerlcli/0.1.0",
                "Content-Type": "application/json",
                "x-origin": "WEB",
            },
        )

        try:
            # Login endpoint
            response = client.post(
                "/services/frontend-service/login",
                json={"email": email, "password": password, "name": ""},
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid email or password.")
            elif response.status_code >= 400:
                raise AuthenticationError(
                    f"Login failed with status {response.status_code}: {response.text}"
                )

            # Extract cookies
            cookies = {name: value for name, value in client.cookies.items()}

            if not cookies:
                raise AuthenticationError("No session cookie received from server.")

            # Create session (expires in 7 days by default)
            session = Session(
                cookies=cookies,
                user_email=email,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7),
            )

            # Save session
            Config.save_session(session)

            return session

        except httpx.HTTPError as e:
            raise AuthenticationError(f"Login request failed: {e}")
        finally:
            client.close()

    @staticmethod
    def logout() -> None:
        """Logout and clear session."""
        Config.clear_session()

    @staticmethod
    def get_stored_credentials(email: str) -> str | None:
        """Get stored password from keyring, .env, or environment variables.

        Priority:
        1. Keyring (secure, cross-platform)
        2. .env file (fallback for Linux/CI)
        3. Environment variables (for Docker/CI)
        """
        # Try keyring first (most secure)
        try:
            password = keyring.get_password(KEYRING_SERVICE, email)
            if password:
                return password
        except Exception:
            # Keyring not available (e.g., on Linux without backend)
            pass

        # Try .env file
        env_email = os.getenv("GURKERL_EMAIL")
        env_password = os.getenv("GURKERL_PASSWORD")

        if env_email == email and env_password:
            return env_password

        # Try environment variables (for any email)
        if env_password:
            return env_password

        return None

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated."""
        session = Config.load_session()
        return session is not None and not session.is_expired()
