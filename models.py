from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    N = 'N'
    E = 'E'
    S = 'S'
    W = 'W'

    def turn_left(self) -> Direction:
        cycle = [Direction.N, Direction.W, Direction.S, Direction.E]
        return cycle[(cycle.index(self) + 1) % len(cycle)]

    def turn_right(self) -> Direction:
        cycle = [Direction.N, Direction.E, Direction.S, Direction.W]
        return cycle[(cycle.index(self) + 1) % len(cycle)]

    def delta(self) -> tuple[int, int]:
        return {
            Direction.N: (0, 1),
            Direction.S: (0, -1),
            Direction.E: (1, 0),
            Direction.W: (-1, 0),
        }[self]


class Command(Enum):
    L = 'L'
    R = 'R'
    F = 'F'


@dataclass
class Position:
    x: int
    y: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __str__(self) -> str:
        return f'({self.x},{self.y})'


@dataclass
class Car:
    name: str
    position: Position
    direction: Direction
    commands: list[Command]



@dataclass
class Field:
    width: int
    height: int

    def contains(self, position: Position) -> bool:
        return 0 <= position.x < self.width and 0 <= position.y < self.height

    def __str__(self) -> str:
        return f'{self.width} x {self.height}'
