import logging
import re
import datetime

from bs4 import BeautifulSoup
from bs4 import NavigableString
import json

from typing import Optional

from bd_crossword.entry_page import entry_page_fix_up
from bd_crossword.common.crossword_clues import CrosswordClue, CrosswordClues
from collections import Counter

# from bd_crossword.common import crossword_index, index_entry

logger = logging.getLogger(__name__)


re_clues = re.compile(
    r"""
    (
        (?:
            ^
            (?P<direction_header>Across|Down)
            $
        )              
        |
        (?:
            ^
            (?P<index_num>\d{1,2})
            (?P<direction>[a|d])?
            \ *
            (?:
                (?: # Optionally this can reference another clue.  e.g. 16d & 19d
                    &amp;\ (?P<cp_pointer_clue_id>\d{1,2})
                    \ *
                    (?P<cp_pointer_direction>Across|Down|a|d)
                    \ *
                )?                
                (?P<clue_text>.+?)\ *
                (?P<listed_solution_length>\([0-9,-]+\))    # In brackets we get the word(s) lengths 
                \n
                \<spoiler\>
                    \ ? 
                    (?P<listed_solution>.+?)  
                    \ ? 
                \<\/spoiler\>
                [:;\.\-]?
                \ *
                (?P<hint>.+$)
            |
                (?:  # This could be a placeholder.  e.g.  See 16 Down
                    \ *
                    (?P<cm_clue_text>
                        See\ 
                        (?P<cm_pointer_clue_id>\d{1,2})
                        \ ?
                        (?P<cm_pointer_clue_direction>Across|Down|a|d)
                    )
                    \ *
                )
            )
        )
    )
""",
    re.VERBOSE + re.MULTILINE,
)

def log_first_lines(html) -> None:
    clue_lines = html.split('\n')
    first_lines = clue_lines[:40]
    logger.debug("<<<<<------- first_lines")
    for line in first_lines:
        logger.debug(line[:160])
    logger.debug("<<<<<------- first_lines end")
    logger.debug("=====================================")

def generate_clue(reg_match: re.Match) -> CrosswordClue:
    result = CrosswordClue(
        clue_id=int(reg_match["index_num"]),
        direction=reg_match["direction"],
        clue_text=reg_match["clue_text"],
        listed_solution=reg_match["listed_solution"],
        listed_solution_length=reg_match["listed_solution_length"],
        hint=reg_match["hint"],
    )
    if reg_match["cp_pointer_clue_id"] is not None:
        result.cp = True
        result.cp_pointer_clue_id = reg_match["cp_pointer_clue_id"]
        result.cp_pointer_direction = reg_match["cp_pointer_direction"]

    if reg_match["cm_pointer_clue_id"] is not None:
        result.cm = True
        result.cm_pointer_clue_id = reg_match["cm_pointer_clue_id"]
        result.cm_pointer_direction = reg_match["cm_pointer_clue_direction"]

    return result


def parse_basic_clues(html: str) -> CrosswordClues:
    log_first_lines(html)


    crossword_clues = CrosswordClues(across={}, down={})

    current_direction = "across"
    for item in re.finditer(re_clues, html):
        logger.debug(item.groupdict())
        if item["direction_header"] is not None:
            current_direction = item["direction_header"].lower()
            continue

        getattr(crossword_clues, current_direction)[int(item["index_num"])] = generate_clue(item)


    # logger.debug("clue_counter is %s", clue_counter)

    return crossword_clues

def get_start_letters(string: str) -> str:
    # logger.debug(f"{string=}")
    words = string.replace("-", " ").split(" ")
    # logger.debug(f"{words=}")
    start_letters_list = [word[0] for word in words]
    return ",".join(start_letters_list)

def enrich_clues(crossword_clues: CrosswordClues) -> CrosswordClues:
    for direction in ("across", "down"):
        for clue_id, clue in getattr(crossword_clues, direction).items():
            if clue.listed_solution is None:
                continue
            clue.actual_solution = re.sub(r"[ \-’']", "", clue.listed_solution)
            clue.actual_solution_length = len(clue.actual_solution)
            clue.solution_start_letters = get_start_letters(clue.listed_solution)

    return crossword_clues

def parse_entry_page(html: str) -> CrosswordClues:
    html = entry_page_fix_up.fix_up_html_03(html)
    crossword_clues = parse_basic_clues(html)
    crossword_clues = enrich_clues(crossword_clues)

    return crossword_clues

