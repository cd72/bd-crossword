import logging
import pytest

from bd_crossword.index_page import index_page_parser

logger = logging.getLogger(__name__)


########################################################
# Parsing only
########################################################
@pytest.mark.parametrize(
    "stars_input,expected_value",
    [
        ("*", 1),
        ("**", 2),
        ("***", 3),
        (" ***", 3),
        ("*** ", 3),
        ("****", 4),
        ("*****", 5),
        ("******", 6),
        ("*/**", 1.5),
        ("**/***", 2.5),
        ("***/****", 3.5),
        ("****/*****", 4.5),
    ],
)
def test_stars_to_numbers(stars_input, expected_value):
    assert index_page_parser.convert_stars_to_number(stars_input) == expected_value


def test_stars_to_numbers_exception():
    stars_input = "**********"
    with pytest.raises(ValueError) as excinfo:
        index_page_parser.convert_stars_to_number(stars_input)
    assert "Invalid stars rating pattern found" in str(excinfo.value)
    assert stars_input in str(excinfo.value)
