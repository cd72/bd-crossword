import logging
import types
from datetime import date
import pytest
import pathlib

from bd_crossword.index_page import index_downloader

logger = logging.getLogger(__name__)


@pytest.fixture
def mock_requests_get(mocker):
    mock = mocker.patch("requests.get")
    html_mock_file = pathlib.Path(__file__).parent / "data" / "test01.html"
    logger.debug("using html mock file : %s", str(html_mock_file.resolve()))
    mock.return_value.text = html_mock_file.read_text()
    mock.return_value.status_code = 200
    return mock


def test_dates_in_range_returns_generator():
    test_date = date(2019, 10, 10)
    test_count = 5

    test_data = index_downloader.dates_in_range(test_date, test_count)
    logger.debug(type(test_data))
    assert isinstance(test_data, types.GeneratorType)


def test_dates_in_range_01():
    test_date = date(2019, 10, 10)
    test_count = 5
    expected_data = [
        date(2019, 10, 10),
        date(2019, 10, 9),
        date(2019, 10, 8),
        date(2019, 10, 7),
        date(2019, 10, 6),
    ]

    test_data = list(index_downloader.dates_in_range(test_date, test_count))
    logger.debug("test_data : %s", test_data)
    assert test_data == expected_data


def test_download_index_for_date(mock_requests_get):
    test_date = date(2019, 10, 10)
    html_text = index_downloader.download_index_for_date(test_date)
    assert len(html_text) == 62309
