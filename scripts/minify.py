import argparse
import pathlib

import htmlmin


def entry():
    """The main entrypoint"""
    parser = argparse.ArgumentParser(description="Minify the XMLTV document")
    parser.add_argument("--input", "-i", type=pathlib.Path, help="Input file")
    parser.add_argument("output", type=pathlib.Path, help="Output file")
    args = parser.parse_args()
    with pathlib.Path(args.input).open() as file:
        data = file.read()
    minified = htmlmin.minify(
        data,
        remove_comments=True,
        remove_empty_space=True,
        remove_all_empty_space=True,
        reduce_empty_attributes=True,
        remove_optional_attribute_quotes=True,
        convert_charrefs=True,
    )
    stdout = not (args.output and args.output != "-")
    if stdout:
        print(minified)
    else:
        pathlib.Path(args.output).write_text(minified)


if __name__ == "__main__":
    entry()

