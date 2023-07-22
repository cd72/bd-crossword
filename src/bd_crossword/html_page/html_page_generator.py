import logging
import click
from . import __version__
from bd_crossword.common import crossword_index
from datetime import date
from bd_crossword.entry_page import entry_page_getter
from bd_crossword.entry_page import entry_page_parser
from bd_crossword.common import crossword_clues
from bd_crossword.entry_page.entry_page_fill_grid import FillGrid


logger: logging.Logger = logging.getLogger(__name__)


def get_grid_for_date(page_date_string):
    logger.info("get_grid_for_date")
    print("get_grid_for_date starting")

    database_file = "bd_crossword.db"
    db = crossword_index.CrosswordIndex(filename=database_file)

    click.echo(f"Getting entry pages starting at {page_date_string}")
    page_date = date.fromisoformat(page_date_string)
    logger.debug("page_date : %s", str(page_date))
    parsed_clues = get_entry_page(page_date, db)
    logger.debug(type(crossword_clues).__name__)

    sorted_clue_list = (
        crossword_clues.CrosswordCluesSortedByID.new_from_crossword_clues(
            parsed_clues
        )
    )
    fill_grid = FillGrid(sorted_clue_list)
    return fill_grid.fill_grid()
    
def get_entry_page(page_date, db):
    index_entry = db.retrieve_index_entry_for_date(page_date)
    logger.debug(f"{index_entry=}")
    page_html = entry_page_getter.get_entry_page(index_entry.title, index_entry.url)
    crossword_clues = entry_page_parser.parse_entry_page(page_html)

    return crossword_clues

def get_all_entry_pages(db):
    for title, url in db.retrieve_all_urls():
        logger.debug(f"{title=}")
        logger.debug(f"{url=}")
        entry_page_getter.get_entry_page(title, url)

def main(page_date_string):
    logger.info("main")
    print("main starting")

    database_file = "bd_crossword.db"
    db = crossword_index.CrosswordIndex(filename=database_file)

    if page_date_string == "ALL":
        logger.info("No page date specified.")
        get_all_entry_pages(db)
    else:
        get_grid_for_date(page_date_string)

