#import click.testing
import pytest
import logging
from bd_crossword.html_page import html_page_generator
from bd_crossword.entry_page.entry_page_fill_grid import FillGrid

logger = logging.getLogger(__name__)

def test_console():
    #output = html_page_generator.get_grid_for_date("2023-07-03")
    output = html_page_generator.get_grid_for_date("2023-06-21")
    assert type(output) is str


