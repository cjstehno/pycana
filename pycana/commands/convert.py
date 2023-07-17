"""
Command used to convert spellbook files from the XML (.xml or .xml.gz)
format to the TEXT (.sbk or .sbk.gz) format
"""
import os
import gzip
from pathlib import Path
from typing import TextIO, List

import click
from rich.console import Console

from pycana.models import Spell
from pycana.services.xml_loader import load_spells


@click.command()
@click.option(
    "--source-directory",
    prompt="What directory are the source files in? ",
    help="The directory containing the source files to be installed.",
)
@click.option(
    "--source-compressed",
    is_flag=True,
    default=False,
    help="Specifies that the compressed XML files will be loaded, rather than the uncompressed.",
)
@click.option(
    "--dest-directory",
    prompt="What directory should the converted files be placed? ",
    help="The directory where the converted files will saved.",
)
@click.option(
    "--dest-compressed", is_flag=True, default=False, help="Specifies that the generated files will be compressed."
)
@click.option("--verbose", is_flag=True, help="Enables more extensive logging messages.", default=False)
def convert(
    source_directory: str,
    source_compressed: bool,
    dest_directory: str,
    dest_compressed: bool,
    verbose: bool,
) -> None:
    """
    Converts the .xml or .xml.gz files in the source directory to the spellbook text format in the destination
    directory.
    """
    console = Console()

    source_state = "compressed " if source_compressed else ""
    dest_state = "compressed " if dest_compressed else ""

    console.print(
        f"Converting {source_state}files in '{source_directory}' to {dest_state}files in '{dest_directory}'...",
    )

    src_suffix = ".xml.gz" if source_compressed else ".xml"

    dest_root = Path(dest_directory)
    dest_root.mkdir(parents=True, exist_ok=True)

    for file in filter(lambda f: f.endswith(src_suffix), os.listdir(source_directory)):
        spells = load_spells(console, str(Path(source_directory, file)), verbose=verbose)

        sbk_path = Path(dest_root, file.replace(src_suffix, ".sbk.gz" if dest_compressed else ".sbk"))

        console.print(f"Writing {len(spells)} spells into {sbk_path}", style="yellow")

        if dest_compressed:
            with gzip.open(sbk_path, "wt", encoding="utf-8") as sbk_file:
                _write_spells(sbk_file, spells)
        else:
            with open(sbk_path, "w", encoding="utf-8") as sbk_file:
                _write_spells(sbk_file, spells)

        console.print(f" \u221f Wrote {len(spells)} spells into {sbk_path}", style="green i")


def _write_spells(sbk_file, spells: List[Spell]) -> None:
    # Write the header (assuming all spells in bundle are same book)
    _write_field(sbk_file, "book", spells[0].book)
    _write_field(sbk_file, "guild", "Y" if spells[0].guild else "N")
    sbk_file.write("\n\n")

    for spell in spells:
        _write_field(sbk_file, "name", spell.name)
        _write_field(sbk_file, "level", str(spell.level))
        _write_field(sbk_file, "school", spell.school.name)
        _write_field(sbk_file, "category", spell.category if spell.category is not None else "")
        _write_field(sbk_file, "casting-time", spell.casting_time)
        _write_field(sbk_file, "ritual", "Y" if spell.ritual else "N")
        _write_field(sbk_file, "range", spell.range)
        _write_field(sbk_file, "duration", spell.duration)
        _write_field(sbk_file, "components", _display_components(spell.components, details=True))
        _write_field(sbk_file, "casters", _display_casters(spell.casters))
        sbk_file.write("description:\n")
        sbk_file.write(spell.description)
        sbk_file.write("\n^^^\n\n")


def _write_field(file: TextIO, field: str, value: str) -> None:
    file.write(f"{field}: {value}\n")


def _display_casters(casters) -> str:
    return ", ".join(map(str, casters))


def _display_components(components, details: bool = False) -> str:
    comps = []
    for comp in components:
        if comp["type"] == "material":
            comps.append(f"M{' (' + comp['details'] + ')' if details and comp['details'] else ''}")
        else:
            comps.append(comp["type"][0].upper())
    return ", ".join(comps)
