"""
Configuration for Yene Lottery Bot.

Database behavior:
- SQLite is the default (file: yene_lottery.db) — zero setup required.
- PostgreSQL is optional: set DATABASE_URL OR set DB_HOST (plus the
  DB_PORT/DB_NAME/DB_USER/DB_PASSWORD values) in .env to activate it.
"""
import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _parse_ids(value: str) -> List[int]:
    return [int(x.strip()) for x in value.replace(",", " ").split() if x.strip().isdigit()]


def _parse_strs(value: str) -> List[str]:
    return [x.strip().lstrip("@") for x in value.replace(",", " ").split() if x.strip()]


@dataclass
class Config:
    bot_token: str = field(
        default_factory=lambda: os.getenv("BOT_TOKEN", "")
    )
    admin_group_id: int = field(
        default_factory=lambda: int(os.getenv("ADMIN_GROUP_ID", "0") or 0)
    )
    public_group_id: int = field(
        default_factory=lambda: int(os.getenv("PUBLIC_GROUP_ID", "0") or 0)
    )
    super_admin_ids: List[int] = field(
        default_factory=lambda: _parse_ids(os.getenv("SUPER_ADMIN_IDS", ""))
    )
    super_admin_usernames: List[str] = field(
        default_factory=lambda: _parse_strs(os.getenv("SUPER_ADMIN_USERNAMES", ""))
    )

    # ── Database ──
    # Empty string means "not explicitly set"; SQLite is used unless
    # DATABASE_URL is provided or DB_HOST is configured.
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "").strip()
    )
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "").strip())
    db_port: str = field(default_factory=lambda: os.getenv("DB_PORT", "5432"))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "yene_lottery"))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))

    # ── Misc ──
    debug: bool = field(
        default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true"
    )

    def __post_init__(self):
        # Build a PostgreSQL DSN from DB_* fields when DATABASE_URL is not
        # set but DB_HOST is. This keeps .env.example's classic DB_* vars
        # working without forcing users to write a full DATABASE_URL.
        if not self.database_url and self.db_host:
            self.database_url = (
                f"postgresql://{self.db_user}:{self.db_password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )


cfg = Config()
