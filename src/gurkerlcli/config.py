"""Configuration and session management for gurkerlcli."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class Session(BaseModel):
    """User session data."""

    cookies: dict[str, str]
    user_email: str | None = None
    created_at: datetime
    expires_at: datetime | None = None

    def is_expired(self) -> bool:
        """Check if session is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class Config:
    """Configuration manager."""

    config_dir: Path = Path.home() / ".config" / "gurkerlcli"
    session_file: Path = config_dir / "session.json"
    cache_dir: Path = config_dir / "cache"

    @classmethod
    def ensure_dirs(cls) -> None:
        """Create config directories if they don't exist."""
        cls.config_dir.mkdir(parents=True, exist_ok=True)
        cls.cache_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def save_session(cls, session: Session) -> None:
        """Save session to disk."""
        cls.ensure_dirs()
        with open(cls.session_file, "w") as f:
            json.dump(session.model_dump(mode="json"), f, indent=2)

    @classmethod
    def load_session(cls) -> Session | None:
        """Load session from disk."""
        if not cls.session_file.exists():
            return None
        try:
            with open(cls.session_file) as f:
                data = json.load(f)
            session = Session(**data)
            if session.is_expired():
                cls.clear_session()
                return None
            return session
        except (json.JSONDecodeError, ValueError):
            return None

    @classmethod
    def clear_session(cls) -> None:
        """Delete session file."""
        if cls.session_file.exists():
            cls.session_file.unlink()
