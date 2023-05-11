import logging
import re
from dataclasses import dataclass, field
import datetime

from bs4 import BeautifulSoup
from bs4 import NavigableString
import json

from typing import Optional

from bd_crossword.entry_page import entry_page_fix_up
from collections import Counter

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
                (?P<clue_text>.+?)
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

def count_clues_03(html: str):
    html = entry_page_fix_up.fix_up_html_03(html)

    clue_lines = html.split('\n')
    first_lines = clue_lines[:40]
    logger.debug("<<<<<------- first_lines")
    for line in first_lines:
        logger.debug(line[:160])
    logger.debug("<<<<<------- first_lines end")
    clue_counter = Counter()


    logger.debug("=====================================")
    current_direction = "across"
    for item in re.finditer(re_clues, html):

        logger.debug(item.groupdict())
        # logger.debug(item["direction_header"])
        if item["direction_header"] is not None:
            current_direction = item["direction_header"].lower()
            continue

        clue_counter[current_direction] += 1

    logger.debug("clue_counter is %s", clue_counter)

    return clue_counter
