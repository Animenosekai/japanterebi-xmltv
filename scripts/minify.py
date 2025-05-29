import argparse
import pathlib


def minify(data: str):
    """
    Minify the XMLTV document.

    Yields
    ------
    str
        A line in the minified document.
    """
    for line in data.splitlines():
        line = line.strip()
        if line:
            yield line


def entry():
    """The main entrypoint"""
    parser = argparse.ArgumentParser(description="Minify the XMLTV document")
    parser.add_argument("--input", "-i", type=pathlib.Path, help="Input file")
    parser.add_argument("output", type=pathlib.Path, help="Output file")
    args = parser.parse_args()
    with pathlib.Path(args.input).open() as file:
        data = file.read()
    minified = "\n".join(minify(data))
    stdout = not (args.output and args.output != "-")
    if stdout:
        print(minified)
    else:
        pathlib.Path(args.output).write_text(minified)


if __name__ == "__main__":
    entry()
