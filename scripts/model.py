"""This module contains the Channel class, which represents a TV channel."""
import dataclasses
import datetime
import typing


@dataclasses.dataclass
class Channel:
    id: str
    name: str
    alt_names: list[str]
    network: typing.Optional[str]
    owners: list[str]
    country: str
    subdivision: typing.Optional[str]
    city: typing.Optional[str]
    broadcast_area: str
    languages: list[str]
    categories: list[str]
    is_nsfw: bool
    launched: typing.Optional[datetime.datetime]
    closed: typing.Optional[datetime.datetime]
    replaced_by: typing.Optional[str]
    website: typing.Optional[str]
    logo: str

    @property
    def as_dict(self):
        """Returns a dictionary representation of the object."""
        return {
            key: value.timestamp() if isinstance(value, datetime.datetime) else value
            for key, value in dataclasses.asdict(self).items()
        }

