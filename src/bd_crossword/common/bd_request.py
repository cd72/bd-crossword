import requests
from datetime import datetime
from datetime import timedelta
from random import gauss
import logging
import time

logger = logging.getLogger(__name__)

headers = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
    + "KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,i"
    + "mage/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

start_referer = "https://www.google.com/"
url_template = "http://bigdave44.com/{year}/{month}/{day}"
DEFAULT_SLEEP_INTERVAL = 8


class BDRequest:
    last_request_time = datetime.now() - timedelta(days=7)

    @classmethod
    def update_last_request_time(cls, the_time=datetime.now()):
        cls.last_request_time = the_time

    @classmethod
    def whats_the_time(cls):
        logger.debug(cls)
        return datetime.today()

    def __init__(self, mean_interval=DEFAULT_SLEEP_INTERVAL):
        self.last_url = start_referer
        self.mean_interval = mean_interval

    def get_random_sleep_interval(self):
        return gauss(self.mean_interval, 1)

    def calculate_sleep_period(self, interval_s):
        logger.debug("sleep interval is %s", str(interval_s))
        logger.debug("Current time %s", datetime.now())
        wait_until_time = self.last_request_time + timedelta(seconds=interval_s)

        logger.debug("Waiting until time %s", wait_until_time)
        time_now = datetime.now()
        if time_now < wait_until_time:
            logger.debug("Waiting until %s", wait_until_time.isoformat())
            return (wait_until_time - time_now).total_seconds()
        else:
            return 0

    def pause_for_sleep(self, random_interval=None):
        if random_interval is None:
            random_interval = self.get_random_sleep_interval()
        sleep_time = self.calculate_sleep_period(random_interval)
        logger.info("Sleeping for %s seconds", sleep_time)
        time.sleep(sleep_time)

    def download_url(self, url):
        headers["Referer"] = self.last_url

        self.pause_for_sleep()

        logger.info(f"..fetching page {url}")
        response = requests.get(url, headers=headers)

        response.raise_for_status()
        self.last_url = url
        self.update_last_request_time(datetime.now())
        return response.text

    def download_index_for_date(self, index_date):
        url = url_template.format(
            year=index_date.year, month=index_date.month, day=index_date.day
        )

        return self.download_url(url)
