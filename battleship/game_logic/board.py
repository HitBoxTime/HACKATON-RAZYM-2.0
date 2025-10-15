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
            
            while not placed and attempts < 200:
                orientation = random.randint(0, 1)
                
                if orientation == 0:
                    x = random.randint(0, self.size - size)
                    y = random.randint(0, self.size - 1)
                else: 
                    x = random.randint(0, self.size - 1)
                    y = random.randint(0, self.size - size)
                
                if self.can_place_ship(size, x, y, orientation):
                    if self.place_ship(size, x, y, orientation):
                        placed = True
                        print(f"Размещен {size}-палубный корабль в ({x},{y}), ориентация: {'горизонтальная' if orientation == 0 else 'вертикальная'}")
                
                attempts += 1
            
            if not placed:
                print(f"Не удалось разместить {size}-палубный корабль после {attempts} попыток")
                return False
        
        print(f"Всего размещено кораблей: {len(self.ships)}")
        return True
    
    def can_place_ship(self, size, x, y, orientation):
        """Проверяет можно ли разместить корабль в указанной позиции"""
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
                            self.mark_around_sunken_ship(ship)
                            return "sunk"
                        return "hit"
            return "hit"
        else:
            return "miss"
    
    def mark_around_sunken_ship(self, ship):
        for pos in ship.positions:
            px, py = pos
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size and not self.shots[ny][nx]:
                        self.shots[ny][nx] = True

    def all_ships_sunk(self):
        return all(ship.is_sunk() for ship in self.ships)