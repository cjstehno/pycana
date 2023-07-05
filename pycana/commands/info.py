"""
Command used to generate a report of the database contents.
"""
from typing import Dict

import click
from rich.console import Console
from rich.table import Table

from pycana.services.database import db_info, resolve_db_path

# FIXME: add ability to show only one of the tables (show: book, school, caster, level, total)


@click.command()
@click.option("-f", "--db-file", default=None, help="The file to be used for the database.")
def info(db_file: str) -> None:
    """
    Generates a report of the database contents with statistics about the spells
    currently contained within it.

    Args:
        db_file: the path to the database file (or None)
    """
    console = Console()
    db_file = resolve_db_path(db_file)

    info_results = db_info(db_file)

    console.print(f"There are {info_results['total']} spells in the database.\n")

    # noinspection PyTypeChecker
    if info_results["total"] > 0:
        console.print(_build_table(info_results, "Book", "books"))
        console.print(_build_table(info_results, "School", "schools"))
        console.print(_build_table(info_results, "Caster", "casters"))
        console.print(_build_table(info_results, "Levels", "levels"))


def _build_table(results: Dict[str, Dict[str, int]], label: str, info_group: str) -> Table:
    table = Table(title=f"By {label}", width=50)
    table.add_column(label)
    table.add_column("Count", justify="center")

    for key in results[info_group].keys():
        table.add_row(str(key), str(results[info_group][key]))

    return table
