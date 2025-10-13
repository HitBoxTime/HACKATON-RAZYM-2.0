import json
import os

class ScoreManager:
    def __init__(self, filename="battleship_scores.json"):
        self.filename = filename
        self.scores = {1: 0, 2: 0}
        self.load_scores()
    
    def load_scores(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.scores[1] = data.get("player1", 0)
                    self.scores[2] = data.get("player2", 0)
            except:
                # If there's an error loading, reset scores
                self.scores = {1: 0, 2: 0}
    
    def save_scores(self):
        with open(self.filename, 'w') as f:
            json.dump({
                "player1": self.scores[1],
                "player2": self.scores[2]
            }, f)
    
    def add_win(self, player):
        if player in self.scores:
            self.scores[player] += 1
            self.save_scores()
    
    def get_score(self, player):
        return self.scores.get(player, 0)
    
    def reset_scores(self):
        self.scores = {1: 0, 2: 0}
        self.save_scores()