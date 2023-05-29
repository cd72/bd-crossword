import logging
import pytest
from datetime import date
from bd_crossword.common import index_entry
from bd_crossword.entry_page import entry_page_parser
from bd_crossword.entry_page.entry_page_fill_grid import FillGrid
from bd_crossword.entry_page import entry_page_getter
from bd_crossword.common.crossword_grid import CrosswordGrid

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
        columns = {
            0: "BALD#IMPRESARIO",
            14: "CHEAPSKATE#APSE"
        }

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
    def crossword_clues(self, entry_page_html):
        return entry_page_parser.parse_entry_page(entry_page_html)
    
    def test_fill_grid_constructor(self, crossword_clues, grid_test):
        test_result = FillGrid(crossword_clues.by_number_sorted_clues())
        logger.debug("test_result is %s", test_result)
        assert test_result is not None
        assert isinstance(test_result, FillGrid)
        assert hasattr(test_result, "grid")
        assert isinstance(test_result.grid, CrosswordGrid)
        assert hasattr(test_result, "clues")
        assert isinstance(test_result.clues, list)


    def test_fill_grid(self, crossword_clues, grid_test):
        fill_grid = FillGrid(crossword_clues.by_number_sorted_clues()[:])
        fill_grid.list_clues()

        result_grid = fill_grid.fill_grid().grid
        assert isinstance(result_grid, CrosswordGrid)

        print("result_grid is:")
        result_grid.display()

        assert result_grid.get_row_as_string(0) == "BOMBAYDUCK#MARC"
        assert result_grid.get_col_as_string(0) == "BALD#IMPRESARIO"
  




