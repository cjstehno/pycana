# PyCana

A command line interface for searching through an installed list of DnD 5e spells. It requires spell content bundled 
in custom XML-formatted files (optionally gzipped). Due to the copyright and licensing issues with the spell content,
these bundles are NOT provided in any form.

> This application is intended for my personal use only, use it at your own risk.

# Usage

There are main commands available to the application, accessible by running (either on the source code or installed 
wheel):

    pycana <command>

or 

    pycana --help

for help.

## Install Command

TBD... installs the XML bundled content into the database.

## Info Command

TBD... retrieves info about the database contents.

## Clean Command

TBD... clears out the content of the database.

## Find Command

TBD... flexible ways to filter the list of spells in the database.


## Development

Run `make virtualenvironement` in the project directory to setup the virtual environment in the `.venv` directory - 
if you don't already have one setup for use.

The first time you try to run (for development) locally, you will need to run (in the project root):

    python setup.py develop

(This will not be required if you have recently run the `make virtualenvironment` task).

When running the application locally, you need to run it from the `pycana` subdirectory of the project.

See the `Makefile` for other available tasks, such as running lints and tests.

## Building

To build a distribution (source and wheel), from the root of the project run:

    make dist

then install the wheel where desired with 

    pip install <wheel-file> --user

