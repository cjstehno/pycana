import click

from pycana.commands import install, clean, find, info


@click.group(help="... a CLI tool...")
def cli():
    pass


cli.add_command(install.install)
cli.add_command(clean.clean)
cli.add_command(find.find)
cli.add_command(info.info)

if __name__ == '__main__':
    cli()
