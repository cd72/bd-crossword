import logging
import pytest
from datetime import date
import pathlib
import dataclasses
import json
from bd_crossword.common import index_entry
from bd_crossword.entry_page import entry_page_parser
from bd_crossword.entry_page import entry_page_getter

import datetime
from bd_crossword.common import crossword_index


logger = logging.getLogger(__name__)
logger.info(__name__)


def metadata_idfn(a_test):
    return (
        a_test["title"].replace(" ", "-") + "_" + a_test["comments"].replace(" ", "-")
    )


@pytest.fixture(scope="module")
def crossword_index_database():
    return crossword_index.CrosswordIndex("./bd_crossword.db")

clue_count_tests = [
    {
        "title": "DT 30151",
        "comments": "Direction headers not in their own paragraph",
        "across_clues": 14,
        "down_clues": 16,
    },
    {
        "title": "DT 30232",
        "comments": "a randomly chosen Mr K",
        "across_clues": 14,
        "down_clues": 14,
    },
    {
        "title": "DT 30276",
        "comments": "random pommers",
        "across_clues": 16,
        "down_clues": 14,
    },
    {
        "title": "DT 30270",
        "comments": "random falcon",
        "across_clues": 14,
        "down_clues": 14,
    },
    {
        "title": "DT 30253",
        "comments": "random Twmbarlwm",
        "across_clues": 14,
        "down_clues": 16,
    },
    {
        "title": "DT 30247",
        "comments": "text decoration styles",
        "across_clues": 16,
        "down_clues": 16,
    },
    {
        "title": "DT 30258",
        "comments": "Across Clues not Across",
        "across_clues": 14,
        "down_clues": 14,
    },
    {
        "title": "DT 30063",
        "comments": "daft clues like 23ac. And 8d.",
        "across_clues": 14,
        "down_clues": 14,
    },
    {
        "title": "DT 30016",
        "comments": "26Ac. 15ac missing close bracket, clue length on next line . in clue length, missing clue length absolute shambles",
        "across_clues": 14,
        "down_clues": 14,
    },
    {
        "title": "DT 30075",
        "comments": "spaces before clue ids, 15a spoiler contains hint",
        "across_clues": 14,
        "down_clues": 14,
    },
    {
        "title": "DT 30100",
        "comments": "no across heading",
        "across_clues": 14,
        "down_clues": 14,
    },
    {
        "title": "DT 30180",
        "comments": "space in clue id 9 a",
        "across_clues": 12,
        "down_clues": 15,
    },
    {
        "title": "DT 28218",
        "comments": "disappearing spoiler <br> not <br/>",
        "across_clues": 12,
        "down_clues": 16,
    },
    {
        "title": "DT 28350",
        "comments": "Across hints by Mr Kitty, Down hints by Kitty",
        "across_clues": 16,
        "down_clues": 16,
    },
    {
        "title": "DT 30078",
        "comments": "Composite Down Clue",
        "across_clues": 16,
        "down_clues": 14,
    },
    {
        "title": "DT 30295",
        "comments": "just numbers, no a or d in the clue ids",
        "across_clues": 16,
        "down_clues": 16,
    },
    {
        "title": "DT 29992",
        "comments": "hints before spoilers",
        "across_clues": 14,
        "down_clues": 14,
    },
    {
        "title": "DT 29931",
        "comments": "Direction Drown",
        "across_clues": 14,
        "down_clues": 14,
    },
    {
        "title": "DT 28903",
        "comments": "Leading spaces on spoiler lines",
        "across_clues": 14,
        "down_clues": 16,
    },
    {
        "title": "DT 28742",
        "comments": "no clues from entry page getter",
        "across_clues": 14,
        "down_clues": 14,
    },

]


@pytest.mark.parametrize("clues_test", clue_count_tests, ids=metadata_idfn, scope="class")
class TestClueCount:
    # Arrange
    @pytest.fixture(scope="class")
    def an_index_entry(self, clues_test, crossword_index_database):
        title = clues_test["title"]
        return crossword_index_database.retrieve_index_entry_for_title(title)

    @pytest.fixture(scope="class")
    def entry_page_html(self, an_index_entry: index_entry.IndexEntry):
        return entry_page_getter.get_entry_page(
            an_index_entry.title, an_index_entry.url
        )

    def test_clue_count(self, entry_page_html, clues_test):
        logger.debug("id is %s", id(self))
        logger.debug("clues_test is %s", clues_test)
        with open("page_content.txt", "w") as file:
            file.write(entry_page_html)

        test_result = entry_page_parser.parse_entry_page(entry_page_html)
        logger.debug("test_result is %s", test_result)
        assert (clues_test["across_clues"], clues_test["down_clues"]) == (
            len(test_result.across),
            len(test_result.down),
        )


clue_content_tests = [
    {
        "title": "DT 30151",
        "comments": "a randomly chosen 1 across",
        "direction": "across",
        "clue_id": 1,
        "content": {
            "clue_id": 1,
            "direction": "a",
            "clue_text": "<u>Food</u> from disco somewhere in Kent",
            "listed_solution": "CLUB SANDWICH",
            "listed_solution_length": "(4,8)",
            "hint": "Another word for a disco is followed by a town in Kent that's 2 miles from the village of Ham, to many tourists' amusement",
            }
    },
    {
        "title": "DT 30296",
        "comments": "two word solution",
        "direction": "down",
        "clue_id": 2,
        "content": {
            "listed_solution": "SMALL TALK",
            "actual_solution": "SMALLTALK",
            "actual_solution_length": 9,
            "solution_start_letters": "S,T",
        }
    }
]

@pytest.mark.parametrize("clues_test", clue_content_tests, ids=metadata_idfn, scope="class")
class TestClueContent:
    # Arrange
    @pytest.fixture(scope="class")
    def an_index_entry(self, clues_test, crossword_index_database):
        title = clues_test["title"]
        return crossword_index_database.retrieve_index_entry_for_title(title)

    @pytest.fixture(scope="class")
    def entry_page_html(self, an_index_entry: index_entry.IndexEntry):
        return entry_page_getter.get_entry_page(
            an_index_entry.title, an_index_entry.url
        )

    def test_clue_content(self, entry_page_html, clues_test):
        logger.debug("id is %s", id(self))
        logger.debug("clues_test is %s", clues_test)
        with open("page_content.txt", "w") as file:
            file.write(entry_page_html)

        test_result = entry_page_parser.parse_entry_page(entry_page_html)
        # logger.debug("test_result is %s", test_result)
        expected_result = clues_test["content"]
        actual_result = getattr(test_result, clues_test["direction"])[clues_test["clue_id"]]

        for attribute in expected_result.keys():
            assert expected_result[attribute] == getattr(actual_result, attribute)




