#import click.testing
import pytest
import logging
from bd_crossword.html_page import console
from bd_crossword.entry_page.entry_page_fill_grid import FillGrid

logger = logging.getLogger(__name__)

@pytest.fixture
def runner():
    return click.testing.CliRunner()

# test we can call the console utility
# def test_console_utility(runner):
#     result = runner.invoke(console.main, ["-p", "2023-07-05"])
#     #result = runner.invoke(console.main, ["ALL"])
#     assert result.exit_code == 0

def test_console():
    console.main("2023-07-04")
    #console.main("2023-07-05")

