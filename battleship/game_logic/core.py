from game_logic.board import Board
from data.score_manager import ScoreManager

class Game:
    def __init__(self):
        self.player1_board = Board("Игрок 1")
        self.player2_board = Board("Игрок 2")
        self.current_player = 1
        self.game_state = "placing"  
        self.selected_ship_size = 4
        self.ship_orientation = 0
        self.placing_player = 1
        self.message = "Игрок 1 расставляет корабли"
        self.score_manager = ScoreManager()
        self.available_ships = {4: 1, 3: 2, 2: 3, 1: 4}
        self.placed_ships = {4: 0, 3: 0, 2: 0, 1: 0}
    
    def switch_turn(self):
        """Переключение хода между игроками"""
        if self.current_player == 1:
            self.current_player = 2
            self.message = "Ход игрока 2"
        else:
            self.current_player = 1
            self.message = "Ход игрока 1"
        print(f"Переключение хода: теперь ходит игрок {self.current_player}")
    
    def switch_player(self):
        """Переключение между игроками при расстановке кораблей"""
        if self.placing_player == 1:
            self.placing_player = 2
            self.message = "Игрок 2 расставляет корабли"
            self.selected_ship_size = 4
            self.placed_ships = {4: 0, 3: 0, 2: 0, 1: 0} 
            print("Переключение на игрока 2")
        else:
            self.placing_player = 1
            self.game_state = "playing"
            self.current_player = 1
            self.message = "Игра началась! Ход игрока 1"
            print("Все корабли расставлены, начинаем игру!")
    
    def place_ship_click(self, x, y):
        """Размещение корабля при клике"""
        if self.placing_player == 1:
            board = self.player1_board
        else:
            board = self.player2_board
            
        ship_size = self.selected_ship_size
        
        if self.can_place_ship(board, x, y, ship_size, self.ship_orientation):
            if board.place_ship(ship_size, x, y, self.ship_orientation):
                self.placed_ships[ship_size] += 1
                print(f"Игрок {self.placing_player} разместил {ship_size}-палубный корабль в ({x},{y})")
                
                next_size = None
                for size in [4, 3, 2, 1]:
                    if self.placed_ships[size] < self.available_ships[size]:
                        next_size = size
                        break
                
                if next_size is not None:
                    self.selected_ship_size = next_size
                    self.message = f"Игрок {self.placing_player}: разместите {next_size}-палубный корабль"
                else:
                    self.switch_player()
                return True
            else:
                self.message = "Ошибка размещения корабля"
                return False
        else:
            self.message = "Невозможно разместить корабль здесь"
            return False
    
    def get_opponent_board(self):
        """Возвращает доску противника"""
        if self.game_state == "placing":
            return self.player2_board if self.placing_player == 1 else self.player1_board
        else:
            return self.player2_board if self.current_player == 1 else self.player1_board

    def get_current_board(self):
        """Возвращает доску текущего игрока"""
        if self.game_state == "placing":
            return self.player1_board if self.placing_player == 1 else self.player2_board
        else:
            return self.player1_board if self.current_player == 1 else self.player2_board

    def can_place_ship(self, board, x, y, size, orientation):
        """Проверяет можно ли разместить корабль"""
        if orientation == 0: 
            if x + size > 10:
                return False
            for i in range(size):
                if board.grid[y][x + i] != 0:
                    return False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = y + dy, x + i + dx
                        if 0 <= ny < 10 and 0 <= nx < 10 and board.grid[ny][nx] != 0:
                            return False
        else: 
            if y + size > 10:
                return False
            for i in range(size):
                if board.grid[y + i][x] != 0:
                    return False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = y + i + dy, x + dx
                        if 0 <= ny < 10 and 0 <= nx < 10 and board.grid[ny][nx] != 0:
                            return False
        return True
    
    def rotate_ship(self):
        self.ship_orientation = 1 - self.ship_orientation
        orientation_text = "Вертикальная" if  self.ship_orientation == 1 else "Горизонтальная"
        self.message = f"Ориентация корабля: {orientation_text}"
        print (f"Поврот корабля: {orientation_text}")
        return self.ship_orientation

    def auto_place_ships(self):
        """Авторасстановка кораблей для текущего игрока"""
        if self.placing_player == 1:
            board = self.player1_board
        else:
            board = self.player2_board
            
        if board.auto_place_ships():
            for size in self.available_ships:
                self.placed_ships[size] = self.available_ships[size]
            
            print(f"Авторасстановка завершена для игрока {self.placing_player}")
            self.switch_player()
            return True
        return False
    
    def fire(self, x, y):
        """Обработка выстрела в локальной игре"""
        print(f"Выстрел: игрок {self.current_player} в ({x},{y})")
        
        if self.current_player == 1:
            result = self.player2_board.receive_shot(x, y)
            target_player = 2
        else:
            result = self.player1_board.receive_shot(x, y)
            target_player = 1
        
        print(f"Результат выстрела: {result}")
        
        if result == "miss":
            self.message = f"Игрок {self.current_player} промахнулся!"
            self.switch_turn()
        elif result == "hit":
            self.message = f"Игрок {self.current_player} попал в корабль!"
        elif result == "sunk":
            self.message = f"Игрок {self.current_player} потопил корабль!"
            
            if target_player == 1:
                if self.player1_board.all_ships_sunk():
                    self.game_state = "game_over"
                    self.message = f"Игрок {self.current_player} победил!"
                    self.score_manager.add_win(self.current_player)
                    print(f"Игра окончена! Победил игрок {self.current_player}")
            else:
                if self.player2_board.all_ships_sunk():
                    self.game_state = "game_over"
                    self.message = f"Игрок {self.current_player} победил!"
                    self.score_manager.add_win(self.current_player)
                    print(f"Игра окончена! Победил игрок {self.current_player}")
    
    def reset_game(self):
        """Полный сброс игры для новой партии"""
        print("СБРОС ЛОКАЛЬНОЙ ИГРЫ")
        
        self.player1_board = Board("Игрок 1")
        self.player2_board = Board("Игрок 2")
        
        self.current_player = 1
        self.game_state = "placing"
        self.selected_ship_size = 4
        self.ship_orientation = 0
        self.placing_player = 1
        self.message = "Игрок 1 расставляет корабли"
        
        self.placed_ships = {4: 0, 3: 0, 2: 0, 1: 0}
        
        print("Локальная игра полностью сброшена")
