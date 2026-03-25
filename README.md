# Auto Driving Car Simulation

A command-line simulation of autonomous cars moving on a rectangular grid, with rudimentary collision detection.

## Requirements

- Python 3.10+
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

## Collision Detection

After every step, the simulation checks whether any two active cars occupy the same grid cell. If they do, both are marked as collided, stop processing further commands, and report the step and position at which the collision occurred.

### Known Limitation: Swap Collisions

The current implementation only detects collisions based on final positions after each step. It does not detect cars that pass through each other during a step.

Consider two cars on the same axis moving toward each other:

```
Step N:   A is at (4,0) facing East, B is at (5,0) facing West
Step N+1: A moves to (5,0), B moves to (4,0)
```

In reality these cars would collide as they cross the same point between cells. However the current implementation moves both cars to their new positions and then checks — finding no two cars at the same cell, it records no collision.

### Possible Future Work

- **Swap detection:** Before applying movement, check whether any two cars are about to exchange positions along the same axis. If so, treat it as a collision at the midpoint or at the step boundary.
- **Multi-car pileups:** When three or more cars converge on the same cell, each car currently records only one partner. Future work could report all cars involved in a pileup.
- **Simultaneous arrival from different directions:** Two cars could arrive at the same cell from non-opposing directions (e.g. one moving North and one moving East). This is already detected, but the collision partner reported is determined by list order rather than any meaningful priority.
- **Starting position validation:** Cars are not currently prevented from being placed on the same starting cell, which would produce an immediate collision at step 1 that is never reported.

## Running Tests

```bash
pytest tests/ -v
```
