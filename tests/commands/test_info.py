from typing import Callable, List

from click.testing import CliRunner
from rich.console import Console

from pycana.commands.info import info
from pycana.models import Spell
from pycana.services.database import load_db


def test_info_without_spells(spells_db: str) -> None:
    runner = CliRunner()
    result = runner.invoke(info, ["-f", spells_db])

    assert result.exit_code == 0
    assert result.output.strip() == "There are 0 spells in the database."


def test_info_with_spells(
    spells_db: str,
    spells_from: Callable[[str], List[Spell]],
) -> None:
    spells = spells_from("spells_a.xml")
    load_db(Console(), spells_db, spells)

    runner = CliRunner()
    result = runner.invoke(info, ["-f", spells_db])

    assert result.exit_code == 0
    assert result.output.splitlines(False)[0] == f"There are {len(spells)} spells in the database."
    # FIXME: assert the generated content tables
