import sqlite3
from typing import Final, Dict, List, Any

from rich.console import Console

from pycana.models import Spell, SpellCriteria, Caster

# noinspection SqlNoDataSourceInspection
_CREATE_SQL: Final[str] = '''
    CREATE TABLE IF NOT EXISTS spells (
        book TEXT not null,
        name TEXT not null, 
        level INTEGER not null,
        school TEXT not null,
        ritual INTEGER not null default 0,
        guild INTEGER NOT NULL DEFAULT 0,
        category TEXT,
        range TEXT NOT NULL,
        duration TEXT NOT NULL,
        casting_time TEXT NOT NULL,
        description TEXT NOT NULL,
        casters TEXT NOT NULL,
        components TEXT NOT NULL,
        PRIMARY KEY (book, name)
    )
    '''

# noinspection SqlNoDataSourceInspection
_SAVE_SQL: Final[str] = '''
    INSERT INTO spells
        (
            book, name, level, school, ritual, guild, category, range, duration, 
            casting_time, description, casters, components
        )
    VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

# noinspection SqlNoDataSourceInspection
_CLEAR_SQL: Final[str] = 'DELETE FROM spells'

# noinspection SqlNoDataSourceInspection
_FIND_SQL = '''
    SELECT
        book, name, level, school, ritual, guild, category, range, duration, casting_time, 
        description, casters, components
    FROM spells
'''

# noinspection SqlNoDataSourceInspection
_INFO_TOTAL: Final[str] = 'select count(*) from spells'

# noinspection SqlNoDataSourceInspection
_INFO_BOOKS: Final[str] = 'SELECT book, count(*) from spells group by book'

# noinspection SqlNoDataSourceInspection
_INFO_LEVELS: Final[str] = 'select level,count(*) from spells group by level'

# noinspection SqlNoDataSourceInspection
_INFO_SCHOOLS: Final[str] = 'select school, count(*) from spells group by school'

# noinspection SqlNoDataSourceInspection
_INFO_CASTERS: Final[str] = "select count(*) from spells where lower(casters) like"


def create_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as cn:
        c = cn.cursor()
        c.execute(_CREATE_SQL)
        c.close()
        cn.commit()


def load_db(console: Console, db_path: str, spells: List[Spell], verbose: bool = False) -> None:
    stored_count = 0

    if verbose:
        console.print(f"Loading {len(spells)} spells...", style='yellow')

    with sqlite3.connect(db_path) as cn:
        c = cn.cursor()

        for spell in spells:
            c.execute(_SAVE_SQL, spell.to_row())

            if verbose:
                console.print(f"\u2714 Stored: {spell}", style='green i')

            stored_count += 1

        c.close()
        cn.commit()

        if verbose:
            console.print(f"Stored all {stored_count} spells.", style='blue b')


def clear_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as cn:
        c = cn.cursor()
        c.execute(_CLEAR_SQL)
        c.close()
        cn.commit()


# FIXME: list spells matching criteria - as AND
# FIXME: document the query stuff
# wildcard matching: book, name, category, range, duration, casting-time, description
# equal to: level, ritual, guild
# equal to or one of: school, casters
#
# wildcard matching - book='chest' ==> Dead Man's Chest (case insensitive contains)
#
# equal to - level=3, ritual=True, guild=False
#
# one-of - casters='(Wizard, Warlock)' ==> wizard OR warlock
# equal to - casters=wizard
#
# should also support global='foo' which will find all with any field containing


def find_spells(db_path: str, criteria: SpellCriteria = None) -> List[Spell]:
    spells = []

    with sqlite3.connect(db_path) as cn:
        c = cn.cursor()
        c.execute(f"{_FIND_SQL} {criteria.where() if criteria and not criteria.empty() else ''}")
        results = c.fetchall()
        for row in results:
            spells.append(Spell.from_row(row))
        c.close()
        cn.commit()

    return spells


def db_info(db_path: str) -> Dict[str, Dict[str, int]]:
    """
    Used to retrieve statistical information about the contents of the spell database.

    :param db_path: the path to the database file
    :return: a dictionary containing the statistical information (counts by type)
    """
    info: Dict[str, Dict[str, int]] = {
        'total': _query(db_path, _INFO_TOTAL)[0][0],
        'books': {},
        'levels': {},
        'schools': {},
        'casters': {}
    }

    for bc in _query(db_path, _INFO_BOOKS):
        info['books'][bc[0]] = bc[1]

    for lv in _query(db_path, _INFO_LEVELS):
        info['levels'][lv[0]] = lv[1]

    for sc in _query(db_path, _INFO_SCHOOLS):
        info['schools'][sc[0]] = sc[1]

    for caster in Caster.__members__.values():
        for cs in _query(db_path, f"{_INFO_CASTERS} '%{caster.name.lower()}%'"):
            info['casters'][caster.name] = cs[0]

    return info


def _query(db_path: str, sql: str) -> List[Any]:
    query_results = []

    with sqlite3.connect(db_path) as cn:
        c = cn.cursor()
        c.execute(sql)
        results = c.fetchall()
        for row in results:
            query_results.append(row)
        c.close()
        cn.commit()

    return query_results
