from random import randint
from dataclasses import dataclass, field
import dataclasses
import heapq
import copy
import argparse


@dataclass(frozen=True)
class Coordinates:
    """Pair of values to navigate in the 2d grid."""

    x: int
    y: int

    @classmethod
    def top_left(cls):
        return cls(x=0, y=0)

    @classmethod
    def to_the_left_of(cls, coord: "Coordinates"):
        return cls(x=coord.x - 1, y=coord.y)

    @classmethod
    def at_the_top_of(cls, coord: "Coordinates"):
        return cls(x=coord.x, y=coord.y - 1)

    @classmethod
    def to_the_right_of(cls, coord: "Coordinates"):
        return cls(x=coord.x + 1, y=coord.y)

    @classmethod
    def at_the_bottom_of(cls, coord: "Coordinates"):
        return cls(x=coord.x, y=coord.y + 1)

    def is_valid(self, max_size: int) -> bool:
        return (
            (self.x >= 0)
            and (self.y >= 0)
            and (self.x < max_size)
            and (self.y < max_size)
        )

    def get_adj_coords(self, max_size: int) -> list["Coordinates"]:
        return [
            adj_coord
            for adj_coord in [
                Coordinates.to_the_left_of(self),
                Coordinates.at_the_top_of(self),
                Coordinates.to_the_right_of(self),
                Coordinates.at_the_bottom_of(self),
            ]
            if adj_coord.is_valid(max_size)
        ]


@dataclass
class Grid:
    """Color matrix representation.
    Each value inside matrix are a color representation.
    - Matrix is a square matrix.
    - Strictly negative numbers are forbiden.
    """

    colors: set
    matrix: list[list[int]]
    nb_color: int = field(init=False)
    size: int = field(init=False)

    @classmethod
    def from_csv(cls, csv_file_name: str):
        with open(csv_file_name) as f:
            lines = f.readlines()
            matrix = [list(map(int, line.split(","))) for line in lines[:]]
            colors = {color for line in matrix for color in line}
            return cls(matrix=matrix, colors=colors)

    def __post_init__(self):
        if not all(len(self.matrix) == len(row) for row in self.matrix):
            raise ValueError("Not a square matrix.")
        if not all(color >= 0 for row in self.matrix for color in row):
            raise ValueError("Negative values are forbiden.")
        self.size = len(self.matrix)
        self.nb_color = len(self.colors)

    def __str__(self):
        return "\n".join(
            [" ".join([str(color) for color in row]) for row in self.matrix]
        )

    def set_color(self, coord: Coordinates, color: int) -> None:
        self.matrix[coord.y][coord.x] = color

    def get_color(self, coord: Coordinates) -> int:
        return self.matrix[coord.y][coord.x]

    def get_top_left_color(self) -> int:
        return self.get_color(Coordinates.top_left())

    def is_solved(self) -> bool:
        top_left_color = self.get_top_left_color()
        # We begin to iterate at the bottom right corner.
        for i in range(self.size**2 - 1, 0, -1):
            color = self.get_color(Coordinates(x=i % self.size, y=i // self.size))
            if color != top_left_color:
                return False
        return True

    def act(self, color: int) -> bool:
        return self.flood(color=color, start_coord=Coordinates.top_left())

    def flood(self, start_coord: Coordinates, color: int) -> bool:
        # A move is useful if
        # - Color from targeted cell has changed.
        # - Area flooded by new color was next to a cell with the same color.
        useful_move: bool = False
        original_color = self.get_color(start_coord)

        if original_color != color:
            queue: list[Coordinates] = [start_coord]
            while queue:
                current_coord = queue.pop(0)
                self.set_color(current_coord, color)
                for new_coord in current_coord.get_adj_coords(max_size=self.size):
                    if (
                        self.get_color(new_coord) == original_color
                        and not new_coord in queue
                    ):
                        queue.append(new_coord)

                    elif self.get_color(new_coord) == color:
                        useful_move = True
        return useful_move


@dataclass
class GridState:
    """Color matrix interactions."""

    grid: Grid
    moves: list[int] = field(default_factory=lambda: [], init=False)
    heuristic_value: float = field(init=False)

    def __post_init__(self) -> None:
        self.grid = self.clone_grid()

    def __str__(self):
        return str(self.grid)

    def __lt__(self, other: "GridState"):
        return self.heuristic_value < other.heuristic_value

    def clone_grid(self) -> Grid:
        return copy.deepcopy(self.grid)

    def copy_state(self) -> "GridState":
        new_state = dataclasses.replace(self)
        new_state.moves = self.moves[:]
        return new_state

    def set_heuristic_value(self) -> None:
        grid_mask = self.clone_grid()
        nb_area = 0
        marker_color = -1  # Unused color, used like a marker
        for i in range(grid_mask.size):
            for j in range(grid_mask.size):
                coord = Coordinates(i, j)
                if grid_mask.get_color(coord) == marker_color:
                    continue
                grid_mask.flood(color=marker_color, start_coord=coord)
                nb_area += 1

        self.heuristic_value = nb_area / self.grid.nb_color


class Game:
    def __init__(self, input: str, output: str, verbose: bool = False):
        """TO THE ORGANISER: I'm sorry for this code. But I did my best to win the plush."""
        g = Grid.from_csv(input)
        if verbose:
            print(f"{g}")
        moves = self.solver(g)
        if verbose:
            print(f"Moves: {moves}, length: {len(moves)}")
            print(f"Verified: {self.verify_moves(g, moves)}")
        self.to_csv_file(moves, output)

    @staticmethod
    def to_csv_file(moves: list[int], output: str) -> None:
        with open(output, "w") as f:
            f.write("\n".join([str(move) for move in moves]))

    @staticmethod
    def solver(grid: Grid) -> list[int]:
        """A* algorithm.

        Args:
            grid (Grid): Color matrix.

        Returns:
            list[int]: Ordored colors used to complete the puzzle.
        """
        priority_queue: list[GridState] = [GridState(grid)]
        heapq.heapify(priority_queue)

        while priority_queue:
            current_state = heapq.heappop(priority_queue)
            if current_state.grid.is_solved():
                return current_state.moves

            current_color = current_state.grid.get_top_left_color()
            available_colors = grid.colors - {current_color}
            for color in available_colors:
                new_state = current_state.copy_state()
                new_state.moves.append(color)

                if new_state.grid.act(color):
                    new_state.set_heuristic_value()
                    heapq.heappush(priority_queue, new_state)

    @staticmethod
    def verify_moves(grid: Grid, moves: list[int]) -> bool:
        for color in moves:
            grid.act(color)
        return grid.is_solved()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description of your program")
    parser.add_argument(
        "-i",
        "--input",
        help="Input .csv file",
        nargs="?",
        default="input.csv",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output .csv file",
        nargs="?",
        default="output.csv",
        type=str,
    )
    parser.add_argument(
        "--verbose",
        help="Verbose mode with prints.",
        required=False,
        action="store_true",
    )
    args = vars(parser.parse_args())
    Game(**args)
