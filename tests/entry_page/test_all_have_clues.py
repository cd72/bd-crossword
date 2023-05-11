import pathlib
import pytest
import logging
from bd_crossword.entry_page import entry_page_parser

logger = logging.getLogger(__name__)


def html_files():
    test_file_location = pathlib.Path(__file__).parent.parent.parent / "bd_entry_page_cache"
    return sorted(list(test_file_location.rglob("DT*.html")))

def html_file_content():
    return [html_file.read_text() for html_file in html_files()]

def title_name():
    return [f.name for f in html_files()]

@pytest.mark.parametrize("html", html_file_content(), ids=title_name(), scope="class")
class TestClues03:
    @pytest.fixture(scope="class", autouse=True)
    def act(self, html: str):
        logger.debug("Act")
        logger.debug("id is %s", id(self))

        return entry_page_parser.count_clues_03(html)

    def test_across_clues_header_found(self, act):
        logger.debug("Testing across clues")
        logger.debug("id is %s", id(self))

        assert act["across"] >= 11
        assert act["down"] >= 12