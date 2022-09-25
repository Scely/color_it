from dataclasses import dataclass, field
import dataclasses
import heapq

from random import randint
import copy

# https://github.com/moondemon68/Flood-It-Solver/blob/master/solver.cpp


@dataclass(frozen=True)
class Coordinates():
    x: int
    y: int
    
    @classmethod
    def left(cls, x: int, y: int):
        return cls(x=x-1, y=y)
    
    @classmethod
    def top(cls, x: int, y: int):
        return cls(x=x, y=y-1)
    
    @classmethod
    def right(cls, x: int, y: int):
        return cls(x=x+1, y=y)
    
    @classmethod
    def bottom(cls, x: int, y: int):
        return cls(x=x, y=y+1)
    
    def is_valid(self, size: int) -> bool:
        return (self.x >= 0) and (self.y >= 0) and (self.x < size) and (self.y < size)

@dataclass
class Grid():
    size: int = 8
    nb_color: int = 5
    values: list[list[int]] = field(init=False)
    
    def __post_init__(self):
        self.values = [[randint(1, self.nb_color) for elem in range(self.size)] for row in range(self.size)]
        
    def __str__(self):
        return "\n".join([" ".join([ str(value) for value in row]) for row in self.values ])
    
    def set_value(self, coord: Coordinates, value: int)-> None:
        self.values[coord.y][coord.x] = value
    
    def get_value(self, coord: Coordinates) -> int:
        return self.values[coord.y][coord.x]
    

@dataclass
class GridState():
    grid: Grid
    moves: list[int] = field(default_factory=lambda: [], init=False)
    h_value: float = field(init=False)
    
    def __post_init__(self) -> None:
        self.grid = self.clone_grid()
    
    def clone_grid(self) -> Grid:
        return copy.deepcopy(self.grid)
                        
    def is_solved(self) -> bool:
        for row in self.grid.values:
            for value in row:
                if value != self.grid.get_value(Coordinates(0, 0)):
                    return False
        return True
    
    def get_top_left_color(self) -> int:
        return self.grid.get_value(Coordinates(x=0, y=0))
        
    def flood(self, value: int) -> bool:
                
        original_value: int = self.get_top_left_color()
        
        queue: list[Coordinates] = [Coordinates(x=0, y=0)]
        # A move is useful if
        # - the top left corner value had changed
        # - new top left corner value is next to a cell with its new value
        useful_move: bool = False
        
        if original_value == value:
            return useful_move
        
        while queue:
            current_coord = queue.pop(0)
            self.grid.set_value(coord=current_coord, value=value)
            # On regarde les cases voisines
            new_coords: list[Coordinates] = [
                Coordinates.left(**vars(current_coord)),
                Coordinates.top(**vars(current_coord)),
                Coordinates.right(**vars(current_coord)),
                Coordinates.bottom(**vars(current_coord))
            ]
            # print(f"find neigbours of COORD: {current_coord}, {self.grid.get_value(current_coord)}")
            for new_coord in new_coords:
                if not new_coord.is_valid(self.grid.size):
                    continue
                # print(f"new_coord: {new_coord}, value: {self.grid.get_value(new_coord)}")
                if self.grid.get_value(new_coord) == original_value and not new_coord in queue:
                    queue.append(new_coord)
                elif self.grid.get_value(new_coord) == value:
                    useful_move =True
                    
            
            # print(f"TOUR {debug_counter}: {queue}")
            
            # return 
        print(self.grid)
        return useful_move
    
    def _copy_state(self):
        new_state = dataclasses.replace(self)
        new_state.moves = self.moves
        return new_state
    
    def __str__(self):
        return str(self.grid)
    
    def __lt__(self, other: "GridState"):
        return self.h_value < other.h_value
           

def solver(grid: Grid) -> list[int]:
    # TODO rename queue
    a = 0
    queue: list[GridState] = [GridState(grid=grid)] # should be a prio queue (see class in C++)
    # greates elem is h value !
    # https://docs.python.org/3/library/heapq.html
    while queue:
        a += 1
        print(f"{len(queue)=}")
        current_state = queue.pop(0)
        if current_state.is_solved():
            print("SOLVED ! :D")
            return current_state.moves

        # Get color used by top left corner
        current_color = current_state.get_top_left_color()
        
        for color in range(1, grid.nb_color+1):
            if color == current_color:
                continue
            print(f"{current_color=}, {color=}")
            new_state = current_state._copy_state()
            new_state.moves.append(color)
            # appliquer le flood de la color choisie
            useful_move = new_state.flood(value=color)
            # print(new_state.grid)
            if useful_move:
                # new_state.find_h_value()
                queue.append(new_state)
    

def debug():
    
    g = Grid(size = 3, nb_color = 3) 
    g.values = [
        [2, 2, 2],
        [3, 3, 2],
        [1, 2, 3],
    ]
    state = GridState(g)
    print(state.flood(3))
    print(state.flood(2))
    
def test_heapq():
    @dataclass
    class toto:
        val: int
        
        def __lt__(self, other):
            return self.val < other.val
        
    my_list = [toto(1), toto(2), toto(0)]
    heapq.heapify(my_list)
    print(my_list, type(my_list))

def main():
    g = Grid(size = 3, nb_color = 3)
    res = solver(g)
    print(f"RESULTS: {res}")
    print(f"{g}")

if __name__ == "__main__":
    # debug()
    # main()
    test_heapq()
    
