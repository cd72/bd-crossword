import click.testing
import pytest
import logging
import requests
import pathlib
import time
from bd_crossword.index_page import console
from bd_crossword.index_page import index_page_getter

logger = logging.getLogger(__name__)


@pytest.fixture
def runner():
    return click.testing.CliRunner()


@pytest.fixture
def html_mock_file():
    return pathlib.Path(__file__).parent / "test_data_files" / "dump_2022-09-19.html"


@pytest.fixture
def mock_requests_get(mocker, request, html_mock_file):

    mock = mocker.patch("requests.get")
    logger.debug("using html mock file : %s", str(html_mock_file.resolve()))
    mock.return_value.text = html_mock_file.read_text()
    mock.return_value.status_code = 200

    return mock


@pytest.fixture
def mock_time_sleep(mocker):
    mock_time = mocker.patch(
        f"{index_page_getter.bd_request.__name__}.time", wraps=time
    )
    mock_time.sleep.return_value = None


def test_main_succeeds_new(runner, mock_requests_get, mock_time_sleep):
    result = runner.invoke(console.main)
    # logger.debug(result.output)
    # logger.debug(result.exit_code)
    assert result.exit_code == 0


def test_main_prints_message_on_request_error(runner, mock_requests_get):
    mock_requests_get.side_effect = requests.RequestException
    result = runner.invoke(console.main, ["--days=1", "--force-download"])
    # logger.debug("result.error is %s", result.stderr)
    logger.debug("result.output is %s", result.output)
    logger.debug("result.exit_code is %s", result.exit_code)

    assert "Error" in result.output


def test_main_exit_1_on_request_error(runner, mock_requests_get):
    mock_requests_get.side_effect = requests.RequestException
    result = runner.invoke(console.main, ["--days=1", "--force-download"])
    logger.debug("result.exit_code is %s", result.exit_code)

    assert result.exit_code == 1


@pytest.fixture
def setup_dump_files(runner, mock_requests_get):
    date_string = "2020-01-01"
    result = runner.invoke(
        console.main,
        [
            f"--start-date-string={date_string}",
            "--days=1",
            "--dump",
            "--force-download",
        ],
    )

    html_dump_file = pathlib.Path(f"dump_{date_string}.html")
    index_dump_file = pathlib.Path(f"dump_{date_string}.index")
    logger.debug(html_dump_file.resolve())
    logger.debug(index_dump_file.resolve())

    yield {
        "result": result,
        "html_dump_file": html_dump_file,
        "index_dump_file": index_dump_file,
    }

    html_dump_file.unlink()
    index_dump_file.unlink()


def test_html_dump_files(runner, mock_requests_get, setup_dump_files):
    assert setup_dump_files["result"].exit_code == 0
    assert setup_dump_files["html_dump_file"].exists()
    assert setup_dump_files["index_dump_file"].exists()
    assert setup_dump_files["html_dump_file"].read_text().startswith("<!doctype html>")
