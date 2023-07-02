from bd_crossword.common.crossword_grid import CrosswordGrid
import logging
import queue

logger = logging.getLogger(__name__)


class FillGrid:
    def __init__(self, clues, grid=None, row=0, col=0, try_count=0, recurse_count=0, stop_after=None):
        logger.debug("Making new %s with clues param of type %s",type(self).__name__,type(clues).__name__)

        if grid is None:
            grid = CrosswordGrid(15, 15)
        self.grid = grid
        self.clues = clues
        self.row = row
        self.col = col
        self.try_count = try_count
        self.recurse_count = recurse_count
        self.stop_after = stop_after
        self.failure = False

    def has_failed(self):
        return self.failure
    
    def succeded(self):
        return not self.failure

    def fill_clue(self):
        item = self.clues.get_first_clue()
        word, clue_id, direction = item.actual_solution, item.clue_id, item.direction
        for try_num in range(35):
            self.try_count += 1
            logger.debug("%s%s %s, r%sc%s, try is %s", clue_id, direction, word, self.row, self.col, try_num)

            new_fill_grid = self.deep_copy()
            if new_fill_grid.grid.write_direction(new_fill_grid.row, new_fill_grid.col, word, direction, clue_id):
                logger.debug("before recurse call grid is %s", new_fill_grid.grid.text_grid())
                if word == new_fill_grid.stop_after:
                    self.restore_from(new_fill_grid)
                    return

                new_fill_grid.fill_grid()
                if new_fill_grid.succeded():
                    logger.debug("fill_grid succeeded and returned %s", new_fill_grid.grid.text_grid())
                    self.restore_from(new_fill_grid)
                    logger.debug("restored grid is %s", self.grid.text_grid())

                    return

                logger.debug("<<<<<<<< fill_grid returned as failed, so we restore the grid to %s", self.grid.text_grid())

            self.move_to_next_square()

        logger.debug(
            "no more tries left, row is %s, col is %s, word is %s, direction is %s, grid is %s",
            self.row, self.col, word, direction, self.grid.text_grid()
        )
        self.failure = True
        return self

    def fill_grid(self):
        self.recurse_count += 1
        logger.debug("fill_grid called at depth %s, clues left are %s", self.recurse_count, len(self.clues))
        if len(self.clues) > 0:
            self.fill_clue()

        logger.debug("type of self is %s", type(self-__name__))
        logger.debug("type of self.grid is %s", type(self.grid).__name__)
        logger.debug("fill_grid returning grid %s", self.grid.text_grid())
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
        new_clues = self.clues.clone()
        return FillGrid(new_clues, new_grid, self.row, self.col, self.try_count, self.recurse_count, self.stop_after)
    
    def restore_from(self, deep_copy):
        self.grid = deep_copy.grid.deep_copy()
        self.clues = deep_copy.clues.clone()
        self.row = deep_copy.row
        self.col = deep_copy.col
        self.failure = deep_copy.failure
        # self.try_count = deep_copy.try_count

    def list_clues(self):
        for clue in self.clues:
            logger.debug("%2d%s %s", clue.clue_id, clue.direction, clue.actual_solution)



