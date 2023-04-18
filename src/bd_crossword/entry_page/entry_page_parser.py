import logging
import re
from dataclasses import dataclass, field
import datetime

from bs4 import BeautifulSoup
from typing import Optional

from bd_crossword.entry_page import entry_page_fix_up

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
    title: str = None
    hints_author: str = None
    difficulty: float = None
    enjoyment: float = None
    url: Optional[str] = None
    puzzle_date: Optional[datetime.date] = None
    across_clues: Optional[dict[int, CrosswordClue]] = None
    down_clues: Optional[dict[int, CrosswordClue]] = None
    clues: Optional[list[CrosswordClue]] = None


def get_puzzle_id_number(puzzle_html):
    return re.search(r"Daily Telegraph Cryptic No (\d{5})", puzzle_html)[1]


def get_puzzle_title(puzzle_html):
    # puzzle_title = soup.select_one("h1.entry-title").text
    return f"DT {get_puzzle_id_number(puzzle_html)}"


def parse_html(html: str) -> Crossword:
    logger.debug("Runing parse_html")
    return Crossword(
        title=get_puzzle_title(html),
        hints_author=get_puzzle_hints_author(html),
        difficulty=get_difficulty(html),
        enjoyment=get_enjoyment(html),
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
    return re.search(r"Hints and tips by (.+?) ?<", puzzle_html, re.MULTILINE)[1]


def get_difficulty(html):
    puzzles_without_difficulty = {"DT 29608"}
    if get_puzzle_title(html) in puzzles_without_difficulty:
        return 3

    m = re.search(r"Difficulty ([\*\/\ ]+)", html, re.MULTILINE)
    return convert_stars_to_number(m[1])

def get_enjoyment(html):
    puzzles_without_enjoyment = {"DT 29608"}
    if get_puzzle_title(html) in puzzles_without_enjoyment:
        return 3
    m = re.search(r"Enjoyment ([\*\/\ ]+)", html, re.MULTILINE)
    return convert_stars_to_number(m[1])

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


def get_soup(html):
    return BeautifulSoup(html, "html.parser")

re_clue_line = re.compile(
    r"""
    (\d{1,2})([a|d])                    # Clue Identifier
    \s*                                 # After the clue identifier we 
                                        # can see whitespace
    (.+?)                               # Then the actual clue
    \s*                                 # Then more whitespace before an open bracket
    (\([0-9,-]+\))                      # In brackets we get the word(s) lengths 
                                        # sometimes comma separated
    (.*?\n)                             # Ignore anything else up to the end of the
                                        # line and start of next
    .{0,5}                              # A few chars at start of next line.  e.g. <p>             
    \<span\ class="spoiler"\>           # <span class="spoiler">
    \s?                                 # Optional space
    (.+?)                               # The solution
    \s?                                 # Optional space
    \<\/span\>
    \s??                                # Optional space
    [:–—.]                              # Either a colon or a dash
                                        # or in the case of 29925 10d even a .
    ?                                   # or according to 29932 13a nothing at all
    \s*
    (.+)                               # The hint
""",
    re.VERBOSE + re.DOTALL + re.MULTILINE,
)

from collections import Counter
def parse_for_clues(html):
    logger.debug("running...")
    html = entry_page_fix_up.fix_up_html(html)
    soup = get_soup(html)
    clues = Counter()
    current_direction = None


    for paragraph in soup.select("p"):
        #logger.debug(type(paragraph))
        logger.debug(paragraph)

        logger.debug('.%s.',str(paragraph.text).strip())
        paragraph_text = str(paragraph.text).strip()
        
        if paragraph_text in  ["Across", "Down"]:
            logger.debug(f"{paragraph_text} Header Found")
            current_direction = paragraph_text
            next

        if current_direction is None:
            next

        if match := re.search(re_clue_line, str(paragraph)):
            print("Match found")
            clues[current_direction]+=1
        else:
            print("no match found")


        #logger.debug(str(paragraph))


    return clues
