from typing import Callable, List

from click.testing import CliRunner
from rich.console import Console

from pycana.commands.clean import clean
from pycana.models import Spell
from pycana.services.database import load_db, db_info


def test_clean(
    spells_db: str,
    spells_from: Callable[[str], List[Spell]],
) -> None:
    spells = spells_from("spells_a.xml")
    load_db(Console(), spells_db, spells, verbose=False)

    info = db_info(spells_db)
    assert info["meta"]["total"] == 17

    runner = CliRunner()
    result = runner.invoke(clean, ["-f", spells_db])
    assert result.exit_code == 0
    assert result.output.splitlines()[0].startswith("Cleaning the database")
    assert result.output.splitlines()[3].endswith("Done.")
