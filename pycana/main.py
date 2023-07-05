"""
The main entry point for the pycana command line application.
"""
import click

from .commands import install, clean, find, info


@click.group(help="... a CLI tool...")
def main():
    pass


main.add_command(install.install)
main.add_command(clean.clean)
main.add_command(find.find)
main.add_command(info.info)

if __name__ == "__main__":
    main()
