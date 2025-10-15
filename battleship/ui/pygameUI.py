import pygame
import sys
from game_logic.core import Game

class PyGameUI:
    def __init__(self, game):
        self.game = game
        self.screen_width = 1300
        self.screen_height = 700
        self.cell_size = 40
        self.margin = 50
        self.board1_x = self.margin
        self.board2_x = self.screen_width - self.margin - 10 * self.cell_size
        self.board_y = 150
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Морской бой - Одиночная игра")
        
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
        print(f"Клик в локальной игре: x={mouse_x}, y={mouse_y}, состояние={self.game.game_state}")
    
        if self.game.game_state == "placing":
            if self.game.placing_player == 1:
                current_board_x = self.board1_x
            else:
                current_board_x = self.board2_x
            
            if (current_board_x <= mouse_x < current_board_x + 10 * self.cell_size and 
                self.board_y <= mouse_y < self.board_y + 10 * self.cell_size):
                cell_x = (mouse_x - current_board_x) // self.cell_size
                cell_y = (mouse_y - self.board_y) // self.cell_size
                
                print(f"Клик по доске игрока {self.game.placing_player} в клетку ({cell_x},{cell_y})")
                self.game.place_ship_click(cell_x, cell_y)
            
            if (self.screen_width // 2 - 100 <= mouse_x < self.screen_width // 2 + 100 and 
                self.board_y + 10 * self.cell_size + 20 <= mouse_y < self.board_y + 10 * self.cell_size + 60):
                print("Нажата кнопка 'Авторасстановка'")
                self.game.auto_place_ships()
            
            if (self.screen_width // 2 - 100 <= mouse_x < self.screen_width // 2 + 100 and 
                self.board_y + 10 * self.cell_size + 70 <= mouse_y < self.board_y + 10 * self.cell_size + 110):
                print("Нажата кнопка 'Повернуть корабль'")
                self.game.rotate_ship()
        
        elif self.game.game_state == "playing":
            if self.game.current_player == 1:
                opponent_board_x = self.board2_x
            else:
                opponent_board_x = self.board1_x
            
            if (opponent_board_x <= mouse_x < opponent_board_x + 10 * self.cell_size and 
                self.board_y <= mouse_y < self.board_y + 10 * self.cell_size):
                cell_x = (mouse_x - opponent_board_x) // self.cell_size
                cell_y = (mouse_y - self.board_y) // self.cell_size
                
                opponent_board = self.game.get_opponent_board()
                if not opponent_board.shots[cell_y][cell_x]:
                    print(f"Игрок {self.game.current_player} стреляет в ({cell_x},{cell_y})")
                    self.game.fire(cell_x, cell_y)
        
        elif self.game.game_state == "game_over":
            if (self.screen_width // 2 - 100 <= mouse_x < self.screen_width // 2 + 100 and 
                self.board_y + 10 * self.cell_size + 20 <= mouse_y < self.board_y + 10 * self.cell_size + 60):
                print("Нажата кнопка 'Новая игра' в локальной игре")
                self.game.reset_game()

    
    def draw_board(self, board, x, y, show_ships=True):
        pygame.draw.rect(self.screen, (240, 240, 240), 
                        (x-5, y-5, 10*self.cell_size+10, 10*self.cell_size+10))

        for i in range(11):
            pygame.draw.line(self.screen, (0, 0, 0), 
                            (x, y + i * self.cell_size), 
                            (x + 10 * self.cell_size, y + i * self.cell_size), 2)
            pygame.draw.line(self.screen, (0, 0, 0), 
                            (x + i * self.cell_size, y), 
                            (x + i * self.cell_size, y + 10 * self.cell_size), 2)

        for i in range(10):
            letter = self.font.render(chr(65 + i), True, (0, 0, 0))
            self.screen.blit(letter, (x + i * self.cell_size + self.cell_size//2 - 5, y - 30))

        for i in range(10):
            number = self.font.render(str(i + 1), True, (0, 0, 0))
            self.screen.blit(number, (x - 30, y + i * self.cell_size + self.cell_size//2 - 10))

        if show_ships:
            for ship in board.ships:
                for pos in ship.positions:
                    px, py = pos
                    if board.shots[py][px]:
                        color = (200, 0, 0)  # Красный для попаданий
                    else:
                        color = (0, 150, 0)  # Зеленый для целых кораблей

                    pygame.draw.rect(self.screen, color, 
                                   (x + px * self.cell_size + 2, 
                                    y + py * self.cell_size + 2, 
                                    self.cell_size - 4, self.cell_size - 4))

                    # Рамка
                    pygame.draw.rect(self.screen, (0, 0, 0), 
                                   (x + px * self.cell_size + 2, 
                                    y + py * self.cell_size + 2, 
                                    self.cell_size - 4, self.cell_size - 4), 1)

        # Выстрелы
        for i in range(10):
            for j in range(10):
                if board.shots[j][i]:
                    if board.grid[j][i] == 1:  # Попадание
                        # Красный крестик
                        pygame.draw.line(self.screen, (255, 0, 0), 
                                       (x + i * self.cell_size + 8, y + j * self.cell_size + 8),
                                       (x + (i+1) * self.cell_size - 8, y + (j+1) * self.cell_size - 8), 3)
                        pygame.draw.line(self.screen, (255, 0, 0), 
                                       (x + (i+1) * self.cell_size - 8, y + j * self.cell_size + 8),
                                       (x + i * self.cell_size + 8, y + (j+1) * self.cell_size - 8), 3)
                    else:  # Промах
                        # Синяя точка
                        pygame.draw.circle(self.screen, (0, 0, 200), 
                                         (x + i * self.cell_size + self.cell_size//2, 
                                          y + j * self.cell_size + self.cell_size//2), 
                                          self.cell_size//6)
    
    def draw_ship_preview(self, x, y, board_x, board_y):
        if self.game.game_state == "placing":
            ship_size = self.game.selected_ship_size
            orientation = self.game.ship_orientation

            can_place = True
            if orientation == 0:
                if x + ship_size > 10:
                    can_place = False
            else:
                if y + ship_size > 10:
                    can_place = False

            color = (0, 200, 0) if can_place else (200, 0, 0)

            # Создаем полупрозрачную поверхность для предпросмотра
            if orientation == 0:
                preview_surface = pygame.Surface((ship_size * self.cell_size, self.cell_size), pygame.SRCALPHA)
                pygame.draw.rect(preview_surface, (*color, 150), (0, 0, ship_size * self.cell_size, self.cell_size))
                self.screen.blit(preview_surface, (board_x + x * self.cell_size, board_y + y * self.cell_size))
            else:
                preview_surface = pygame.Surface((self.cell_size, ship_size * self.cell_size), pygame.SRCALPHA)
                pygame.draw.rect(preview_surface, (*color, 150), (0, 0, self.cell_size, ship_size * self.cell_size))
                self.screen.blit(preview_surface, (board_x + x * self.cell_size, board_y + y * self.cell_size))

    def draw_button(self, x, y, width, height, text):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = (x <= mouse_pos[0] <= x + width and 
                     y <= mouse_pos[1] <= y + height)
        
        color = (135, 206, 250) if is_hovered else (173, 216, 230)
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, width, height), 2)
        
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
    
    def draw(self):
        self.screen.fill((255, 255, 255))

        title = self.title_font.render("МОРСКОЙ БОЙ - ЛОКАЛЬНАЯ ИГРА", True, (0, 0, 139))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 20))

        # Отладочная информация
        debug_text = f"Состояние: {self.game.game_state}, Игрок: {self.game.placing_player if self.game.game_state == 'placing' else self.game.current_player}"
        debug_surface = self.font.render(debug_text, True, (100, 100, 100))
        self.screen.blit(debug_surface, (10, 80))

        player1_text = "Игрок 1" + (" (РАССТАВЛЯЕТ)" if self.game.placing_player == 1 and self.game.game_state == "placing" else " (ИГРАЕТ)" if self.game.current_player == 1 and self.game.game_state == "playing" else "")
        player2_text = "Игрок 2" + (" (РАССТАВЛЯЕТ)" if self.game.placing_player == 2 and self.game.game_state == "placing" else " (ИГРАЕТ)" if self.game.current_player == 2 and self.game.game_state == "playing" else "")

        player1_surface = self.font.render(player1_text, True, (0, 0, 0))
        player2_surface = self.font.render(player2_text, True, (0, 0, 0))

        self.screen.blit(player1_surface, (self.board1_x + 10 * self.cell_size // 2 - player1_surface.get_width() // 2, self.board_y - 60))
        self.screen.blit(player2_surface, (self.board2_x + 10 * self.cell_size // 2 - player2_surface.get_width() // 2, self.board_y - 60))

        if self.game.game_state == "placing":
            # В режиме расстановки показываем корабли только у текущего игрока
            show_ships_player1 = (self.game.placing_player == 1)
            show_ships_player2 = (self.game.placing_player == 2)

            self.draw_board(self.game.player1_board, self.board1_x, self.board_y, show_ships=show_ships_player1)
            self.draw_board(self.game.player2_board, self.board2_x, self.board_y, show_ships=show_ships_player2)

            # Предпросмотр корабля
            current_board_x = self.board1_x if self.game.placing_player == 1 else self.board2_x
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (current_board_x <= mouse_x < current_board_x + 10 * self.cell_size and 
                self.board_y <= mouse_y < self.board_y + 10 * self.cell_size):
                cell_x = (mouse_x - current_board_x) // self.cell_size
                cell_y = (mouse_y - self.board_y) // self.cell_size
                self.draw_ship_preview(cell_x, cell_y, current_board_x, self.board_y)

            message_text = self.font.render(self.game.message, True, (0, 0, 0))
            self.screen.blit(message_text, (self.screen_width // 2 - message_text.get_width() // 2, self.board_y + 10 * self.cell_size - 30))

            score_text = self.font.render(f"Счет: Игрок 1 - {self.game.score_manager.get_score(1)} | Игрок 2 - {self.game.score_manager.get_score(2)}", True, (0, 0, 0))
            self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, self.board_y + 10 * self.cell_size - 5))

            self.draw_button(self.screen_width // 2 - 100, self.board_y + 10 * self.cell_size + 20, 200, 40, "Авторасстановка")
            self.draw_button(self.screen_width // 2 - 100, self.board_y + 10 * self.cell_size + 70, 200, 40, "Повернуть корабль")

            ship_info = f"Размещаемый корабль: {self.game.selected_ship_size}-палубный"
            info_surface = self.font.render(ship_info, True, (0, 0, 139))
            self.screen.blit(info_surface, (self.screen_width // 2 - info_surface.get_width() // 2, self.board_y + 10 * self.cell_size + 120))

            ships_left = sum(self.game.available_ships[size] - self.game.placed_ships[size] for size in [4, 3, 2, 1])
            counter_text = f"Осталось разместить: {ships_left} кораблей"
            counter_surface = self.font.render(counter_text, True, (0, 0, 0))
            self.screen.blit(counter_surface, (self.screen_width // 2 - counter_surface.get_width() // 2, self.board_y + 10 * self.cell_size + 150))

        elif self.game.game_state == "playing":
            # В режиме игры показываем корабли на своей доске, на чужой - только выстрелы
            if self.game.current_player == 1:
                self.draw_board(self.game.player1_board, self.board1_x, self.board_y, show_ships=True)
                self.draw_board(self.game.player2_board, self.board2_x, self.board_y, show_ships=False)
            else:
                self.draw_board(self.game.player1_board, self.board1_x, self.board_y, show_ships=False)
                self.draw_board(self.game.player2_board, self.board2_x, self.board_y, show_ships=True)

            message_text = self.font.render(self.game.message, True, (0, 0, 0))
            self.screen.blit(message_text, (self.screen_width // 2 - message_text.get_width() // 2, self.board_y + 10 * self.cell_size - 30))

            score_text = self.font.render(f"Счет: Игрок 1 - {self.game.score_manager.get_score(1)} | Игрок 2 - {self.game.score_manager.get_score(2)}", True, (0, 0, 0))
            self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, self.board_y + 10 * self.cell_size - 5))

            turn_indicator = "ХОД ИГРОКА 1" if self.game.current_player == 1 else "ХОД ИГРОКА 2"
            turn_color = (0, 150, 0) if self.game.current_player == 1 else (200, 0, 0)
            turn_surface = self.font.render(turn_indicator, True, turn_color)
            self.screen.blit(turn_surface, (self.screen_width // 2 - turn_surface.get_width() // 2, self.board_y + 10 * self.cell_size + 30))

        elif self.game.game_state == "game_over":
            # В конце игры показываем все корабли на обеих досках
            self.draw_board(self.game.player1_board, self.board1_x, self.board_y, show_ships=True)
            self.draw_board(self.game.player2_board, self.board2_x, self.board_y, show_ships=True)

            message_text = self.font.render(self.game.message, True, (0, 0, 0))
            self.screen.blit(message_text, (self.screen_width // 2 - message_text.get_width() // 2, self.board_y + 10 * self.cell_size - 30))

            score_text = self.font.render(f"Счет: Игрок 1 - {self.game.score_manager.get_score(1)} | Игрок 2 - {self.game.score_manager.get_score(2)}", True, (0, 0, 0))
            self.screen.blit(score_text, (self.screen_width // 2 - score_text.get_width() // 2, self.board_y + 10 * self.cell_size - 5))

            self.draw_button(self.screen_width // 2 - 100, self.board_y + 10 * self.cell_size + 20, 200, 40, "Новая игра")