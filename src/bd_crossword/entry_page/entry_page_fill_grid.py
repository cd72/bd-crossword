from bd_crossword.common.crossword_grid import CrosswordGrid
import logging
import queue

logger = logging.getLogger(__name__)


class FillGrid:
    def __init__(self, clues, grid=None, row=0, col=0):
        if grid is None:
            grid = CrosswordGrid(15, 15)
        
        self.grid = grid
        self.clues = clues
        self.row = row
        self.col = col

    def fill_grid(self):
        logger.debug("fill_grid called clues left are %s", len(self.clues))
        while len(self.clues) > 0:
            item = self.clues.pop(0)
            word, clue_id, direction = item.actual_solution, item.clue_id, item.direction
            for try_num in range(35):
                logger.debug("%s%s %s, r%sc%s, try is %s", clue_id, direction, word, self.row, self.col, try_num)

                if self.grid.write_direction(self.row, self.col, word, direction, clue_id):
                    logger.debug("now grid is %s", self.grid.text_grid())
                    new_fill_grid = self.deep_copy()
                    if new_fill_grid := new_fill_grid.fill_grid():
                        logger.debug("returned new_fill_grid back to us with content %s", new_fill_grid.grid.text_grid())
                        return new_fill_grid


                self.move_to_next_square()

            logger.debug(
                "no more tries left, row is %s, col is %s, word is %s, direction is %s, grid is %s",
                self.row, self.col, word, direction, self.grid.text_grid()
            )
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
        return FillGrid(list(self.clues), new_grid, self.row, self.col)

    def list_clues(self):
        for clue in self.clues:
            logger.debug("clue is %s, %s, %s", clue.clue_id, clue.direction, clue.actual_solution)



