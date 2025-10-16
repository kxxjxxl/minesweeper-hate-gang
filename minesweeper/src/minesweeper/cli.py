import argparse


from .board import Grid
from .solver import Solver

DEFAULT_GRID = """
[3] [?] [2] [?]
[?] [?] [ ] [?]
"""


class CLI:

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--timeout", type=int, default=100)
        parser.add_argument("--grid", type=str, default=DEFAULT_GRID)
        args = parser.parse_args()
        grid = Grid.from_string(args.grid)
        solver_instance = Solver(grid=grid)
        solver_instance.run(timeout=args.timeout)
        if solver_instance.finished():
            solver_instance.final_state.show()
