from typing import Callable, List

from click.testing import CliRunner
from rich.console import Console

from pycana.commands.find import find
from pycana.models import Spell
from pycana.services.database import load_db


# TODO: more testing
# book
# name
# category
# level
# ritual
# guild
# caster
# school
# range
# duration
# casting-time
# description


def test_find(spells_db: str, spells_from: Callable[[str], List[Spell]]) -> None:
    spells = spells_from("spells_a.xml")
    load_db(Console(), spells_db, spells)

    runner = CliRunner()
    result = runner.invoke(
        find,
        [
            "--db-file",
            spells_db,
            "--no-selection",
            "--school",
            "divination",
            "--caster",
            '("cleric", "warlock")',
        ],
    )

    assert result.exit_code == 0

    lines = result.output.splitlines()
    assert len(lines) == 6
    assert lines[3].strip() == "│ 1 │ OGL A │ Augury │ 2     │ Divi… │ -      │ Y     │ Y     │ Cleric │ V, S, │"


def test_find_with_caster(spells_db: str, spells_from: Callable[[str], List[Spell]]):
    spells = spells_from("spells_a.xml")
    load_db(Console(), spells_db, spells)

    runner = CliRunner()
    result = runner.invoke(
        find,
        [
            "--db-file",
            spells_db,
            "--show-cols=name,casters",
            "--no-selection",
            "--caster",
            '("wizard", "cleric")',
        ],
    )

    # FIXME: roll this into param test with asserts

    assert result.exit_code == 0
    lines = result.output.splitlines()
    for line in lines:
        print(line)


def test_find_with_caster2(spells_db: str, spells_from: Callable[[str], List[Spell]]):
    spells = spells_from("spells_a.xml")
    load_db(Console(), spells_db, spells)

    runner = CliRunner()
    result = runner.invoke(
        find,
        [
            "--db-file",
            spells_db,
            "--show-cols=name,casters",
            "--no-selection",
            "--caster",
            "bard",
        ],
    )

    # FIXME: roll this into param test with asserts

    assert result.exit_code == 0
    lines = result.output.splitlines()
    for line in lines:
        print(line)


def test_find_with_caster_general(spells_db: str, spells_from: Callable[[str], List[Spell]]):
    available_spells = spells_from("spells_a.xml") + spells_from("spells_b.xml") + spells_from("spells_c.xml")
    load_db(Console(), spells_db, available_spells, verbose=False)

    runner = CliRunner()
    result = runner.invoke(
        find,
        [
            "--db-file",
            spells_db,
            "--show-cols=name,casters",
            "--no-selection",
            "--caster",
            "cleric",
            "--general",
            "heal",
        ],
    )

    # wizard - general heal -> 0
    # cleric - general heal -> 2

    # FIXME: roll this into param test with asserts

    assert result.exit_code == 0
    lines = result.output.splitlines()
    for line in lines:
        print(line)
