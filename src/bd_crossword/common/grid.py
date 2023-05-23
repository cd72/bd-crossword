import logging

logger = logging.getLogger(__name__)



class CrosswordGrid:
    BLANK = '_'
    FILL = '#'

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[CrosswordGrid.BLANK for _ in range(cols)] for _ in range(rows)]

    def is_valid_position(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_empty(self, row, col):
        return self.grid[row][col] == CrosswordGrid.BLANK

    def is_blocked(self, row, col):
        return self.grid[row][col] == CrosswordGrid.FILL

    def set_letter(self, row, col, letter):
        self.grid[row][col] = letter

    def can_write_across(self, row, col, word):
        if col + len(word) > self.cols:
            return False

        for i, letter in enumerate(word):
            if self.is_blocked(row, col + i):
                return False
            if not self.is_empty(row, col + i):
                if self.grid[row][col + i] != letter:
                    return False

        return True
    
    def can_write_down(self, row, col, word):
        if row + len(word) > self.rows:
            return False

        for i, letter in enumerate(word):
            if self.is_blocked(row + i, col):
                return False
            if not self.is_empty(row + i, col):
                if self.grid[row + i][col] != letter:
                    return False

        return True

    def get_row(self, row):
        return self.grid[row]
    
    def get_col(self, col):
        return [row[col] for row in self.grid]

    def set_blocked(self, row, col):
        if self.is_valid_position(row, col):
            self.grid[row][col] = CrosswordGrid.FILL

    def write_across(self, row, col, word):
        if self.can_write_across(row, col, word) == False:
            return False

        for i, letter in enumerate(word):
            self.set_letter(row, col + i, letter)

        return True

    def write_down(self, row, col, word):
        if self.can_write_down(row, col, word) == False:
            return False
        
        for i, letter in enumerate(word):
            self.set_letter(row + i, col, letter)

        return True
    
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