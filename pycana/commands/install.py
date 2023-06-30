import click
from rich.console import Console

from pycana.services.database import create_db, load_db, clear_db
from pycana.services.xml_loader import load_all_spells


@click.command()
@click.option(
    '-d', '--source-directory',
    prompt='What directory are the source files in? ',
    help='The directory containing the source files to be installed.'
)
@click.option(
    '-f', '--db-file',
    prompt='What file should be used for the database? ',
    help='The file to be used for the database.'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Enables more extensive logging messages.',
    default=False,
)
def install(source_directory: str, db_file: str, verbose: bool):
    console = Console()
    console.print(f"Installing spells from {source_directory} into {db_file}...", style='blue')

    create_db(db_file)
    clear_db(db_file)
    load_db(
        console,
        db_file,
        load_all_spells(
            console,
            source_directory,
            verbose=verbose,
        ),
        verbose=verbose,
    )

    console.print(f"Done.", style='green b')
