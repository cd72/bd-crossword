from . import index_page_parser
from bd_crossword.common import bd_request
from datetime import timedelta
import itertools
from bd_crossword.common import crossword_index
import logging

logger = logging.getLogger(__name__)
DEFAULT_SLEEP_INTERVAL = 8

class IndexPageGetter:
    @classmethod
    def dates_in_range(cls, start_date, days):
        one_day = timedelta(days=1)
        days_generator = (
            start_date - (day_count * one_day) for day_count in range(days * 3)
        )
        weekdays_generator = (day for day in days_generator if day.isoweekday() <= 5)
        return itertools.islice(weekdays_generator, days)

    def __init__(
        self, database_file="bd_crossword.db", dump=False, force_download=False
    ):
        self.database_file = database_file
        self.dump = dump
        self.force_download = force_download
        self.db = crossword_index.CrosswordIndex(filename=database_file)

    def dump_out(self, file_type, content, index_date):
        if self.dump:
            dump_file = f"dump_{str(index_date.isoformat())}.{file_type}"
            with open(dump_file, "w", encoding="utf-8") as f:
                f.write(content)

    def get_index_entry_for_date(self, index_date):
        if not self.force_download:
            if entry_for_date := self.db.retrieve_index_entry_for_date(index_date):
                logger.debug(f"Found entry for date {index_date} in db")
                return entry_for_date

        logger.debug(f"Downloading entry for date {index_date=}")
        bd = bd_request.BDRequest(mean_interval=DEFAULT_SLEEP_INTERVAL)
        html_text = bd.download_index_for_date(index_date)
        logger.debug("html length : %d", len(html_text))
        logger.debug("html : %s", html_text[:100])
        self.dump_out("html", html_text, index_date)

        entries_for_date = index_page_parser.parse_index_page(html_text, index_date)

        if len(entries_for_date) == 0:
            logger.warning(f"Did not find any entries for {index_date}")
        else:
            logger.debug(
                f"The number of index entries found was {len(entries_for_date)}"
            )

        [entry_for_date] = entries_for_date

        self.db.new_index_entry(entry_for_date)
        logger.info(entry_for_date)
        self.dump_out("index", repr(entry_for_date), index_date)

        return entry_for_date

    def download_date_range(self, start_date, days):
        logger.debug(f"{start_date=}")
        logger.debug(f"{days=}")
        return [
            self.get_index_entry_for_date(index_date)
            for index_date in self.dates_in_range(start_date, days)
        ]
