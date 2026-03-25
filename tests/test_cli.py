'''
CLI tests simulate stdin by patching builtins.input with a side_effect list.
stdout is captured via pytest's capsys fixture.
'''
from unittest.mock import patch

import pytest

import cli
from models import Car, Command, Direction, Field, Position
from simulation import CarResult, CollisionResult


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

class TestFormatCar:
    def test_format_includes_name_position_direction_commands(self):
        car = Car(name='A', position=Position(1, 2), direction=Direction.N,
                  commands=[Command('F'), Command('F'), Command('R')])
        assert cli._format_car(car) == '- A, (1,2) N, FFR'

    def test_format_empty_commands(self):
        car = Car(name='Z', position=Position(0, 0), direction=Direction.S, commands=[])
        assert cli._format_car(car) == '- Z, (0,0) S, '


class TestFormatResult:
    def test_no_collision_formats_final_position(self):
        car = Car(name='A', position=Position(5, 4), direction=Direction.S, commands=[])
        result = CarResult(car=car, collision=None)
        assert cli._format_result(result) == '- A, (5,4) S'

    def test_collision_formats_collision_details(self):
        car = Car(name='A', position=Position(5, 4), direction=Direction.S, commands=[])
        collision = CollisionResult('A', 'B', Position(5, 4), step=7)
        result = CarResult(car=car, collision=collision)
        assert cli._format_result(result) == '- A, collides with B at (5,4) at step 7'


def run_cli_with_inputs(*inputs: str, capsys) -> str:
    '''Drive main() with the given sequence of input strings and return captured stdout.'''
    with patch('builtins.input', side_effect=list(inputs)):
        cli.main()
    return capsys.readouterr().out


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

class TestPromptField:
    def test_valid_input_returns_field(self):
        with patch('builtins.input', side_effect=['10 10']):
            field = cli._prompt_field()
        assert field == Field(10, 10)

    def test_invalid_then_valid_input_retries(self, capsys):
        with patch('builtins.input', side_effect=['abc', '5 5']):
            field = cli._prompt_field()
        assert field == Field(5, 5)
        assert 'Invalid' in capsys.readouterr().out

    def test_zero_dimensions_rejected(self, capsys):
        with patch('builtins.input', side_effect=['0 10', '10 10']):
            field = cli._prompt_field()
        assert field.width == 10


class TestPromptCarName:
    def test_valid_name_accepted(self):
        with patch('builtins.input', return_value='A'):
            name = cli._prompt_car_name(set())
        assert name == 'A'

    def test_duplicate_name_rejected_then_accepted(self, capsys):
        with patch('builtins.input', side_effect=['A', 'B']):
            name = cli._prompt_car_name({'A'})
        assert name == 'B'
        assert 'already exists' in capsys.readouterr().out

    def test_empty_name_rejected(self, capsys):
        with patch('builtins.input', side_effect=['', 'C']):
            name = cli._prompt_car_name(set())
        assert name == 'C'
        assert 'empty' in capsys.readouterr().out


class TestPromptCarPosition:
    def test_valid_position_accepted(self):
        field = Field(10, 10)
        with patch('builtins.input', return_value='1 2 N'):
            pos, direction = cli._prompt_car_position('A', field, [])
        assert pos == Position(1, 2)
        assert direction == Direction.N

    def test_out_of_bounds_rejected_then_accepted(self, capsys):
        field = Field(10, 10)
        with patch('builtins.input', side_effect=['15 15 N', '1 1 S']):
            pos, direction = cli._prompt_car_position('A', field, [])
        assert pos == Position(1, 1)
        assert 'outside' in capsys.readouterr().out

    def test_invalid_direction_rejected(self, capsys):
        field = Field(10, 10)
        with patch('builtins.input', side_effect=['1 1 X', '1 1 N']):
            pos, direction = cli._prompt_car_position('A', field, [])
        assert direction == Direction.N
        assert 'Invalid direction' in capsys.readouterr().out

    def test_occupied_position_rejected_then_accepted(self, capsys):
        field = Field(10, 10)
        existing = Car(name='X', position=Position(1, 1), direction=Direction.N, commands=[])
        with patch('builtins.input', side_effect=['1 1 N', '2 2 N']):
            pos, direction = cli._prompt_car_position('A', field, [existing])
        assert pos == Position(2, 2)
        assert 'occupied' in capsys.readouterr().out


class TestPromptCommands:
    def test_valid_commands_accepted(self):
        with patch('builtins.input', return_value='FFRLL'):
            commands = cli._prompt_commands('A')
        assert [c.value for c in commands] == ['F', 'F', 'R', 'L', 'L']

    def test_invalid_character_rejected_then_accepted(self, capsys):
        with patch('builtins.input', side_effect=['FXYZ', 'FF']):
            commands = cli._prompt_commands('A')
        assert [c.value for c in commands] == ['F', 'F']
        assert 'Invalid' in capsys.readouterr().out

    def test_lowercase_commands_accepted(self):
        with patch('builtins.input', return_value='ffrll'):
            commands = cli._prompt_commands('A')
        assert [c.value for c in commands] == ['F', 'F', 'R', 'L', 'L']


# Integration Tests
class TestCLIIntegration:
    def test_scenario_1_single_car_no_collision(self, capsys):
        output = run_cli_with_inputs(
            '10 10',    # field
            '1',            # add car
            'A',            # name
            '1 2 N',        # position
            'FFRFFFFRRL',   # commands
            '2',            # run simulation
            '2',            # exit
            capsys=capsys,
        )
        assert 'You have created a field of 10 x 10' in output
        assert '- A, (1,2) N, FFRFFFFRRL' in output
        assert '- A, (5,4) S' in output
        assert 'Thank you for running the simulation. Goodbye!' in output

    def test_scenario_2_two_cars_collision(self, capsys):
        output = run_cli_with_inputs(
            '10 10',        # field
            '1',            # add car A
            'A',
            '1 2 N',
            'FFRFFFFRRL',
            '1',            # add car B
            'B',
            '7 8 W',
            'FFLFFFFFFF',
            '2',            # run simulation
            '2',            # exit
            capsys=capsys,
        )
        assert '- A, collides with B at (5,4) at step 7' in output
        assert '- B, collides with A at (5,4) at step 7' in output

    def test_start_over_restarts_session(self, capsys):
        output = run_cli_with_inputs(
            # First session
            '10 10',
            '1',
            'A',
            '0 0 N',
            'F',
            '2',
            '1',            # start over
            # Second session
            '5 5',
            '1',
            'B',
            '2 2 E',
            'FF',
            '2',
            '2',            # exit
            capsys=capsys,
        )
        # Both sessions' welcome messages should appear
        assert output.count('Welcome to Auto Driving Car Simulation!') == 2
        assert 'You have created a field of 5 x 5' in output

    def test_invalid_menu_choice_then_valid(self, capsys):
        output = run_cli_with_inputs(
            '10 10',
            '9',            # invalid choice
            '1',            # add car
            'A',
            '0 0 N',
            'F',
            '2',            # run
            '2',            # exit
            capsys=capsys,
        )
        assert 'Invalid choice' in output
        assert '- A, (0,1) N' in output

    def test_run_simulation_without_cars_shows_error(self, capsys):
        output = run_cli_with_inputs(
            '10 10',
            '2',            # run simulation with no cars
            '1',            # then add a car
            'A',
            '0 0 N',
            'F',
            '2',            # run
            '2',            # exit
            capsys=capsys,
        )
        assert 'No cars have been added' in output
        assert '- A, (0,1) N' in output
