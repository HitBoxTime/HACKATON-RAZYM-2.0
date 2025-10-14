from game_logic.ship import Ship
import random

class Board:
    def __init__(self, player_name):
        self.player_name = player_name
        self.size = 10
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.ships = []
        self.shots = [[False for _ in range(self.size)] for _ in range(self.size)]
    
    def place_ship(self, size, x, y, orientation):
        if orientation == 0:
            if x + size > self.size:
                return False
            for i in range(size):
                if self.grid[y][x + i] != 0:
                    return False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = y + dy, x + i + dx
                        if 0 <= ny < self.size and 0 <= nx < self.size and self.grid[ny][nx] != 0:
                            return False
        else:
            if y + size > self.size:
                return False
            for i in range(size):
                if self.grid[y + i][x] != 0:
                    return False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = y + i + dy, x + dx
                        if 0 <= ny < self.size and 0 <= nx < self.size and self.grid[ny][nx] != 0:
                            return False
        
        ship = Ship(size)
        ship.orientation = orientation
        ship.positions = []
        
        if orientation == 0:
            for i in range(size):
                self.grid[y][x + i] = 1
                ship.positions.append((x + i, y))
        else:
            for i in range(size):
                self.grid[y + i][x] = 1
                ship.positions.append((x, y + i))
        
        self.ships.append(ship)
        return True
    
    def auto_place_ships(self):
        self.ships = []
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        
        for size in ship_sizes:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                orientation = random.randint(0, 1)
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                
                if self.place_ship(size, x, y, orientation):
                    placed = True
                attempts += 1
            
            if not placed:
                return False
        
        return True
    
    def receive_shot(self, x, y):
        if self.shots[y][x]:
            return "already_shot"
        
        self.shots[y][x] = True
        
        if self.grid[y][x] == 1: 
            for ship in self.ships:
                for i, (sx, sy) in enumerate(ship.positions):
                    if sx == x and sy == y:
                        ship.hit(i)
                        if ship.is_sunk():
                            return "sunk"
                        return "hit"
            return "hit"
        else:
            return "miss"
    
    def all_ships_sunk(self):
        return all(ship.is_sunk() for ship in self.ships)