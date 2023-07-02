import logging
import pytest
from datetime import date
from bd_crossword.common import index_entry
from bd_crossword.entry_page import entry_page_parser
from bd_crossword.entry_page.entry_page_fill_grid import FillGrid
from bd_crossword.entry_page import entry_page_getter
from bd_crossword.common.crossword_grid import CrosswordGrid
from bd_crossword.common import crossword_clues

import datetime
from bd_crossword.common import crossword_index


logger = logging.getLogger(__name__)
logger.info(__name__)
logging.getLogger('entry_page_parser').setLevel(logging.INFO)

def metadata_idfn(a_test):
    return (
        a_test["title"].replace(" ", "-") + "_" + a_test["comments"].replace(" ", "-")
    )

@pytest.fixture(scope="module")
def crossword_index_database():
    return crossword_index.CrosswordIndex("./bd_crossword.db")


fill_grid_tests = [
    # {
    #     "title": "DT 30151",
    #     "comments": "A simple example",

    # },
    {
        "title": "DT 30056",
        "comments": "A simple example",
        "rows": {
            0: "BOMBAYDUCK#MARC",
           14: "OWNS#BROWNSAUCE"
        },
        "columns": {
            0: "BALD#IMPRESARIO",
            14: "CHEAPSKATE#APSE"
        },
        "max_tries": 247,
        "max_recurse": 100,
    },
    {
        "title": "DT 30062",
        "comments": "A simple example",
        "rows": {
            0: "NINCOMPOOP#STUD",
           14: "DATA#HYDRANGEAS"
        },
        "columns": {
            0: "NIBS#HARDBOILED",
            14: "DISORDERLY#KRIS"
        },
        "max_tries": 418,
        "max_recurse": 100,
    },
    {
        "title": "DT 30292",
        "comments": "A simple example",
        "rows": {
            0: "UNEXCITED#TOPIC",
           14: "ENEMY#STEAMSHIP"
        },
        "columns": {
            0: "UNDO#FOREXAMPLE",
            14: "CATEGORISE#STEP"
        },
        "max_tries": 418,
        "max_recurse": 100,
    },
]

@pytest.mark.parametrize("grid_test", fill_grid_tests, ids=metadata_idfn, scope="class")
class TestFillGrid:
    # Arrange
    @pytest.fixture(scope="class")
    def an_index_entry(self, grid_test, crossword_index_database):
        title = grid_test["title"]
        return crossword_index_database.retrieve_index_entry_for_title(title)

    @pytest.fixture(scope="class")
    def entry_page_html(self, an_index_entry: index_entry.IndexEntry):
        return entry_page_getter.get_entry_page(
            an_index_entry.title, an_index_entry.url
        )
    
    @pytest.fixture(scope="class")
    def sorted_clues(self, entry_page_html):
        parsed_clues = entry_page_parser.parse_entry_page(entry_page_html)
        sorted_clue_list = crossword_clues.CrosswordCluesSortedByID.new_from_crossword_clues(parsed_clues)
        logger.debug("The type of sorted_clue_list is %s",type(sorted_clue_list).__name__)

        return sorted_clue_list
    
    def test_fill_grid_constructor(self, sorted_clues, grid_test):
        test_result = FillGrid(sorted_clues)
        logger.debug("test_result is %s", test_result)
        assert test_result is not None
        assert isinstance(test_result, FillGrid)
        assert hasattr(test_result, "grid")
        assert isinstance(test_result.grid, CrosswordGrid)
        assert hasattr(test_result, "clues")
        assert isinstance(test_result.clues, crossword_clues.CrosswordCluesSortedByID)


    def test_fill_grid(self, sorted_clues, grid_test):
        logger.debug("The type of sorted_clues is %s",type(sorted_clues).__name__)
        fill_grid = FillGrid(sorted_clues)
        fill_grid.list_clues()

        fill_grid.fill_grid()

        result_grid = fill_grid.grid
        assert isinstance(result_grid, CrosswordGrid)

        logger.debug("result_grid is: \n%s", result_grid.text_grid())
        logger.debug("Ran with recurse_count %s and try_count %s", fill_grid.recurse_count, fill_grid.try_count)

        for row, row_text in grid_test["rows"].items():
            assert result_grid.get_row_as_string(row) == row_text

        for col, col_text in grid_test["columns"].items():
            assert result_grid.get_col_as_string(col) == col_text

        assert fill_grid.recurse_count <= grid_test["max_recurse"]
        assert fill_grid.try_count <= grid_test["max_tries"]

  
partial_grid_tests = [
    {
        "title": "DT 30062",
        "comments": "not starting next to existing word",
        "rows": {},
        "columns": {
            8: "OASIS##PRISONER",
        },
        "stop_after": "PRISONER",
        "max_tries": 418,
        "max_recurse": 100,
    },
    # {
    #     "title": "DT 30308",
    #     "comments": "unit test for fills from both ends",
    #     "rows": {},
    #     "columns": {
    #        0:  "PUBCRAWL#______",
    #        14: "______#CENSORED",
    #     },
    #     "stop_after": "ILLEGAL",
    #     "max_tries": 418,
    #     "max_recurse": 100,
    # },
]

@pytest.mark.parametrize("grid_test", partial_grid_tests, ids=metadata_idfn, scope="class")
class TestPartialFillGrid:
    # Arrange
    @pytest.fixture(scope="class")
    def an_index_entry(self, grid_test, crossword_index_database):
        title = grid_test["title"]
        return crossword_index_database.retrieve_index_entry_for_title(title)

    @pytest.fixture(scope="class")
    def entry_page_html(self, an_index_entry: index_entry.IndexEntry):
        return entry_page_getter.get_entry_page(
            an_index_entry.title, an_index_entry.url
        )
    
    @pytest.fixture(scope="class")
    def sorted_clues(self, entry_page_html):
        parsed_clues = entry_page_parser.parse_entry_page(entry_page_html)
        sorted_clue_list = crossword_clues.CrosswordCluesSortedByID.new_from_crossword_clues(parsed_clues)
        logger.debug("The type of sorted_clue_list is %s",type(sorted_clue_list).__name__)

        return sorted_clue_list
    
    def test_fill_grid_partial(self, sorted_clues, grid_test):
        fill_grid = FillGrid(sorted_clues, stop_after=grid_test["stop_after"])
        fill_grid.list_clues()

        fill_grid.fill_grid()

        result_grid = fill_grid.grid
        assert isinstance(result_grid, CrosswordGrid)

        logger.debug("result_grid is: \n%s", result_grid.text_grid())
        logger.debug("Ran with recurse_count %s and try_count %s", fill_grid.recurse_count, fill_grid.try_count)

        for row, row_text in grid_test["rows"].items():
            assert result_grid.get_row_as_string(row) == row_text

        for col, col_text in grid_test["columns"].items():
            assert result_grid.get_col_as_string(col) == col_text

        assert fill_grid.recurse_count <= grid_test["max_recurse"]
        assert fill_grid.try_count <= grid_test["max_tries"]

