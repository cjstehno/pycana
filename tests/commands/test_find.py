from typing import Callable, List

from click.testing import CliRunner
from rich.console import Console

from pycana.models import Spell
from pycana.services.database import load_db
from pycana.commands.find import find

# TODO: more testing


def test_find(
    spells_db: str,
    spells_from: Callable[[str], List[Spell]],
) -> None:
    spells = spells_from("spells_a.xml")
    load_db(Console(), spells_db, spells)

    runner = CliRunner()
    result = runner.invoke(find, [
        "-f", spells_db,
        '--no-selection',
        '--school', 'divination',
        '--caster', '("cleric", "warlock")',
    ])

    assert result.exit_code == 0

    lines = result.output.splitlines()
    assert len(lines) == 6
    assert lines[3].strip() == "│ 1 │ OGL A │ Augury │ 2     │ Divi… │ -      │ Y     │ Y     │ Cleric │ V, S, │"
