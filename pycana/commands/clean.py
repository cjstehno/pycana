"""
Command used to clean the contents of the specified database.
"""
import click
from rich.console import Console

from pycana.services.database import clear_db, resolve_db_path


@click.command()
@click.option("--db-file", default=None, help="The file to be used for the database.")
def clean(db_file: str) -> None:
    """
    Cleans the database contents, but does not delete the file.

    Args:
        db_file: the path to the database file (or None).
    """
    console = Console()
    db_file = resolve_db_path(db_file)

    console.print(f"Cleaning the database ({db_file})...", style="blue")

    clear_db(db_file)

    console.print("Done.", style="green b")
