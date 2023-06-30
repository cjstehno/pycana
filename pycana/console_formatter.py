"""
Configuration for the rich console.
"""
from rich.console import Console


console = Console()


def format_success(message):
    """Formats the success messages."""
    return console.print(f"[bold green]{message}[/bold green]")


def format_error(message):
    """Formats the error messages."""
    return console.print(f"[bold red]{message}[/bold red]")
