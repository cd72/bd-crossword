import logging
import re
from dataclasses import dataclass, field
import datetime

from bs4 import BeautifulSoup
from typing import Optional

# from bd_crossword.common import crossword_index, index_entry

logger = logging.getLogger(__name__)


@dataclass(order=True)
class CrosswordClue:
    """Class for keeping track of individual crossword clue information"""

    sort_index: str = field(init=False, repr=False)
    clue_id: int
    direction: str
    clue_text: str
    listed_solution: Optional[str] = None
    listed_solution_length: Optional[str] = None
    actual_solution: Optional[str] = None
    actual_solution_length: Optional[str] = None
    hint: Optional[str] = None
    begins_with: Optional[str] = None
    cp: bool = False  # Composite Placeholder
    cp_pointer_clue_id: Optional[int] = None  # What the composite placeholder points to
    cp_pointer_direction: Optional[str] = None
    cm: bool = False  # Composite Main
    cm_pointer_clue_id: Optional[int] = None  # What the composite main points to
    cm_pointer_direction: Optional[str] = None

    def __post_init__(self):
        self.sort_index = f"{self.direction}{int(self.clue_id):02d}"


@dataclass
class Crossword:
    title: Optional[str] = None
    hints_author: Optional[str] = None
    difficulty: Optional[float] = None
    enjoyment: Optional[float] = None
    url: Optional[str] = None
    puzzle_date: Optional[datetime.date] = None
    across_clues: Optional[dict[int, CrosswordClue]] = None
    down_clues: Optional[dict[int, CrosswordClue]] = None
    clues: Optional[list[CrosswordClue]] = None

def get_puzzle_id_number(puzzle_html):
    return re.search(
        r"Daily Telegraph Cryptic No (\d{5})", puzzle_html
    )[1]

def get_puzzle_title(puzzle_html):
    # puzzle_title = soup.select_one("h1.entry-title").text
    return f"DT {get_puzzle_id_number(puzzle_html)}"

def parse_html(html: str) -> Crossword:
    return Crossword(
        title = get_puzzle_title(html),
        hints_author = get_puzzle_hints_author(html)
    )

def convert_stars_to_number(stars):
    stars = stars.replace(" ", "")
    if stars == "*":
        return 1
    elif stars == "**":
        return 2
    elif stars == "***":
        return 3
    elif stars == "****":
        return 4
    elif stars == "*****":
        return 5
    elif stars == "******":
        return 6
    elif stars == "*/**":
        return 1.5
    elif stars == "**/***":
        return 2.5
    elif stars == "***/****":
        return 3.5
    elif stars == "****/*****":
        return 4.5
    else:
        return 999


def get_puzzle_hints_author(puzzle_html):
    # puzzle_author = soup.select_one("span.author").text
    return re.search(r"Hints and tips by (.+?)$", puzzle_html, re.MULTILINE)[1]


def parse_string_for_difficulty(html_string):
    m = bd_regexes.re_difficulty_stars.search(html_string)
    if not m:
        raise Exception("NO DIFFICULTY FOUND")

    logger.debug(f"difficulty stars {repr(m.group(1))}")
    difficulty = convert_stars_to_number(m.group(1))
    logger.debug(f"difficulty: {difficulty}")
    return difficulty


def parse_string_for_enjoyment(html_string):
    m = bd_regexes.re_enjoyment_stars.search(html_string)
    if not m:
        raise Exception("NO ENJOYMENT FOUND")

    logger.debug(f"enjoyment stars {repr(m.group(1))}")
    enjoyment = convert_stars_to_number(m.group(1))
    logger.debug(f"enjoyment: {enjoyment}")
    return enjoyment


def get_puzzle_difficulty(html):
    entry_content = html.select_one(".entry-content")
    return parse_string_for_difficulty(entry_content.text)


def get_puzzle_enjoyment(html):
    entry_content = html.select_one(".entry-content")
    return parse_string_for_enjoyment(entry_content.text)


def get_puzzle_url(html):
    match = re.findall(bd_regexes.re_page_url, html)
    if not match:
        raise ValueError("Could not match a url")

    return match[0]


def get_puzzle_date(html):
    match = re.search(bd_regexes.re_page_date, html)
    if not match:
        raise ValueError("Could not match a date")
    return datetime.date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
