import pytest

from pycana.models import School


@pytest.mark.parametrize(
    'label, expected',
    [
        ('ABJURATION', School.ABJURATION),
        ('abjuration', School.ABJURATION),
        ('CONJURATION', School.CONJURATION),
        ('conjuration', School.CONJURATION),
        ('DIVINATION', School.DIVINATION),
        ('divination', School.DIVINATION),
        ('ENCHANTMENT', School.ENCHANTMENT),
        ('enchantment', School.ENCHANTMENT),
        ('EVOCATION', School.EVOCATION),
        ('evocation', School.EVOCATION),
        ('ILLUSION', School.ILLUSION),
        ('illusion', School.ILLUSION),
        ('NECROMANCY', School.NECROMANCY),
        ('necromancy', School.NECROMANCY),
        ('TRANSMUTATION', School.TRANSMUTATION),
        ('transmutation', School.TRANSMUTATION),
    ]
)
def test_school_from_str(label: str, expected: School) -> None:
    assert School.from_str(label) == expected