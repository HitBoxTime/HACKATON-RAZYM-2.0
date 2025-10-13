import pygame
from game_logic.core import Game
from data.score_manager import ScoreManager

class PyGameUI:
    def __init__(self, game):
        self.game = game
        self.screen_width = 1300
        self.screen_height = 800
        self.cell_size = 40
        self.margin = 80 
        self.board1_x = self.margin
        self.board2_x = self.screen_width - self.margin - 10 * self.cell_size
        self.board_y = 180 
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Морской бой")
        
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(*pygame.mouse.get_pos())
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
    
    def handle_click(self, mouse_x, mouse_y):
        if self.game.game_state == "placing":
            current_board_x = self.board1_x if self.game.placing_player == 1 else self.board2_x
            
            if (current_board_x <= mouse_x < current_board_x + 10 * self.cell_size and 
                self.board_y <= mouse_y < self.board_y + 10 * self.cell_size):
                cell_x = (mouse_x - current_board_x) // self.cell_size
                cell_y = (mouse_y - self.board_y) // self.cell_size
                self.game.place_ship_click(cell_x, cell_y)
            
            if (self.screen_width // 2 - 100 <= mouse_x < self.screen_width // 2 + 100 and 
                self.board_y + 10 * self.cell_size + 80 <= mouse_y < self.board_y + 10 * self.cell_size + 120):
                self.game.auto_place_ships()
            
            if (self.screen_width // 2 - 100 <= mouse_x < self.screen_width // 2 + 100 and 
                self.board_y + 10 * self.cell_size + 130 <= mouse_y < self.board_y + 10 * self.cell_size + 170):
                self.game.rotate_ship()
        
        elif self.game.game_state == "playing":
            opponent_board_x = self.board2_x if self.game.current_player == 1 else self.board1_x
            
            if (opponent_board_x <= mouse_x < opponent_board_x + 10 * self.cell_size and 
                self.board_y <= mouse_y < self.board_y + 10 * self.cell_size):
                cell_x = (mouse_x - opponent_board_x) // self.cell_size
                cell_y = (mouse_y - self.board_y) // self.cell_size
                
                opponent_board = self.game.get_opponent_board()
                if not opponent_board.shots[cell_y][cell_x]:
                    self.game.fire(cell_x, cell_y)
        
        elif self.game.game_state == "game_over":
            if (self.screen_width // 2 - 100 <= mouse_x < self.screen_width // 2 + 100 and 
                self.board_y + 10 * self.cell_size + 80 <= mouse_y < self.board_y + 10 * self.cell_size + 120):
                self.game.reset_game()
    
    def draw_board(self, board, x, y, show_ships=True):
        for i in range(board.size + 1):
            pygame.draw.line(self.screen, (0, 0, 0), (x, y + i * self.cell_size), 
                             (x + board.size * self.cell_size, y + i * self.cell_size), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (x + i * self.cell_size, y), 
                             (x + i * self.cell_size, y + board.size * self.cell_size), 2)
        
        for i in range(board.size):
            letter = self.font.render(chr(65 + i), True, (0, 0, 0))
            number = self.font.render(str(i + 1), True, (0, 0, 0))
            self.screen.blit(letter, (x + i * self.cell_size + self.cell_size // 2 - 5, y - 30))
            self.screen.blit(number, (x - 30, y + i * self.cell_size + self.cell_size // 2 - 10))
        
        if show_ships:
            for ship in board.ships:
                for pos in ship.positions:
                    px, py = pos
                    pygame.draw.rect(self.screen, (0, 0, 139), 
                                    (x + px * self.cell_size + 2, y + py * self.cell_size + 2, 
                                     self.cell_size - 4, self.cell_size - 4))
        
        for i in range(board.size):
            for j in range(board.size):
                if board.shots[j][i]:
                    if board.grid[j][i] == 1:
                        pygame.draw.circle(self.screen, (255, 0, 0), 
                                          (x + i * self.cell_size + self.cell_size // 2, 
                                           y + j * self.cell_size + self.cell_size // 2), 
                                          self.cell_size // 3)
                    else:
                        pygame.draw.circle(self.screen, (0, 0, 255), 
                                          (x + i * self.cell_size + self.cell_size // 2, 
                                           y + j * self.cell_size + self.cell_size // 2), 
                                          self.cell_size // 6)
    
    def draw_ship_preview(self, x, y, board_x, board_y):
        if self.game.game_state == "placing":
            ship_size = self.game.selected_ship_size
            orientation = self.game.ship_orientation
            
            board = self.game.player1_board if self.game.placing_player == 1 else self.game.player2_board
            temp_ship = type('TempShip', (), {'size': ship_size, 'orientation': orientation})()
            
            can_place = True
            if orientation == 0:
                if x + ship_size > 10:
                    can_place = False
            else:
                if y + ship_size > 10:
                    can_place = False
            
            color = (0, 255, 0) if can_place else (255, 0, 0)
            if orientation == 0:
                pygame.draw.rect(self.screen, color, 
                                (board_x + x * self.cell_size, board_y + y * self.cell_size, 
                                 ship_size * self.cell_size, self.cell_size), 3)
            else:
                pygame.draw.rect(self.screen, color, 
                                (board_x + x * self.cell_size, board_y + y * self.cell_size, 
                                 self.cell_size, ship_size * self.cell_size), 3)
    
    def draw_button(self, x, y, width, height, text):
        pygame.draw.rect(self.screen, (173, 216, 230), (x, y, width, height))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, width, height), 2)
        
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
    
    def draw(self):
        self.screen.fill((255, 255, 255))
        
        title = self.title_font.render("МОРСКОЙ БОЙ", True, (0, 0, 139))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 30))
        
        player1_text = self.font.render("Игрок 1", True, (0, 0, 0))
        player2_text = self.font.render("Игрок 2", True, (0, 0, 0))
        self.screen.blit(player1_text, (self.board1_x + 10 * self.cell_size // 2 - player1_text.get_width() // 2, self.board_y - 60))
        self.screen.blit(player2_text, (self.board2_x + 10 * self.cell_size // 2 - player2_text.get_width() // 2, self.board_y - 60))
        
        message_text = self.font.render(self.game.message, True, (0, 0, 0))
        self.screen.blit(message_text, (self.screen_width // 2 - message_text.get_width() // 2, self.board_y + 10 * self.cell_size + 20))
        
        score_text = self.font.render(
            f"Счет: Игрок 1 - {self.game.score_manager.get_score(1)} | Игрок 2 - {self.game.score_manager.get_score(2)}", 
            True, (0, 0, 0)
        )
        self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, self.board_y + 10 * self.cell_size + 50))
        
        if self.game.game_state == "placing":
            self.draw_board(self.game.player1_board, self.board1_x, self.board_y, show_ships=True)
            self.draw_board(self.game.player2_board, self.board2_x, self.board_y, show_ships=True)
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            current_board_x = self.board1_x if self.game.placing_player == 1 else self.board2_x
            
            if (current_board_x <= mouse_x < current_board_x + 10 * self.cell_size and 
                self.board_y <= mouse_y < self.board_y + 10 * self.cell_size):
                cell_x = (mouse_x - current_board_x) // self.cell_size
                cell_y = (mouse_y - self.board_y) // self.cell_size
                self.draw_ship_preview(cell_x, cell_y, current_board_x, self.board_y)
            
            self.draw_button(self.screen_width // 2 - 100, self.board_y + 10 * self.cell_size + 80, 200, 40, "Авторасстановка")
            self.draw_button(self.screen_width // 2 - 100, self.board_y + 10 * self.cell_size + 130, 200, 40, "Повернуть корабль")
            
            ship_info = self.font.render(f"Размещаемый корабль: {self.game.selected_ship_size}-палубный", True, (0, 0, 0))
            self.screen.blit(ship_info, (self.screen_width // 2 - ship_info.get_width() // 2, self.board_y + 10 * self.cell_size + 180))
        
        elif self.game.game_state == "playing":
            current_board = self.game.get_current_board()
            opponent_board = self.game.get_opponent_board()
            
            current_board_x = self.board1_x if self.game.current_player == 1 else self.board2_x
            opponent_board_x = self.board2_x if self.game.current_player == 1 else self.board1_x
            
            self.draw_board(current_board, current_board_x, self.board_y, show_ships=True)
            self.draw_board(opponent_board, opponent_board_x, self.board_y, show_ships=False)
        
        elif self.game.game_state == "game_over":
            self.draw_board(self.game.player1_board, self.board1_x, self.board_y, show_ships=True)
            self.draw_board(self.game.player2_board, self.board2_x, self.board_y, show_ships=True)
            
            self.draw_button(self.screen_width // 2 - 100, self.board_y + 10 * self.cell_size + 80, 200, 40, "Новая игра")