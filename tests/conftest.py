"""
Configuration for pytest.
"""
from pathlib import Path
from typing import List, Callable

import pytest
from rich.console import Console

from pycana.services.database import create_db, clear_db
from pycana.models import Spell
from pycana.services.xml_loader import load_spells


@pytest.fixture
def spells_db(tmp_path) -> str:
    """
    Test fixture used to create and destroy a test database around the test operations.

    Args:
        tmp_path: the temporary path where the database will be created.

    Returns: A string that should be used as the database path for other commands.
    """
    db_path = Path(tmp_path, "test.db")
    create_db(str(db_path))
    yield db_path
    clear_db(str(db_path))


@pytest.fixture
def spells_from() -> Callable[[str], List[Spell]]:
    """
    Test fixture providing a helper function for loading spells from xml files stored in the
    `tests/resources` directory.

    Returns: A function accepting the name of a spell XML file.
    """

    # FIXME: be nice to accept a varargs type thing
    def _here(name: str):
        pth = str(Path(__file__).parent.joinpath("resources", name))
        return load_spells(Console(), pth, verbose=False)

    return _here
