import argparse
import pathlib
import re

# The '&' character is not escaped in some XMLTV document.
REGEX = re.compile(r"&(?!amp;)(?!lt;)(?!gt;)(?!apos;)(?!quot;)")


def fix(data: str):
    """
    Fixes the XMLTV document.

    Returns
    -------
    str
        The fixed document.
    """
    return REGEX.sub("&amp;", data)


def entry():
    """The main entrypoint"""
    parser = argparse.ArgumentParser(description="Fixes the XMLTV document")
    parser.add_argument("--input", "-i", type=pathlib.Path, help="Input file")
    parser.add_argument("output", type=pathlib.Path, help="Output file")
    args = parser.parse_args()
    with pathlib.Path(args.input).open() as file:
        data = file.read()
    fixed = fix(data)
    stdout = not (args.output and args.output != "-")
    if stdout:
        print(fixed)
    else:
        pathlib.Path(args.output).write_text(fixed)


if __name__ == "__main__":
    entry()
