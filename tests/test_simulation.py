import pytest

from models import Car, Command, Direction, Field, Position
from simulation import (
    CarResult,
    CollisionResult,
    SimulationEngine,
    _apply_command,
    _detect_collisions,
)


def make_car(name: str, x: int, y: int, direction: Direction, commands: str) -> Car:
    return Car(
        name=name,
        position=Position(x, y),
        direction=direction,
        commands=[Command(c) for c in commands],
    )


FIELD_10x10 = Field(10, 10)


# ---------------------------------------------------------------------------
# _apply_command
# ---------------------------------------------------------------------------

class TestApplyCommand:
    def test_turn_left_updates_direction_only(self):
        pos, direction = _apply_command(Command.L, Position(3, 3), Direction.N, FIELD_10x10)
        assert direction == Direction.W
        assert pos == Position(3, 3)

    def test_turn_right_updates_direction_only(self):
        pos, direction = _apply_command(Command.R, Position(3, 3), Direction.N, FIELD_10x10)
        assert direction == Direction.E
        assert pos == Position(3, 3)

    def test_forward_moves_in_facing_direction(self):
        pos, direction = _apply_command(Command.F, Position(3, 3), Direction.N, FIELD_10x10)
        assert pos == Position(3, 4)
        assert direction == Direction.N

    def test_forward_at_north_boundary_is_ignored(self):
        pos, direction = _apply_command(Command.F, Position(5, 9), Direction.N, FIELD_10x10)
        assert pos == Position(5, 9)

    def test_forward_at_south_boundary_is_ignored(self):
        pos, direction = _apply_command(Command.F, Position(5, 0), Direction.S, FIELD_10x10)
        assert pos == Position(5, 0)

    def test_forward_at_east_boundary_is_ignored(self):
        pos, direction = _apply_command(Command.F, Position(9, 5), Direction.E, FIELD_10x10)
        assert pos == Position(9, 5)

    def test_forward_at_west_boundary_is_ignored(self):
        pos, direction = _apply_command(Command.F, Position(0, 5), Direction.W, FIELD_10x10)
        assert pos == Position(0, 5)


# ---------------------------------------------------------------------------
# _detect_collisions
# ---------------------------------------------------------------------------

class TestDetectCollisions:
    def test_no_collision_when_cars_at_different_positions(self):
        positions = {'A': Position(1, 1), 'B': Position(2, 2)}
        result = _detect_collisions(positions, {'A', 'B'}, step=1)
        assert result == {}

    def test_collision_detected_when_two_cars_share_position(self):
        positions = {'A': Position(5, 4), 'B': Position(5, 4)}
        result = _detect_collisions(positions, {'A', 'B'}, step=7)
        assert 'A' in result
        assert 'B' in result
        assert result['A'].step == 7
        assert result['A'].position == Position(5, 4)
        assert result['A'].other_car_name == 'B'
        assert result['B'].other_car_name == 'A'

    def test_only_active_cars_are_checked(self):
        positions = {'A': Position(5, 4), 'B': Position(5, 4), 'C': Position(5, 4)}
        # C is already collided so excluded from active set
        result = _detect_collisions(positions, {'A', 'B'}, step=3)
        assert 'C' not in result


# SimulationEngine
class TestSimulationEngineSingleCar:
    '''Spec scenario 1: single car, no collision.'''

    def test_spec_example_final_position(self):
        car = make_car('A', 1, 2, Direction.N, 'FFRFFFFRRL')
        results = SimulationEngine(FIELD_10x10, [car]).run()
        assert len(results) == 1
        result = results[0]
        assert result.collision is None
        assert result.car.position == Position(5, 4)
        assert result.car.direction == Direction.S

    def test_car_with_no_commands_stays_put(self):
        car = make_car('A', 3, 3, Direction.N, '')
        results = SimulationEngine(FIELD_10x10, [car]).run()
        assert results[0].car.position == Position(3, 3)

    def test_boundary_commands_are_ignored(self):
        # Start at (0,0) facing South — F should be ignored
        car = make_car('A', 0, 0, Direction.S, 'FFF')
        results = SimulationEngine(FIELD_10x10, [car]).run()
        assert results[0].car.position == Position(0, 0)


class TestSimulationEngineMultipleCars:
    '''Spec scenario 2: two cars with collision.'''

    def test_spec_example_collision_at_step_7(self):
        car_a = make_car('A', 1, 2, Direction.N, 'FFRFFFFRRL')
        car_b = make_car('B', 7, 8, Direction.W, 'FFLFFFFFFF')
        results = SimulationEngine(FIELD_10x10, [car_a, car_b]).run()

        result_a, result_b = results[0], results[1]

        assert result_a.collision is not None
        assert result_a.collision.other_car_name == 'B'
        assert result_a.collision.position == Position(5, 4)
        assert result_a.collision.step == 7

        assert result_b.collision is not None
        assert result_b.collision.other_car_name == 'A'
        assert result_b.collision.position == Position(5, 4)
        assert result_b.collision.step == 7

    def test_cars_moving_in_opposite_directions_do_not_collide(self):
        # A starts at (5,5) facing N, B starts at (5,6) facing S — they swap positions
        # each step and never occupy the same cell at the end of a step.
        car_a = make_car('A', 5, 5, Direction.N, 'FFFF')
        car_b = make_car('B', 5, 6, Direction.S, 'FFFF')
        results = SimulationEngine(FIELD_10x10, [car_a, car_b]).run()
        # After step 1, A moves to (5,6) and B moves to (5,5) — no same position.
        # After step 2, A moves to (5,7) and B moves to (5,4) — no same position.
        assert results[0].collision is None
        assert results[1].collision is None

    def test_same_start_position_not_detected_as_collision(self):
        # Known limitation: two cars placed on the same cell are never flagged as collided
        # because collision detection only runs after commands are applied.
        car_a = make_car('A', 5, 5, Direction.N, '')
        car_b = make_car('B', 5, 5, Direction.E, '')
        results = SimulationEngine(FIELD_10x10, [car_a, car_b]).run()
        assert results[0].collision is None
        assert results[1].collision is None

    def test_swap_collision_not_detected(self):
        # Known limitation: two cars exchanging cells in a single step are not detected
        # as colliding because the check is based on final positions after the step.
        car_a = make_car('A', 4, 0, Direction.E, 'F')
        car_b = make_car('B', 5, 0, Direction.W, 'F')
        results = SimulationEngine(FIELD_10x10, [car_a, car_b]).run()
        # After step 1: A is at (5,0), B is at (4,0) — no shared cell, so no collision.
        assert results[0].collision is None
        assert results[1].collision is None

    def test_shorter_command_list_car_stays_put_after_exhaustion(self):
        # Car A has 1 command; car B has 5. A should hold position after step 1.
        car_a = make_car('A', 0, 0, Direction.N, 'F')
        car_b = make_car('B', 9, 9, Direction.S, 'FFFFF')
        results = SimulationEngine(FIELD_10x10, [car_a, car_b]).run()
        result_a = next(r for r in results if r.car.name == 'A')
        assert result_a.car.position == Position(0, 1)
        assert result_a.collision is None

    def test_no_collision_returns_final_positions(self):
        car_a = make_car('A', 0, 0, Direction.E, 'FF')
        car_b = make_car('B', 9, 9, Direction.W, 'FF')
        results = SimulationEngine(FIELD_10x10, [car_a, car_b]).run()
        assert results[0].collision is None
        assert results[1].collision is None
        assert results[0].car.position == Position(2, 0)
        assert results[1].car.position == Position(7, 9)

