"""Merges the redundant program data in an XMLTV file."""

from __future__ import annotations

import argparse
import logging
import pathlib
from xml.dom.minidom import Document, Element, parse

import tqdm


class ChildNodes:
    """A set of DOM elements"""

    def __init__(self, parent: Element) -> None:
        """Initialize tracker for a parent element."""
        super().__init__()
        cloned = parent.cloneNode(deep=False)
        if not cloned:
            msg = "Couldn't clone parent element"
            raise ValueError(msg)
        self.parent: Element = cloned
        self.seen_elements: set[str] = set()

        for child in self.parent.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                self.add_unique_element(child)

    def __contains__(self, element: Element | None) -> bool:
        """Check if an element is already seen."""
        if not element:
            return False
        signature = self.generate_signature(element)
        return signature in self.seen_elements

    def __len__(self) -> int:
        """Get the number of unique elements."""
        return len(self.seen_elements)

    @classmethod
    def normalize(cls, text: str) -> str:
        """Normalize text content for comparison."""
        if not text:
            return ""
        return text.strip().lower().replace("\n", " ").replace("\t", " ")

    @classmethod
    def generate_signature(cls, element: Element) -> str:
        """
        Create a unique signature for an element.

        Based on tag, attributes, and text.
        """
        try:
            tag = element.tagName
            # Get sorted attributes for consistent comparison
            attrs = sorted(element.attributes.items()) if element.attributes else []
            attr_str = ",".join(f"{k}={v}" for k, v in attrs)

            # Get normalized text content
            text_content = ""
            for child in element.childNodes:
                if child.nodeType == child.TEXT_NODE:
                    text_content += cls.normalize(child.nodeValue or "")
        except AttributeError:
            # Handle text nodes or other node types
            if hasattr(element, "nodeValue") and element.nodeValue:
                return f"TEXT|{cls.normalize(element.nodeValue)}"  # type: ignore[unreachable]
            return "UNKNOWN"
        except Exception as e:
            msg = f"Error generating signature for element: {e}"
            logging.exception(msg)
            return "ERROR"
        else:
            return f"{tag}|{attr_str}|{text_content}"

    def add_unique_element(self, element: Element | None) -> bool:
        """Add element if it's unique, return True if added."""
        if not element:
            return False

        signature = self.generate_signature(element)
        if signature in self.seen_elements:
            return False

        self.seen_elements.add(signature)
        cloned = element.cloneNode(deep=True)
        if not cloned:
            return False
        self.parent.appendChild(cloned)
        return True


def merge_programs(programs: list[Element]) -> Element:
    """
    Merge redundant program data from multiple program elements.

    Parameters
    ----------
    programs: List[Element]
        List of program elements to merge

    Returns
    -------
    Element
        Merged program element containing unique child elements
    """
    if not programs:
        msg = "Cannot merge empty program list"
        raise ValueError(msg)

    cloned = programs[0].cloneNode(deep=True)
    if not cloned:
        msg = "Couldn't clone the first program element"
        raise ValueError(msg)
    child_nodes = ChildNodes(cloned)

    # Merge children from other programs
    for program in programs[1:]:
        for child in program.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                child_nodes.add_unique_element(child)

    return child_nodes.parent


def find_duplicate_programs(dom: Document) -> dict[str, list[Element]]:
    """
    Find programs with the same start time and channel.

    Parameters
    ----------
    dom: Document
        XML document to search for duplicate programs

    Returns
    -------
    dict[str, list[Element]]
        Dictionary mapping program keys to lists of duplicate elements
    """
    program_groups: dict[str, list[Element]] = {}

    for program in dom.getElementsByTagName("programme"):
        start_time = program.getAttribute("start")
        channel = program.getAttribute("channel")

        if not start_time or not channel:
            msg = "Program missing start time or channel"
            msg += f": {program.toxml()[:100]}..."
            logging.warning(msg)
            continue

        key = f"{channel}:{start_time}"
        try:
            program_groups[key].append(program)
        except KeyError:
            program_groups[key] = [program]

    # Return only groups with duplicates
    return {
        key: programs for key, programs in program_groups.items() if len(programs) > 1
    }


def main(dom: Document, *, show_progress: bool = False) -> int:
    """
    Merge duplicate programs in XMLTV document.

    Parameters
    ----------
    dom: Document
        XMLTV document to process
    show_progress: bool, default=False
        Whether to show progress bar

    Returns
    -------
    int
        Number of merged programs
    """
    duplicate_groups = find_duplicate_programs(dom)

    if not duplicate_groups:
        logging.info("No duplicate programs found")
        return 0

    merged_count = 0

    progress_iter = tqdm.tqdm(
        duplicate_groups.items(),
        desc="Merging programs",
        disable=not show_progress,
        unit="group",
    )

    for key, programs in progress_iter:
        try:
            # Merge all programs in the group
            merged_program = merge_programs(programs)

            for index, program in enumerate(programs):
                if not program.parentNode:
                    continue

                # Replace first program with merged version
                parent = program.parentNode
                parent.replaceChild(merged_program, program)

                # Remove all subsequent duplicates
                for child in programs[index + 1 :]:
                    if child.parentNode:
                        parent.removeChild(child)
                break

            merged_count += len(programs) - 1

        except Exception as e:
            msg = f"Error merging programs for key {key}: {e}"
            logging.exception(msg)
            continue

    msg = (
        f"Merged {merged_count} duplicate programs into {len(duplicate_groups)} "
        "unique programs"
    )
    logging.info(msg)
    return merged_count


def validate_xmltv_file(file_path: pathlib.Path) -> Document:
    """
    Validate and parse XMLTV file.

    Args:
        file_path: Path to XMLTV file

    Returns:
        Parsed XML document

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If not a valid XMLTV file
    """
    if not file_path.exists():
        msg = f"Input file not found: {file_path}"
        raise FileNotFoundError(msg)

    with file_path.open("r") as f:
        dom = parse(f)  # noqa: S318

    # Basic XMLTV validation
    root = dom.documentElement
    if not root:
        msg = f"Empty XML document: {file_path}"
        raise ValueError(msg)
    if root.tagName != "tv":
        msg = f"Not a valid XMLTV file: root element is '{root.tagName}', expected 'tv'"
        raise ValueError(msg)

    return dom


def entry() -> None:
    """Entrypoint for the script."""
    parser = argparse.ArgumentParser(
        prog="xmltv-merger",
        description="Merge duplicate program data in XMLTV files",
    )

    parser.add_argument(
        "--input",
        "-i",
        help="Input XMLTV file path",
        type=pathlib.Path,
        required=True,
        metavar="FILE",
    )

    parser.add_argument(
        "output",
        default="-",
        help="Output file path (use '-' to print to console)",
        type=pathlib.Path,
        metavar="FILE",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        help="Enable verbose logging",
        action="store_true",
    )

    parser.add_argument(
        "--no-progress",
        help="Disable progress bar",
        action="store_true",
    )

    args = parser.parse_args()

    stdout = not (args.output and args.output != "-")

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if stdout:
        logging.disable()

    # Parse and validate input file
    msg = f"Loading XMLTV file: {args.input}"
    logging.info(msg)
    dom = validate_xmltv_file(args.input)

    # Count initial programs
    initial_count = len(dom.getElementsByTagName("programme"))
    msg = f"Found {initial_count} programs in input file"
    logging.info(msg)

    # Merge duplicate programs
    merged_count = main(dom, show_progress=not stdout and not args.no_progress)

    # Generate output
    result = dom.toxml(encoding="utf-8").decode("utf-8")

    if stdout:
        print(result)  # noqa: T201
    else:
        pathlib.Path(args.output).write_text(result)
        final_count = len(dom.getElementsByTagName("programme"))
        msg = f"Saved merged XMLTV to: {args.output}"
        logging.info(msg)
        msg = f"Initial program count: {initial_count}"
        logging.info(msg)
        msg = f"Final program count: {final_count} (removed {merged_count} duplicates)"
        logging.info(msg)


if __name__ == "__main__":
    entry()
