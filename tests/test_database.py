from pathlib import Path
from typing import List, Callable, Final

import pytest
from rich.console import Console

from pycana.services.database import create_db, clear_db, db_info, load_db, find_spells
from pycana.models import Spell, School, Caster, SpellCriteria
from pycana.services.xml_loader import load_spells

_A_SPELL_NAMES: Final[List[str]] = [
    'Acid Splash', 'Aid', 'Alarm', 'Alter Self', 'Animal Friendship', 'Animal Messenger',
    'Animal Shapes', 'Animate Dead', 'Animate Objects', 'Antilife Shell', 'Antimagic Field',
    'Antipathy or Sympathy', 'Arcane Eye', 'Arcane Lock', 'Astral Projection', 'Augury', 'Awaken'
]


@pytest.fixture()
def spells_db(tmp_path) -> str:
    db_path = Path(tmp_path, 'test.db')
    create_db(str(db_path))
    yield db_path
    clear_db(str(db_path))


@pytest.fixture()
def spells_from() -> Callable[[str], List[Spell]]:
    # FIXME: be nice to accept a varargs type thing
    def _here(name: str):
        p = Path(__file__).parent.joinpath('resources', name)
        return load_spells(Console(), str(p), verbose=False, zipped=False)

    return _here


def test_db_info(spells_db: str, spells_from: Callable[[str], List[Spell]]) -> None:
    load_db(
        Console(),
        spells_db,
        spells_from('spells_a.xml') + spells_from('spells_b.xml') + spells_from('spells_c.xml'),
        verbose=False,
    )

    info = db_info(spells_db)

    assert info['total'] == 64
    assert info['books'] == {
        'OGL A': 17,
        'OGL B': 13,
        'OGL C': 34,
    }
    assert info['levels'] == {
        0: 2,
        1: 11,
        2: 10,
        3: 9,
        4: 8,
        5: 11,
        6: 6,
        7: 1,
        8: 5,
        9: 1,
    }
    assert info['schools'] == {
        School.ABJURATION.name: 8,
        School.CONJURATION.name: 10,
        School.DIVINATION.name: 7,
        School.ENCHANTMENT.name: 10,
        School.EVOCATION.name: 7,
        School.ILLUSION.name: 3,
        School.NECROMANCY.name: 10,
        School.TRANSMUTATION.name: 9,
    }
    assert info['casters'] == {
        Caster.BARD.name: 14,
        Caster.CLERIC.name: 24,
        Caster.DRUID.name: 22,
        Caster.PALADIN.name: 7,
        Caster.RANGER.name: 8,
        Caster.SORCERER.name: 21,
        Caster.WARLOCK.name: 11,
        Caster.WIZARD.name: 37,
    }


def test_find_spells_mapper(spells_db: str, spells_from: Callable[[str], List[Spell]]):
    load_db(
        Console(),
        spells_db,
        spells_from('spells_a.xml'),
        verbose=False,
    )

    found_spells = find_spells(spells_db)

    assert found_spells[0] == Spell(
        book='OGL A',
        name='Acid Splash',
        level=0,
        school=School.CONJURATION,
        ritual=False,
        guild=True,
        category=None,
        range='60 feet',
        duration='Instantaneous',
        casting_time='1 action',
        description='You hurl a bubble of acid.\n'
                    '\n'
                    'Choose one creature within range, or choose two creatures '
                    'within range that are within 5 feet of each other. A target '
                    'must succeed on a Dexterity saving throw or take 1d6 acid '
                    'damage.\n'
                    '\n'
                    '**At higher level.** This spell’s damage increases by 1d6 '
                    'when you reach 5th level (2d6), 11th level (3d6), and 17th '
                    'level (4d6).',
        casters=[Caster.SORCERER, Caster.WIZARD],
        components=[{'type': 'verbal'}, {'type': 'somatic'}]
    )


@pytest.mark.parametrize(
    'criteria, expected_results', [
        (None, _A_SPELL_NAMES),
        (SpellCriteria(), _A_SPELL_NAMES),
        (SpellCriteria(name='animal'), ['Animal Friendship', 'Animal Messenger', 'Animal Shapes']),
        (SpellCriteria(name='ANIMAL'), ['Animal Friendship', 'Animal Messenger', 'Animal Shapes']),
        (SpellCriteria(name='gerbil'), []),
        (SpellCriteria(name='animal', level='(1, 2)'), ['Animal Friendship', 'Animal Messenger']),
        (SpellCriteria(name='animal', level='2'), ['Animal Messenger']),
        (SpellCriteria(book='ogl A', range="('30', '60')", caster='cleric'), ['Aid']),
        (SpellCriteria(duration='instantaneous',casting_time='action'), ['Acid Splash']),
        (SpellCriteria(school='necromancy'), ['Animate Dead', 'Astral Projection']),
        (SpellCriteria(ritual=True), ['Alarm', 'Animal Messenger', 'Augury']),
        (SpellCriteria(general='dead'), ['Animate Dead', 'Antilife Shell'])
    ]
)
def test_find_spells(
    spells_db: str,
    spells_from: Callable[[str], List[Spell]],
    criteria: SpellCriteria,
    expected_results: List[str],
) -> None:
    available_spells = spells_from('spells_a.xml')
    load_db(Console(), spells_db, available_spells, verbose=False)

    found_spells = find_spells(spells_db, criteria)

    assert len(found_spells) == len(expected_results)
    assert set(map(lambda x: x.name, found_spells)) == set(expected_results)

