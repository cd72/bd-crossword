import logging
from datetime import date
import pytest
import pathlib
import time

from bd_crossword.index_page import index_page_getter

logger = logging.getLogger(__name__)


# @pytest.fixture
# def mock_requests_get(mocker):
#     mock = mocker.patch("requests.get")
#     html_mock_file = pathlib.Path(__file__).parent / "data" / "test_2022-09-27.html"
#     logger.debug("using html mock file : %s", str(html_mock_file.resolve()))
#     mock.return_value.text = html_mock_file.read_text()
#     mock.return_value.status_code = 200
#     return mock


@pytest.fixture()
def getter():
    return index_page_getter.IndexPageGetter(database_file=":memory:")


@pytest.fixture()
def mock_time_dot_sleep(mocker):
    mock_time = mocker.patch(
        f"{index_page_getter.bd_request.__name__}.time", wraps=time
    )
    mock_time.sleep.return_value = None
    return mock_time


def test_dates_in_range(getter):
    test_date = date(2019, 10, 11)
    test_count = 5
    expected_data = [
        date(2019, 10, 11),
        date(2019, 10, 10),
        date(2019, 10, 9),
        date(2019, 10, 8),
        date(2019, 10, 7),
    ]

    test_data = list(getter.dates_in_range(test_date, test_count))
    logger.debug("test_data : %s", test_data)
    assert test_data == expected_data


def test_dates_in_range_over_weekend(getter):
    test_date = date(2019, 10, 7)
    test_count = 2
    expected_data = [
        date(2019, 10, 7),
        date(2019, 10, 4),
    ]

    test_data = list(getter.dates_in_range(test_date, test_count))
    logger.debug("test_data : %s", test_data)
    assert test_data == expected_data


def test_dates_in_range_zero_days(getter):
    test_date = date(2019, 10, 7)
    test_count = 0
    expected_data = []

    test_data = list(getter.dates_in_range(test_date, test_count))
    logger.debug("test_data : %s", test_data)
    assert test_data == expected_data


class TestGetIndexEntriesForDate:
    # def test_using_test01(self, mock_requests_get):
    #     index_entry = index_downloader.get_index_entries_for_date(date(2022, 9, 27))
    #     assert index_entry == [
    #         index_downloader.IndexEntry(
    #             title="DT 30103",
    #             url="http://bigdave44.com/2022/09/27/dt-30103/",
    #             hints_author="Twmbarlwm",
    #             difficulty=2,
    #             enjoyment=4,
    #             last_updated="2022-09-27T16:27:12+01:00",
    #         )
    #     ]

    test_file_location = pathlib.Path(__file__).parent / "test_data_files"
    test_files = list(test_file_location.rglob("dump_2022-09-21.html"))
    assert len(test_files) == 1

    @pytest.fixture(params=test_files)
    def mock_requests_index(self, mocker, request):
        html_mock_file = request.param
        index_res_file = html_mock_file.with_suffix(".index")
        test_date_string = html_mock_file.stem.removeprefix("dump_")[:10]

        mock = mocker.patch("requests.get")
        logger.debug("using html mock file : %s", str(html_mock_file.resolve()))
        mock.return_value.text = html_mock_file.read_text()
        mock.return_value.status_code = 200

        logger.debug("using index res file : %s", str(index_res_file.resolve()))
        index_res = index_res_file.read_text()

        return {
            "mock": mock,
            "index_res": index_res,
            "test_date_string": test_date_string,
        }

    def test_using_dump_file(self, mock_requests_index, getter, mock_time_dot_sleep):
        logger.debug("testing for date %s", mock_requests_index["test_date_string"])

        index_entry = getter.get_index_entry_for_date(
            date.fromisoformat(mock_requests_index["test_date_string"])
        )
        logger.debug(index_entry)
        assert mock_time_dot_sleep.sleep.called
        # assert repr(index_entry) == mock_requests_index["index_res"]
