import click
from datetime import date
from datetime import datetime
from . import __version__, index_page_getter
import logging
import requests

logger = logging.getLogger(__name__)

log_cli_format = (
    "%(asctime)s.%(msecs)03d [%(filename)20s:%(lineno)04d]"
    + " %(levelname)-8s %(funcName)-30s %(message)s"
)
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(
    level=logging.DEBUG, format=log_cli_format, datefmt=log_cli_date_format
)

print("====================" + __name__)


@click.command()
@click.option(
    "--start-date-string",
    "-s",
    default=datetime.now().strftime("%Y-%m-%d"),
    help="The start date of the days to get",
    metavar="YYYY-MM-DD",
    show_default=True,
)
@click.option(
    "--days",
    "-d",
    default=5,
    help="The number of days to download (counting backwards"
    + " from start-date and including the start-date)",
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
def main(start_date_string, days, dump, force_download):
    """CLI for downloading BD index pages"""
    logger.debug("Running main...")
    # print("Running main...")
    click.echo(
        f"Getting index pages starting at {start_date_string} and "
        + f"going back {days} days."
    )
    start_date = date.fromisoformat(start_date_string)
    index_getter = index_page_getter.IndexPageGetter(
        dump=dump, force_download=force_download
    )

    try:
        data = index_getter.download_date_range(
            start_date=start_date,
            days=days,
        )
    except requests.RequestException as error:
        message = str(error)
        raise click.ClickException(message) from error

    print(data)
