import pytest

from models import Car, Command, Direction, Field, Position


# ---------------------------------------------------------------------------
# Direction
# ---------------------------------------------------------------------------

class TestDirectionTurnLeft:
    def test_north_turns_to_west(self):
        assert Direction.N.turn_left() == Direction.W

    def test_west_turns_to_south(self):
        assert Direction.W.turn_left() == Direction.S

    def test_south_turns_to_east(self):
        assert Direction.S.turn_left() == Direction.E

    def test_east_turns_to_north(self):
        assert Direction.E.turn_left() == Direction.N

    def test_full_cycle_returns_to_start(self):
        direction = Direction.N
        for _ in range(4):
            direction = direction.turn_left()
        assert direction == Direction.N


class TestDirectionTurnRight:
    def test_north_turns_to_east(self):
        assert Direction.N.turn_right() == Direction.E

    def test_east_turns_to_south(self):
        assert Direction.E.turn_right() == Direction.S

    def test_south_turns_to_west(self):
        assert Direction.S.turn_right() == Direction.W

    def test_west_turns_to_north(self):
        assert Direction.W.turn_right() == Direction.N

    def test_full_cycle_returns_to_start(self):
        direction = Direction.N
        for _ in range(4):
            direction = direction.turn_right()
        assert direction == Direction.N


class TestDirectionDelta:
    def test_north_moves_positive_y(self):
        assert Direction.N.delta() == (0, 1)

    def test_south_moves_negative_y(self):
        assert Direction.S.delta() == (0, -1)

    def test_east_moves_positive_x(self):
        assert Direction.E.delta() == (1, 0)

    def test_west_moves_negative_x(self):
        assert Direction.W.delta() == (-1, 0)


# ---------------------------------------------------------------------------
# Position
# ---------------------------------------------------------------------------

class TestPosition:
    def test_equal_positions(self):
        assert Position(3, 4) == Position(3, 4)

    def test_unequal_positions(self):
        assert Position(3, 4) != Position(3, 5)

    def test_positions_usable_as_dict_keys(self):
        mapping = {Position(1, 2): 'a', Position(3, 4): 'b'}
        assert mapping[Position(1, 2)] == 'a'

    def test_equal_positions_have_same_hash(self):
        assert hash(Position(5, 5)) == hash(Position(5, 5))

    def test_str_format(self):
        assert str(Position(7, 3)) == '(7,3)'

    def test_str_zero_origin(self):
        assert str(Position(0, 0)) == '(0,0)'


# ---------------------------------------------------------------------------
# Car
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Field
# ---------------------------------------------------------------------------

class TestFieldContains:
    def setup_method(self):
        self.field = Field(10, 10)

    def test_origin_is_inside(self):
        assert self.field.contains(Position(0, 0))

    def test_top_right_corner_is_inside(self):
        assert self.field.contains(Position(9, 9))

    def test_negative_x_is_outside(self):
        assert not self.field.contains(Position(-1, 5))

    def test_negative_y_is_outside(self):
        assert not self.field.contains(Position(5, -1))

    def test_x_equal_to_width_is_outside(self):
        assert not self.field.contains(Position(10, 5))

    def test_y_equal_to_height_is_outside(self):
        assert not self.field.contains(Position(5, 10))

    def test_str_format(self):
        assert str(Field(10, 10)) == '10 x 10'
