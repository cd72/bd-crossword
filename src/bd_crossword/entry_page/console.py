import click
from datetime import date
from datetime import datetime
from . import __version__

from . import entry_page_getter
import logging
import requests

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

    entry_page = entry_page_getter.EntryPageGetter(
        dump=dump, force_download=force_download
    )

    try:
        page_data = entry_page.get_entry_page_for_date(page_date)
    except requests.RequestException as error:
        message = str(error)
        raise click.ClickException(message) from error

    print(page_data)
