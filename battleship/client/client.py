import socket
import threading
import json
import pygame

from ui.networkUI import MultiplayerUI
from game_logic.core import Game

class BattleshipClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.client_socket = None
        self.setup_client()
        
    def setup_client(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)
        except Exception as e:
            print(f"Ошибка создания сокета: {e}")
            raise
    
    def safe_send(self, message_deict):
        try: 
            json_data = json.dumps(message_deict, ensure_ascii=False)
            data = (json_data + '\n').encode('utf-8')
            self.client_socket.send(data)
            return True
        
        except Exception as e:
            print(e)
            return False
        
    def connect(self):
        try:
            print(f"Подключаюсь к {self.host}:{self.port}...")
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            print("✓ Успешное подключение к серверу!")
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except socket.timeout:
            print("✗ Таймаут подключения. Сервер не отвечает.")
            return False
        except ConnectionRefusedError:
            print("✗ Сервер отверг подключение. Убедитесь что сервер запущен.")
            return False
        except Exception as e:
            print(f"✗ Ошибка подключения: {e}")
            return False
    
    def receive_messages(self):
        while self.connected:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                self.process_message(message)
                
            except Exception as e:
                print(f"Ошибка при приеме сообщения: {e}")
                break
        
        self.connected = False
        print("Отключен от сервера")
    
    def process_message(self, message):
        msg_type = message.get("type")
        
        if msg_type == "welcome":
            self.player_id = message["player_id"]
            print(f"Вы игрок {self.player_id}")
        
        elif msg_type == "player_joined":
            print(f"Игрок {message['player_id']} присоединился к игре")
            self.game.message = f"Игрок {message['player_id']} присоединился. Ожидание готовности..."
        
        elif msg_type == "player_left":
            print(message["message"])
            self.game.message = message["message"]
        
        elif msg_type == "game_start":
            self.game.reset_game()
            self.game.game_state = "playing"
            self.player_id = message["player_ids"][self.player_id]
            self.game.current_player = message["current_player"]
            self.game.message = "Игра началась!" if self.game.current_player == self.player_id else "Ход противника"
            print("Игра началась!")
        
        elif msg_type == "chat_update":
            self.chat_messages = message["messages"]
        
        elif msg_type == "shot_result":
            player_name = "Вы" if message["player"] == self.player_id else "Противник"
            if message["result"] in ["hit", "sunk"]:
                self.game.message = f"{player_name} попали в корабль!"
            else:
                self.game.message = f"{player_name} промахнулись."
        
        elif msg_type == "turn_change":
            self.game.current_player = message["current_player"]
            self.game.message = "Ваш ход!" if self.game.current_player == self.player_id else "Ход противника"
        
        elif msg_type == "game_over":
            self.game.game_state = "game_over"
            self.game.message = message["message"]
            print(f"Игра окончена: {message['message']}")
        
        elif msg_type == "player_ready":
            ready_player = "Вы" if message["player"] == self.player_id else "Противник"
            self.game.message = f"{ready_player} готов к игре!"
    
    def send_message(self, message):
        if self.connected:
            try:
                data = json.dumps(message).encode('utf-8')
                self.client_socket.send(data)
            except Exception as e:
                print(f"Ошибка отправки сообщения: {e}")
    
    def send_chat_message(self, text):
        if text.strip():
            self.send_message({
                "type": "chat_message",
                "text": text,
                "timestamp": pygame.time.get_ticks()
            })
    
    def send_shot(self, x, y):
        self.send_message({
            "type": "fire",
            "x": x,
            "y": y
        })
    
    def send_ship_placement(self, x, y, size, orientation):
        self.send_message({
            "type": "place_ship",
            "x": x, "y": y, "size": size, "orientation": orientation
        })
    
    def send_auto_place(self):
        self.send_message({
            "type": "auto_place"
        })
    
    def send_ready(self):
        self.send_message({
            "type": "ready"
        })
    
    def run(self):
        self.player_id = None
        self.game = Game()
        self.ui = None
        self.connected = False
        self.chat_messages = []
        
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
                            self.send_chat_message(self.ui.chat_input)
                            self.ui.chat_input = ""
                            self.ui.chat_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.ui.chat_input = self.ui.chat_input[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            self.ui.chat_input = ""
                            self.ui.chat_active = False
                        else:
                            self.ui.chat_input += event.unicode
                    else:
                        if event.key == pygame.K_RETURN:
                            self.ui.chat_active = True
                        elif event.key == pygame.K_r and self.game.game_state == "waiting":
                            self.send_ready()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    chat_x = self.ui.screen_width - 350
                    chat_y = 120
                    chat_width = 300
                    chat_height = 400
                    
                    if (chat_x <= mouse_pos[0] <= chat_x + chat_width and
                        chat_y + chat_height - 40 <= mouse_pos[1] <= chat_y + chat_height):
                        self.ui.chat_active = True
                    elif self.ui.chat_active:
                        self.ui.chat_active = False
                    else:
                        self.handle_click(*mouse_pos)
            
            self.ui.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        if self.client_socket:
            self.client_socket.close()

    def handle_click(self, mouse_x, mouse_y):
        board1_x, board2_x, board_y = self.ui.board1_x, self.ui.board2_x, self.ui.board_y
        center_x = self.ui.screen_width // 2
        
        button_y = board_y + 10 * self.ui.cell_size + 10
        
        if self.game.game_state == "waiting":
            if (center_x - 100 <= mouse_x <= center_x + 100 and
button_y <= mouse_y <= button_y + 40):
                self.send_ready()
        
        elif self.game.game_state == "placing":
            if (center_x - 100 <= mouse_x <= center_x + 100 and
                button_y <= mouse_y <= button_y + 40):
                self.send_auto_place()
            
            elif (center_x - 100 <= mouse_x <= center_x + 100 and
                  button_y + 50 <= mouse_y <= button_y + 90):
                self.game.rotate_ship()
            
            elif self.game.placing_player == self.player_id:
                board_x = board1_x if self.player_id == 1 else board2_x
                
                if (board_x <= mouse_x < board_x + 10 * self.ui.cell_size and 
                    board_y <= mouse_y < board_y + 10 * self.ui.cell_size):
                    cell_x = (mouse_x - board_x) // self.ui.cell_size
                    cell_y = (mouse_y - board_y) // self.ui.cell_size
                    
                    if self.game.place_ship_click(cell_x, cell_y):
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
                    
                    opponent_board = self.game.get_opponent_board()
                    if not opponent_board.shots[cell_y][cell_x]:
                        self.send_shot(cell_x, cell_y)
        
        elif self.game.game_state == "game_over":
            if (center_x - 100 <= mouse_x <= center_x + 100 and
                button_y <= mouse_y <= button_y + 40):
                self.game.reset_game()
                self.send_ready()

if __name__ == "__main__":
    client = BattleshipClient()
    client.run()
