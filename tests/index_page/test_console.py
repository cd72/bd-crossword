import click.testing
import pytest
import logging
import requests
import pathlib
from bd_crossword.index_page import console

logger = logging.getLogger(__name__)


@pytest.fixture
def runner():
    return click.testing.CliRunner()


@pytest.fixture
def mock_requests_get(mocker):
    mock = mocker.patch("requests.get")

    mock.return_value.text = "<html>This is the page</html>"
    mock.return_value.status_code = 200
    return mock


def test_main_succeeds_new(runner, mock_requests_get):
    result = runner.invoke(console.main)
    # logger.debug(result.output)
    # logger.debug(result.exit_code)
    assert result.exit_code == 0


def test_main_prints_message_on_request_error(runner, mock_requests_get):
    mock_requests_get.side_effect = requests.RequestException
    result = runner.invoke(console.main)
    logger.debug("result.output is %s", result.stdout)
    # logger.debug("result.error is %s", result.stderr)
    assert "Error" in result.output


def test_html_dump_files(runner, mock_requests_get):
    date_string = "2010-01-01"
    result = runner.invoke(
        console.main, [f"--start-date-string={date_string}", "--days=1", "--dump"]
    )

    html_dump_file = pathlib.Path(f"dump_{date_string}.html")
    index_dump_file = pathlib.Path(f"dump_{date_string}.index")

    logger.debug(html_dump_file.resolve())
    # logger.debug(result.output)
    # logger.debug(result.exit_code)
    assert result.exit_code == 0
    assert html_dump_file.exists()
    assert index_dump_file.exists()
    assert html_dump_file.read_text() == "<html>This is the page</html>"


# @pytest.fixture
# def mock_wikipedia_random_page(mocker):
#     return mocker.patch("hypermodern_python_iitt.wikipedia.random_page")


# def test_main_uses_specified_language(runner, mock_wikipedia_random_page):
#     runner.invoke(console.main, ["--language=pl"])
#     mock_wikipedia_random_page.assert_called_with(language="pl")


# @pytest.mark.e2e
# def test_main_succeeds_in_production_env(runner):
#     result = runner.invoke(console.main)
#     assert result.exit_code == 0


# def test_main_invokes_requests_get(runner, mock_requests_get):
#     runner.invoke(console.main)
#     assert mock_requests_get.called


# def test_main_uses_en_wikipedia_org(runner, mock_requests_get):
#     runner.invoke(console.main)
#     args, _ = mock_requests_get.call_args
#     assert "en.wikipedia.org" in args[0]


# def test_main_fails_on_request_error(runner, mock_requests_get):
#     mock_requests_get.side_effect = Exception("Boom")
#     result = runner.invoke(console.main)
#     logger.debug(result.output)

#     assert result.exit_code == 1


# def test_main_succeeds_new(runner, mock_requests_get):
#     result = runner.invoke(console.main)
#     logger.debug(result.output)

#     assert result.exit_code == 0


# def test_main_prints_message_on_request_error(runner, mock_requests_get):
#     mock_requests_get.side_effect = requests.RequestException
#     result = runner.invoke(console.main)
#     logger.debug(result.output)
#     assert "Error" in result.output
