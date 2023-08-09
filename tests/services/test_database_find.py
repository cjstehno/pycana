from typing import Callable, List

import pytest
from rich.console import Console

from pycana.models import Spell, SpellCriteria
from pycana.services.database import load_db, find_spells


# TODO: more testing
# book
# name
# category
# level
# ritual
# guild
# school
# range
# duration
# casting-time
# description
# combinations

@pytest.mark.parametrize(
    "casters, expected_spells",
    [
        ("warlock", ["Astral Projection"]),
        ("bard", ['Awaken', 'Animate Objects', 'Animal Messenger', 'Animal Friendship']),
        ("cleric", ['Augury', 'Aid', 'Animate Dead', 'Astral Projection', 'Antimagic Field']),
        (
            "druid",
            [
                'Animal Friendship',
                'Animal Messenger',
                'Animal Shapes',
                'Antilife Shell',
                'Antipathy or Sympathy',
                'Awaken',
            ],
        ),
        (
            "wizard",
            [
                'Acid Splash',
                'Alarm',
                'Alter Self',
                'Animate Dead',
                'Animate Objects',
                'Antimagic Field',
                'Antipathy or Sympathy',
                'Arcane Eye',
                'Arcane Lock',
                'Astral Projection',
            ]
        ),
        (
            "('wizard', 'cleric')",
            [
                'Acid Splash',
                'Aid',
                'Alarm',
                'Alter Self',
                'Animate Dead',
                'Animate Objects',
                'Antimagic Field',
                'Antipathy or Sympathy',
                'Arcane Eye',
                'Arcane Lock',
                'Astral Projection',
                'Augury',
            ]
        ),
    ],
)
def test_find_with_caster(
    spells_db: str,
    spells_from: Callable[[str], List[Spell]],
    casters: str,
    expected_spells: List[str],
) -> None:
    available_spells = spells_from("spells_a.xml")
    load_db(Console(), spells_db, available_spells, verbose=False)

    criteria = SpellCriteria(caster=casters)

    found_spells = find_spells(spells_db, criteria)

    assert len(found_spells) == len(expected_spells)
    assert set(map(lambda x: x.name, found_spells)) == set(expected_spells)


@pytest.mark.parametrize(
    "casters, general, expected_spells",
    [
        ("wizard", "water", ["Alter Self", "Conjure Elemental", "Contingency", "Control Water"]),
        ("wizard", "heal", []),
        ("cleric", "heal", ["Beacon of Hope", "Cure Wounds"]),
        ("('wizard','cleric')", "water", [
            'Alter Self',
            'Conjure Elemental',
            'Contingency',
            'Control Water',
            'Create Food and Water',
            'Create or Destroy Water',
        ])
    ],
)
def test_find_with_caster_general(
    spells_db: str,
    spells_from: Callable[[str], List[Spell]],
    casters: str,
    general: str,
    expected_spells: List[str],
) -> None:
    available_spells = spells_from("spells_a.xml") + spells_from("spells_b.xml") + spells_from("spells_c.xml")
    load_db(Console(), spells_db, available_spells, verbose=False)

    criteria = SpellCriteria(caster=casters, general=general)

    found_spells = find_spells(spells_db, criteria)

    assert len(found_spells) == len(expected_spells)
    assert set(map(lambda x: x.name, found_spells)) == set(expected_spells)
