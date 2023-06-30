import click
from rich.console import Console

from pycana.services.database import clear_db


@click.command()
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
def clean(db_file: str, verbose: bool):
    console = Console()
    console.print(f"Cleaning the database ({db_file})...", style='blue')

    clear_db(db_file)

    console.print(f"Done.", style='green b')
