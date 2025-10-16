import itertools
import logging
import time
import copy
from typing import List, Optional

from .board import Grid, Status

logger = logging.getLogger(__name__)


def is_valid(grid: Grid, hint_i: int, hint_j: int) -> bool:
    hint = grid.get_aware(i=hint_i, j=hint_j, detached=False)
    n_flags_max = hint.main.status.value
    n_flags_current = len([cell for cell in hint.neighbors if cell.status.name == Status.FLG.__name__])
    return n_flags_current <= n_flags_max


def unmark(grid: Grid, hint_i: int,  hint_j: int):
    hint = grid.get_aware(i=hint_i, j=hint_j, detached=False)
    for cell in hint.neighbors:
        if cell.status.name in [Status.FLG.__name__, Status.NUM.__name__]:
            continue
        cell.as_empty()


def mark(grid: Grid, hint_i: int, hint_j: int) -> List[Grid]:
    hint = grid.get_aware(i=hint_i, j=hint_j, detached=False)
    n_neighbors = len(hint.neighbors)
    possibilities = itertools.combinations(range(n_neighbors), hint.main.status.value)
    grids = []
    for possibility in possibilities:
        hint = grid.get_aware(i=hint_i, j=hint_j, detached=True)
        flagged = 0
        for position, cell in enumerate(hint.neighbors):
            if position in possibility:
                cell.as_flagged()
            flagged += 1 if cell.status.name == Status.FLG.__name__ else 0

        if flagged <= hint.main.status.value:
            unmark(hint.grid, hint_i=hint_i, hint_j=hint_j)
            grids.append(hint.grid)
    return grids


class Solver:

    def __init__(self, grid: Grid):
        self.initial_grid = copy.deepcopy(grid)
        self.states = [grid]
        self.final_state = None
        self.hints = [
            (i, j)
            for i in range(grid.nrows())
            for j in range(grid.ncols())
            for cell in [grid.get(i, j)]
            if cell.status.name == Status.NUM.__name__
        ]

    def reduce(self, i: int, j: int):
        self.states = [grid for grid in self.states if is_valid(grid, hint_i=i, hint_j=j)]

    def expand(self, i: int, j: int):
        self.states = [
            grid
            for prev_grid in self.states
            for grid in mark(prev_grid, hint_i=i, hint_j=j)
        ]

    def iterate(self):
        for i, j in self.hints:
            self.reduce(i, j)
            self.expand(i, j)

    def finished(self) -> bool:
        num_states = len(self.states)
        if num_states > 1:
            return False
        grid = self.states[0]
        return all(
            [
                cell.status.name != Status.UNK.__name__
                for row in grid.values
                for cell in row
            ]
        )

    def run(self, timeout: Optional[int] = None):
        count = 0
        start = time.time()
        timeout_reached = False
        while not self.finished():
            logger.info(f"Iteration {count} with {len(self.states)} states.")
            duration = time.time() - start
            if timeout is not None and duration > timeout:
                logger.error(f"Timeout reached: {duration} > {timeout}")
                timeout_reached = True
                break
            self.iterate()
            count += 1
        self.final_state = self.states[0] if not timeout_reached else None
