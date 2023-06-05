from bd_crossword.common.crossword_grid import CrosswordGrid
import logging
import queue

logger = logging.getLogger(__name__)


class FillGrid:
    def __init__(self, clues, grid=None, row=0, col=0, try_count=0, recurse_count=0, stop_after=None):
        if grid is None:
            grid = CrosswordGrid(15, 15)
        
        self.grid = grid
        self.clues = clues
        self.row = row
        self.col = col
        self.try_count = try_count
        self.recurse_count = recurse_count
        self.stop_after = stop_after


    def fill_clue(self):
        item = self.clues.pop(0)
        word, clue_id, direction = item.actual_solution, item.clue_id, item.direction
        for try_num in range(35):
            self.try_count += 1
            logger.debug("%s%s %s, r%sc%s, try is %s", clue_id, direction, word, self.row, self.col, try_num)

            grid_savepoint = self.deep_copy()
            if self.grid.write_direction(self.row, self.col, word, direction, clue_id):
                logger.debug("before recurse call grid is %s", self.grid.text_grid())
                if word == self.stop_after:
                    return self

                if self.fill_grid() is not False:
                    logger.debug("returned fill_grid back to us with content %s", self.grid.text_grid())
                    return self

                logger.debug("<<<<<<<< fill_grid returned False, so we restore the grid to %s", grid_savepoint.grid.text_grid())
                self.restore_from_deep_copy(grid_savepoint)

            self.move_to_next_square()

        logger.debug(
            "no more tries left, row is %s, col is %s, word is %s, direction is %s, grid is %s",
            self.row, self.col, word, direction, self.grid.text_grid()
        )
        return False

    def fill_grid(self):
        self.recurse_count += 1
        logger.debug("fill_grid called at depth %s, clues left are %s", self.recurse_count, len(self.clues))
        if len(self.clues) > 0:
            if self.fill_clue() is False:
                logger.debug("fill_clue returned False, so we return False")
                return False

        return self        
                # return self.fill_grid_starting_with(row, col + 1, current_clue_index + 1)
        # return self.grid

    def move_to_next_square(self):
        if self.grid.is_empty(self.row, self.col):
            self.grid.set_blocked(self.row, self.col)
    
        if self.col < self.grid.cols - 1:
            self.col += 1
        else:
            self.col = 0
            self.row += 1

    def deep_copy(self):
        new_grid = self.grid.deep_copy()
        return FillGrid(list(self.clues), new_grid, self.row, self.col, self.try_count, self.recurse_count, self.stop_after)
    
    def restore_from_deep_copy(self, deep_copy):
        self.grid = deep_copy.grid.deep_copy()
        self.clues = list(deep_copy.clues)
        self.row = deep_copy.row
        self.col = deep_copy.col
        self.try_count = deep_copy.try_count


    def list_clues(self):
        for clue in self.clues:
            logger.debug("clue is %s, %s, %s", clue.clue_id, clue.direction, clue.actual_solution)



