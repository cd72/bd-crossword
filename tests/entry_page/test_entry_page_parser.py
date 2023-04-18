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




metadata_tests = [
    {
        "title": "DT 30231",
        "comments": "a randomly chosen StephenL",
        "hints_author": "StephenL",
        "difficulty": 2,
        "enjoyment": 4.5,
    },
    {
        "title": "DT 30232",
        "comments": "a randomly chosen Mr K",
        "hints_author": "Mr K",
        "difficulty": 2,
        "enjoyment": 3,
    },
    {
        "title": "DT 29608",
        "comments": "no difficulty or enjoyment stars set",
        "hints_author": "Miffypops",
        "difficulty": 3,
        "enjoyment": 3,
    },
]


@pytest.mark.parametrize(
    "metadata_test", metadata_tests, ids=metadata_idfn, scope="class"
)
class TestMetadata:
    # Arrange
    @pytest.fixture(scope="class")
    def an_index_entry(self, metadata_test, crossword_index_database):
        title = metadata_test["title"]
        return crossword_index_database.retrieve_index_entry_for_title(title)

    @pytest.fixture(scope="class")
    def an_entry_page_html(self, an_index_entry: index_entry.IndexEntry):
        return entry_page_getter.get_entry_page(
            an_index_entry.title, an_index_entry.url
        )

    # Act
    @pytest.fixture(scope="class", autouse=True)
    def parse_result(self, an_entry_page_html: str):
        logger.debug("Act")
        logger.debug("Different one")

        return entry_page_parser.parse_html(an_entry_page_html)

    # Assert
    def test_parse_html_result_type(self, parse_result):
        assert type(parse_result) is entry_page_parser.Crossword

    def test_title(self, parse_result, an_index_entry):
        assert parse_result.title == an_index_entry.title

    def test_author(self, parse_result, metadata_test):
        assert parse_result.hints_author == metadata_test["hints_author"]

    def test_difficulty(self, parse_result, metadata_test):
        assert parse_result.difficulty == metadata_test["difficulty"]

    def test_enjoyment(self, parse_result, metadata_test):
        assert parse_result.enjoyment == metadata_test["enjoyment"]


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
]


@pytest.mark.parametrize("clues_test", clues_tests, ids=metadata_idfn, scope="class")
class TestParsing:
    # Arrange
    @pytest.fixture(scope="class")
    def an_index_entry(self, clues_test, crossword_index_database):
        title = clues_test["title"]
        return crossword_index_database.retrieve_index_entry_for_title(title)

    @pytest.fixture(scope="class")
    def an_entry_page_html(self, an_index_entry: index_entry.IndexEntry):
        return entry_page_getter.get_entry_page(
            an_index_entry.title, an_index_entry.url
        )

    @pytest.fixture(scope="class", autouse=True)
    def act(self, an_entry_page_html: str):
        logger.debug("Act")
        logger.debug("id is %s", id(self))

        return entry_page_parser.parse_for_clues(an_entry_page_html)

    
    # @pytest.fixture(scope="function", autouse=True)
    # def function_act_caplog_records(self, caplog, act):
    #     logger.debug("Checking caplog records")

    #     logger.debug(self.__dict__)

    #     if "act_caplog_records" not in self.__dict__.keys():
    #         logger.debug("key act_caplog_records was NOT found")
    #         caplog_records = caplog.get_records(when="setup")
    #         act_index = [x.msg for x in caplog_records].index("Act")
    #         # act_index = -1
    #         self.act_caplog_records = caplog_records[act_index + 1 :]
    #     else:
    #         logger.debug("key act_caplog_records was found")
    #     logger.debug(self.__dict__)

    #     return self.act_caplog_records


    # @pytest.fixture(scope="function")
    # def function_act_caplog_messages(self, function_act_caplog_records):
    #     return [log_record.msg for log_record in function_act_caplog_records]

    def test_across_clues_header_found(self, act, clues_test):
        logger.debug("Testing across clues")
        logger.debug("id is %s", id(self))

        # across_clues = entry_page_parser.get_across_clues(an_entry_page_html)
        # for log_message in function_act_caplog_messages:
        #     logger.debug(log_message)
# 
        assert clues_test["across_clues"] == act["Across"]

    def test_down_clues_header_found(self, act, clues_test):
        logger.debug("Testing down clues")
        logger.debug("id is %s", id(self))

        # across_clues = entry_page_parser.get_across_clues(an_entry_page_html)
        # for log_message in function_act_caplog_messages:
        #     logger.debug(log_message)

        assert clues_test["down_clues"] == act["Down"]

        # assert len(across_clues) == clues_test["across_clues"]
        # assert clues_test["across_clues"] == len(across_clues)
