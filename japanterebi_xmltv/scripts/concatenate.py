"""Concatenate XMLTV documents."""

import argparse
import pathlib
import typing


def concatenate(files: typing.Iterable[pathlib.Path]) -> typing.Iterable[str]:
    """
    Concatenate the XMLTV documents.

    Parameters
    ----------
    files: Iterable
        The XMLTV files to concatenate.

    Yields
    ------
    str
        A line in the concatenated document.
    """
    first_file = True
    for file_path in files:
        with file_path.open() as file:
            for line in file:
                if first_file:
                    if line.strip() == "</tv>":
                        continue
                    yield line
                else:
                    if line.strip().startswith("<?xml") or line.strip().startswith(
                        "<!DOCTYPE"
                    ):
                        continue
                    if line.strip() == "<tv>":
                        continue
                    if line.strip() == "</tv>":
                        continue
                    yield line
        first_file = False
    yield "</tv>\n"


def entry() -> None:
    """Entrypoint for the script."""
    parser = argparse.ArgumentParser(description="Concatenate XMLTV documents")
    parser.add_argument(
        "--input",
        "-i",
        type=pathlib.Path,
        help="Input file",
        nargs="+",
        action="extend",
        required=True,
    )
    parser.add_argument("output", type=pathlib.Path, help="Output file")
    args = parser.parse_args()
    concatenated = "".join(concatenate(args.input))
    stdout = not (args.output and args.output != "-")
    if stdout:
        print(concatenated)  # noqa: T201
    else:
        pathlib.Path(args.output).write_text(concatenated)


if __name__ == "__main__":
    entry()
