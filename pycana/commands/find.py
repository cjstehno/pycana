"""
Command used to find spells in the database by criteria.
"""
import html
from typing import List, Final, Callable, Any, Dict, Optional, Union

import click
from rich.console import Console, ConsoleRenderable, RichCast
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text

from pycana.models import SpellCriteria, Spell
from pycana.services.database import find_spells, resolve_db_path

_COLUMNS: Final[Dict[str, Callable[[Any], Optional[Union[ConsoleRenderable, RichCast, str]]]]] = {
    "book": lambda sp: html.unescape(sp.book),
    "name": lambda sp: html.unescape(sp.name),
    "level": lambda sp: str(sp.level),
    "school": lambda sp: str(sp.school),
    "category": lambda sp: sp.category if sp.category else "-",
    "ritual": lambda sp: "Y" if sp.ritual else "N",
    "guild": lambda sp: "Y" if sp.guild else "N",
    "range": lambda sp: sp.range,
    "duration": lambda sp: sp.duration,
    "casting_time": lambda sp: sp.casting_time,
    "description": lambda sp: Markdown(sp.description),
    "casters": lambda sp: _display_casters(sp.casters),
    "components": lambda sp: _display_components(sp.components),
}


# FIXME: maybe make default cols a configured thing ~/.pycana/pycana.cfg ?
# FIXME: add ability to search range, casting_time, duration, and description individually


@click.command()
@click.option("-f", "--db-file", default=None, help="The file to be used for the database.")
@click.option("-b", "--book", default=None, help='Filters the results for "book" containing the given string.')
@click.option("-n", "--name", default=None, help='Filters the results for "name" containing the given string.')
@click.option("--category", default=None, help='Filters the results for "category" containing the given string.')
@click.option("-l", "--level", default=None, help='Filters the results for "level" matching the criteria.')
@click.option("-r", "--ritual", default=None, help='Filters the results for "ritual" containing the given string.')
@click.option("--guild", default=None, help='Filters the results for "guild" containing the given string.')
@click.option("-c", "--caster", default=None, help='Filers the results for "caster" containing the given string.')
@click.option("-s", "--school", default=None, help='Filers the results for "school" containing the given string.')
@click.option(
    "--limit", default=None, help="Limits the results to the specified number of rows (unlimited by default)."
)
@click.option(
    "-g",
    "--general",
    default=None,
    help="Filers the results for multiple fields containing the given string.",
)
@click.option(
    "--sort-by",
    default=None,
    help="Sorts the results by the specified field (book, name, level, category, or school). May be asc or desc.",
)
@click.option(
    "--selection/--no-selection",
    default=True,
    help="Shows or hides the single spell selection option and just renders the table.",
)
@click.option(
    "--show-cols",
    default=None,
    help="Specifies the columns that are to be shown (book, name, level, school, ritual, guild, category, range, "
    "duration, casting_time, casters, components, or description)",
)
@click.option(
    "--hide-cols",
    default=None,
    help="Specifies the columns that are to be hidden (book, name, level, school, ritual, guild, category, range, "
    "duration, casting_time, casters, components, or description)",
)
# pylint: disable=too-many-locals
def find(
    db_file: str,
    book: str,
    name: str,
    category: str,
    level: str,
    ritual: str,
    guild: str,
    caster: str,
    school: str,
    limit: int,
    general: str,
    sort_by: str,
    selection: bool,
    show_cols: str,
    hide_cols: str,
) -> None:
    """
    Finds spells filtered by the provided criteria from the specified database.
    """
    console = Console()

    spells = find_spells(
        resolve_db_path(db_file),
        _build_criteria(book, name, category, level, ritual, guild, caster, school, general),
        limit,
        sort_by,
    )

    if len(spells) == 0:
        console.print("No spells found matching your criteria.", style="yellow b i")
        return

    _display_results(console, spells, _resolve_visible_cols(show_cols, hide_cols))

    if selection:
        selected = console.input(f"Which one would you like to view (1-{len(spells)}; 0 to quit)? ").strip()
        if selected != "0":
            _display_single(console, spells[(int(selected) - 1)])


def _build_criteria(
    book: str,
    name: str,
    category: str,
    level: str,
    ritual: str,
    guild: str,
    caster: str,
    school: str,
    general: str,
) -> SpellCriteria:
    criteria = SpellCriteria()

    if general and len(general) > 0:
        criteria.general = general

    if book and len(book) > 0:
        criteria.book = html.unescape(book)

    if name and len(name) > 0:
        criteria.name = html.unescape(name)

    if category and len(category) > 0:
        criteria.category = category

    if caster and len(caster) > 0:
        criteria.caster = caster

    if school and len(school) > 0:
        criteria.school = school

    if level and len(level) > 0:
        criteria.level = level

    if ritual and len(ritual) > 0:
        criteria.ritual = ritual.lower() in ["true", "yes", "y"]

    if guild and len(guild) > 0:
        criteria.guild = guild.lower() in ["true", "yes", "y"]

    return criteria


def _resolve_visible_cols(shown_cols: str, hidden_cols: str) -> List[str]:
    # FIXME: call configuration:load(location)['default_columns']
    # FIXME: add ability to add a column to the default list
    visible_cols = ["book", "name", "level", "school", "category", "ritual", "guild", "casters", "components"]

    if shown_cols:
        visible_cols = list(map(lambda x: x.strip(), shown_cols.split(",")))

    if hidden_cols:
        hidden_cols_list = list(map(lambda x: x.strip(), hidden_cols.split(",")))
        visible_cols = [i for i in visible_cols if i not in hidden_cols_list]

    return visible_cols


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


def _output_field(console: Console, field_name: str, field_value: str) -> None:
    console.print(Text.assemble((f"{field_name}: ", "white b"), field_value))


def _display_results(console: Console, spells: List[Spell], visible_cols: List[str]) -> None:
    table = Table(highlight=True)
    table.add_column("N", style="blue b")

    for vis_col in visible_cols:
        table.add_column(vis_col.capitalize())

    for idx, spell in enumerate(spells):
        cols: List[Union[ConsoleRenderable, RichCast, str]] = [str(idx + 1)]
        for vis_col in visible_cols:
            cols.append(_COLUMNS[vis_col](spell))  # type: ignore[arg-type]

        table.add_row(*cols)

    console.print(table)


def _display_single(console: Console, spell: Spell) -> None:
    console.print(f"\n{html.unescape(spell.name)}", style="red b")
    console.print(f"level {spell.level} {spell.school}{' (ritual)' if spell.ritual else ''}", style="white b i")
    if spell.category and len(spell.category) > 0:
        console.print(f"Category: {spell.category}")

    _output_field(console, "Book", html.unescape(spell.book))
    _output_field(console, "Range", spell.range)
    _output_field(console, "Duration", spell.duration)
    _output_field(console, "Casting Time", spell.casting_time)
    _output_field(console, "Components", _display_components(spell.components, details=True))
    _output_field(console, "Casters", _display_casters(spell.casters))

    console.print()
    console.print(Markdown(spell.description))
