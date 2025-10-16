import re
import copy
from abc import ABCMeta
from typing import List, Optional, Union
from dataclasses import dataclass


class ValidStatus(metaclass=ABCMeta):

    @property
    def name(self):
        return self.__class__.__name__


class Status:
    @dataclass
    class NUM(ValidStatus):
        value: int

    @dataclass
    class EMT(ValidStatus):
        value: str = " "

    @dataclass
    class UNK(ValidStatus):
        value: str = "?"

    @dataclass
    class FLG(ValidStatus):
        value: str = "*"


@dataclass
class Cell:
    status: Union[Status.NUM, Status.EMT, Status.UNK, Status.FLG]

    def as_flagged(self):
        self.status = Status.FLG()

    def as_empty(self):
        self.status = Status.EMT()

    def to_string(self) -> str:
        return f"[{self.status.value}]"

    @staticmethod
    def emt():
        return Cell(Status.EMT())

    @staticmethod
    def unk():
        return Cell(Status.UNK())

    @staticmethod
    def num(val: int):
        return Cell(Status.NUM(val))

    @classmethod
    def from_string(cls, value: str) -> 'Cell':
        if value.startswith(" "):
            return cls.from_string(value.strip())
        if Status.EMT().value in value:
            return Cell.emt()
        if Status.FLG().value in value:
            return Cell(Status.FLG())
        if Status.UNK().value in value:
            return Cell.unk()
        if re.match("\[[0-8]\]", value):
            num = int(value[1])
            return Cell.num(val=num)
        raise ValueError(f"Cannot infer cell-type from string: {value}")


@dataclass
class AwareCell:
    main: Cell
    neighbors: List[Cell]
    grid: 'Grid'


class Grid:

    def __init__(self, values: Optional[List[List[Cell]]] = None):
        self.values = values or [[]]

    @staticmethod
    def from_string(value: str) -> 'Grid':
        return Grid(
            values=[
                [
                    Cell.from_string(val)
                    for val in re.findall("\[.*?\]", row)
                ]
                for row in value.splitlines()
                if len(row.strip())
            ]
        )

    def to_string(self) -> str:
        return "\n".join(" ".join(cell.to_string() for cell in row) for row in self.values)

    def show(self):
        print(self.to_string())

    def get(self, i, j) -> Cell:
        return self.values[i][j]

    def get_aware(self, i, j, detached: bool = False):
        nrows, ncols = self.nrows(), self.ncols()
        # row params
        row_start = i if i - 1 <= 0 else i - 1
        row_final = i + 1 if i + 1 < nrows else i
        # col params
        col_start = j if j - 1 <= 0 else j - 1
        col_final = j + 1 if j + 1 < ncols else j
        # Get grid
        grid = Grid(copy.deepcopy(self.values)) if detached else self
        return AwareCell(
            main=grid.get(i, j),
            neighbors=[
                cell
                for ni in range(row_start, row_final + 1)
                for nj in range(col_start, col_final + 1)
                for cell in [grid.get(ni, nj)]
                if (ni, nj) != (i, j) and cell.status.name not in [
                    Status.EMT.__name__,
                    Status.NUM.__name__
                ]
            ],
            grid=grid
        )

    def get_nums(self, aware: bool = False) -> Union[List[Cell], List[AwareCell]]:
        return [
            self.get(i, j) if not aware else self.get_aware(i, j)
            for i in range(self.nrows())
            for j in range(self.ncols())
            for cell in [self.get(i, j)]
            if cell.status.name == Status.NUM.__name__
        ]

    def nrows(self) -> int:
        return len([row for row in self.values if row])

    def ncols(self) -> int:
        return 0 if not self.nrows() else {len(row) for row in self.values}.pop()
