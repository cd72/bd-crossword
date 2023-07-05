import click
from datetime import date
from datetime import datetime
from . import __version__
from bd_crossword.common import crossword_index

from . import entry_page_getter
from . import entry_page_parser
import logging

logger: logging.Logger = logging.getLogger(__name__)

log_cli_format = (
    "%(asctime)s.%(msecs)03d [%(filename)20s:%(lineno)04d]"
    + " %(levelname)-8s %(funcName)-30s %(message)s"
)
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(
    level=logging.DEBUG, format=log_cli_format, datefmt=log_cli_date_format
)


# default=datetime.now().strftime("%Y-%m-%d"),
@click.command()
@click.option(
    "--page-date-string",
    "-p",
    default="ALL",
    help="The page date of the day to get",
    metavar="YYYY-MM-DD or ALL",
    show_default=True,
)
@click.option(
    "--dump",
    is_flag=True,
    show_default=True,
    default=False,
    help="Dump the html and index entries to the filesystem.",
)
@click.option(
    "--force-download",
    "-f",
    is_flag=True,
    show_default=True,
    default=False,
    help="Always download rather than using the cached entry in the database.",
)
@click.version_option(version=__version__)
def main(page_date_string, dump, force_download):
    """CLI for downloading BD entry pages"""

    database_file = "bd_crossword.db"
    db = crossword_index.CrosswordIndex(filename=database_file)

    if page_date_string == "ALL":
        logger.info("No page date specified.")
        get_all_entry_pages(db)
    else:
        click.echo(f"Getting entry pages starting at {page_date_string}")
        page_date = date.fromisoformat(page_date_string)
        logger.debug("page_date : %s", str(page_date))
        get_entry_page(page_date, db)

def get_entry_page(page_date, db):
    index_entry = db.retrieve_index_entry_for_date(page_date)
    logger.debug(f"{index_entry=}")
    page_html = entry_page_getter.get_entry_page(index_entry.title, index_entry.url)
    crossword_clues = entry_page_parser.parse_entry_page(page_html)
    
    across_clues = crossword_clues["across"]
    down_clues = crossword_clues["down"]

    for clue_id, clue in across_clues.items():
        logger.debug(f"{clue_id=}, {clue=}")


def get_all_entry_pages(db):
    for title, url in db.retrieve_all_urls():
        print(f"{url=}")
        entry_page_getter.get_entry_page(title, url)
