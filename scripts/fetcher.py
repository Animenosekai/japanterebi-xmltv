"""Get the fetchers for the given channels."""
import argparse
import json
import pathlib
import typing
from xml.dom.minidom import Element, parse

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
    try:
        with (site / f"{site.name}.channels.xml").open() as file:
            dom = parse(file)
            for node in dom.getElementsByTagName("channel"):
                yield node
    except FileNotFoundError:
        print("Warning: No channels file found for", site.name)


def main(sites: pathlib.Path, channels: list[Channel]) -> typing.Iterable[str]:
    """
    Get the fetchers for the given channels.

    Parameters
    ----------
    sites: Path
        The path to the fetchers.
    channels: list
        The list of channels.

    Returns
    -------
    Iterable
    typing.Iterable[pathlib.Path]
    """
    ids = set((channel.id for channel in channels))
    for site in sites.iterdir():
        if site.is_dir():
            for node in get_nodes(site):
                if node.getAttribute("xmltv_id") in ids:
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
    decoded = json.loads(pathlib.Path(args.input).read_text())
    channels = [Channel(**channel) for channel in decoded]
    sites = main(args.sites, channels)
    result = '<?xml version="1.0" encoding="UTF-8"?>\n<channels>\n    {channel}\n</channels>'.format(
        channel="\n    ".join(sites)
    )
    if args.output and args.output != "-":
        pathlib.Path(args.output).write_text(result)
    else:
        print(result)


if __name__ == "__main__":
    entry()

