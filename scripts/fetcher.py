"""Get the fetchers for the given channels."""

import argparse
import json
import pathlib
import typing
from xml.dom.minidom import Element, parse

import tqdm
from model import Channel


def get_nodes(site: pathlib.Path) -> typing.Iterable[Element]:
    """
    Get the channels for the given site.

    Parameters
    ----------
    site: Path
        The path to the site.

    Returns
    -------
    Iterable
    typing.Iterable[str]
    """
    for element in site.iterdir():
        if element.name.endswith(".channels.xml"):
            with element.open() as file:
                dom = parse(file)
                for node in dom.getElementsByTagName("channel"):
                    yield node


def main(
    sites: pathlib.Path, channels: list[Channel], progress: bool = False
) -> typing.Iterable[str]:
    """
    Get the fetchers for the given channels.

    Parameters
    ----------
    sites: Path
        The path to the fetchers.
    channels: list
        The list of channels.
    progress: bool, default = True

    Returns
    -------
    Iterable
    typing.Iterable[pathlib.Path]
    """
    channels_map = {channel.id: channel for channel in channels}
    for site in tqdm.tqdm(sites.iterdir(), disable=not progress):
        if site.is_dir():
            for node in get_nodes(site):
                channel_id, _, feed_id = node.getAttribute("xmltv_id").partition("@")
                if channel_id not in channels_map:
                    continue

                if feed_id:
                    if feed_id not in channels_map[channel_id].feeds:
                        continue
                elif not channels_map[channel_id].has_main_feed:
                    continue

                yield node.toxml()


def entry():
    """The main entrypoint for the script."""
    parser = argparse.ArgumentParser(prog="fetcher", description="Fetch channels")
    parser.add_argument(
        "--input", "-i", help="The channels list", type=pathlib.Path, required=True
    )
    parser.add_argument(
        "--sites", "-s", help="The site fetchers", type=pathlib.Path, required=True
    )
    parser.add_argument("output", default="-", help="The output path", nargs="?")
    args = parser.parse_args()
    stdout = not (args.output and args.output != "-")
    decoded = json.loads(pathlib.Path(args.input).read_text())
    channels = [Channel(**channel) for channel in decoded]
    sites = main(args.sites, channels, progress=not stdout)
    result = '<?xml version="1.0" encoding="UTF-8"?>\n<channels>\n    {channel}\n</channels>'.format(
        channel="\n    ".join(sites)
    )
    if stdout:
        print(result)
    else:
        pathlib.Path(args.output).write_text(result)


if __name__ == "__main__":
    entry()
