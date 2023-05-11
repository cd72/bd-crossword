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


# metadata_tests = [
#     {
#         "title": "DT 30231",
#         "comments": "a randomly chosen StephenL",
#         "hints_author": "StephenL",
#         "difficulty": 2,
#         "enjoyment": 4.5,
#     },
#     {
#         "title": "DT 30232",
#         "comments": "a randomly chosen Mr K",
#         "hints_author": "Mr K",
#         "difficulty": 2,
#         "enjoyment": 3,
#     },
#     {
#         "title": "DT 29608",
#         "comments": "no difficulty or enjoyment stars set",
#         "hints_author": "Miffypops",
#         "difficulty": 3,
#         "enjoyment": 3,
#     },
# ]


# @pytest.mark.parametrize(
#     "metadata_test", metadata_tests, ids=metadata_idfn, scope="class"
# )
# class TestMetadata:
#     # Arrange
#     @pytest.fixture(scope="class")
#     def an_index_entry(self, metadata_test, crossword_index_database):
#         title = metadata_test["title"]
#         return crossword_index_database.retrieve_index_entry_for_title(title)

#     @pytest.fixture(scope="class")
#     def an_entry_page_html(self, an_index_entry: index_entry.IndexEntry):
#         return entry_page_getter.get_entry_page(
#             an_index_entry.title, an_index_entry.url
#         )

#     # Act
#     @pytest.fixture(scope="class", autouse=True)
#     def parse_result(self, an_entry_page_html: str):
#         logger.debug("Act")
#         logger.debug("Different one")

#         return entry_page_parser.parse_html(an_entry_page_html)

#     # Assert
#     def test_parse_html_result_type(self, parse_result):
#         assert type(parse_result) is entry_page_parser.Crossword

#     def test_title(self, parse_result, an_index_entry):
#         assert parse_result.title == an_index_entry.title

#     def test_author(self, parse_result, metadata_test):
#         assert parse_result.hints_author == metadata_test["hints_author"]

#     def test_difficulty(self, parse_result, metadata_test):
#         assert parse_result.difficulty == metadata_test["difficulty"]

#     def test_enjoyment(self, parse_result, metadata_test):
#         assert parse_result.enjoyment == metadata_test["enjoyment"]


clues_tests = [
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


]


@pytest.mark.parametrize("clues_test", clues_tests, ids=metadata_idfn, scope="class")
class TestClues03:
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
        assert (clues_test["across_clues"], clues_test["down_clues"]) == (
            entry_page_parser.count_clues_03(entry_page_html)["across"],
            entry_page_parser.count_clues_03(entry_page_html)["down"],
        )
