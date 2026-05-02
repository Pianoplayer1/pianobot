"""Wynncraft v3 API client and response models."""

from api.client import WynncraftClient
from api.exceptions import NotFoundError, RateLimitedError, WynncraftError
from api.models import (
    Guild,
    GuildLeaderboardEntry,
    GuildListEntry,
    GuildMember,
    OnlinePlayers,
    OnlinePlayersByUuid,
    Player,
    TerritorySnapshot,
)

__all__ = [
    "Guild",
    "GuildListEntry",
    "GuildMember",
    "GuildLeaderboardEntry",
    "NotFoundError",
    "OnlinePlayers",
    "OnlinePlayersByUuid",
    "Player",
    "RateLimitedError",
    "TerritorySnapshot",
    "WynncraftClient",
    "WynncraftError",
]
