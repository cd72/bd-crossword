from dataclasses import dataclass, field
import logging
from typing import Optional

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
    solution_start_letters: Optional[str] = None
    cp: bool = False  # Composite Placeholder
    cp_pointer_clue_id: Optional[int] = None  # What the composite placeholder points to
    cp_pointer_direction: Optional[str] = None
    cm: bool = False  # Composite Main
    cm_pointer_clue_id: Optional[int] = None  # What the composite main points to
    cm_pointer_direction: Optional[str] = None

    def __post_init__(self):
        self.sort_index = f"{self.direction}{int(self.clue_id):02d}"


# @dataclass
# class Crossword:
#     title: str = None
#     hints_author: str = None
#     difficulty: float = None
#     enjoyment: float = None
#     url: Optional[str] = None
#     puzzle_date: Optional[datetime.date] = None
#     across_clues: Optional[dict[int, CrosswordClue]] = None
#     down_clues: Optional[dict[int, CrosswordClue]] = None
#     clues: Optional[list[CrosswordClue]] = None


@dataclass
class CrosswordClues:
    across: dict[int, CrosswordClue]
    down: dict[int, CrosswordClue]
