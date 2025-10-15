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
    
    def get_sunk_ships_positions(self):
        """Возвращает все позиции потопленных кораблей"""
        sunk_positions = []
        for ship in self.ships:
            if all(ship["hits"]): 
                sunk_positions.extend(ship["positions"])
        return sunk_positions
  
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
                            surrounding = self.get_surrounding_cells(ship["positions"])
                      
                            for nx, ny in surrounding:
                                if not self.shots[ny][nx]:
                                    self.shots[ny][nx] = True
                            return {
                                "result": "sunk",
                                "ship_positions": ship["positions"],
                                "surrounding_cells": surrounding
                            }
                        return {"result": "hit"}
            return {"result": "hit"}
        else:
            return {"result": "miss"}
        
    def get_surrounding_cells(self, ship_positions):
        surrounding = set()
        for pos in ship_positions:
            px, py = pos
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if self.grid[ny][nx] == 0:
                            surrounding.add((nx, ny))
        return list(surrounding)
    
    def all_ships_sunk(self):
        for ship in self.ships:
            if not all(ship["hits"]):
                return False
        return True

    def mark_around_sunken_ship(self, ship):
        for pos in ship["positions"]:
            px, py = pos
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size and not self.shots[ny][nx]:
                        self.shots[ny][nx] = True 
                        
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
        except:
            pass
        
        print(f"\nОжидаю подключения игроков...")
        print("=" * 50)

    def send_to_client(self, client_socket, message):
        try:
            json_data = json.dumps(message, ensure_ascii=False)
            data = (json_data + '\n').encode('utf-8')
            client_socket.send(data)
            return True
        except Exception as e:
            return False
    
    def broadcast(self, message, exclude_player=None):
        disconnected_players = []
        
        for player_id, player_socket in self.players.items():
            if player_socket != exclude_player:
                try:
                    self.send_to_client(player_socket, message)
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
            
                buffer += data.decode('utf-8')
            
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = json.loads(line)
                            self.process_message(message, client_socket, player_id)
                        except json.JSONDecodeError:
                            continue
                        
        except Exception as e:
            print(f"Ошибка с клиентом {player_id}: {e}")
        finally:
            self.remove_player(player_id)
    
    def process_message(self, message, client_socket, player_id):
        try:
            msg_type = message.get("type")
            
            if msg_type == "chat_message":
                text = message.get("text", "").strip()
                if text:
                    chat_msg = {
                        "player": player_id,
                        "text": text,
                        "timestamp": message.get("timestamp", 0)
                    }
                    self.chat_messages.append(chat_msg)
                    
                    if len(self.chat_messages) > 50:
                        self.chat_messages = self.chat_messages[-50:]
                    
                    self.broadcast({
                        "type": "chat_update",
                        "messages": self.chat_messages
                    })
            
            elif msg_type == "place_ship":
                if player_id not in self.player_boards:
                    self.player_boards[player_id] = Board(f"Игрок {player_id}")

                board = self.player_boards[player_id]
                x = message.get("x", 0)
                y = message.get("y", 0)
                size = message.get("size", 1)
                orientation = message.get("orientation", 0)

                if x < 0 or x >= 10 or y < 0 or y >= 10:
                    try:
                        self.send_to_client(client_socket, {
                            "type": "error", 
                            "message": "Неверные координаты"
                        })
                    except:
                        pass
                    return

                ship_counts = {}
                for ship in board.ships:
                    ship_size = ship["size"]
                    ship_counts[ship_size] = ship_counts.get(ship_size, 0) + 1

                limits = {4: 1, 3: 2, 2: 3, 1: 4}
                if ship_counts.get(size, 0) >= limits.get(size, 0):
                    try:
                        self.send_to_client(client_socket, {
                            "type": "error",
                            "message": f"Уже размещено максимальное количество {size}-палубных кораблей"
                        })
                    except:
                        pass
                    return

                if board.place_ship(size, x, y, orientation):
                    print(f"Игрок {player_id} разместил {size}-палубный корабль в ({x},{y})")

                    self.broadcast({
                        "type": "ship_placed",
                        "player": player_id,
                        "x": x, "y": y, "size": size, "orientation": orientation
                    })

                    total_ships_placed = len(board.ships)
                    print(f"Игрок {player_id} разместил {total_ships_placed}/10 кораблей")

                    if total_ships_placed >= 10:
                        print(f"Игрок {player_id} завершил расстановку кораблей")
                        self.broadcast({
                            "type": "player_ready",
                            "player": player_id
                        })

                        if len(self.players) == 2:
                            player1_ready = len(self.player_boards.get(1, Board("")).ships) >= 10
                            player2_ready = len(self.player_boards.get(2, Board("")).ships) >= 10

                            if player1_ready and player2_ready:
                                print("Оба игрока готовы! Начинаем игру!")
                                self.start_game()
                else:
                    try:
                        self.send_to_client(client_socket, {
                            "type": "error",
                            "message": "Невозможно разместить корабль здесь"
                        })
                    except:
                        pass
            
            elif msg_type == "rotate_ship":
               self.broadcast({
                   "type": "ship_rotated",
                   "player": player_id
               })

            elif msg_type == "auto_place":
                if player_id not in self.player_boards:
                    self.player_boards[player_id] = Board(f"Игрок {player_id}")

                board = self.player_boards[player_id]
                if board.auto_place_ships():
                    print(f"Игрок {player_id} использовал авторасстановку")
                    print(f"Размещено кораблей: {len(board.ships)}")

                    ship_placements = []
                    for ship in board.ships:
                        x, y = ship["positions"][0]
                        size = ship["size"]
                        orientation = 0 
                        if len(ship["positions"]) > 1:
                            x1, y1 = ship["positions"][1]
                            if x1 == x:
                                orientation = 1

                        ship_placements.append({
                            "x": x, "y": y, "size": size, "orientation": orientation
                        })

                    self.broadcast({
                        "type": "auto_placed", 
                        "player": player_id,
                        "ship_placements": ship_placements
                    })

                    if len(self.players) == 2:
                        player1_ready = len(self.player_boards.get(1, Board("")).ships) >= 10
                        player2_ready = len(self.player_boards.get(2, Board("")).ships) >= 10

                        if player1_ready and player2_ready:
                            print("Оба игрока готовы! Начинаем игру!")
                            self.start_game()
                else:
                    try:
                        self.send_to_client(client_socket, {
                            "type": "error",
                            "message": "Не удалось автоматически расставить корабли"
                        })
                    except:
                        pass
            
            elif msg_type == "fire":
                if self.game_state == "playing" and self.current_player == player_id:
                    target_player = 2 if player_id == 1 else 1

                    if target_player in self.player_boards:
                        target_board = self.player_boards[target_player]
                        x = message.get("x", 0)
                        y = message.get("y", 0)

                        if target_board.shots[y][x]:
                            try:
                                self.send_to_client(client_socket, {
                                    "type": "error",
                                    "message": "Вы уже стреляли в эту клетку"
                                })
                            except:
                                pass
                            return

                        result_data = target_board.receive_shot(x, y)

                        self.broadcast({
                            "type": "shot_result",
                            "player": player_id,
                            "target": target_player,
                            "x": x, "y": y,
                            "result": result_data
                        })

                        if isinstance(result_data, dict):
                            result = result_data.get("result", "miss")
                        else:
                            result = result_data

                        if result == "miss":
                            self.current_player = target_player
                            self.broadcast({
                                "type": "turn_change",
                                "current_player": self.current_player
                            })
                        else:

                            try:
                                self.send_to_client(client_socket, {
                                    "type": "continue_turn",
                                    "message": "Продолжайте стрелять!"
                                })
                            except:
                                pass
                            
                        if target_board.all_ships_sunk():
                            self.game_state = "game_over"
                            self.broadcast({
                                "type": "game_over",
                                "winner": player_id,
                                "message": f"Игрок {player_id} победил!"
                            })
        
            elif msg_type == "reset_game":
                self.reset_game()
                return
            
            elif msg_type == "ready":
                self.broadcast({
                    "type": "player_ready",
                    "player": player_id
                })
                
                if len(self.players) == 2:
                    ready_players = []
                    for pid in self.players:
                        ready_players.append(pid)
                    
                    if len(ready_players) == 2:
                        self.game_state = "placing"
                        self.broadcast({
                            "type": "game_state_change",
                            "game_state": "placing",
                            "placing_player": 1,
                            "message": "Игрок 1 начинает расстановку кораблей"
                        })

        except Exception as e:
            print(f"Ошибка обработки сообщения от игрока {player_id}: {e}")

    def start_game(self):
       self.game_state = "playing"
       self.current_player = 1
       
       player_list = list(self.players.keys())
       self.player_ids = {player_list[0]: 1, player_list[1]: 2}
       
       print("ОБА ИГРОКА ПОДКЛЮЧЕНЫ! НАЧИНАЕМ ИГРУ!")
       print(f"Игрок 1 кораблей: {len(self.player_boards.get(1, Board('')).ships)}")
       print(f"Игрок 2 кораблей: {len(self.player_boards.get(2, Board('')).ships)}")
       

       
       self.broadcast({
           "type": "game_start",
           "player_ids": self.player_ids,
           "current_player": self.current_player
       })
    
    def reset_game(self):
        """Полный сброс игры для новой партии"""
        print("=" * 50)
        print("ПОЛНЫЙ СБРОС ИГРЫ НА СЕРВЕРЕ")
        print("=" * 50)

        self.player_boards = {}
        for player_id in self.players:
            self.player_boards[player_id] = Board(f"Игрок {player_id}")
            print(f"Создана новая доска для игрока {player_id}")

        self.game_state = "placing"
        self.current_player = 1
        self.placing_player = 1  

        print(f"Состояние игры сброшено: {self.game_state}")
        print(f"Расставляет: игрок {self.placing_player}")
        print("=" * 50)

        self.broadcast({
            "type": "game_reset",
            "game_state": "placing",
            "placing_player": 1,
            "message": "Новая игра! Игрок 1 начинает расстановку кораблей"
        })

    def run(self):
        player_counter = 1
        
        while True:
            try:
                client_socket, addr = self.server.accept()
                print(f"Подключился игрок {player_counter} с адреса {addr[0]}:{addr[1]}")
                
                if len(self.players) >= 2:
                    try:
                        self.send_to_client(client_socket, {
                            "type": "error",
                            "message": "Сервер заполнен (максимум 2 игрока)"
                        })
                    except:
                        pass
                    client_socket.close()
                    print("Отклонено подключение - сервер заполнен")
                    continue
                
                self.players[player_counter] = client_socket
                
                self.send_to_client(client_socket, {
                    "type": "welcome",
                    "player_id": player_counter,
                    "players_count": len(self.players)
                })
                
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
    print("Запуск сервера Морской Бой...")