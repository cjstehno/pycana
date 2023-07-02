"""
Command used to find spells in the database by criteria.
"""
import click
import html
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text

from pycana.services.database import find_spells
from pycana.models import SpellCriteria


@click.command()
@click.option(
    '-f', '--db-file',
    prompt='What file should be used for the database? ',
    help='The file to be used for the database.'
)
@click.option(
    '-b', '--book',
    default=None,
    help='Filters the results for "book" containing the given string.'
)
@click.option(
    '-n', '--name',
    default=None,
    help='Filters the results for "name" containing the given string.'
)
@click.option(
    '--category',
    default=None,
    help='Filters the results for "category" containing the given string.'
)
@click.option(
    '-l', '--level',
    default=None,
    help='Filters the results for "level" matching the criteria.'
)
@click.option(
    '-r', '--ritual',
    default=None,
    help='Filters the results for "ritual" containing the given string.'
)
@click.option(
    '-c', '--caster',
    default=None,
    help='Filers the results for "caster" containing the given string.'
)
@click.option(
    '--limit',
    default=None,
    help='Limits the results to the specified number of rows.'
)
def find(
    db_file: str,
    book: str,
    name: str,
    category: str,
    level: str,
    ritual: str,
    caster: str,
    limit: int,
) -> None:
    """
    Finds spells by criteria from the specified database.

    Args:
        db_file: the database file path
        book: optional book criteria
        name: optional name criteria
        level: optional level criteria
        ritual: optional ritual criteria


    Returns:

    """
    console = Console()

    # FIXME: would be nice to be able to specify cols shown (or show limited set)
    # FIXME: sorting
    # FIXME: a param to limit the number of rows (offset?)
    # FIXME: add fields: shcool, guild, global

    criteria = SpellCriteria()

    if book and len(book) > 0:
        criteria.book = html.unescape(book)

    if name and len(name) > 0:
        criteria.name = html.unescape(name)

    if category and len(category) > 0:
        criteria.category = category

    if caster and len(caster) > 0:
        criteria.caster = caster

    if level and len(level) > 0:
        criteria.level = level

    if ritual and len(ritual) > 0:
        criteria.ritual = ritual.lower() in ['true', 'yes', 'y']

    spells = find_spells(db_file, criteria) # FIXME: limit shoudl be in query
    spells = spells[0:int(limit)]

    table = Table(highlight=True)

    table.add_column("N", style='blue b')
    table.add_column("Book", no_wrap=True)
    table.add_column("Name", no_wrap=True)
    table.add_column("Lvl")
    table.add_column("School")
    table.add_column("Category")
    table.add_column("Ritual")
    table.add_column("Guild")
    table.add_column("Casters")
    table.add_column("Components")

    for idx, spell in enumerate(spells):
        casters = _display_casters(spell.casters)
        components = _display_components(spell.components)
        table.add_row(
            str(idx+1),
            html.unescape(spell.book),
            html.unescape(spell.name),
            str(spell.level),
            str(spell.school),
            spell.category if spell.category else '-',
            'Y' if spell.ritual else 'N',
            'Y' if spell.guild else 'N',
            casters, components,
        )

    console.print(table)

    selected = console.input(f"Which one would you like to view (1-{len(spells)}; 0 to quit)? ")
    if selected.strip() != '0':
        spell = spells[(int(selected) - 1)]

        console.print(f"\n{html.unescape(spell.name)}", style='red b')
        console.print(
            f"level {spell.level} {spell.school}{' (ritual)' if spell.ritual else ''}",
            style='white b i'
        )
        if spell.category and len(spell.category) > 0:
            console.print(f"Category: {spell.category}")

        _output_field(console, 'Book', html.unescape(spell.book))
        _output_field(console, 'Range', spell.range)
        _output_field(console, 'Duration', spell.duration)
        _output_field(console, 'Casting Time', spell.casting_time)
        _output_field(console, 'Components', _display_components(spell.components, details=True))
        _output_field(console, 'Casters', _display_casters(spell.casters))

        console.print()
        console.print(Markdown(spell.description))


def _display_casters(casters) -> str:
    return ', '.join(map(str, casters))


def _display_components(components, details: bool = False) -> str:
    comps = []
    for comp in components:
        if comp['type'] == 'material':
            comps.append(f"M{' (' + comp['details'] + ')' if details and comp['details'] else ''}")
        else:
            comps.append(comp['type'][0].upper())
    return ', '.join(comps)


def _output_field(console: Console, field_name: str, field_value: str) -> None:
    console.print(Text.assemble((f'{field_name}: ', 'white b'), field_value))