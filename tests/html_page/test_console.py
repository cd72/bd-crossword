import click.testing
import pytest
import logging
from bd_crossword.html_page import console
logger = logging.getLogger(__name__)

@pytest.fixture
def runner():
    return click.testing.CliRunner()

# test we can call the console utility
def test_console_utility(runner):
    result = runner.invoke(console, [])
    assert result.exit_code == 0

