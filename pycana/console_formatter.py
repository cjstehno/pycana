from rich.console import Console


console = Console()


def format_success(message):
    return console.print(f"[bold green]{message}[/bold green]")


def format_error(message):
    return console.print(f"[bold red]{message}[/bold red]")
