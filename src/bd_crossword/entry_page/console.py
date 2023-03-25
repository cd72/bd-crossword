import click
from datetime import date
from datetime import datetime
from . import __version__
from bd_crossword.common import crossword_index

from . import entry_page_getter
import logging

# import requests

logger = logging.getLogger(__name__)

log_cli_format = (
    "%(asctime)s.%(msecs)03d [%(filename)20s:%(lineno)04d]"
    + " %(levelname)-8s %(funcName)-30s %(message)s"
)
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(
    level=logging.DEBUG, format=log_cli_format, datefmt=log_cli_date_format
)


@click.command()
@click.option(
    "--page-date-string",
    "-p",
    default=datetime.now().strftime("%Y-%m-%d"),
    help="The page date of the days to get",
    metavar="YYYY-MM-DD",
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

    click.echo(f"Getting entry pages starting at {page_date_string}")
    page_date = date.fromisoformat(page_date_string)
    logger.debug("page_date : %s", str(page_date))

    database_file = "bd_crossword.db"
    db = crossword_index.CrosswordIndex(filename=database_file)

    for title, url in db.retrieve_all_urls():
        print(f"{url=}")
        entry_page_getter.get_entry_page(title, url)
