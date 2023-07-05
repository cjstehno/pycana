"""
The shared models for the application.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, unique, auto
from typing import List, Dict, Tuple, Optional


@unique
class School(Enum):
    ABJURATION = auto()
    CONJURATION = auto()
    DIVINATION = auto()
    ENCHANTMENT = auto()
    EVOCATION = auto()
    ILLUSION = auto()
    NECROMANCY = auto()
    TRANSMUTATION = auto()

    def __str__(self) -> str:
        return self.name.capitalize()

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def from_str(label: str) -> School:
        return School[label.upper()]


@unique
class Caster(Enum):
    BARD = auto()
    CLERIC = auto()
    DRUID = auto()
    PALADIN = auto()
    RANGER = auto()
    SORCERER = auto()
    WARLOCK = auto()
    WIZARD = auto()

    def __str__(self) -> str:
        return self.name.capitalize()

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def from_str(label: str) -> Caster:
        return Caster[label.upper()]

    @staticmethod
    def as_string(casters: List[Caster]) -> str:
        return ",".join(list(map(lambda cst: cst.name, casters)))


@dataclass
class Spell:
    book: str
    name: str
    level: int
    school: School
    ritual: bool
    guild: bool
    category: str
    range: str
    duration: str
    casting_time: str
    description: str
    casters: List[Caster]
    components: List[Dict[str, str]]

    def __str__(self):
        return f"{self.book} ({self.level}): {self.name}"

    def to_row(self) -> Tuple:
        return (
            self.book,
            self.name,
            self.level,
            self.school.name,
            1 if self.ritual else 0,
            1 if self.guild else 0,
            self.category,
            self.range,
            self.duration,
            self.casting_time,
            self.description,
            Caster.as_string(self.casters),
            json.dumps(self.components),
        )

    @staticmethod
    def from_row(row) -> Spell:
        return Spell(
            book=row[0],
            name=row[1],
            level=row[2],
            school=School.from_str(row[3]),
            ritual=row[4] == 1,
            guild=row[5] == 1,
            category=row[6],
            range=row[7],
            duration=row[8],
            casting_time=row[9],
            description=row[10],
            casters=list(map(Caster.from_str, str(row[11]).split(","))),
            components=json.loads(row[12]),
        )


@dataclass()
class SpellCriteria:
    book: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    range: Optional[str] = None
    duration: Optional[str] = None
    casting_time: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None  # 1 -or- (1, 3, 7)
    ritual: Optional[bool] = None
    guild: Optional[bool] = None
    school: Optional[str] = None  # conjuration -or- (conjuration, evocation)
    caster: Optional[str] = None  # wizard -or- (wizard, warlock)
    general: Optional[str] = None

    def where(self) -> str:
        clauses = []

        if self.empty():
            return ""
        else:
            self._apply_clause(clauses, "book", self.book)
            self._apply_clause(clauses, "name", self.name)
            self._apply_clause(clauses, "category", self.category)
            self._apply_clause(clauses, "range", self.range)
            self._apply_clause(clauses, "duration", self.duration)
            self._apply_clause(clauses, "casting_time", self.casting_time)
            self._apply_clause(clauses, "description", self.description)
            self._apply_int_clause(clauses, "level", self.level)
            self._apply_bool_clause(clauses, "ritual", self.ritual)
            self._apply_bool_clause(clauses, "guild", self.guild)
            self._apply_clause(clauses, "school", self.school)
            self._apply_clause(clauses, "casters", self.caster)
            self._apply_general_clause(clauses, self.general)

        return f"WHERE {' AND '.join(clauses)}" if len(clauses) > 0 else ""

    @staticmethod
    def _apply_general_clause(clauses: List[str], value: str) -> None:
        general_clauses = []

        if SpellCriteria._not_empty(value):
            SpellCriteria._apply_clause(general_clauses, "book", value)
            SpellCriteria._apply_clause(general_clauses, "name", value)
            SpellCriteria._apply_clause(general_clauses, "category", value)
            SpellCriteria._apply_clause(general_clauses, "range", value)
            SpellCriteria._apply_clause(general_clauses, "duration", value)
            SpellCriteria._apply_clause(general_clauses, "casting_time", value)
            SpellCriteria._apply_clause(general_clauses, "description", value)
            SpellCriteria._apply_clause(general_clauses, "school", value)
            SpellCriteria._apply_clause(general_clauses, "casters", value)

        if len(general_clauses) > 0:
            clauses.append(" OR ".join(general_clauses))

    @staticmethod
    def _apply_clause(clauses: List[str], name: str, value: str) -> None:
        if SpellCriteria._not_empty(value):
            if value.startswith("(") and value.endswith(")"):
                # pylint: disable=eval-used
                clauses.append(SpellCriteria._or_values(name, eval(value)))
            else:
                clauses.append(SpellCriteria._like_contains(name, value))

    @staticmethod
    def _apply_bool_clause(clauses: List[str], name: str, value: Optional[bool]) -> None:
        if value is not None:
            clauses.append(f"{name} = {1 if value else 0}")

    @staticmethod
    def _apply_int_clause(clauses: List[str], name: str, value: str) -> None:
        if SpellCriteria._not_empty(value):
            if value.startswith("(") and value.endswith(")"):
                # pylint: disable=eval-used
                items = map(lambda x: SpellCriteria._value_eq(name, x), eval(value))
                clauses.append(f"({' OR '.join(items)})")
            else:
                clauses.append(SpellCriteria._value_eq(name, value))

    @staticmethod
    def _value_eq(name: str, value: str, quoted: bool = False):
        used_value = f"'{value}'" if quoted else value
        return f"{name} = {used_value}"

    @staticmethod
    def _like_contains(name: str, value: str) -> str:
        return f"LOWER({name}) like '%{value.lower()}%'"

    @staticmethod
    def _or_values(name: str, values: Tuple[str]) -> str:
        return f"({' OR '.join(map(lambda x: SpellCriteria._like_contains(name, x), values))})"

    def empty(self) -> bool:
        return all(
            [
                self._empty(self.general),
                self._empty(self.book),
                self._empty(self.name),
                self._empty(self.category),
                self._empty(self.range),
                self._empty(self.duration),
                self._empty(self.casting_time),
                self._empty(self.description),
                self._empty(self.level),
                self.ritual is not None,
                self.guild is not None,
                self._empty(self.school),
                self._empty(self.caster),
            ]
        )

    @staticmethod
    def _empty(value: str) -> bool:
        return not value or len(value) == 0

    @staticmethod
    def _not_empty(value: str) -> bool:
        return value and len(value) > 0
