"""HTTP client for gurkerl.at API."""

from __future__ import annotations

from typing import Any

import httpx
from rich.console import Console

from .config import Config, Session
from .exceptions import APIError, AuthenticationError, NotFoundError, RateLimitError

console = Console(stderr=True)


class GurkerlClient:
    """HTTP client wrapper for gurkerl.at API."""

    BASE_URL = "https://www.gurkerl.at"

    def __init__(self, session: Session | None = None, debug: bool = False):
        """Initialize client with optional session."""
        self.session = session
        self.debug = debug
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "gurkerlcli/0.1.0",
                "Accept": "application/json",
                "x-origin": "WEB",
            },
        )
        if session:
            self._client.cookies.update(session.cookies)

    def __enter__(self) -> GurkerlClient:
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self._client.close()

    def _log_request(self, method: str, url: str) -> None:
        """Log request if debug enabled."""
        if self.debug:
            console.print(f"[dim]→ {method} {url}[/dim]")

    def _log_response(self, response: httpx.Response) -> None:
        """Log response if debug enabled."""
        if self.debug:
            console.print(
                f"[dim]← {response.status_code} {response.request.method} {response.url}[/dim]"
            )

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        self._log_response(response)

        if response.status_code == 401:
            raise AuthenticationError("Authentication failed. Please login again.")
        elif response.status_code == 404:
            raise NotFoundError("Resource not found.")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded. Please try again later.")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get("message", response.text)
            except Exception:
                error_msg = response.text
            raise APIError(f"API error ({response.status_code}): {error_msg}")

        if not response.content:
            return {}

        try:
            return response.json()
        except Exception:
            return {"text": response.text}

    def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """GET request."""
        self._log_request("GET", path)
        response = self._client.get(path, **kwargs)
        return self._handle_response(response)

    def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """POST request."""
        self._log_request("POST", path)
        response = self._client.post(path, **kwargs)
        return self._handle_response(response)

    def put(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """PUT request."""
        self._log_request("PUT", path)
        response = self._client.put(path, **kwargs)
        return self._handle_response(response)

    def delete(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """DELETE request."""
        self._log_request("DELETE", path)
        response = self._client.delete(path, **kwargs)
        return self._handle_response(response)

    @classmethod
    def from_config(cls, debug: bool = False) -> GurkerlClient:
        """Create client from saved session."""
        session = Config.load_session()
        if not session:
            raise AuthenticationError(
                "Not authenticated. Please run 'gurkerlcli login' first."
            )
        return cls(session=session, debug=debug)
