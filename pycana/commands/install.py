"""
Command used to install spells in a database.
"""
import click
from rich.console import Console

from pycana.services.database import create_db, load_db, clear_db, resolve_db_path
from pycana.services.xml_loader import load_all_spells

# FIXME: add support for text format (spellbook text - .sbk or .sbk.gz)

@click.command()
@click.option(
    "--source-directory",
    prompt="What directory are the source files in? ",
    help="The directory containing the source files to be installed.",
)
@click.option("--db-file", default=None, help="The file to be used for the database.")
@click.option("--name-filter", default=None, help="Suffix filter used to restrict the files loaded.")
@click.option("--verbose", is_flag=True, help="Enables more extensive logging messages.", default=False)
def install(source_directory: str, db_file: str, name_filter: str, verbose: bool) -> None:
    """
    Installs the spells from the specified source directory into the given database file.
    """
    console = Console()

    db_file = resolve_db_path(db_file)

    console.print(f"Installing spells from {source_directory} into {db_file}...", style="blue")

    create_db(db_file)
    clear_db(db_file)
    load_db(
        console,
        db_file,
        load_all_spells(
            console,
            source_directory,
            name_filter=name_filter,
            verbose=verbose,
        ),
        verbose=verbose,
    )

    console.print("Done.", style="green b")
