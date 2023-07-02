from dataclasses import dataclass, field
import logging
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass(order=True)
class CrosswordClue:
    """Class for keeping track of individual crossword clue information"""

    by_direction_sort_index: str = field(init=False, repr=False)
    by_number_sort_index: str = field(init=False, repr=False)
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
        self.by_direction_sort_index = f"{self.direction}{int(self.clue_id):02d}"
        self.by_number_sort_index = f"{int(self.clue_id):02d}{self.direction}"


@dataclass
class CrosswordClues:
    across: dict[int, CrosswordClue]
    down: dict[int, CrosswordClue]

    def by_number_sorted_clues(self):
        all_clues = list(self.across.values()) + list(self.down.values())
        # ensure all_clues is sorted by first clue_id as primary sort key then by direction as a secondary sort key
        all_clues.sort(key=lambda clue: clue.by_number_sort_index)
        return all_clues
        

class CrosswordCluesSortedByID:
    @classmethod
    def new_from_crossword_clues(cls, crossword_clues: CrosswordClues):
        logger.debug("new_from_crossword_clues is called with crossword_clues of type %s",type(crossword_clues).__name__)
        clue_list = list(crossword_clues.across.values()) + list(crossword_clues.down.values())

        logger.debug("clue_list is of type %s",type(clue_list).__name__)
        clue_list.sort(key=lambda clue: clue.by_number_sort_index)
        
        logger.debug("clue_list is of type %s",type(clue_list).__name__)
    
        logger.debug("About to call the constructor with a parameter of type %s",type(clue_list).__name__)

        sorted_clue_list = cls(clue_list)
        logger.debug("The type of sorted_clue_list is %s",type(sorted_clue_list).__name__)
        return sorted_clue_list


    def __init__(self, sorted_clue_list: list[CrosswordClue]):
        logger.debug("Making new %s with param of type %s",type(self).__name__,type(sorted_clue_list).__name__)
        self.clues_sorted = sorted_clue_list


    def __len__(self):
        return len(self.clues_sorted)
    
    def __iter__(self):
        return iter(self.clues_sorted)
    
    def get_first_clue(self):
        return self.clues_sorted.pop(0)
    
    def get_last_clue(self, direction:str, actual_solution_length: int):
        for clue in reversed(self.clues_sorted):
            if clue.actual_solution_length == actual_solution_length and clue.direction == direction:
                return self.clues_sorted.pop(self.clues_sorted.index(clue))
        raise ValueError(f"No clue with direction {direction} and actual_solution_length {actual_solution_length}")
    
    def clone(self):
        return CrosswordCluesSortedByID(self.clues_sorted.copy())
        

