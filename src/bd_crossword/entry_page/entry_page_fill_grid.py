from bd_crossword.common.crossword_grid import CrosswordGrid
from bd_crossword.common.crossword_clues import CrosswordClue

import logging
import queue

logger = logging.getLogger(__name__)


class FillGrid:
    def __init__(self, clues, grid=None, head_row=0, head_col=0, tail_row=14, tail_col=14, try_count=0, recurse_count=0, stop_after=None, state=None):
        logger.debug("Making new %s with clues param of type %s",type(self).__name__,type(clues).__name__)

        if grid is None:
            grid = CrosswordGrid(15, 15)
        self.grid = grid
        self.clues = clues
        self.head_row = head_row
        self.head_col = head_col
        self.tail_row = tail_row
        self.tail_col = tail_col
        self.try_count = try_count
        self.recurse_count = recurse_count
        self.stop_after = stop_after
        self.state = None

    def has_failed(self):
        return self.state == "Failed"
    
    def succeded(self):
        return self.state == "Success"

    def try_filling(self, head_clue, tail_clue):
        logger.debug("head is r%sc%s, tail is r%sc%s", self.head_row, self.head_col, self.tail_row, self.tail_col)
        logger.debug("head_clue is %s%s %s(%d)", head_clue.clue_id, head_clue.direction, head_clue.actual_solution, head_clue.actual_solution_length)
        if tail_clue:
            logger.debug("tail_clue is %s%s %s(%d)", tail_clue.clue_id, tail_clue.direction, tail_clue.actual_solution, tail_clue.actual_solution_length)

        new_fill_grid = self.deep_copy()
        if new_fill_grid.grid.write_direction(new_fill_grid.head_row, new_fill_grid.head_col, head_clue.actual_solution, head_clue.direction, head_clue.clue_id):
            logger.debug("wrote %s at r%sc%s", head_clue.actual_solution, new_fill_grid.head_row, new_fill_grid.head_col)
            if tail_clue is None or new_fill_grid.grid.write_tail_direction(new_fill_grid.tail_row, new_fill_grid.tail_col, tail_clue.actual_solution, tail_clue.direction, tail_clue.clue_id):
                if tail_clue is not None:
                    logger.debug("wrote %s backwards from r%sc%s", tail_clue.actual_solution, new_fill_grid.tail_row, new_fill_grid.tail_col)

                if head_clue.actual_solution == new_fill_grid.stop_after:
                    logger.debug("stopping after %s", new_fill_grid.stop_after)
                    self.restore_from(new_fill_grid)
                    self.state = "Success"
                    return

                logger.debug("before recurse call grid is %s", new_fill_grid.grid.text_grid())
                new_fill_grid.fill_grid()
                if new_fill_grid.succeded():
                    logger.debug("fill_grid succeeded and returned %s", new_fill_grid.grid.text_grid())
                    self.restore_from(new_fill_grid)
                    logger.debug("restored grid is %s", self.grid.text_grid())

                    return

                logger.debug("<<<<<<<< fill_grid returned as failed, so we restore the grid to %s", self.grid.text_grid())
            else:
                logger.debug("failed to write %s at r%sc%s", tail_clue.actual_solution, new_fill_grid.tail_row, new_fill_grid.tail_col)
        else:
            logger.debug("failed to write %s at r%sc%s", head_clue.actual_solution, new_fill_grid.head_row, new_fill_grid.head_col)



    def fill_clue(self):
        head_clue: CrosswordClue = self.clues.pop_head_clue()
        tail_clue: CrosswordClue | None = self.clues.pop_tail_clue(head_clue.direction, head_clue.actual_solution_length)

        for try_num in range(35):
            self.try_count += 1
            logger.debug("try_num is %s, try_count is %s", try_num, self.try_count)
            self.try_filling(head_clue, tail_clue)

            if self.succeded() or self.has_failed():
                return
            self.move_to_next_square()
        
        logger.debug(
            "no more tries left, head_row is %s, head_col is %s, head_clue.actual_solution is %s, head_clue.direction is %s, grid is %s",
            self.head_row, self.head_col, head_clue.actual_solution, head_clue.direction, self.grid.text_grid()
        )
        self.state = "Failed"
        return self

    def fill_grid(self):
        self.recurse_count += 1
        logger.debug("fill_grid called at depth %s, clues left are %s", self.recurse_count, len(self.clues))
        if len(self.clues) > 0:
            self.fill_clue()
        else:
            self.state = "Success"

        logger.debug("type of self is %s", type(self).__name__)
        logger.debug("type of self.grid is %s", type(self.grid).__name__)
        logger.debug("fill_grid returning grid %s", self.grid.text_grid())
        return self        


    def move_to_next_square(self):
        if self.grid.is_empty(self.head_row, self.head_col):
            self.grid.set_blocked(self.head_row, self.head_col)

        if self.grid.is_empty(self.tail_row, self.tail_col):
            self.grid.set_blocked(self.tail_row, self.tail_col)
    
        if self.head_col < self.grid.cols - 1:
            self.head_col += 1
            self.tail_col -= 1
        else:
            self.head_col = 0
            self.head_row += 1
            self.tail_col = 14
            self.tail_row -= 1

    def deep_copy(self):
        new_grid = self.grid.deep_copy()
        new_clues = self.clues.clone()
        return FillGrid(new_clues, new_grid, self.head_row, self.head_col, self.tail_row, self.tail_col, self.try_count, self.recurse_count, self.stop_after, self.state)
    
    def restore_from(self, deep_copy):
        self.grid = deep_copy.grid.deep_copy()
        self.clues = deep_copy.clues.clone()
        self.head_row = deep_copy.head_row
        self.head_col = deep_copy.head_col
        self.tail_row = deep_copy.tail_row
        self.tail_col = deep_copy.tail_col
        self.state = deep_copy.state
        # self.try_count = deep_copy.try_count

    def list_clues(self):
        for clue in self.clues:
            logger.debug("%2d%s %s", clue.clue_id, clue.direction, clue.actual_solution)



