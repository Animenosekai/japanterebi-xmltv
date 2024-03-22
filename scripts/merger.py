"""Merges the redundant program data in an XMLTV file."""
import argparse
import pathlib
import typing
from xml.dom.minidom import Document, Element, parse

import tqdm


class ChildNodes:
    """A set of DOM elements"""

    def __init__(self, element: Element):
        """
        Parameters
        ----------
        element: Element
        """
        self.element = element
        self.representations = {self.represent(element)}

    def normalize(self, name: str):
        """
        Normalize the name of an element

        Parameters
        ----------
        name: str

        Returns
        -------
        str
        """
        return name.lower().replace(" ", "").replace("\n", "")

    def represent(self, element: Element):
        """
        Represent an element as a string

        Parameters
        ----------
        element: Element

        Returns
        -------
        str
        """
        return self.normalize(element.toxml())

    def add(self, element: Element):
        """
        Add an element to the set

        Parameters
        ----------
        element: Element
        """
        representation = self.represent(element)
        if not representation or representation in self.representations:
            return
        # print(representation, self.representations)
        self.representations.add(representation)
        return self.element.appendChild(element)
        try:
            tag = str(element.tagName)
        except AttributeError:
            return
        value = str(element.nodeValue).lower().replace(" ", "")
        # Only add the element if it is not already in the set
        for el in self.element.childNodes:
            # The tags are different => the elements are different
            try:
                if el.tagName != tag:
                    continue
            except AttributeError:
                pass
            # The content is different => the elements are different
            if str(el.nodeValue).lower().replace(" ", "") != value:
                continue
            try:
                for key, value in el.attributes.items():
                    # The attributes are different => the elements are different
                    if element.attributes.get(key, None) != value:
                        break
                else:
                    # never breaked, so the attributes are the same
                    return
            except AttributeError:
                return
        self.element.appendChild(element)


def merge_programs(programs: typing.List[Element]) -> Element:
    """
    Merges the redundant program data in a list of program elements.

    Parameters
    ----------
    programs: list

    Returns
    -------
    Element
    """
    # Two child elements are merged if they have the same tag name, attributes and text content.
    new_element = programs[0].cloneNode(deep=True)
    children = ChildNodes(new_element)
    for program in programs[1:]:
        for child in program.childNodes:
            children.add(child)
    return new_element


def main(dom: Document, progress: bool = False):
    """
    The core function for the script.

    Parameters
    ----------
    dom: Document
    progress: bool, default = True
    """
    for programme in tqdm.tqdm(
        dom.getElementsByTagName("programme"), disable=not progress
    ):
        same = []
        for other in dom.getElementsByTagName("programme"):
            if programme.getAttribute("start") == other.getAttribute(
                "start"
            ) and programme.getAttribute("channel") == other.getAttribute("channel"):
                same.append(other)
        if len(same) > 1:
            merged = merge_programs(same)
            for other in same[1:]:
                programme.parentNode.removeChild(other)
            programme.parentNode.replaceChild(merged, programme)


def entry():
    """The main entrypoint for the script."""
    parser = argparse.ArgumentParser(prog="merger", description="Merge program data")
    parser.add_argument(
        "--input", "-i", help="The input XMLTV file", type=pathlib.Path, required=True
    )
    parser.add_argument("output", default="-", help="The output path", nargs="?")
    args = parser.parse_args()
    with pathlib.Path(args.input).open() as file:
        dom = parse(file)
    stdout = not (args.output and args.output != "-")
    main(dom, progress=not stdout)
    result = dom.toxml(encoding="utf-8")
    if stdout:
        print(result.decode("utf-8"))
    else:
        pathlib.Path(args.output).write_bytes(result)


if __name__ == "__main__":
    entry()

