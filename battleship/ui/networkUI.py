import pygame
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class MultiplayerUI:
    def __init__(self, game, network_client):
        self.game = game
        self.network_client = network_client
        
        # Настройки экрана
        self.screen_width = 1400
        self.screen_height = 900
        self.cell_size = 40
        self.margin = 80
        self.board1_x = self.margin
        self.board2_x = self.screen_width - self.margin - 10 * self.cell_size
        self.board_y = 180
        
        # Создание экрана
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Морской бой - Сетевая игра")
        
        # Шрифты
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.chat_font = pygame.font.SysFont('Arial', 18)
        
        # Состояние чата
        self.chat_input = ""
        self.chat_active = False
        self.chat_scroll_offset = 0
        
        # Кнопки
        self.buttons = {}
    
    def draw_board(self, board, x, y, show_ships=True, is_current_player=False):
        # Фон поля
        pygame.draw.rect(self.screen, (240, 240, 240), (x-5, y-5, 
                        10*self.cell_size+10, 10*self.cell_size+10))
        
        # Сетка
        for i in range(11):
            pygame.draw.line(self.screen, (0, 0, 0), 
                           (x, y + i * self.cell_size), 
                           (x + 10 * self.cell_size, y + i * self.cell_size), 2)
            pygame.draw.line(self.screen, (0, 0, 0), 
                           (x + i * self.cell_size, y), 
                           (x + i * self.cell_size, y + 10 * self.cell_size), 2)
        
        # Буквы и цифры
        for i in range(10):
            letter = self.font.render(chr(65 + i), True, (0, 0, 0))
            number = self.font.render(str(i + 1), True, (0, 0, 0))
            self.screen.blit(letter, (x + i * self.cell_size + self.cell_size//2 - 5, y - 30))
            self.screen.blit(number, (x - 30, y + i * self.cell_size + self.cell_size//2 - 10))
        
        # Корабли
        if show_ships:
            for ship in board.ships:
                for pos in ship.positions:
                    px, py = pos
                    color = (0, 100, 0) if is_current_player else (0, 0, 139)
                    pygame.draw.rect(self.screen, color, 
                                   (x + px * self.cell_size + 2, 
                                    y + py * self.cell_size + 2, 
                                    self.cell_size - 4, self.cell_size - 4))
        
        # Выстрелы
        for i in range(10):
            for j in range(10):
                if board.shots[j][i]:
                    if board.grid[j][i] == 1:  # Попадание
                        pygame.draw.circle(self.screen, (255, 0, 0), 
                                         (x + i * self.cell_size + self.cell_size//2, 
                                          y + j * self.cell_size + self.cell_size//2), 
                                          self.cell_size//3)
                        # Обводка для лучшей видимости
                        pygame.draw.circle(self.screen, (0, 0, 0), 
                                         (x + i * self.cell_size + self.cell_size//2, 
                                          y + j * self.cell_size + self.cell_size//2), 
                                          self.cell_size//3, 1)
                    else:  # Промах
                        pygame.draw.circle(self.screen, (0, 0, 255), 
                                         (x + i * self.cell_size + self.cell_size//2, 
                                          y + j * self.cell_size + self.cell_size//2), 
                                          self.cell_size//6)
    
    def draw_ship_preview(self, x, y, board_x, board_y):
        if self.game.game_state == "placing":
            ship_size = self.game.selected_ship_size
            orientation = self.game.ship_orientation
            
            # Проверка границ
            can_place = True
            if orientation == 0:  # Горизонтально
                if x + ship_size > 10:
                    can_place = False
            else:  # Вертикально
                if y + ship_size > 10:
                    can_place = False
            
            color = (0, 200, 0) if can_place else (200, 0, 0)
            alpha_surface = pygame.Surface((ship_size * self.cell_size if orientation == 0 else self.cell_size,
                                          self.cell_size if orientation == 0 else ship_size * self.cell_size),
                                          pygame.SRCALPHA)
            pygame.draw.rect(alpha_surface, (*color, 150), alpha_surface.get_rect())
            
            if orientation == 0:
                self.screen.blit(alpha_surface, (board_x + x * self.cell_size, board_y + y * self.cell_size))
            else:
                self.screen.blit(alpha_surface, (board_x + x * self.cell_size, board_y + y * self.cell_size))
    
    def draw_button(self, x, y, width, height, text, color=(173, 216, 230), hover_color=(135, 206, 250)):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = (x <= mouse_pos[0] <= x + width and 
                     y <= mouse_pos[1] <= y + height)
        
        button_color = hover_color if is_hovered else color
        pygame.draw.rect(self.screen, button_color, (x, y, width, height))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, width, height), 2)
        
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
        self.screen.blit(text_surface, text_rect)
        
        return (x, y, width, height, text)
    
    def draw_chat(self):
        chat_x = self.screen_width - 320
        chat_y = 120
        chat_width = 300
        chat_height = 400
        
        # Фон чата
        pygame.draw.rect(self.screen, (250, 250, 250), (chat_x, chat_y, chat_width, chat_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (chat_x, chat_y, chat_width, chat_height), 2)
        
        # Заголовок чата
        title_bg = pygame.Rect(chat_x, chat_y, chat_width, 30)
        pygame.draw.rect(self.screen, (70, 130, 180), title_bg)
        pygame.draw.rect(self.screen, (0, 0, 0), title_bg, 1)
        
        chat_title = self.font.render("ЧАТ ИГРЫ", True, (255, 255, 255))
        self.screen.blit(chat_title, (chat_x + chat_width//2 - chat_title.get_width()//2, chat_y + 5))
        
        # Сообщения
        messages_area = pygame.Rect(chat_x + 5, chat_y + 35, chat_width - 10, chat_height - 80)
        pygame.draw.rect(self.screen, (255, 255, 255), messages_area)
        pygame.draw.rect(self.screen, (200, 200, 200), messages_area, 1)
        
        # Прокрутка сообщений
        visible_messages = self.network_client.chat_messages[-10 + self.chat_scroll_offset:]
        message_y = chat_y + 40
        
        for msg in visible_messages:
            player_color = (0, 100, 200) if msg['player'] == self.network_client.player_id else (200, 100, 0)
            player_text = f"Игрок {msg['player']}:"
            
            player_surface = self.chat_font.render(player_text, True, player_color)
            self.screen.blit(player_surface, (chat_x + 10, message_y))
            
            # Перенос текста
            text = msg['text']
            words = text.split(' ')
            line = ""
            text_y = message_y + 20
            
            for word in words:
                test_line = line + word + " "
                if self.chat_font.size(test_line)[0] < chat_width - 20:
                    line = test_line
                else:
                    if line:
                        text_surface = self.chat_font.render(line, True, (0, 0, 0))
                        self.screen.blit(text_surface, (chat_x + 10, text_y))
                        text_y += 20
                    line = word + " "
            
            if line:
                text_surface = self.chat_font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surface, (chat_x + 10, text_y))
            
            message_y = text_y + 30
            if message_y > chat_y + chat_height - 40:
                break
        
        # Поле ввода
        input_bg = pygame.Rect(chat_x, chat_y + chat_height - 40, chat_width, 40)
        pygame.draw.rect(self.screen, (255, 255, 255), input_bg)
        pygame.draw.rect(self.screen, (0, 0, 0), input_bg, 2)
        
        if self.chat_active:
            input_text = self.chat_input + "|"
            input_color = (0, 0, 0)
        else:
            input_text = "Нажмите здесь чтобы писать..."
            input_color = (150, 150, 150)
        
        input_surface = self.chat_font.render(input_text, True, input_color)
        self.screen.blit(input_surface, (chat_x + 10, chat_y + chat_height - 30))
    
    def draw_game_info(self):
        # Заголовок
        title = self.title_font.render("МОРСКОЙ БОЙ - СЕТЕВАЯ ИГРА", True, (0, 0, 139))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 20))
        
        # Информация о подключении
        status_color = (0, 150, 0) if self.network_client.connected else (200, 0, 0)
        status_text = f"Статус: {'ПОДКЛЮЧЕН' if self.network_client.connected else 'ОТКЛЮЧЕН'}"
        status_surface = self.font.render(status_text, True, status_color)
        self.screen.blit(status_surface, (20, 80))
        
        player_text = f"Ваш ID: {self.network_client.player_id}" if self.network_client.player_id else "Ожидание ID..."
        player_surface = self.font.render(player_text, True, (0, 0, 0))
        self.screen.blit(player_surface, (20, 110))
        
        # Игроки
        player1_text = "Игрок 1 (ВЫ)" if self.network_client.player_id == 1 else "Игрок 1"
        player2_text = "Игрок 2 (ВЫ)" if self.network_client.player_id == 2 else "Игрок 2"
        
        p1_surface = self.font.render(player1_text, True, (0, 0, 0))
        p2_surface = self.font.render(player2_text, True, (0, 0, 0))
        
        self.screen.blit(p1_surface, (self.board1_x + 10*self.cell_size//2 - p1_surface.get_width()//2, self.board_y - 50))
        self.screen.blit(p2_surface, (self.board2_x + 10*self.cell_size//2 - p2_surface.get_width()//2, self.board_y - 50))
        
        # Состояние игры - ПОДНЯЛИ К СЕРЕДИНЕ
        message_color = (0, 0, 0)
        if "победил" in self.game.message or "победа" in self.game.message.lower():
            message_color = (0, 150, 0)
        elif "ход" in self.game.message.lower():
            message_color = (0, 0, 150)
        
        message_surface = self.font.render(self.game.message, True, message_color)
        self.screen.blit(message_surface, (self.screen_width//2 - message_surface.get_width()//2, 
                                         self.board_y + 10*self.cell_size - 40))
        
        # Счет - ПОДНЯЛИ К СЕРЕДИНЕ
        score_text = self.font.render(f"Счет: Игрок 1 - {self.game.score_manager.get_score(1)} | Игрок 2 - {self.game.score_manager.get_score(2)}", True, (0, 0, 0))
        self.screen.blit(score_text, (self.screen_width//2 - score_text.get_width()//2, 
                                    self.board_y + 10*self.cell_size - 15))
    
    def draw_control_panel(self):
        # ПАНЕЛЬ УПРАВЛЕНИЯ - ПОДНЯЛИ К СЕРЕДИНЕ
        panel_y = self.board_y + 10*self.cell_size + 10
        center_x = self.screen_width//2
        
        if self.game.game_state == "waiting":
            self.draw_button(center_x - 100, panel_y, 200, 40, "ГОТОВ К ИГРЕ", 
                           (144, 238, 144), (152, 251, 152))
        
        elif self.game.game_state == "placing":
            self.draw_button(center_x - 100, panel_y, 200, 40, "АВТОРАССТАНОВКА")
            self.draw_button(center_x - 100, panel_y + 50, 200, 40, "ПОВЕРНУТЬ КОРАБЛЬ")
            
            # Информация о текущем корабле - ПОДНЯЛИ К СЕРЕДИНЕ
            ship_info = f"Размещаемый корабль: {self.game.selected_ship_size}-палубный"
            info_surface = self.font.render(ship_info, True, (0, 0, 139))
            self.screen.blit(info_surface, (center_x - info_surface.get_width()//2, panel_y + 110))
            
            # Счетчик кораблей - ПОДНЯЛИ К СЕРЕДИНЕ
            ships_left = sum(self.game.available_ships[size] - self.game.placed_ships[size] 
                           for size in [4, 3, 2, 1])
            counter_text = f"Осталось разместить: {ships_left} кораблей"
            counter_surface = self.font.render(counter_text, True, (0, 0, 0))
            self.screen.blit(counter_surface, (center_x - counter_surface.get_width()//2, panel_y + 140))
        
        elif self.game.game_state == "playing":
            turn_indicator = "ВАШ ХОД" if self.game.current_player == self.network_client.player_id else "ХОД ПРОТИВНИКА"
            turn_color = (0, 150, 0) if self.game.current_player == self.network_client.player_id else (200, 0, 0)
            
            turn_surface = self.font.render(turn_indicator, True, turn_color)
            self.screen.blit(turn_surface, (center_x - turn_surface.get_width()//2, panel_y))
        
        elif self.game.game_state == "game_over":
            self.draw_button(center_x - 100, panel_y, 200, 40, "НОВАЯ ИГРА", 
                           (255, 215, 0), (255, 225, 50))
    
    def draw(self):
        self.screen.fill((245, 245, 245))  # Светло-серый фон
        
        # Отрисовка элементов
        self.draw_game_info()
        
        # Игровые поля
        if self.game.game_state == "placing":
            # В режиме расстановки показываем корабли только у текущего игрока
            is_current_player = (self.game.placing_player == self.network_client.player_id)
            
            # Поле игрока 1 - показываем корабли только если это текущий игрок
            show_ships1 = (self.network_client.player_id == 1 and is_current_player)
            self.draw_board(self.game.player1_board, self.board1_x, self.board_y, 
                          show_ships=show_ships1, is_current_player=(self.network_client.player_id == 1))
            
            # Поле игрока 2 - показываем корабли только если это текущий игрок
            show_ships2 = (self.network_client.player_id == 2 and is_current_player)
            self.draw_board(self.game.player2_board, self.board2_x, self.board_y, 
                          show_ships=show_ships2, is_current_player=(self.network_client.player_id == 2))
            
            # Предпросмотр корабля
            if is_current_player:
                mouse_pos = pygame.mouse.get_pos()
                board_x = self.board1_x if self.network_client.player_id == 1 else self.board2_x
                
                if (board_x <= mouse_pos[0] < board_x + 10*self.cell_size and 
                    self.board_y <= mouse_pos[1] < self.board_y + 10*self.cell_size):
                    cell_x = (mouse_pos[0] - board_x) // self.cell_size
                    cell_y = (mouse_pos[1] - self.board_y) // self.cell_size
                    self.draw_ship_preview(cell_x, cell_y, board_x, self.board_y)
        
        elif self.game.game_state == "playing":
            # В режиме игры показываем свое поле с кораблями и поле противника без кораблей
            is_current_turn = self.game.current_player == self.network_client.player_id
            my_board_x = self.board1_x if self.network_client.player_id == 1 else self.board2_x
            opponent_board_x = self.board2_x if self.network_client.player_id == 1 else self.board1_x
            
            self.draw_board(self.game.get_current_board(), my_board_x, self.board_y, 
                          show_ships=True, is_current_player=True)
            self.draw_board(self.game.get_opponent_board(), opponent_board_x, self.board_y, 
                          show_ships=False, is_current_player=False)
        
        elif self.game.game_state == "game_over":
            # После игры показываем все поля с кораблями
            self.draw_board(self.game.player1_board, self.board1_x, self.board_y, 
                          show_ships=True, is_current_player=self.network_client.player_id == 1)
            self.draw_board(self.game.player2_board, self.board2_x, self.board_y, 
                          show_ships=True, is_current_player=self.network_client.player_id == 2)
        
        # Панель управления и чат
        self.draw_control_panel()
        self.draw_chat()