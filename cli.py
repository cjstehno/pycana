import click
from rich.console import Console


console = Console()


@click.command()
@click.option("--name", prompt="Enter your name: ", help="The name to greet")
def greet(name):
    """Greet the users."""
    greeting = f"Hello, {name}."
    console.print(greeting)


if __name__ == "__main__":
    greet()

