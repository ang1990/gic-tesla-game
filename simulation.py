from __future__ import annotations

from dataclasses import dataclass

from models import Car, Command, Direction, Field, Position


@dataclass
class CollisionResult:
    car_name: str
    other_car_name: str
    position: Position
    step: int



@dataclass
class CarResult:
    car: Car
    collision: CollisionResult | None = None


def _apply_command(
    cmd: Command,
    position: Position,
    direction: Direction,
    field: Field,
) -> tuple[Position, Direction]:
    if cmd == Command.L:
        return position, direction.turn_left()
    if cmd == Command.R:
        return position, direction.turn_right()
    # Command.F
    dx, dy = direction.delta()
    new_pos = Position(position.x + dx, position.y + dy)
    if field.contains(new_pos):
        return new_pos, direction
    return position, direction


def _detect_collisions(
    positions: dict[str, Position],
    active_cars: set[str],
    step: int,
) -> dict[str, CollisionResult]:
    collisions: dict[str, CollisionResult] = {}
    position_occupants: dict[tuple[int, int], list[str]] = {}

    for name in sorted(active_cars):
        key = (positions[name].x, positions[name].y)
        position_occupants.setdefault(key, []).append(name)

    for pos_key, occupants in position_occupants.items():
        if len(occupants) > 1:
            pos = Position(pos_key[0], pos_key[1])
            for name in occupants:
                others = [n for n in occupants if n != name]
                collisions[name] = CollisionResult(
                    car_name=name,
                    other_car_name=others[0],
                    position=pos,
                    step=step,
                )

    return collisions


class SimulationEngine:
    def __init__(self, field: Field, cars: list[Car]) -> None:
        self.field = field
        self.cars = cars

    def run(self) -> list[CarResult]:
        positions = {car.name: Position(car.position.x, car.position.y) for car in self.cars}
        directions = {car.name: car.direction for car in self.cars}
        command_indices = {car.name: 0 for car in self.cars}
        all_collisions: dict[str, CollisionResult] = {}

        max_steps = max((len(car.commands) for car in self.cars), default=0)

        for step in range(1, max_steps + 1):
            active_cars = {car.name for car in self.cars if car.name not in all_collisions}

            for car in self.cars:
                if car.name not in active_cars:
                    continue
                idx = command_indices[car.name]
                if idx >= len(car.commands):
                    continue
                command_indices[car.name] += 1
                new_pos, new_dir = _apply_command(
                    car.commands[idx], positions[car.name], directions[car.name], self.field
                )
                positions[car.name] = new_pos
                directions[car.name] = new_dir

            step_collisions = _detect_collisions(positions, active_cars, step)
            all_collisions.update(step_collisions)

        return [
            CarResult(
                car=Car(
                    name=car.name,
                    position=positions[car.name],
                    direction=directions[car.name],
                    commands=car.commands,
                ),
                collision=all_collisions.get(car.name),
            )
            for car in self.cars
        ]
