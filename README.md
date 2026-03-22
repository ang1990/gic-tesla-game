# Auto Driving Car Simulation

A command-line simulation of autonomous cars moving on a rectangular grid, with collision detection.

## Requirements

- Python 3.14+
- pytest (for running tests)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Simulation

```bash
python main.py
```

You will be prompted to define a field, add one or more cars, and run the simulation.

### Example Session

```
Welcome to Auto Driving Car Simulation!

Please enter the width and height of the simulation field in x y format:
10 10

You have created a field of 10 x 10.

Please choose from the following options:
[1] Add a car to field
[2] Run simulation
1

Please enter the name of the car:
A

Please enter initial position of car A in x y Direction format:
1 2 N

Please enter the commands for car A:
FFRFFFFRRL

Your current list of cars are:
- A, (1,2) N, FFRFFFFRRL

Please choose from the following options:
[1] Add a car to field
[2] Run simulation
2

Your current list of cars are:
- A, (1,2) N, FFRFFFFRRL

After simulation, the result is:
- A, (5,4) S
```

## Commands

| Command | Effect |
|---------|--------|
| `F` | Move forward one grid point |
| `L` | Rotate 90° to the left |
| `R` | Rotate 90° to the right |

- A move that would take a car outside the field boundary is ignored.
- When multiple cars are present, one command per car is processed per step.
- Cars that collide stop moving and report the collision step and position.

## Project Structure

```
gic-tesla-game/
├── main.py           # Entry point
├── models.py         # Direction, Command, Position, Car, Field
├── simulation.py     # SimulationEngine, collision detection
├── cli.py            # Interactive CLI and input validation
├── requirements.txt
└── tests/
    ├── conftest.py
    ├── test_models.py
    ├── test_simulation.py
    └── test_cli.py
```

## Running Tests

```bash
pytest tests/ -v
```
