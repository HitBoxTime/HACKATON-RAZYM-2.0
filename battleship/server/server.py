import socket
import threading
import json
import random
from game_logic.board import Board

class BattleshipServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
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
        
        print(f"Сервер запущен на {self.host}:{self.port}")
        print("Ожидание подключения игроков...")
    
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
            
            player_name = f"Игрок {player_id}"
            del self.players[player_id]
            
            if player_id in self.player_boards:
                del self.player_boards[player_id]
            
            if player_id in self.player_ids:
                del self.player_ids[player_id]
            
            self.broadcast({
                "type": "player_left",
                "player_id": player_id,
                "message": f"{player_name} покинул игру"
            })
            
            if len(self.players) < 2:
                self.game_state = "waiting"
                self.broadcast({"type": "game_reset"})
    
    def handle_client(self, client_socket, player_id):
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                self.process_message(message, client_socket, player_id)
                
        except Exception as e:
            print(f"Ошибка при обработке клиента {player_id}: {e}")
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
            
            board = self.player_boards[player_id]
            x, y, size, orientation = message["x"], message["y"], message["size"], message["orientation"]
            
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
            
            if len(self.players) == 2 and all(pid in self.player_boards for pid in self.players.keys()):
                self.start_game()
    
    def start_game(self):
        self.game_state = "playing"
        self.current_player = 1
        self.chat_messages = []
        
        player_list = list(self.players.keys())
        self.player_ids = {player_list[0]: 1, player_list[1]: 2}
        
        self.broadcast({
            "type": "game_start",
            "player_ids": self.player_ids,
            "current_player": self.current_player
        })
    
    def run(self):
        player_counter = 1
        
        while True:
            client_socket, addr = self.server.accept()
            print(f"Подключился игрок {player_counter} с адресом {addr}")
            
            if len(self.players) >= 2:
                client_socket.send(json.dumps({
                    "type": "error",
                    "message": "Сервер заполнен"
                }).encode('utf-8'))
                client_socket.close()
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
            
            thread = threading.Thread(target=self.handle_client, args=(client_socket, player_counter))
            thread.daemon = True
            thread.start()
            
            player_counter += 1

if __name__ == "__main__":
    server = BattleshipServer()
    server.run()