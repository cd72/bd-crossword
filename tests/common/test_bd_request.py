import logging
from datetime import datetime
from datetime import date
import pytest
from statistics import mean
import time

# import unittest.mock
# from unittest.mock import patch

from bd_crossword.common import bd_request

logger = logging.getLogger(__name__)


def test_update_last_request_time():
    obj1 = bd_request.BDRequest()
    obj2 = bd_request.BDRequest()
    logger.debug(datetime.now())

    obj1.update_last_request_time(datetime.now())
    assert obj2.last_request_time == obj1.last_request_time


def test_get_random_sleep_interval():
    obj1 = bd_request.BDRequest(mean_interval=10)
    intervals = [obj1.get_random_sleep_interval() for _ in range(1000)]
    assert len(intervals) == 1000
    logger.debug("Max : %s", max(intervals))
    logger.debug("Min : %s", min(intervals))

    assert max(intervals) < 20
    assert min(intervals) > 1
    assert pytest.approx(mean(intervals), 0.1) == 10


def test_whats_the_time_01(mocker):
    mock_datetime = mocker.patch(f"{bd_request.__name__}.datetime", wraps=datetime)
    mock_datetime.today.return_value = datetime(2019, 3, 15, 23, 0, 1)

    obj1 = bd_request.BDRequest(mean_interval=10)
    time_now = obj1.whats_the_time()
    logger.debug(time_now)
    assert time_now == datetime(2019, 3, 15, 23, 0, 1)


def test_calculate_sleep_period_01(mocker):
    interval = 5
    obj1 = bd_request.BDRequest()
    obj1.update_last_request_time(datetime(2014, 6, 2, 23, 0, 19))

    mock_datetime = mocker.patch(f"{bd_request.__name__}.datetime", wraps=datetime)
    mock_datetime.now.return_value = datetime(2014, 6, 2, 23, 0, 20)

    sleep_time = obj1.calculate_sleep_period(interval)

    assert sleep_time == 4


def test_calculate_sleep_period_02(mocker):
    interval = 5
    obj1 = bd_request.BDRequest()
    obj1.update_last_request_time(datetime(2014, 6, 2, 23, 0, 19))

    mock_datetime = mocker.patch(f"{bd_request.__name__}.datetime", wraps=datetime)
    mock_datetime.now.return_value = datetime(2014, 6, 2, 23, 0, 30)

    sleep_time = obj1.calculate_sleep_period(interval)

    assert sleep_time == 0


def test_pause_for_sleep_01(mocker):
    obj1 = bd_request.BDRequest()
    obj1.update_last_request_time(datetime(2014, 6, 2, 23, 0, 19))

    mock_time = mocker.patch(f"{bd_request.__name__}.time", wraps=time)
    obj1.pause_for_sleep()

    assert mock_time.sleep.called
    args, kwargs = mock_time.sleep.call_args
    logger.debug("args: %s", args)

    assert args[0] == 0.0


def test_pause_for_sleep_02(mocker):
    obj1 = bd_request.BDRequest()
    obj1.update_last_request_time(datetime(2014, 6, 2, 23, 0, 19))

    mock_datetime = mocker.patch(f"{bd_request.__name__}.datetime", wraps=datetime)
    mock_datetime.now.return_value = datetime(2014, 6, 2, 23, 0, 20)

    mock_time = mocker.patch(f"{bd_request.__name__}.time", wraps=time)
    mock_time.sleep.return_value = None
    # mock_datetime.now.return_value = datetime(2014, 6, 2, 23, 0, 20)

    obj1.pause_for_sleep(15)

    assert mock_time.sleep.called
    args, kwargs = mock_time.sleep.call_args
    logger.debug("args: %s", args)

    assert args[0] == 14.0


@pytest.fixture
def mock_requests(mocker):
    mock_requests = mocker.patch(f"{bd_request.__name__}.requests")

    mock_requests.get.return_value.text = "<html>This is the page</html>"
    mock_requests.return_value.status_code = 200

    return mock_requests


def test_download_index_for_date(mock_requests):
    obj1 = bd_request.BDRequest()
    obj1.update_last_request_time(datetime(2014, 6, 2, 23, 0, 19))

    response_text = obj1.download_index_for_date(date(2019, 10, 11))

    assert response_text == "<html>This is the page</html>"


def test_download_index_for_date_calling(mock_requests):
    obj1 = bd_request.BDRequest()
    obj1.update_last_request_time(datetime(2014, 6, 2, 23, 0, 19))

    response_text = obj1.download_index_for_date(date(2019, 10, 11))
    args, kwargs = mock_requests.get.call_args

    assert kwargs["headers"]["Referer"] == "https://www.google.com/"

    obj1.update_last_request_time(datetime(2014, 6, 2, 23, 0, 19))
    response_text = obj1.download_index_for_date(date(2019, 10, 12))
    args, kwargs = mock_requests.get.call_args
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    assert kwargs["headers"]["User-Agent"].startswith("Mozilla")
    assert kwargs["headers"]["Referer"] == "http://bigdave44.com/2019/10/11"

    assert response_text == "<html>This is the page</html>"
