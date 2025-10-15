import pygame

class MultiplayerUI:
    def __init__(self, game, network_client):
        self.game = game
        self.network_client = network_client
        
        self.screen_width = 1700
        self.screen_height = 900
        self.cell_size = 40
        self.margin = 80
        self.board1_x = self.margin
        self.board2_x = self.screen_width - self.margin - 10 * self.cell_size
        self.board_y = 180
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Морской бой - Сетевая игра")
        
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.chat_font = pygame.font.SysFont('Arial', 18)
        
        self.chat_input = ""
        self.chat_active = False
        self.chat_scroll_offset = 0
        
        self.buttons = {}
    
    def draw_board(self, board, x, y, show_ships=True, is_current_player=False):
        pygame.draw.rect(self.screen, (240, 240, 240), (x-5, y-5, 
                        10*self.cell_size+10, 10*self.cell_size+10))

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
                        color = (200, 0, 0)
                    else:
                        color = (0, 150, 0)

                    pygame.draw.rect(self.screen, color, 
                                   (x + px * self.cell_size + 2, 
                                    y + py * self.cell_size + 2, 
                                    self.cell_size - 4, self.cell_size - 4))
                    pygame.draw.rect(self.screen, (0, 0, 0), 
                                   (x + px * self.cell_size + 2, 
                                    y + py * self.cell_size + 2, 
                                    self.cell_size - 4, self.cell_size - 4), 1)

        for i in range(10):
            for j in range(10):
                if board.shots[j][i]:
                    if board.grid[j][i] == 1:
                        pygame.draw.line(self.screen, (255, 0, 0), 
                                       (x + i * self.cell_size + 8, y + j * self.cell_size + 8),
                                       (x + (i+1) * self.cell_size - 8, y + (j+1) * self.cell_size - 8), 3)
                        pygame.draw.line(self.screen, (255, 0, 0), 
                                       (x + (i+1) * self.cell_size - 8, y + j * self.cell_size + 8),
                                       (x + i * self.cell_size + 8, y + (j+1) * self.cell_size - 8), 3)
                    else:
                        pygame.draw.circle(self.screen, (0, 0, 200), 
                                         (x + i * self.cell_size + self.cell_size//2, 
                                          y + j * self.cell_size + self.cell_size//2), 
                                          self.cell_size//6)
    
    def draw_ship_preview(self, x, y, board_x, board_y, ship_size, orientation):
        """Рисует предпросмотр корабля при размещении"""
        can_place = True

        if orientation == 0:
            if x + ship_size > 10:
                can_place = False
        else:
            if y + ship_size > 10:
                can_place = False

        color = (0, 200, 0) if can_place else (200, 0, 0)

        if orientation == 0:
            preview_surface = pygame.Surface((ship_size * self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.rect(preview_surface, (*color, 150), (0, 0, ship_size * self.cell_size, self.cell_size))
            self.screen.blit(preview_surface, (board_x + x * self.cell_size, board_y + y * self.cell_size))
        else:
            preview_surface = pygame.Surface((self.cell_size, ship_size * self.cell_size), pygame.SRCALPHA)
            pygame.draw.rect(preview_surface, (*color, 150), (0, 0, self.cell_size, ship_size * self.cell_size))
            self.screen.blit(preview_surface, (board_x + x * self.cell_size, board_y + y * self.cell_size))
    
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
        chat_x = self.screen_width - 1000
        chat_y = 120
        chat_width = 300
        chat_height = 400
        
        pygame.draw.rect(self.screen, (250, 250, 250), (chat_x, chat_y, chat_width, chat_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (chat_x, chat_y, chat_width, chat_height), 2)
        
        title_bg = pygame.Rect(chat_x, chat_y, chat_width, 30)
        pygame.draw.rect(self.screen, (70, 130, 180), title_bg)
        pygame.draw.rect(self.screen, (0, 0, 0), title_bg, 1)
        
        chat_title = self.font.render("ЧАТ ИГРЫ", True, (255, 255, 255))
        self.screen.blit(chat_title, (chat_x + chat_width//2 - chat_title.get_width()//2, chat_y + 5))
        
        messages_area = pygame.Rect(chat_x + 5, chat_y + 35, chat_width - 10, chat_height - 80)
        pygame.draw.rect(self.screen, (240, 240, 240), messages_area)
        pygame.draw.rect(self.screen, (200, 200, 200), messages_area, 1)
        
        all_messages = self.network_client.chat_messages
        visible_messages = all_messages[-15:] if all_messages else []
        
        current_y = messages_area.bottom - 10
        
        for i in range(len(visible_messages)-1, -1, -1):
            msg = visible_messages[i]

            if msg['player'] == 0: 
                text_color = (100, 100, 100)
                prefix = "Система"
            elif msg['player'] == self.network_client.player_id:
                text_color = (0, 100, 200)
                prefix = "Вы"
            else: 
                text_color = (200, 100, 0)
                prefix = f"Игрок {msg['player']}"

            display_text = f"{prefix}: {msg['text']}"
            text_surface = self.chat_font.render(display_text, True, text_color)

            if text_surface.get_width() > messages_area.width - 10:
                temp_text = display_text
                while self.chat_font.render(temp_text, True, text_color).get_width() > messages_area.width - 10 and len(temp_text) > 5:
                    temp_text = temp_text[:-1]
                text_surface = self.chat_font.render(temp_text + "...", True, text_color)

            if current_y - text_surface.get_height() < messages_area.top:
                break 
            
            self.screen.blit(text_surface, (messages_area.left + 5, current_y - text_surface.get_height()))

            current_y -= text_surface.get_height() + 5
        
        input_bg = pygame.Rect(chat_x, chat_y + chat_height - 40, chat_width, 40)
        input_color = (220, 220, 255) if self.chat_active else (255, 255, 255)
        pygame.draw.rect(self.screen, input_color, input_bg)
        pygame.draw.rect(self.screen, (0, 0, 0), input_bg, 2)
        
        if self.chat_active:
            input_text = self.chat_input + "|" 
            text_color = (0, 0, 0)
        else:
            input_text = "Нажмите здесь или T чтобы писать..."
            text_color = (150, 150, 150)
        
        input_surface = self.chat_font.render(input_text, True, text_color)
        
        max_text_width = chat_width - 20
        if input_surface.get_width() > max_text_width:
            temp_text = self.chat_input if self.chat_active else input_text
            while self.chat_font.render(temp_text, True, text_color).get_width() > max_text_width and len(temp_text) > 1:
                temp_text = temp_text[:-1]
            display_text = temp_text + ("|" if self.chat_active else "")
            input_surface = self.chat_font.render(display_text, True, text_color)
        
        self.screen.blit(input_surface, (chat_x + 10, chat_y + chat_height - 30))
        
        if self.chat_active:
            hint_text = "Enter - отправить, Esc - отмена"
            hint_surface = self.chat_font.render(hint_text, True, (100, 100, 100))
            self.screen.blit(hint_surface, (chat_x + 5, chat_y + chat_height + 5))

    def wrap_text(self, text, font, max_width):
        """Переносит текст на несколько строк если он слишком широкий"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]

            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))
    
        return lines
        
    def draw_game_info(self):
        title = self.title_font.render("МОРСКОЙ БОЙ - СЕТЕВАЯ ИГРА", True, (0, 0, 139))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 20))

        status_color = (0, 150, 0) if self.network_client.connected else (200, 0, 0)
        status_text = f"Статус: {'ПОДКЛЮЧЕН' if self.network_client.connected else 'ОТКЛЮЧЕН'}"
        status_surface = self.font.render(status_text, True, status_color)
        self.screen.blit(status_surface, (20, 80))

        player_text = f"Ваш ID: {self.network_client.player_id}" if self.network_client.player_id else "Ожидание ID..."
        player_surface = self.font.render(player_text, True, (0, 0, 0))
        self.screen.blit(player_surface, (20, 110))

        state_text = ""
        state_color = (0, 0, 0)

        if self.game.game_state == "waiting":
            state_text = "ОЖИДАНИЕ ПОДКЛЮЧЕНИЯ ИГРОКОВ"
            state_color = (100, 100, 100)
        elif self.game.game_state == "placing":
            if self.game.placing_player == self.network_client.player_id:
                state_text = "ВАША ОЧЕРЕДЬ: РАССТАВЛЯЙТЕ КОРАБЛИ"
                state_color = (0, 150, 0)
            else:
                state_text = f"ОЖИДАНИЕ: Игрок {self.game.placing_player} расставляет корабли"
                state_color = (200, 0, 0)
        elif self.game.game_state == "playing":
            if self.game.current_player == self.network_client.player_id:
                state_text = "ВАШ ХОД - СТРЕЛЯЙТЕ ПО ДОСКЕ ПРОТИВНИКА!"
                state_color = (0, 150, 0)
            else:
                state_text = "ХОД ПРОТИВНИКА - ОЖИДАЙТЕ..."
                state_color = (200, 0, 0)
        elif self.game.game_state == "game_over":
            state_text = "ИГРА ОКОНЧЕНА"
            state_color = (150, 0, 150)

        state_surface = self.font.render(state_text, True, state_color)
        self.screen.blit(state_surface, (self.screen_width//2 - state_surface.get_width()//2, 60))

        message_color = (0, 0, 0)
        if "победил" in self.game.message or "победа" in self.game.message.lower():
            message_color = (0, 150, 0)
        elif "ход" in self.game.message.lower():
            message_color = (0, 0, 150)
        elif "ошибка" in self.game.message.lower():
            message_color = (200, 0, 0)

        message_surface = self.font.render(self.game.message, True, message_color)
        self.screen.blit(message_surface, (self.screen_width//2 - message_surface.get_width()//2, 
                                         self.board_y + 10*self.cell_size - 40))
    
    def draw_control_panel(self):
        panel_y = self.board_y + 10 * self.cell_size + 10
        center_x = self.screen_width // 2

        if self.game.game_state == "waiting":
            self.draw_button(center_x - 100, panel_y, 200, 40, "ГОТОВ К ИГРЕ", 
                           (144, 238, 144), (152, 251, 152))

        elif self.game.game_state == "placing":
            is_our_turn = (self.game.placing_player == self.network_client.player_id)

            if is_our_turn:
                self.draw_button(center_x - 100, panel_y, 200, 40, "АВТОРАССТАНОВКА")

                self.draw_button(center_x - 100, panel_y + 50, 200, 40, "ПОВЕРНУТЬ КОРАБЛЬ")
                ship_size = getattr(self.game, 'selected_ship_size', 4)

                orientation = getattr(self.game, 'ship_orientation', 0)
                orientation_text = "вертикальная" if orientation == 1 else "горизонтальная"
                ship_info = f"Размещаемый корабль: {ship_size}-палубный ({orientation_text})"
                info_surface = self.font.render(ship_info, True, (0, 0, 139))
                self.screen.blit(info_surface, (center_x - info_surface.get_width()//2, panel_y + 100))

                placed_ships = getattr(self.game, 'placed_ships', {4: 0, 3: 0, 2: 0, 1: 0})
                available_ships = getattr(self.game, 'available_ships', {4: 1, 3: 2, 2: 3, 1: 4})

                ships_info = []
                for size in [4, 3, 2, 1]:
                    placed = placed_ships.get(size, 0)
                    available = available_ships.get(size, 0)
                    remaining = available - placed
                    if remaining > 0:
                        ships_info.append(f"{size}-палубных: {remaining}")

                if ships_info:
                    ships_text = "Осталось разместить: " + ", ".join(ships_info)
                    ships_surface = self.font.render(ships_text, True, (0, 0, 0))
                    self.screen.blit(ships_surface, (center_x - ships_surface.get_width()//2, panel_y + 130))
                else:
                    ships_text = "Все корабли размещены!"
                    ships_surface = self.font.render(ships_text, True, (0, 150, 0))
                    self.screen.blit(ships_surface, (center_x - ships_surface.get_width()//2, panel_y + 130))

                hint_text = "Кликните на свою доску чтобы разместить корабль"
                hint_surface = self.chat_font.render(hint_text, True, (100, 100, 100))
                self.screen.blit(hint_surface, (center_x - hint_surface.get_width()//2, panel_y + 160))

            else:
                wait_text = f"Ожидаем расстановки кораблей игроком {self.game.placing_player}"
                wait_surface = self.font.render(wait_text, True, (200, 0, 0))
                self.screen.blit(wait_surface, (center_x - wait_surface.get_width()//2, panel_y))

                placed_ships = getattr(self.game, 'placed_ships', {4: 0, 3: 0, 2: 0, 1: 0})
                total_placed = sum(placed_ships.values())
                total_ships = 10  

                progress_text = f"Прогресс: {total_placed}/{total_ships} кораблей"
                progress_surface = self.font.render(progress_text, True, (0, 0, 150))
                self.screen.blit(progress_surface, (center_x - progress_surface.get_width()//2, panel_y + 40))

        elif self.game.game_state == "playing":
            current_player = getattr(self.game, 'current_player', 1)
            if current_player == self.network_client.player_id:
                turn_text = "ВАШ ХОД - стреляйте по доске противника"
                turn_color = (0, 150, 0)
            else:
                turn_text = f"ХОД ИГРОКА {current_player} - ожидайте..."
                turn_color = (200, 0, 0)

            turn_surface = self.font.render(turn_text, True, turn_color)
            self.screen.blit(turn_surface, (center_x - turn_surface.get_width()//2, panel_y))

        elif self.game.game_state == "game_over":
            self.draw_button(center_x - 100, panel_y, 200, 40, "НОВАЯ ИГРА", 
                           (255, 215, 0), (255, 225, 50))

    def handle_click(self, mouse_x, mouse_y):
        try:
            board1_x, board2_x, board_y = self.board1_x, self.board2_x, self.board_y
            center_x = self.ui.screen_width // 2

            button_y = board_y + 10 * self.ui.cell_size + 10

            if self.game.game_state == "waiting":
                if center_x - 100 <= mouse_x <= center_x + 100 and button_y <= mouse_y <= button_y + 40:
                    self.send_ready()

            elif self.game.game_state == "placing":
                if center_x - 100 <= mouse_x <= center_x + 100 and button_y <= mouse_y <= button_y + 40:
                    self.send_auto_place()

                elif center_x - 100 <= mouse_x <= center_x + 100 and button_y + 50 <= mouse_y <= button_y + 90:
                    self.game.rotate_ship()

                if self.player_id == 1:
                    board_x = board1_x
                else:
                    board_x = board2_x

                if (board_x <= mouse_x < board_x + 10 * self.ui.cell_size and 
                    board_y <= mouse_y < board_y + 10 * self.ui.cell_size):
                    cell_x = (mouse_x - board_x) // self.ui.cell_size
                    cell_y = (mouse_y - board_y) // self.ui.cell_size

                    if 0 <= cell_x < 10 and 0 <= cell_y < 10:
                        self.send_ship_placement(cell_x, cell_y, 
                                            self.game.selected_ship_size,
                                            self.game.ship_orientation)

            elif self.game.game_state == "playing":
                if self.game.current_player == self.player_id:
                    opponent_board_x = board2_x if self.player_id == 1 else board1_x

                    if (opponent_board_x <= mouse_x < opponent_board_x + 10 * self.ui.cell_size and 
                        board_y <= mouse_y < board_y + 10 * self.ui.cell_size):
                        cell_x = (mouse_x - opponent_board_x) // self.ui.cell_size
                        cell_y = (mouse_y - board_y) // self.ui.cell_size

                        if 0 <= cell_x < 10 and 0 <= cell_y < 10:
                            opponent_board = self.game.get_opponent_board()
                            if not opponent_board.shots[cell_y][cell_x]:
                                self.send_shot(cell_x, cell_y)

            elif self.game.game_state == "game_over":
                if center_x - 100 <= mouse_x <= center_x + 100 and button_y <= mouse_y <= button_y + 40:
                    self.game.reset_game()
                    self.send_ready()

        except Exception as e:
            print(f"Ошибка обработки клика: {e}")

    def can_place_ship(self, board, x, y, size, orientation):
        """Проверяет можно ли разместить корабль в указанной позиции"""
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

    def draw(self):
        self.screen.fill((245, 245, 245))

        self.draw_game_info()

        if self.game.game_state == "placing":
            is_current_turn = (self.game.placing_player == self.network_client.player_id)

            show_ships_player1 = (self.network_client.player_id == 1)
            show_ships_player2 = (self.network_client.player_id == 2)

            self.draw_board(self.game.player1_board, self.board1_x, self.board_y, 
                          show_ships=show_ships_player1, is_current_player=(self.network_client.player_id == 1))

            self.draw_board(self.game.player2_board, self.board2_x, self.board_y, 
                          show_ships=show_ships_player2, is_current_player=(self.network_client.player_id == 2))

            if is_current_turn:
                mouse_pos = pygame.mouse.get_pos()

                our_board_x = self.board1_x if self.network_client.player_id == 1 else self.board2_x

                if (our_board_x <= mouse_pos[0] < our_board_x + 10 * self.cell_size and 
                    self.board_y <= mouse_pos[1] < self.board_y + 10 * self.cell_size):

                    cell_x = (mouse_pos[0] - our_board_x) // self.cell_size
                    cell_y = (mouse_pos[1] - self.board_y) // self.cell_size

                    board = self.game.player1_board if self.network_client.player_id == 1 else self.game.player2_board
                    can_place = self.can_place_ship(board, cell_x, cell_y, 
                                                  self.game.selected_ship_size, 
                                                  self.game.ship_orientation)

                    color = (0, 200, 0) if can_place else (200, 0, 0)
                    self.draw_ship_preview(cell_x, cell_y, our_board_x, self.board_y, 
                                         self.game.selected_ship_size, self.game.ship_orientation)

        elif self.game.game_state == "playing":
            if self.network_client.player_id == 1:
                my_board = self.game.player1_board
                my_board_x = self.board1_x
                opponent_board = self.game.player2_board
                opponent_board_x = self.board2_x
            else:
                my_board = self.game.player2_board
                my_board_x = self.board2_x
                opponent_board = self.game.player1_board
                opponent_board_x = self.board1_x

            self.draw_board(my_board, my_board_x, self.board_y, 
                          show_ships=True, is_current_player=True)

            self.draw_board(opponent_board, opponent_board_x, self.board_y, 
                          show_ships=False, is_current_player=False)
            if self.network_client.player_id == 1:
                my_label = "ВАША ДОСКА"
                opponent_label = "ДОСКА ПРОТИВНИКА"
            else:
                my_label = "ВАША ДОСКА" 
                opponent_label = "ДОСКА ПРОТИВНИКА"

            my_label_surface = self.font.render(my_label, True, (0, 100, 0))
            opponent_label_surface = self.font.render(opponent_label, True, (200, 0, 0))

            if self.network_client.player_id == 1:
                self.screen.blit(my_label_surface, (self.board1_x + 10*self.cell_size//2 - my_label_surface.get_width()//2, self.board_y - 50))
                self.screen.blit(opponent_label_surface, (self.board2_x + 10*self.cell_size//2 - opponent_label_surface.get_width()//2, self.board_y - 50))
            else:
                self.screen.blit(opponent_label_surface, (self.board1_x + 10*self.cell_size//2 - opponent_label_surface.get_width()//2, self.board_y - 50))
                self.screen.blit(my_label_surface, (self.board2_x + 10*self.cell_size//2 - my_label_surface.get_width()//2, self.board_y - 50))

        elif self.game.game_state == "game_over":
            self.draw_board(self.game.player1_board, self.board1_x, self.board_y, 
                          show_ships=True, is_current_player=(self.network_client.player_id == 1))
            self.draw_board(self.game.player2_board, self.board2_x, self.board_y, 
                          show_ships=True, is_current_player=(self.network_client.player_id == 2))

        self.draw_control_panel()
        self.draw_chat()