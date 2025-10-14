import socket
import threading
import json
import random
import sys
import os

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
        
        ship = {"size": size, "positions": [], "hits": [False] * size}
        
        if orientation == 0:
            for i in range(size):
                self.grid[y][x + i] = 1
                ship["positions"].append((x + i, y))
        else:
            for i in range(size):
                self.grid[y + i][x] = 1
                ship["positions"].append((x, y + i))
        
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
                for i, (sx, sy) in enumerate(ship["positions"]):
                    if sx == x and sy == y:
                        ship["hits"][i] = True
                        if all(ship["hits"]):
                            return "sunk"
                        return "hit"
            return "hit"
        else:
            return "miss"
    
    def all_ships_sunk(self):
        for ship in self.ships:
            if not all(ship["hits"]):
                return False
        return True

class BattleshipServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = None
        self.setup_server()
    
    def setup_server(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(2)
            
            self.players = {}
            self.player_boards = {}
            self.player_ids = {}
            self.game_state = "waiting"
            self.current_player = 1
            self.chat_messages = []
            
            print("=" * 50)
            print("СЕРВЕР МОРСКОЙ БОЙ ЗАПУЩЕН")
            print("=" * 50)
            self.print_connection_info()
            
        except Exception as e:
            print(f"ОШИБКА ЗАПУСКА СЕРВЕРА: {e}")
            print("Возможные причины:")
            print("1. Порт 5555 уже занят")
            print("2. Брандмауэр блокирует подключения")
            print("3. Нет прав для создания сервера")
            input("Нажмите Enter для выхода...")
            sys.exit(1)
    
    def print_connection_info(self):
        print(f"Порт сервера: {self.port}")
        print("\nДЛЯ ПОДКЛЮЧЕНИЯ:")
        print("1. С ЭТОГО КОМПЬЮТЕРА: используйте 'localhost' или '127.0.0.1'")
        print("2. С ДРУГОГО КОМПЬЮТЕРА: используйте IP-адрес этого компьютера")
        
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"\nIP-адреса этого компьютера:")
            print(f"- {local_ip} (основной)")
            print(f"- 127.0.0.1 (локальный)")
            
            # Пробуем получить все IP
            try:
                ip_list = socket.gethostbyname_ex(hostname)[2]
                for ip in ip_list:
                    if ip != local_ip and not ip.startswith('127.'):
                        print(f"- {ip}")
            except:
                pass
                
        except Exception as e:
            print(f"Не удалось получить IP-адреса: {e}")
        
        print(f"\nОжидаю подключения игроков...")
        print("=" * 50)
    
    def broadcast(self, message, exclude_player=None):
        data = json.dumps(message).encode('utf-8')
        disconnected_players = []
        
        for player_id, player_socket in self.players.items():
            if player_socket != exclude_player:
                try:
                    player_socket.send(data)
                except:
                    disconnected_players.append(player_id)
        
        for player_id in disconnected_players:
            self.remove_player(player_id)
    
    def remove_player(self, player_id):
        if player_id in self.players:
            try:
                self.players[player_id].close()
            except:
                pass
            
            print(f"Игрок {player_id} отключился")
            del self.players[player_id]
            
            if player_id in self.player_boards:
                del self.player_boards[player_id]
            
            if player_id in self.player_ids:
                del self.player_ids[player_id]
            
            self.broadcast({
                "type": "player_left",
                "player_id": player_id,
                "message": f"Игрок {player_id} покинул игру"
            })
            
            if len(self.players) < 2:
                self.game_state = "waiting"
                self.broadcast({"type": "game_reset"})
    
    def handle_client(self, client_socket, player_id):
        buffer = ""
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                buffer += data.dwcode('utf-8')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = json.loads(data.decode('utf-8'))
                            self.process_message(message, client_socket, player_id)

                        except json.JSONDecodeError as e:
                            print(e)
                            
        except Exception as e:
            print(f"Ошибка с клиентом {player_id}: {e}")
        finally:
            self.remove_player(player_id)
    
    def process_message(self, message, client_socket, player_id):
        msg_type = message.get("type")
        
        if msg_type == "chat_message":
            chat_msg = {
                "player": player_id,
                "text": message["text"],
                "timestamp": message.get("timestamp", "")
            }
            self.chat_messages.append(chat_msg)
            self.broadcast({
                "type": "chat_update",
                "messages": self.chat_messages[-20:]
            })
        
        elif msg_type == "place_ship":
            if player_id not in self.player_boards:
                self.player_boards[player_id] = Board(f"Игрок {player_id}")
            
            board = self.player_boards[player_id], x, y, size, orientation = message["x"], message["y"], message["size"], message["orientation"]
            
            if board.place_ship(size, x, y, orientation):
                self.broadcast({
                    "type": "ship_placed",
                    "player": player_id,
                    "x": x, "y": y, "size": size, "orientation": orientation
                })
        
        elif msg_type == "auto_place":
            if player_id not in self.player_boards:
                self.player_boards[player_id] = Board(f"Игрок {player_id}")
            
            board = self.player_boards[player_id]
            if board.auto_place_ships():
                self.broadcast({
                    "type": "auto_placed",
                    "player": player_id
                })
        
        elif msg_type == "fire":
            if self.game_state == "playing" and self.current_player == player_id:
                target_player = 2 if player_id == 1 else 1
                
                if target_player in self.player_boards:
                    target_board = self.player_boards[target_player]
                    x, y = message["x"], message["y"]
                    result = target_board.receive_shot(x, y)
                    
                    self.broadcast({
                        "type": "shot_result",
                        "player": player_id,
                        "target": target_player,
                        "x": x, "y": y,
                        "result": result
                    })
                    
                    if result == "miss":
                        self.current_player = target_player
                        self.broadcast({
                            "type": "turn_change",
                            "current_player": self.current_player
                        })
                    
                    if target_board.all_ships_sunk():
                        self.game_state = "game_over"
                        self.broadcast({
                            "type": "game_over",
                            "winner": player_id,
                            "message": f"Игрок {player_id} победил!"
                        })
        
        elif msg_type == "ready":
            self.broadcast({
                "type": "player_ready",
                "player": player_id
            })
            
            if len(self.players) == 2 and len(self.player_boards) == 2:
                self.start_game()
    
    def start_game(self):
        self.game_state = "playing"
        self.current_player = 1
        self.chat_messages = []
        
        player_list = list(self.players.keys())
        self.player_ids = {player_list[0]: 1, player_list[1]: 2}
        
        print("ОБА ИГРОКА ПОДКЛЮЧЕНЫ! НАЧИНАЕМ ИГРУ!")
        
        self.broadcast({
            "type": "game_start",
            "player_ids": self.player_ids,
            "current_player": self.current_player
        })
    
    def run(self):
        player_counter = 1
        
        while True:
            try:
                client_socket, addr = self.server.accept()
                print(f"Подключился игрок {player_counter} с адреса {addr[0]}:{addr[1]}")
                
                if len(self.players) >= 2:
                    client_socket.send(json.dumps({
                        "type": "error",
                        "message": "Сервер заполнен (максимум 2 игрока)"
                    }).encode('utf-8'))
                    client_socket.close()
                    print("Отклонено подключение - сервер заполнен")
                    continue
                
                self.players[player_counter] = client_socket
                
                client_socket.send(json.dumps({
                    "type": "welcome",
                    "player_id": player_counter,
                    "players_count": len(self.players)
                }).encode('utf-8'))
                
                self.broadcast({
                    "type": "player_joined",
"player_id": player_counter,
                    "players_count": len(self.players)
                })
                
                print(f"Игроков онлайн: {len(self.players)}/2")
                
                thread = threading.Thread(target=self.handle_client, args=(client_socket, player_counter))
                thread.daemon = True
                thread.start()
                
                player_counter += 1
                
            except Exception as e:
                print(f"Ошибка при подключении: {e}")

if __name__ == "__main__":
    print("Запуск сервера Морской Бой...")
    try:
        server = BattleshipServer()
        server.run()
    except KeyboardInterrupt:
        print("\nСервер остановлен пользователем")
    except Exception as e:
        print(f"Сервер аварийно завершил работу: {e}")
        input("Нажмите Enter для выхода...")