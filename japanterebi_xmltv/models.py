"""Models for the japanterebi-xmltv package."""

from __future__ import annotations

import dataclasses
import datetime


@dataclasses.dataclass
class Channel:
    """Represents a TV channel."""

    id: str
    name: str
    alt_names: list[str]
    network: str | None
    owners: list[str]
    country: str
    categories: list[str]
    is_nsfw: bool
    launched: datetime.datetime | None
    closed: datetime.datetime | None
    replaced_by: str | None
    website: str | None
    feeds: list[str]
    has_main_feed: bool = False

    @property
    def as_dict(self) -> dict[str, int | str | list[str] | None]:
        """Returns a dictionary representation of the object."""
        return {
            key: int(value.timestamp())
            if isinstance(value, datetime.datetime)
            else value
            for key, value in dataclasses.asdict(self).items()
        }


@dataclasses.dataclass
class Feed:
    """Represents a TV channel feed."""

    channel: str
    id: str
    name: str
    alt_names: list[str]
    is_main: bool
    broadcast_area: str
    timezone: str
    languages: list[str]
    format: str

    @property
    def as_dict(self) -> dict[str, int | str | list[str] | None]:
        """Returns a dictionary representation of the object."""
        return {
            key: int(value.timestamp())
            if isinstance(value, datetime.datetime)
            else value
            for key, value in dataclasses.asdict(self).items()
        }
