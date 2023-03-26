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


@pytest.fixture(scope="module")
def crossword_index_database():
    return crossword_index.CrosswordIndex("./bd_crossword.db")


class TestMetadata:
    basic_tests = [
        {"title": "DT 30231", "hints_author": "StephenL"},
        {"title": "DT 30232", "hints_author": "Mr K"}
    ]

    """Arrange"""
    @pytest.fixture(scope="class", params=basic_tests)
    def basic_test_data(self, request):
        return request.param

    @pytest.fixture(scope="class")
    def entry_author(self, basic_test_data):
        return basic_test_data["hints_author"]

    @pytest.fixture(scope="class")
    def an_index_entry(self, basic_test_data, crossword_index_database):
        title = basic_test_data["title"]
        return crossword_index_database.retrieve_index_entry_for_title(title)

    @pytest.fixture(scope="class")
    def an_entry_page_html(self, an_index_entry: index_entry.IndexEntry):
        return entry_page_getter.get_entry_page(an_index_entry.title, an_index_entry.url)

    """Act"""
    @pytest.fixture(scope="class", autouse=True)
    def parse_result(self, an_entry_page_html: str):
        return entry_page_parser.parse_html(an_entry_page_html)

    """Assert"""
    def test_parse_html_type(self, parse_result):
        assert type(parse_result) is entry_page_parser.Crossword

    def test_parse_html_title(self, parse_result, an_index_entry):
        assert parse_result.title == an_index_entry.title

    def test_parse_html_author(self, parse_result, entry_author):
        assert parse_result.hints_author == entry_author

