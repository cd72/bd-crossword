import logging
import types
from datetime import date
import pytest
import pathlib

from bd_crossword.index_page import index_downloader

# from bd_crossword.index_page.index_downloader import IndexEntry


logger = logging.getLogger(__name__)


@pytest.fixture
def mock_requests_get(mocker):
    mock = mocker.patch("requests.get")
    html_mock_file = pathlib.Path(__file__).parent / "data" / "test_2022-09-27.html"
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


class TestGetIndexEntriesForDate:
    def test_using_test01(mocker_requests_get):
        index_entry = index_downloader.get_index_entries_for_date(date(2022, 9, 27))
        assert index_entry == [
            index_downloader.IndexEntry(
                title="DT 30103",
                url="http://bigdave44.com/2022/09/27/dt-30103/",
                hints_author="Twmbarlwm",
                difficulty=2,
                enjoyment=4,
                last_updated="2022-09-27T16:27:12+01:00",
            )
        ]


test_file_location = pathlib.Path(__file__).parent / "test_data_files"
test_files = list(test_file_location.rglob("*.html"))
assert len(test_files) > 1


@pytest.fixture(params=test_files)
def mock_requests_index(mocker, request):
    html_mock_file = request.param
    index_res_file = html_mock_file.with_suffix(".index")
    test_date_string = html_mock_file.stem.removeprefix("dump_")[:10]

    mock = mocker.patch("requests.get")
    logger.debug("using html mock file : %s", str(html_mock_file.resolve()))
    mock.return_value.text = html_mock_file.read_text()
    mock.return_value.status_code = 200

    logger.debug("using index res file : %s", str(index_res_file.resolve()))
    index_res = index_res_file.read_text()

    return {"mock": mock, "index_res": index_res, "test_date_string": test_date_string}


def test_using_dump_file(mock_requests_index):
    logger.debug("testing for date %s", mock_requests_index["test_date_string"])

    index_entry = index_downloader.get_index_entries_for_date(
        date.fromisoformat(mock_requests_index["test_date_string"])
    )
    assert repr(index_entry) == mock_requests_index["index_res"]


@pytest.mark.parametrize(
    "stars_input,expected_value",
    [
        ("*", 1),
        ("**", 2),
        ("***", 3),
        (" ***", 3),
        ("*** ", 3),
        ("****", 4),
        ("*****", 5),
        ("******", 6),
        ("*/**", 1.5),
        ("**/***", 2.5),
        ("***/****", 3.5),
        ("****/*****", 4.5),
    ],
)
def test_stars_to_numbers(stars_input, expected_value):
    assert index_downloader.convert_stars_to_number(stars_input) == expected_value


def test_stars_to_numbers_exception():
    stars_input = "**********"
    with pytest.raises(ValueError) as excinfo:
        index_downloader.convert_stars_to_number(stars_input)
    assert "Invalid stars rating pattern found" in str(excinfo.value)
    assert stars_input in str(excinfo.value)
