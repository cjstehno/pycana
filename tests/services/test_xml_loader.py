from pathlib import Path
from typing import List

import pytest
from rich.console import Console

from pycana.models import School, Caster
from pycana.services.xml_loader import load_spells


# FIXME: test
# test with zipped files
# - load_all_spells(verbose=True)
# - bad data (error handling)


@pytest.mark.parametrize(
    "file_name, verbose",
    [
        ("spells_a.xml", True),
        ("spells_a.xml.gz", True),
        ("spells_a.xml", False),
        ("spells_a.xml.gz", False),
    ],
)
def test_load_spells(file_name: str, verbose: bool, monkeypatch) -> None:
    output: List[str] = []

    def _fake_print(*args, **_):
        output.append(args[0])

    console = Console()

    # stub out the print method, so we can collect call values
    monkeypatch.setattr(console, "print", _fake_print)

    xml_file = str(Path(__file__).parent.parent.joinpath("resources", file_name))

    spells = load_spells(console, xml_file, verbose=verbose)

    assert len(spells) == 17

    assert spells[3].book == "OGL A"
    assert spells[3].name == "Alter Self"
    assert spells[3].level == 2
    assert spells[3].school == School.TRANSMUTATION
    assert spells[3].casters == [Caster.SORCERER, Caster.WIZARD]
    assert spells[3].range == "Self"
    assert spells[3].duration == "Concentration, up to 1 hour."
    assert spells[3].casting_time == "1 action"
    assert not spells[3].ritual
    assert spells[3].guild
    assert spells[3].category == ""
    assert spells[3].components == [{"type": "verbal"}, {"type": "somatic"}]
    assert spells[3].description.strip().startswith("You assume a different form.")

    if verbose:
        assert len(output) == 2

        assert output[0].startswith("Loading ") and output[0].endswith(f"/pycana/tests/resources/{file_name}...")
        assert output[1].startswith(" ∟ Loaded 17 spells from ") and output[1].endswith(" s).")

    else:
        assert len(output) == 0
