import pytest
from bd_crossword.common.crossword_grid import CrosswordGrid


@pytest.fixture
def crossword_grid():
    grid = CrosswordGrid(5, 5)
    yield grid
    grid.display()


def test_set_letter(crossword_grid):
    crossword_grid.set_letter(1, 1, "P")
    assert crossword_grid.grid[1][1] == "P"


def test_set_blocked(crossword_grid):
    crossword_grid.set_blocked(2, 2)
    assert crossword_grid.grid[2][2] == "#"


def test_write_across(crossword_grid):
    assert crossword_grid.write_across(2, 2, "PYT") == True
    assert crossword_grid.grid[2][2:5] == ["P", "Y", "T"]


def test_write_across_fail(crossword_grid):
    assert crossword_grid.write_across(2, 2, "PYTHON") == False


def test_write_down(crossword_grid):
    assert crossword_grid.write_down(1, 2, "CODE") == True
    assert crossword_grid.get_col(2)[1:] == list("CODE")


def test_write_across_pass(crossword_grid):
    crossword_grid.set_letter(1, 0, "S")
    crossword_grid.set_letter(1, 1, "N")
    crossword_grid.set_letter(1, 2, "A")

    assert crossword_grid.write_across(1, 0, "SNAKE") == True


def test_can_write_across_fail(crossword_grid):
    crossword_grid.set_letter(1, 0, "S")
    crossword_grid.set_letter(1, 1, "N")
    crossword_grid.set_letter(1, 2, "A")

    assert crossword_grid.can_write_across(1, 0, "SKATE") == False


def test_can_write_down_fail(crossword_grid):
    crossword_grid.write_across(1, 0, "SNAKE")
    assert crossword_grid.can_write_down(0, 1, "SCATE") == False


def test_can_write_down_fail2(crossword_grid):
    crossword_grid.write_across(1, 0, "SNAKE")
    assert crossword_grid.can_write_down(0, 1, "SNAKE") == True


def test_fill_squares(crossword_grid):
    crossword_grid.write_across(1, 0, "SNAKE")
    crossword_grid.set_fill_squares()
    assert crossword_grid.get_col(1) == ["#", "N", "#", "#", "#"]


def test_remove_solutions(crossword_grid):
    crossword_grid.write_across(1, 0, "SNAKE")
    crossword_grid.set_fill_squares()
    crossword_grid.remove_solutions()
    assert crossword_grid.get_col(1) == ["#", "_", "#", "#", "#"]
