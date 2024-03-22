"""Filter channels from the iptv-org/database repository"""
import argparse
import datetime
import json
import pathlib
import typing

import tqdm
from model import Channel


def read_file(file_path: pathlib.Path) -> typing.Iterable[Channel]:
    """
    Read a file and return its content as a list of strings.

    Parameters
    ----------
    file_path: Path | str
        The path to the file.

    Returns
    -------
    Iterable
    Generator
    list
        The content of the file as a list of strings.
    """
    with file_path.open() as file:
        file.readline()
        for line in file:
            line = line.strip()
            (
                id,
                name,
                alt_names,
                network,
                owners,
                country,
                subdivision,
                city,
                broadcast_area,
                languages,
                categories,
                is_nsfw,
                launched,
                closed,
                replaced_by,
                website,
                logo,
            ) = line.split(",")
            yield Channel(
                id=id,
                name=name,
                alt_names=alt_names.split(";") if alt_names else [],
                network=network or None,
                owners=owners.split(";") if owners else [],
                country=country,
                subdivision=subdivision or None,
                city=city or None,
                broadcast_area=broadcast_area,
                languages=languages.split(";") if languages else [],
                categories=categories.split(";") if categories else [],
                is_nsfw=is_nsfw == "TRUE",
                launched=datetime.datetime.strptime(launched, "%Y-%m-%d")
                if launched
                else None,
                closed=datetime.datetime.strptime(closed, "%Y-%m-%d")
                if closed
                else None,
                replaced_by=replaced_by or None,
                website=website or None,
                logo=logo,
            )


def main(
    file_path: pathlib.Path,
    languages: list[str],
    countries: list[str],
    categories: list[str],
    add: list[str],
    remove: list[str],
    progress: bool = False,
) -> typing.Iterable[Channel]:
    """
    The main function of the script.

    Parameters
    ----------
    file_path: Path
    languages: list
    countries: list
    categories: list
    add: list
    remove: list
    progress: bool, default = True
    language: list
    category: list

    Returns
    -------
    Iterable
    Generator
    """
    for channel in tqdm.tqdm(read_file(file_path), disable=not progress):
        if not channel.id in add:
            if channel.id in remove:
                continue
            if not (
                any((lang in channel.languages for lang in languages))
                or any((cat in channel.categories for cat in categories))
                or any((country == channel.country for country in countries))
            ):
                continue
        yield channel


def entry():
    """The entry point of the script."""
    parser = argparse.ArgumentParser(prog="filter", description="Filter channels")
    parser.add_argument("--language", help="The language of the channels", nargs="*")
    parser.add_argument("--country", help="The country of the channels", nargs="*")
    parser.add_argument("--category", help="The category of the channels", nargs="*")
    parser.add_argument("--add", help="Add a channel to the list", nargs="*")
    parser.add_argument("--remove", help="Remove a channel from the list", nargs="*")
    parser.add_argument("--input", "-i", help="The input database file", required=True)
    parser.add_argument(
        "--minify", "-m", action="store_true", help="Minify the JSON result"
    )
    parser.add_argument("output", default="-", help="The output path", nargs="?")
    args = parser.parse_args()
    stdout = not (args.output and args.output != "-")
    results = main(
        file_path=pathlib.Path(args.input),
        languages=args.language or [],
        countries=args.country or [],
        categories=args.category or [],
        add=args.add or [],
        remove=args.remove or [],
        progress=not stdout,
    )
    extra_args = {"separators": (",", ":")} if args.minify else {"indent": 4}
    encoded_result = json.dumps(
        [result.as_dict for result in results], ensure_ascii=False, **extra_args
    )
    if stdout:
        print(encoded_result)
    else:
        pathlib.Path(args.output).write_text(encoded_result)


if __name__ == "__main__":
    entry()

