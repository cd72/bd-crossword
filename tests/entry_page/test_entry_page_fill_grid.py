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
        "columns": {
            0: "BALD#IMPRESARIO",
            14: "CHEAPSKATE#APSE"
        },
        "partial_clues": None,
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
        "partial_clues": None,
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

        # assert result_grid.get_row_as_string(0) == "BOMBAYDUCK#MARC"
        # assert result_grid.get_col_as_string(0) == "BALD#IMPRESARIO"
  


# TODO FIX/SHORTCUT THIS ISSUE BOTH ACROSS AND DOWN
# 22:48:32.663 [  entry_page_fill_grid.py:0019] DEBUG    fill_grid                      fill_grid called clues left are 12
# 22:48:32.664 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r6c9, try is 0
# 22:48:32.665 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r6c10, try is 1
# 22:48:32.666 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r6c11, try is 2
# 22:48:32.668 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r6c12, try is 3
# 22:48:32.670 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r6c13, try is 4
# 22:48:32.671 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r6c14, try is 5
# 22:48:32.673 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r7c0, try is 6
# 22:48:32.674 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r7c1, try is 7
# 22:48:32.676 [        crossword_grid.py:0106] DEBUG    can_write_down                 left_contiguous is 3, right_contiguous is 0
# 22:48:32.676 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r7c2, try is 8
# 22:48:32.678 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r7c3, try is 9
# 22:48:32.679 [        crossword_grid.py:0106] DEBUG    can_write_down                 left_contiguous is 0, right_contiguous is 3
# 22:48:32.680 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r7c4, try is 10
# 22:48:32.681 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r7c5, try is 11
# 22:48:32.683 [        crossword_grid.py:0106] DEBUG    can_write_down                 left_contiguous is 3, right_contiguous is 0
# 22:48:32.683 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r7c6, try is 12
# 22:48:32.685 [  entry_page_fill_grid.py:0024] DEBUG    fill_grid                      16d PRISONER, r7c7, try is 13
# 22:48:32.686 [  entry_page_fill_grid.py:0028] DEBUG    fill_grid                      now grid is 
# N|I|N|C|O|M|P|O|O|P|#|S|T|U|D
# I|#|A|#|U|#|L|#|A|#|#|#|W|#|I
# B|I|R|E|T|T|A|#|S|U|B|M|I|T|S
# S|#|R|#|O|#|N|#|I|#|L|#|N|#|O
# #|#|O|F|F|O|N|E|S|R|O|C|K|E|R
# H|#|W|#|P|#|I|#|#|#|O|#|L|#|D
# A|N|S|E|R|I|N|E|#|A|D|H|E|R|E
# R|#|#|#|A|#|G|P|_|_|R|_|#|_|R
# D|_|_|_|C|_|#|R|_|_|E|_|_|_|L
# B|_|_|_|T|_|_|I|_|_|L|_|_|_|Y
# O|_|_|_|I|_|_|S|_|_|A|_|_|_|#
# I|_|_|_|C|_|_|O|_|_|T|_|_|_|_
# L|_|_|_|E|_|_|N|_|_|I|_|_|_|_
# E|_|_|_|#|_|_|E|_|_|O|_|_|_|_
# D|_|_|_|_|_|_|R|_|_|N|_|_|_|_

