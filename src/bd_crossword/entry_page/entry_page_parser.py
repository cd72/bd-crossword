import logging
import re
from dataclasses import dataclass, field
import datetime

from bs4 import BeautifulSoup
from bs4 import NavigableString
import json

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
def count_clues_01(html: str):
    clues = Counter()
    html = entry_page_fix_up.fix_up_html(html)

    soup = get_soup(html)
    current_direction = None

    for paragraph in soup.select("p"):
        logger.debug(paragraph)
        paragraph_text = str(paragraph.text).strip()

        if paragraph_text.lower() in {"across", "down"}:
            logger.debug("===== %s Header Found", paragraph_text.lower())
            current_direction = paragraph_text.lower()
            next

        if current_direction is None:
            next

        if match := re.search(re_clue_line, str(paragraph)):
            logger.debug("Match found")
            clues[current_direction]+=1
        else:
            logger.debug("no match found")


            #logger.debug(str(paragraph))

    return clues

re_clues = re.compile(
    r"""
    ^\<p\>                                # <p>
    (
        (Across|Down)                     # Across or Down
        |
        (?:\<strong\>)?                   # optional strong
        (\d{1,2})([a|d])                  # Clue Identifier
        (?:\<\/strong\>)?
        \s*                               # Whitespace
        (.+?)                             # Then anything up to the next
    )
    \<\/p\>                               # </p>
""",
    re.VERBOSE + re.DOTALL + re.MULTILINE,
)
def count_clues_02(html: str):
    clue_counter = Counter()
    html = entry_page_fix_up.fix_up_html(html)
    current_direction = None
    clues = re.findall(re_clues, html)

    first_lines = html.split('\n')[:40]
    logger.debug("<<<<<------- first_lines")
    for line in first_lines:
        logger.debug(line[:160])
    logger.debug("<<<<<------- first_lines end")

    for clue_line in clues:
        logger.debug("iterating")
        full_clue_html = clue_line[0]
        direction_header = clue_line[1]
        clue_id = int(clue_line[2]) if clue_line[2] != "" else 0
        direction = clue_line[3]
        logger.debug(full_clue_html)
        logger.debug(f"{current_direction=}")
        logger.debug(f"{direction=}")

        if direction_header != "":
            logger.debug(f"{direction_header=}")
            if direction_header == "Across":
                current_direction = "across"
            elif direction_header == "Down":
                current_direction = "down"
            else:
                raise ValueError(f"Direction {direction_header} is not valid")
            continue

            
        clue_counter[current_direction] += 1
        logger.debug("clue_counter is %s", clue_counter)
        # logger.info(clue_counter)

    return clue_counter



def count_clues_03(html: str):
    html = entry_page_fix_up.fix_up_html_03(html)

    clue_lines = html.split('\n')
    first_lines = clue_lines[:40]
    logger.debug("<<<<<------- first_lines")
    for line in first_lines:
        logger.debug(line[:160])
    logger.debug("<<<<<------- first_lines end")
    clue_counter = Counter()
    re_clues = re.compile(
        r"""
        (
            (?:
                ^
                (?P<direction_header>Across|Down)
                $
            )              
            |
            ^
            (?P<index_num>\d{1,2})
            (?P<direction>[a|d])
            \ *                
            (?P<clue_text>.+?)
            (?P<listed_solution_length>\([0-9,-]+\))                    # In brackets we get the word(s) lengths 
            \n
            \<spoiler\>                       # <span class="spoiler">
            \ ?                               # Optional space
            (?P<listed_solution>.+?)                             # The solution
            \ ?                               # Optional space
            \<\/spoiler\>
            [:\.\-]?
            \ *
            (?P<hint>.+$)
        )
    """,
        re.VERBOSE + re.MULTILINE,
    )


    logger.debug("=====================================")
    current_direction = "across"
    for item in re.finditer(re_clues, html):

        logger.debug(item.groupdict())
        logger.debug(item["direction_header"])
        if item["direction_header"] is not None:
            current_direction = item["direction_header"].lower()
            continue

        if item["direction"] is not None:
            clue_counter[current_direction] += 1

    logger.debug("clue_counter is %s", clue_counter)

    return clue_counter
