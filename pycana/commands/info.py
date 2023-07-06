"""
Command used to generate a report of the database contents.
"""
from typing import Dict, Optional

import click
from rich.console import Console
from rich.table import Table

from pycana.services.database import db_info, resolve_db_path


@click.command()
@click.option("--db-file", default=None, help="The file to be used for the database.")
@click.option(
    "--show-table",
    type=click.Choice(["total", "book", "school", "caster", "level"], case_sensitive=False),
    default=None,
    help="Show only the specified info table in the results.",
)
def info(db_file: str, show_table: str) -> None:
    """
    Generates a report of the database contents with statistics about the spells currently contained within it.
    """
    console = Console()
    db_file = resolve_db_path(db_file)

    info_results = db_info(db_file)

    total_spell_count = info_results["meta"]["total"]

    if show_table is None or show_table.lower() == "total":
        console.print(f"There are {total_spell_count} spells in the database.\n")

    if total_spell_count > 0:
        _show(console, info_results, show_table, "book")
        _show(console, info_results, show_table, "school")
        _show(console, info_results, show_table, "caster")
        _show(console, info_results, show_table, "level")


def _show(console: Console, results: Dict[str, Dict[str, int]], show_table: Optional[str], table: str) -> None:
    if show_table is None or show_table.lower() == table:
        console.print(_build_table(results, table.capitalize(), f"{table}s"))


def _build_table(results: Dict[str, Dict[str, int]], label: str, info_group: str) -> Table:
    table = Table(title=f"By {label}", width=50)
    table.add_column(label)
    table.add_column("Count", justify="center")

    for key in results[info_group].keys():
        table.add_row(str(key), str(results[info_group][key]))

    return table
