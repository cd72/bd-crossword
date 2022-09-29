import click
from datetime import date
from datetime import datetime
from . import __version__, index_downloader
import logging
import requests

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--start-date-string",
    "-s",
    default=datetime.today().strftime("%Y-%m-%d"),
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
@click.version_option(version=__version__)
def main(start_date_string, days, dump):
    """CLI for downloading BD index pages"""
    logger.debug("Running main...")
    # print("Running main...")
    click.echo(
        f"Getting index pages starting at {start_date_string} and "
        + f"going back {days} days."
    )
    start_date = date.fromisoformat(start_date_string)

    try:
        data = index_downloader.download_date_range(
            start_date=start_date, days=days, dump=dump
        )
    except requests.RequestException as error:
        message = str(error)
        raise click.ClickException(message)

    print(data)
