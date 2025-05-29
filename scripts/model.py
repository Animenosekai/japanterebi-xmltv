"""This module contains the Channel class, which represents a TV channel."""

import dataclasses
import datetime
import typing


@dataclasses.dataclass
class Channel:
    id: str
    name: str
    alt_names: typing.List[str]
    network: typing.Optional[str]
    owners: typing.List[str]
    country: str
    subdivision: typing.Optional[str]
    city: typing.Optional[str]
    categories: typing.List[str]
    is_nsfw: bool
    launched: typing.Optional[datetime.datetime]
    closed: typing.Optional[datetime.datetime]
    replaced_by: typing.Optional[str]
    website: typing.Optional[str]
    logo: str
    feeds: typing.List[str]
    has_main_feed: bool = False

    @property
    def as_dict(self):
        """Returns a dictionary representation of the object."""
        return {
            key: value.timestamp() if isinstance(value, datetime.datetime) else value
            for key, value in dataclasses.asdict(self).items()
        }


@dataclasses.dataclass
class Feed:
    channel: str
    id: str
    name: str
    is_main: bool
    broadcast_area: str
    timezone: str
    languages: typing.List[str]
    video_format: str

    @property
    def as_dict(self):
        """Returns a dictionary representation of the object."""
        return {
            key: value.timestamp() if isinstance(value, datetime.datetime) else value
            for key, value in dataclasses.asdict(self).items()
        }
