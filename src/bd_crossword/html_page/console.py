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

# log_cli_format = (
#     "%(asctime)s.%(msecs)03d [%(filename)20s:%(lineno)04d]"
#     + " %(levelname)-8s %(funcName)-30s %(message)s"
# )
# log_cli_date_format = "%Y-%m-%d %H:%M:%S"
# logging.basicConfig(
#     level=logging.DEBUG, format=log_cli_format, datefmt=log_cli_date_format
# )

# @click.command()
# @click.option(
#     "--page-date-string",
#     "-p",
#     default="ALL",
#     help="The page date of the day to get",
#     metavar="YYYY-MM-DD or ALL",
#     show_default=True,
# )

# @click.version_option(version=__version__)

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

