"""
Functions used to load Spell XML files (zipped or unzipped)
"""
from __future__ import annotations

import gzip
import os
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, cast, Optional
from xml.etree.ElementTree import Element

from rich.console import Console

from pycana.models import Spell, School, Caster


def load_all_spells(
    console: Console,
    spells_dir: str,
    name_filter: Optional[str] = ".xml.gz",
    verbose: Optional[bool] = False,
) -> List[Spell]:
    """
    Loads all spells contained in the spell book files (.xml or .xml.gz) contained in the given directory (not
    recursive). If a `name_filter` is provided, it will be used to match the file names as an "ends-with" check.

    Args:
        console: the output console to be used
        spells_dir: the path to the directory containing the spell book files
        name_filter: an optional (ends-with) name filter (.xml.gz will be used by default)
        verbose: an optional flag that will generate more detailed console output

    Returns: a list of spells from all of the loaded books.
    """
    overall_start_time = time.time()
    used_filter: str = name_filter if name_filter is not None else ".xml.gz"

    all_spells = []
    for file in filter(lambda f: f.endswith(used_filter), os.listdir(spells_dir)):
        all_spells += load_spells(console, str(Path(spells_dir, file)), verbose=verbose)

    overall_elapsed = format(time.time() - overall_start_time, ".2f")

    if verbose:
        console.print(
            f"\u2606\u2606 Done loading {len(all_spells)} spells ({overall_elapsed} s) \u2606\u2606.",
            style="blue b",
        )

    return all_spells


def load_spells(
    console: Console,
    xml_file: str,
    verbose: Optional[bool] = False,
) -> List[Spell]:
    """
    Loads all the spells contained in the given spell book file (.xml.gz if zipped, otherwise .xml).

    Args:
        console: the output console
        xml_file: the xml file to be read (.xml.gz or .xml)
        verbose: optional verbose flag - when True, it will write more information to the console

    Returns: a list of spells parsed from the file.
    """

    zipped = xml_file.endswith(".xml.gz")

    if verbose:
        console.print(f"Loading {xml_file}...", style="yellow")

    if zipped:
        with gzip.open(xml_file, "rb") as f:
            return _read_xml(console, xml_file, f, verbose)
    else:
        with open(xml_file, "r", encoding="utf-8") as f:
            return _read_xml(console, xml_file, f, verbose)


def _read_xml(console: Console, source: str, file, verbose: Optional[bool]) -> List[Spell]:
    spells = []

    file_start_time = time.time()
    tree = ET.ElementTree(ET.fromstring(file.read()))
    root = tree.getroot()

    spell_count = 0
    for child in root.iter("spell"):
        if root.get("name") is not None:
            spells.append(_parse_spell(str(root.get("name")), child))
            spell_count += 1

    if verbose:
        file_elapsed_time = format(time.time() - file_start_time, ".2f")
        console.print(
            f" \u221f Loaded {spell_count} spells from {source} ({file_elapsed_time} s).",
            style="green i",
        )

    return spells


def _find_elt_text(elt: Element, name: str, required: bool = True) -> str:
    if elt.find(name) is not None and elt.find(name).text is not None:  # type: ignore[union-attr]
        return str(cast(Element, elt.find(name)).text)
    elif required:
        raise ValueError(f"Element ({name}) has no value!")
    else:
        return ""


def _required_attr(elt: Element, name: str) -> str:
    if elt.get(name) is not None:
        return elt.get(name)  # type: ignore[return-value]
    else:
        raise ValueError(f"Element ({elt.tag}) has no attribute ({name})!")


def _parse_spell(book: str, elt: Element) -> Spell:
    """
    Extracts a Spell object from the provided XML element data, and the given book name.

    :param book: the name of the book containing the spell
    :param elt: the XML element enclosing the spell information
    :return: the loaded spell instance
    """
    spell = Spell(
        book=book if book else "Loose Spells",
        name=_find_elt_text(elt, "name"),
        level=int(_required_attr(elt, "level")),
        school=School.from_str(_required_attr(elt, "school")),
        ritual=_required_attr(elt, "ritual").lower() == "true",
        guild=_required_attr(elt, "guild").lower() == "true",
        category=_find_elt_text(elt, "category", required=False),
        range=_find_elt_text(elt, "range"),
        duration=_find_elt_text(elt, "duration"),
        casting_time=_find_elt_text(elt, "casting-time"),
        description=_find_elt_text(elt, "description"),
        casters=[],
        components=[],
    )

    spell.casters = []
    for caster in cast(Element, elt.find("casters")).iter():
        if caster.tag.lower() != "casters":
            spell.casters.append(Caster.from_str(caster.tag))

    spell.components = []
    for component in cast(Element, elt.find("components")).iter():
        if component.tag.lower() == "components":
            continue
        if component.tag.lower() == "material":
            spell.components.append({"type": "material", "details": component.text if component.text else ""})
        else:
            spell.components.append({"type": component.tag})

    return spell
