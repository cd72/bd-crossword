import logging
import pytest
from bd_crossword.common import crossword_index
from bd_crossword.common import index_entry
import datetime

logger = logging.getLogger(__name__)


@pytest.fixture
def index_entry_01():
    return index_entry.IndexEntry(
        page_date=datetime.date(2019, 10, 11),
        title="Title for test case 01",
        url="https://testcase01",
        hints_author="Author01",
        difficulty=5,
        enjoyment=3,
        last_updated=datetime.datetime(2019, 10, 11, 23, 59, 00),
    )


@pytest.fixture
def in_memory_db():
    return crossword_index.CrosswordIndex(filename=":memory:")


def test_contructor(in_memory_db):
    logger.debug(type(in_memory_db))
    assert isinstance(in_memory_db, crossword_index.CrosswordIndex)


def test_insert(in_memory_db, index_entry_01):
    in_memory_db.new_index_entry(index_entry_01)
    returned_index_entry = in_memory_db.retrieve_index_entry_for_date(
        index_entry_01.page_date
    )

    assert returned_index_entry.hints_author == "Author01"


def test_row_not_found(in_memory_db, index_entry_01):
    in_memory_db.new_index_entry(index_entry_01)
    returned_index_entry = in_memory_db.retrieve_index_entry_for_date(
        datetime.datetime(2011, 10, 11, 23, 59, 00),
    )
    assert returned_index_entry is None
