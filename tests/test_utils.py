import pytest

from releasify.utils import boolify


@pytest.mark.parametrize("input,expected", [
    ('y', True),
    ('Y', True),
    ('yes', True),
    ('YES', True),
    ('Yes', True),
    ('true', True),
    ('True', True),
    (1, True),
    ('1', True),
    ('no', False),
    ('N', False),
    ('false', False),
])
def test_boolify(input, expected):
    assert boolify(input) == expected
