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
    
    def switch_player(self):
        if self.placing_player == 1:
            self.placing_player = 2
            self.message = "Игрок 2 расставляет корабли"
            self.selected_ship_size = 4
            self.placed_ships = {4: 0, 3: 0, 2: 0, 1: 0}
        else:
            self.placing_player = 1
            self.game_state = "playing"
            self.current_player = 1
            self.message = "Игрок 1 делает ход"
    
    def switch_turn(self):
        if self.current_player == 1:
            self.current_player = 2
            self.message = "Игрок 2 делает ход"
        else:
            self.current_player = 1
            self.message = "Игрок 1 делает ход"
    
    def fire(self, x, y):
        if self.current_player == 1:
            result = self.player2_board.receive_shot(x, y)
            if result == "miss":
                self.switch_turn()
            elif result == "sunk":
                if self.player2_board.all_ships_sunk():
                    self.game_state = "game_over"
                    self.message = "Игрок 1 победил!"
                    self.score_manager.add_win(1)
                else:
                    self.message = "Игрок 1 потопил корабль! Ход снова его."
            elif result == "hit":
                self.message = "Игрок 1 попал! Ход снова его."
        else:
            result = self.player1_board.receive_shot(x, y)
            if result == "miss":
                self.switch_turn()
            elif result == "sunk":
                if self.player1_board.all_ships_sunk():
                    self.game_state = "game_over"
                    self.message = "Игрок 2 победил!"
                    self.score_manager.add_win(2)
                else:
                    self.message = "Игрок 2 потопил корабль! Ход снова его."
            elif result == "hit":
                self.message = "Игрок 2 попал! Ход снова его."
    
    def place_ship_click(self, x, y):
        board = self.player1_board if self.placing_player == 1 else self.player2_board
        ship_size = self.selected_ship_size
        
        if board.place_ship(ship_size, x, y, self.ship_orientation):
            self.placed_ships[ship_size] += 1
            
            next_size = None
            for size in [4, 3, 2, 1]:
                if self.placed_ships[size] < self.available_ships[size]:
                    next_size = size
                    break
            
            if next_size is not None:
                self.selected_ship_size = next_size
            else:
                self.switch_player()
            return True
        return False
    
    def rotate_ship(self):
        self.ship_orientation = 1 - self.ship_orientation
    
    def auto_place_ships(self):
        board = self.player1_board if self.placing_player == 1 else self.player2_board
        if board.auto_place_ships():
            for size in self.available_ships:
                self.placed_ships[size] = self.available_ships[size]
            self.switch_player()
            return True
        return False
    
    def reset_game(self):
        self.player1_board = Board("Игрок 1")
        self.player2_board = Board("Игрок 2")
        self.current_player = 1
        self.game_state = "placing"
        self.selected_ship_size = 4
        self.ship_orientation = 0
        self.placing_player = 1
        self.message = "Игрок 1 расставляет корабли"
        self.placed_ships = {4: 0, 3: 0, 2: 0, 1: 0}
    
    def get_current_board(self):
        if self.game_state == "placing":
            return self.player1_board if self.placing_player == 1 else self.player2_board
        else:
            return self.player1_board if self.current_player == 1 else self.player2_board
    
    def get_opponent_board(self):
        if self.game_state == "placing":
            return self.player2_board if self.placing_player == 1 else self.player1_board
        else:
            return self.player2_board if self.current_player == 1 else self.player1_board