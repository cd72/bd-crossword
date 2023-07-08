import logging

logger = logging.getLogger(__name__)

class CrosswordGrid:
    BLANK = '_'
    FILL = '#'

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[CrosswordGrid.BLANK for _ in range(cols)] for _ in range(rows)]
        self.clue_ids = [[None for _ in range(cols)] for _ in range(rows)]

    def above_is_alpha(self, row, col):
        return False if row == 0 else self.grid[row - 1][col].isalpha()
    
    def below_is_alpha(self, row, col):
        return False if row == self.rows - 1 else self.grid[row + 1][col].isalpha()
    
    def left_is_alpha(self, row, col):
        return False if col == 0 else self.grid[row][col - 1].isalpha()
    
    def right_is_alpha(self, row, col):
        return False if col == self.cols - 1 else self.grid[row][col + 1].isalpha()

    def deep_copy(self):
        new_grid = CrosswordGrid(self.rows, self.cols)
        new_grid.grid = [row[:] for row in self.grid]
        new_grid.clue_ids = [row[:] for row in self.clue_ids]
        return new_grid

    def is_valid_position(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_empty(self, row, col):
        return self.grid[row][col] == CrosswordGrid.BLANK

    def is_blocked(self, row, col):
        return self.grid[row][col] == CrosswordGrid.FILL

    def set_letter(self, row, col, letter):
        self.grid[row][col] = letter

    def can_write_across(self, row, col, word, clue_id):
        above_contiguous = 0
        below_contiguous = 0
    
        if self.clue_ids[row][col] is not None and self.clue_ids[row][col] != clue_id:
            return False

        if col + len(word) > self.cols:
            return False
        
        if self.left_is_alpha(row, col):
            return False
        
        if self.right_is_alpha(row, col + len(word) - 1):
            return False

        for i, letter in enumerate(word):
            if self.is_blocked(row, col + i):
                return False
            if not self.is_empty(row, col + i):
                if self.grid[row][col + i] != letter:
                    return False
                
            if self.above_is_alpha(row, col + i):
                above_contiguous += 1
            else:
                above_contiguous = 0

            if self.below_is_alpha(row, col + i):
                below_contiguous += 1
            else:
                below_contiguous = 0

            if above_contiguous > 2 or below_contiguous > 2:
                logger.debug("above_contiguous is %s, below_contiguous is %s", above_contiguous, below_contiguous)
                return False

        return True
    
    def can_write_down(self, row, col, word, clue_id):
        left_contiguous = 0
        right_contiguous = 0
    
        if self.clue_ids[row][col] is not None and self.clue_ids[row][col] != clue_id:
            return False

        if row + len(word) > self.rows:
            return False
        
        if self.above_is_alpha(row, col):
            return False
        
        if self.below_is_alpha(row + len(word) - 1, col):
            return False

        for i, letter in enumerate(word):
            if self.is_blocked(row + i, col):
                return False
            if not self.is_empty(row + i, col):
                if self.grid[row + i][col] != letter:
                    return False
                
            if self.left_is_alpha(row + i, col):
                left_contiguous += 1
            else:
                left_contiguous = 0

            if self.right_is_alpha(row + i, col):
                right_contiguous += 1
            else:
                right_contiguous = 0

            if left_contiguous > 2 or right_contiguous > 2:
                logger.debug("left_contiguous is %s, right_contiguous is %s", left_contiguous, right_contiguous)
                return False
            
        return True
    
    def can_write_direction(self, row, col, word, direction, clue_id):
        if direction == 'a':
            return self.can_write_across(row, col, word, clue_id)
        elif direction == 'd':
            return self.can_write_down(row, col, word, clue_id)
        else:
            raise ValueError(f"Unknown direction {direction}")

    def get_row(self, row):
        return self.grid[row]
    
    def get_col(self, col):
        return [row[col] for row in self.grid]
    
    def get_row_as_string(self, row):
        return ''.join(self.get_row(row))
    
    def get_col_as_string(self, col):      
        return ''.join(self.get_col(col))

    def set_blocked(self, row, col):
        if self.is_valid_position(row, col):
            self.grid[row][col] = CrosswordGrid.FILL

    def write_across(self, row:int, col:int, word:str, clue_id:int):
        self.clue_ids[row][col] = clue_id
        if self.can_write_across(row, col, word, clue_id) == False:
            return False

        for i, letter in enumerate(word):
            self.set_letter(row, col + i, letter)

        if col + len(word) < self.cols:
            self.set_blocked(row, col + len(word))

        if col > 0:
            self.set_blocked(row, col - 1)

        return True

    def write_down(self, row:int, col:int, word:str, clue_id:int):
        self.clue_ids[row][col] = clue_id
        if self.can_write_down(row, col, word, clue_id) == False:
            return False
        
        for i, letter in enumerate(word):
            self.set_letter(row + i, col, letter)

        if row > 0:
            self.set_blocked(row - 1, col)

        if row + len(word) < self.rows:
            self.set_blocked(row + len(word), col)

        return True
    
    def write_direction(self, row, col, word, direction, clue_id):
        if direction == 'a':
            return self.write_across(row, col, word, clue_id)
        elif direction == 'd':
            return self.write_down(row, col, word, clue_id)
        else:
            raise ValueError(f"Unknown direction {direction}")
    
    def write_tail_direction(self, row, col, word, direction, clue_id):
        if direction == 'a':
            col = (col - len(word)) + 1
            if col < 0:
                raise ValueError(f"Cannot write across {word} from row {row} col {col}")
            return self.write_across(row, col, word, clue_id)
        elif direction == 'd':
            row = (row - len(word)) + 1
            if row < 0:
                raise ValueError(f"Cannot write down {word} from row {row} col {col}")
            return self.write_down(row, col, word, clue_id)
        else:
            raise ValueError(f"Unknown direction {direction}")

    def set_fill_squares(self):
        # convert all the empty squares to fill squares in the entire grid
        for row in range(self.rows):
            for col in range(self.cols):
                if self.is_empty(row, col):
                    self.set_blocked(row, col)

    def remove_solutions(self):
        """Remove all the letters from the grid leaving the fill squares intact"""
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.is_blocked(row, col):
                    self.set_letter(row, col, CrosswordGrid.BLANK)


    def display(self):
        print()
        for row in self.grid:
            print('|'.join(row))

    def text_grid(self):
        grid_text = '\n'
        for row in self.grid:
            grid_text += '|'.join(row)
            grid_text += '\n'
        grid_text += '\n'
        return grid_text