from bd_crossword.common.crossword_grid import CrosswordGrid
import logging
import queue

logger = logging.getLogger(__name__)


class FillGrid:
    def __init__(self, clues, grid=None, head_row=0, head_col=0, tail_row=14, tail_col=14, try_count=0, recurse_count=0, stop_after=None):
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
        self.failure = False

    def has_failed(self):
        return self.failure
    
    def succeded(self):
        return not self.failure

    def fill_clue(self):
        head_clue = self.clues.pop_head_clue()
        word, wordlen, clue_id, direction = head_clue.actual_solution, head_clue.actual_solution_length, head_clue.clue_id, head_clue.direction

        if len(self.clues) > 0:
            tail_clue = self.clues.pop_tail_clue(direction, wordlen)
        else:
            tail_clue = None


        for try_num in range(35):
            self.try_count += 1
            logger.debug("head is r%sc%s", self.head_row, self.head_col)
            logger.debug("tail is r%sc%s", self.tail_row, self.tail_col)
            logger.debug("head_clue is %s%s %s(%d), r%sc%s, try is %s", clue_id, direction, word, wordlen, self.head_row, self.head_col, try_num)
            if tail_clue:
                logger.debug("tail_clue is %s%s %s(%d)", tail_clue.clue_id, tail_clue.direction, tail_clue.actual_solution, tail_clue.actual_solution_length)

            new_fill_grid = self.deep_copy()
            if new_fill_grid.grid.write_direction(new_fill_grid.head_row, new_fill_grid.head_col, word, direction, clue_id):
                logger.debug("wrote %s at r%sc%s", word, new_fill_grid.head_row, new_fill_grid.head_col)
                if tail_clue is None or new_fill_grid.grid.write_tail_direction(new_fill_grid.tail_row, new_fill_grid.tail_col, tail_clue.actual_solution, tail_clue.direction, tail_clue.clue_id):
                    if word == new_fill_grid.stop_after:
                        self.restore_from(new_fill_grid)
                        return

                    logger.debug("before recurse call grid is %s", new_fill_grid.grid.text_grid())
                    new_fill_grid.fill_grid()
                    if new_fill_grid.succeded():
                        logger.debug("fill_grid succeeded and returned %s", new_fill_grid.grid.text_grid())
                        self.restore_from(new_fill_grid)
                        logger.debug("restored grid is %s", self.grid.text_grid())

                        return

                    logger.debug("<<<<<<<< fill_grid returned as failed, so we restore the grid to %s", self.grid.text_grid())

            self.move_to_next_square()

        logger.debug(
            "no more tries left, head_row is %s, head_col is %s, word is %s, direction is %s, grid is %s",
            self.head_row, self.head_col, word, direction, self.grid.text_grid()
        )
        self.failure = True
        return self

    def fill_grid(self):
        self.recurse_count += 1
        logger.debug("fill_grid called at depth %s, clues left are %s", self.recurse_count, len(self.clues))
        if len(self.clues) > 0:
            self.fill_clue()

        logger.debug("type of self is %s", type(self).__name__)
        logger.debug("type of self.grid is %s", type(self.grid).__name__)
        logger.debug("fill_grid returning grid %s", self.grid.text_grid())
        return self        
                # return self.fill_grid_starting_with(head_row, head_col + 1, current_clue_index + 1)
        # return self.grid

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
        return FillGrid(new_clues, new_grid, self.head_row, self.head_col, self.tail_row, self.tail_col, self.try_count, self.recurse_count, self.stop_after)
    
    def restore_from(self, deep_copy):
        self.grid = deep_copy.grid.deep_copy()
        self.clues = deep_copy.clues.clone()
        self.head_row = deep_copy.head_row
        self.head_col = deep_copy.head_col
        self.tail_row = deep_copy.tail_row
        self.tail_col = deep_copy.tail_col
        self.failure = deep_copy.failure
        # self.try_count = deep_copy.try_count

    def list_clues(self):
        for clue in self.clues:
            logger.debug("%2d%s %s", clue.clue_id, clue.direction, clue.actual_solution)



