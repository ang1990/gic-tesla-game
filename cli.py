from __future__ import annotations

from models import Car, Command, Direction, Field, Position
from simulation import CarResult, SimulationEngine


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def _prompt(message: str) -> str:
    return input(message).strip()


def _prompt_field() -> Field:
    while True:
        raw = _prompt("Please enter the width and height of the simulation field in x y format:\n")
        parts = raw.split()
        if len(parts) == 2:
            try:
                width, height = int(parts[0]), int(parts[1])
                if width > 0 and height > 0:
                    return Field(width, height)
            except ValueError:
                pass
        print("Invalid input. Please enter two positive integers (e.g. 10 10).")


def _prompt_car_name(existing_names: set[str]) -> str:
    while True:
        name = _prompt("Please enter the name of the car:\n")
        if not name:
            print("Name cannot be empty.")
        elif name in existing_names:
            print(f"A car named '{name}' already exists. Please enter a unique name.")
        else:
            return name


def _prompt_car_position(name: str, field: Field) -> tuple[Position, Direction]:
    valid_directions = {d.value for d in Direction}
    while True:
        raw = _prompt(f"Please enter initial position of car {name} in x y Direction format:\n")
        parts = raw.split()
        if len(parts) == 3:
            try:
                x, y = int(parts[0]), int(parts[1])
                direction_str = parts[2].upper()
                if direction_str not in valid_directions:
                    print(f"Invalid direction '{direction_str}'. Only N, S, W, E are allowed.")
                    continue
                pos = Position(x, y)
                if not field.contains(pos):
                    print(f"Position ({x},{y}) is outside the field (0,0) to ({field.width - 1},{field.height - 1}).")
                    continue
                return pos, Direction(direction_str)
            except ValueError:
                pass
        print("Invalid input. Please enter x y Direction (e.g. 1 2 N).")


def _prompt_commands(name: str) -> list[Command]:
    valid_commands = {c.value for c in Command}
    while True:
        raw = _prompt(f"Please enter the commands for car {name}:\n").upper()
        if raw and all(ch in valid_commands for ch in raw):
            return [Command(ch) for ch in raw]
        print("Invalid commands. Only L, R, F are allowed and input cannot be empty.")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _print_car_list(cars: list[Car]) -> None:
    print("Your current list of cars are:")
    for car in cars:
        print(car.display())


def _print_main_menu() -> None:
    print("Please choose from the following options:")
    print("[1] Add a car to field")
    print("[2] Run simulation")


def _print_post_simulation_menu() -> None:
    print("Please choose from the following options:")
    print("[1] Start over")
    print("[2] Exit")


# ---------------------------------------------------------------------------
# Flow steps
# ---------------------------------------------------------------------------

def _add_car(field: Field, cars: list[Car]) -> None:
    existing_names = {car.name for car in cars}
    name = _prompt_car_name(existing_names)
    position, direction = _prompt_car_position(name, field)
    commands = _prompt_commands(name)
    cars.append(Car(name=name, position=position, direction=direction, commands=commands))


def _run_simulation(field: Field, cars: list[Car]) -> None:
    print()
    _print_car_list(cars)
    print()

    results: list[CarResult] = SimulationEngine(field, cars).run()

    print("After simulation, the result is:")
    for result in results:
        print(str(result))


# ---------------------------------------------------------------------------
# Session loop
# ---------------------------------------------------------------------------

def _run_session() -> bool:
    """Run one full simulation session. Returns True if the user wants to start over."""
    print("Welcome to Auto Driving Car Simulation!")
    print()

    field = _prompt_field()
    print(f"\nYou have created a field of {field}.")
    print()

    cars: list[Car] = []

    while True:
        _print_main_menu()
        choice = _prompt("")

        if choice == "1":
            _add_car(field, cars)
            print()
            _print_car_list(cars)
            print()
        elif choice == "2":
            if not cars:
                print("No cars have been added. Please add at least one car first.\n")
                continue
            _run_simulation(field, cars)
            print()
            _print_post_simulation_menu()
            post_choice = _prompt("")
            return post_choice == "1"
        else:
            print("Invalid choice. Please enter 1 or 2.\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    while True:
        start_over = _run_session()
        if not start_over:
            print("Thank you for running the simulation. Goodbye!")
            break
        print()
