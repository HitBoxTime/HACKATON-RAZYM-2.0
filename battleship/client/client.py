import socket
import threading
import json
import pygame
from ui.networkUI import MultiplayerUI
from game_logic.core import Game
import time

class BattleshipClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.player_id = None
        self.game = Game()
        self.ui = None
        self.connected = False
        
        self.chat_messages = []
        self.receive_buffer = ""

        self.sunken_ships_positions = []
        
    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            self.client_socket.settimeout(0.1)
            self.connected = True
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def receive_messages(self):
        while self.connected:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                
                self.receive_buffer += data.decode('utf-8')
                
                while '\n' in self.receive_buffer:
                    line, self.receive_buffer = self.receive_buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = json.loads(line)
                            self.process_message(message)
                        except json.JSONDecodeError:
                            pass
                
            except socket.timeout:
                continue
            except Exception:
                break
        
        self.connected = False
    
    def process_message(self, message):
        msg_type = message.get("type")
        
        if msg_type == "welcome":
            self.player_id = message["player_id"]
            welcome_msg = {
                "player": 0,
                "text": f"Вы подключились как Игрок {self.player_id}",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(welcome_msg)

        elif msg_type == "player_joined":
            player_id = message["player_id"]
            self.game.message = f"Игрок {player_id} присоединился. Ожидание готовности..."
            if player_id == self.player_id:
                self.game.game_state = "placing"
                self.game.placing_player = self.player_id
                self.game.selected_ship_size = 4
                self.game.placed_ships = {4: 0, 3: 0, 2: 0, 1: 0}

            join_msg = {
                "player": 0,
                "text": f"Игрок {player_id} присоединился к игре",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(join_msg)

        elif msg_type == "player_left":
            player_id = message["player_id"]
            self.game.message = message.get("message", f"Игрок {player_id} покинул игру")
            leave_msg = {
                "player": 0,
                "text": f"Игрок {player_id} покинул игру",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(leave_msg)
        
        elif msg_type == "ship_placed":
            placed_player = message["player"]
            x, y, size, orientation = message["x"], message["y"], message["size"], message["orientation"]       

            if placed_player == self.player_id:
                if self.player_id == 1:
                    board = self.game.player1_board
                else:
                    board = self.game.player2_board     

                success = board.place_ship(size, x, y, orientation)
                if success:
                    print(f"Успешно размещен корабль размером {size} в ({x},{y})")

                    self.game.placed_ships[size] += 1

                    next_size = None
                    for ship_size in [4, 3, 2, 1]:
                        if self.game.placed_ships[ship_size] < self.game.available_ships[ship_size]:
                            next_size = ship_size
                            break
                        
                    if next_size is not None:
                        self.game.selected_ship_size = next_size
                        self.game.message = f"Разместите {next_size}-палубный корабль"
                        print(f"Следующий корабль: {next_size}-палубный")
                    else:
                        self.game.message = "Все корабли размещены! Ожидайте начала игры."
                        print("Все корабли размещены!")

                else:
                    print(f"Ошибка размещения корабля размером {size} в ({x},{y})")

        elif msg_type == "ship_rotated":
            rotated_player = message["player"]
            if rotated_player == self.player_id:
                orientation_text = "вертикальная" if self.game.ship_orientation == 1 else "горизонтальная"
                rotate_msg = {
                   "player": 0,
                   "text": f"Игрок {rotated_player} повернул корабль ({orientation_text})",
                   "timestamp": pygame.time.get_ticks()
                }
                self.chat_messages.append(rotate_msg)

        elif msg_type == "game_start":
            self.game.game_state = "playing"
            if "player_ids" in message:
                player_ids = {}
                for k, v in message["player_ids"].items():
                    player_ids[int(k)] = v
                self.player_id = player_ids.get(self.player_id, self.player_id)
            self.game.current_player = message["current_player"]
            self.game.message = "Игра началась!" if self.game.current_player == self.player_id else "Ход противника"

            print(f"DEBUG: Начало игры! Player ID: {self.player_id}")
            print(f"DEBUG: Player1 ships: {len(self.game.player1_board.ships)}")
            print(f"DEBUG: Player2 ships: {len(self.game.player2_board.ships)}")

            start_msg = {
                "player": 0,
                "text": "=== ИГРА НАЧАЛАСЬ ===",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(start_msg)
        
        elif msg_type == "chat_update":
            new_messages = message.get("messages", [])
            if new_messages:
                self.chat_messages = new_messages

                if len(self.chat_messages) > 50:
                    self.chat_messages = self.chat_messages[-50:]
        
        elif msg_type == "shot_result":
            player = message["player"]
            result_data = message["result"]

            if isinstance(result_data, dict):
                result = result_data.get("result", "miss")
                ship_positions = result_data.get("ship_positions", [])
                surrounding_cells = result_data.get("surrounding_cells", [])
            else:
                result = result_data
                ship_positions = []
                surrounding_cells = []

            player_name = "Вы" if player == self.player_id else "Противник"

            if result == "hit":
                result_text = f"{player_name} попали в корабль!"
            elif result == "sunk":
                result_text = f"{player_name} потопили корабль!"
                if player == self.player_id:  
                    self.sunken_ships_positions.extend(ship_positions)

                for pos in surrounding_cells:
                    x, y = pos
                    if player == self.player_id: 
                        target_player = 2 if self.player_id == 1 else 1
                        if target_player == 1:
                            board = self.game.player1_board
                        else:
                            board = self.game.player2_board
                    else: 
                        if self.player_id == 1:
                            board = self.game.player1_board
                        else:
                            board = self.game.player2_board

                    board.shots[y][x] = True

            else:
                result_text = f"{player_name} промахнулись."

            self.game.message = result_text

            if player == self.player_id:
                target_player = 2 if self.player_id == 1 else 1
                if target_player == 1:
                    board = self.game.player1_board
                else:
                    board = self.game.player2_board

                x, y = message["x"], message["y"]
                if result == "hit" or result == "sunk":
                    board.grid[y][x] = 1 
                board.shots[y][x] = True 

            else: 
                if self.player_id == 1:
                    board = self.game.player1_board
                else:
                    board = self.game.player2_board

                x, y = message["x"], message["y"]
                if result == "hit" or result == "sunk":
                    board.grid[y][x] = 1 
                board.shots[y][x] = True 

            shot_msg = {
                "player": 0,
                "text": result_text,
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(shot_msg)
        
        elif msg_type == "turn_change":
            self.game.current_player = message["current_player"]
            if self.game.current_player == self.player_id:
                self.game.message = "Ваш ход! Стреляйте по доске противника."
            else:
                self.game.message = "Ход противника. Ожидайте..."

            turn_msg = {
                "player": 0,
                "text": f"Ход переходит к Игроку {message['current_player']}",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(turn_msg)

        elif msg_type == "game_over":
            self.game.game_state = "game_over"
            self.game.message = message["message"]

            end_msg = {
                "player": 0,
                "text": f"=== {message['message']} ===",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(end_msg)
        
        elif msg_type == "game_reset":
            self.game.reset_game()
            self.game.game_state = ("game_state", "waiting")
            self.game.message = "Игра сброшена. Нажмите 'Готов к игре' для новой партии."

            self.sunken_ships_positions = []

            reset_msg = {
                "player": 0,
                "text": "=== НОВАЯ ИГРА ===",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(reset_msg)

        elif msg_type == "game_state_change":
            self.game.game_state = message["game_state"]
            if "placing_player" in message:
                self.game.placing_player = message["placing_player"]
            self.game.message = message.get("message", "Состояние игры изменено")

        elif msg_type == "player_ready":
            ready_player = message["player"]
            ready_text = "Вы готовы к игре!" if ready_player == self.player_id else "Противник готов к игре!"
            self.game.message = ready_text

            ready_msg = {
                "player": 0,
                "text": f"Игрок {ready_player} готов",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(ready_msg)
        
        elif msg_type == "auto_placed":
            player = message["player"]
            ship_placements = message.get("ship_placements", [])

            if player == self.player_id:
                if self.player_id == 1:
                    board = self.game.player1_board
                else:
                    board = self.game.player2_board

                board.ships = []
                board.grid = [[0 for _ in range(10)] for _ in range(10)]
                board.shots = [[False for _ in range(10)] for _ in range(10)]

                for placement in ship_placements:
                    x = placement["x"]
                    y = placement["y"]
                    size = placement["size"]
                    orientation = placement["orientation"]

                    board.place_ship(size, x, y, orientation)

                print(f"Локальная доска синхронизирована. Кораблей: {len(board.ships)}")

                for size in [4, 3, 2, 1]:
                    self.game.placed_ships[size] = self.game.available_ships[size]

                self.game.message = "Все корабли размещены автоматически!"

            auto_text = "Вы использовали авторасстановку" if player == self.player_id else "Противник использовал авторасстановку"

            auto_msg = {
                "player": 0,
                "text": f"Игрок {player} использовал авторасстановку",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(auto_msg)

        elif msg_type == "error":
            error_text = message["message"]
            self.game.message = f"Ошибка: {error_text}"

            error_msg = {
                "player": 0,
                "text": f"Ошибка: {error_text}",
                "timestamp": pygame.time.get_ticks()
            }
            self.chat_messages.append(error_msg)

    def handle_click(self, mouse_x, mouse_y):
        board1_x, board2_x, board_y = self.ui.board1_x, self.ui.board2_x, self.ui.board_y
        center_x = self.ui.screen_width // 2
        button_y = board_y + 10 * self.ui.cell_size + 10
    
        if self.game.game_state == "waiting":
            if center_x - 100 <= mouse_x <= center_x + 100 and button_y <= mouse_y <= button_y + 40:
                self.send_ready()
    
        elif self.game.game_state == "placing":
            if center_x - 100 <= mouse_x <= center_x + 100 and button_y <= mouse_y <= button_y + 40:
                self.send_auto_place()
    
            elif center_x - 100 <= mouse_x <= center_x + 100 and button_y + 50 <= mouse_y <= button_y + 90:
                new_orientation = self.game.rotate_ship()
                self.send_rotate_ship()
                print(f"Повернут корабль. Новая ориентация: {'вертикальная' if new_orientation == 1 else 'горизонтальная'}")
    
            elif self.game.placing_player == self.player_id:
                if self.player_id == 1:
                    board_x = self.ui.board1_x
                else:
                    board_x = self.ui.board2_x
    
                if (board_x <= mouse_x < board_x + 10 * self.ui.cell_size and 
                    board_y <= mouse_y < board_y + 10 * self.ui.cell_size):
                    cell_x = (mouse_x - board_x) // self.ui.cell_size
                    cell_y = (mouse_y - board_y) // self.ui.cell_size
    
                    if 0 <= cell_x < 10 and 0 <= cell_y < 10:
                        print(f"Пытаемся разместить {self.game.selected_ship_size}-палубный корабль в ({cell_x},{cell_y})")
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
                        else:
                            print("Уже стреляли в эту клетку")
    
        elif self.game.game_state == "game_over":
            if center_x - 100 <= mouse_x <= center_x + 100 and button_y <= mouse_y <= button_y + 40:
                self.send_reset_game()
            

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
                        else:
                            print("Уже стреляли в эту клетку")

        elif self.game.game_state == "game_over":
            if center_x - 100 <= mouse_x <= center_x + 100 and button_y <= mouse_y <= button_y + 40:
                self.game.reset_game()
                self.send_reset_game()
                self.send_ready()
    
    def send_message(self, message):
        if self.connected:
            try:
                json_data = json.dumps(message, ensure_ascii=False)
                data = (json_data + '\n').encode('utf-8')
                self.client_socket.send(data)
                return True
            except Exception as e:
                print(f"Ошибка отправки: {e}")
                return False
        return False
    
    def send_chat_message(self, text):
        if text and text.strip():
            try:
                return self.send_message({
                    "type": "chat_message",
                    "text": text.strip(),
                    "timestamp": pygame.time.get_ticks()
                })
            except Exception as e:
                print(f"Ошибка отправки сообщения: {e}")
                return False
        return False

    def send_ship_placement(self, x, y, size, orientation):
        try:
            return self.send_message({
                "type": "place_ship",
                "x": int(x), 
                "y": int(y), 
                "size": int(size), 
                "orientation": int(orientation)
            })
        except Exception as e:
            print(f"Ошибка отправки размещения корабля: {e}")
            return False

    def send_shot(self, x, y):
        try:
            return self.send_message({
                "type": "fire",
                "x": int(x),
                "y": int(y)
            })
        except Exception as e:
            print(f"Ошибка отправки выстрела: {e}")
            return False
    
    def send_rotate_ship(self):
        self.send_message({
            "type": "rotate_ship"
        })

    def send_auto_place(self):
        self.send_message({
            "type": "auto_place"
        })
    
    def send_ready(self):
        self.send_message({
            "type": "ready"
        })
     
    def send_reset_game(self):
        """Отправляет запрос на сброс игры"""
        self.send_message({
            "type": "reset_game"
        })
        
        self.send_ready()

    def run(self):
        if not self.connect():
            print("Не удалось подключиться к серверу")
            return
        
        self.ui = MultiplayerUI(self.game, self)
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.connected = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.ui.chat_active:
                        if event.key == pygame.K_RETURN:
                            if self.ui.chat_input.strip():
                                success = self.send_chat_message(self.ui.chat_input)
                                if success:
                                    my_msg = {
                                        "player": self.player_id,
                                        "text": self.ui.chat_input,
                                        "timestamp": pygame.time.get_ticks()
                                    }
                                    self.chat_messages.append(my_msg)
                            self.ui.chat_input = ""
                            self.ui.chat_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.ui.chat_input = self.ui.chat_input[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            self.ui.chat_input = ""
                            self.ui.chat_active = False
                        else:
                            if len(self.ui.chat_input) < 100 and event.unicode.isprintable():
                                self.ui.chat_input += event.unicode
                    else:
                        if event.key == pygame.K_RETURN or event.key == pygame.K_t:
                            self.ui.chat_active = True
                            self.ui.chat_input = ""
                        elif event.key == pygame.K_r and self.game.game_state == "waiting":
                            self.send_ready()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    chat_x = self.ui.screen_width - 1000
                    chat_y = 120
                    chat_width = 300
                    chat_height = 400
                    
                    input_field = pygame.Rect(chat_x, chat_y + chat_height - 40, chat_width, 40)
                    if input_field.collidepoint(mouse_pos):
                        self.ui.chat_active = True
                    elif self.ui.chat_active:
                        self.ui.chat_active = False
                    else:
                        self.handle_click(*mouse_pos)
            
            self.ui.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        try:
            self.client_socket.close()
        except:
            pass