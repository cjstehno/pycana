"""
Command used to find spells in the database by criteria.
"""
import html
import random
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
    "description": lambda sp: Markdown(sp.description[0:150] + "..."),
    "casters": lambda sp: _display_casters(sp.casters),
    "components": lambda sp: _display_components(sp.components),
}


# FIXME: add --offset N to offset the starting index (when using --liomit)


@click.command()
@click.option("--db-file", default=None, help="The file to be used for the database, if not using the default.")
@click.option("--book", default=None, help='Filters the results for "book" containing the given string.')
@click.option("--name", default=None, help='Filters the results for "name" containing the given string.')
@click.option("--category", default=None, help='Filters the results for "category" containing the given string.')
@click.option("--level", default=None, help='Filters the results for "level" matching the criteria.')
@click.option("--ritual", default=None, help='Filters the results for "ritual" containing the given string.')
@click.option("--guild", default=None, help='Filters the results for "guild" containing the given string.')
@click.option("--caster", default=None, help='Filers the results for "caster" containing the given string.')
@click.option("--school", default=None, help='Filers the results for "school" containing the given string.')
@click.option("--range", default=None, help='Filters the results for "range" containing the given string.')
@click.option("--duration", default=None, help='Filters the results for "duration" containing the given string.')
@click.option("--casting-time", default=None, help='Filters the results for "casting time" containing the given value.')
@click.option("--description", default=None, help='Filters the results for "description" containing the given string.')
@click.option(
    "--limit", default=None, help="Limits the results to the specified number of rows (unlimited by default)."
)
@click.option(
    "--general",
    default=None,
    help="Filers the results for multiple fields containing the given string.",
)
@click.option(
    "--sort-by",
    default=None,
    help="Sorts the results by the specified field. Direction ('asc' or 'desc') may specified by adding it to the end.",
)
@click.option("--no-selection", is_flag=True, help="Hides the spell selection option and just renders the table.")
@click.option("--show-cols", default=None, help="Specifies the columns that are to be shown.")
@click.option("--hide-cols", default=None, help="Specifies the columns that are to be hidden.")
@click.option("--add-cols", default=None, help="Adds the specified columns to the display.")
@click.option("--random-selection", is_flag=True, help="Randomly selects a spell matching the provided criteria.")
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
    range: str,  # pylint: disable=redefined-builtin
    duration: str,
    casting_time: str,
    description: str,
    limit: int,
    general: str,
    sort_by: str,
    no_selection: bool,
    show_cols: str,
    hide_cols: str,
    add_cols: str,
    random_selection: bool,
) -> None:
    """
    Finds spells filtered by the provided criteria from the specified database.

    The various criteria parameters may be single- or multi-value, where multiple values are specified as "('one',
    'two', 'three')". Each of the values is an OR clause.

    Example: `--level 3 --caster "('wizard', 'warlock')"` would find third-level spells that can be cast by a wizard or
    warlock.

    The values are compared with string "contains" comparisons ignoring case.

    The available columns are: book, name, level, school, ritual, guild, category, range, duration, casting_time,
    casters, components, and description
    """
    console = Console()

    spells = find_spells(
        resolve_db_path(db_file),
        _build_criteria(
            book,
            name,
            category,
            level,
            ritual,
            guild,
            caster,
            school,
            range,
            duration,
            casting_time,
            description,
            general,
        ),
        limit,
        sort_by,
    )

    if len(spells) == 0:
        console.print("No spells found matching your criteria.", style="yellow b i")
        return

    # FIXME: if there is only one result - just show it?

    if not random_selection:
        _display_results(console, spells, _resolve_visible_cols(show_cols, hide_cols, add_cols))

    if not no_selection:
        if random_selection:
            selected = random.randint(0, len(spells) - 1)
            _display_single(console, spells[selected])
        else:
            selected = int(console.input(f"Which one would you like to view (1-{len(spells)}; 0 to quit)? ").strip())
            if selected != 0:
                _display_single(console, spells[selected - 1])


def _build_criteria(
    book: str,
    name: str,
    category: str,
    level: str,
    ritual: str,
    guild: str,
    caster: str,
    school: str,
    spell_range: str,
    duration: str,
    casting_time: str,
    description: str,
    general: str,
) -> SpellCriteria:
    criteria = SpellCriteria()

    _apply_criteria(criteria, "general", general)
    _apply_criteria(criteria, "book", book, escaped=True)
    _apply_criteria(criteria, "name", name, escaped=True)
    _apply_criteria(criteria, "category", category)
    _apply_criteria(criteria, "range", spell_range)
    _apply_criteria(criteria, "duration", duration)
    _apply_criteria(criteria, "description", description)
    _apply_criteria(criteria, "casting_time", casting_time)
    _apply_criteria(criteria, "caster", caster)
    _apply_criteria(criteria, "school", school)
    _apply_criteria(criteria, "level", level)
    _apply_bool_criteria(criteria, "ritual", ritual)
    _apply_bool_criteria(criteria, "guild", guild)

    return criteria


def _apply_criteria(criteria: SpellCriteria, name: str, value: Optional[str], escaped: Optional[bool] = False) -> None:
    if value is not None and len(value) > 0:
        setattr(criteria, name, value if not escaped else html.unescape(value))


def _apply_bool_criteria(criteria: SpellCriteria, name: str, value: Optional[str]) -> None:
    if value is not None and len(value) > 0:
        setattr(criteria, name, value.lower() in ["true", "yes", "y"])


def _resolve_visible_cols(shown_cols: str, hidden_cols: str, add_cols: str) -> List[str]:
    # FIXME: call configuration:load(location)['default_columns']
    visible_cols = ["book", "name", "level", "school", "category", "ritual", "guild", "casters", "components"]

    if shown_cols is not None:
        visible_cols = _extract_cols(shown_cols)

    if hidden_cols is not None:
        hidden_cols_list = _extract_cols(hidden_cols)
        visible_cols = [i for i in visible_cols if i not in hidden_cols_list]

    if add_cols is not None:
        for col in _extract_cols(add_cols):
            visible_cols.append(col)

    return visible_cols


def _extract_cols(col_list: str) -> List[str]:
    return list(map(lambda x: x.strip(), col_list.split(",")))


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
