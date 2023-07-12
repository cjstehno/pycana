"""
The main entry point for the pycana command line application.
"""
import click

from .commands import install, clean, find, info, convert


@click.version_option()
@click.group(help="A tool for searching through a spell database.")
def main():
    pass


main.add_command(install.install)
main.add_command(clean.clean)
main.add_command(find.find)
main.add_command(info.info)
main.add_command(convert.convert)

if __name__ == "__main__":  # pragma: no cover
    main()
