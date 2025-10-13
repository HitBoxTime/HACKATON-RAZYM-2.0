"""
Логика корабля

"""

class Ship:
    def __init__(self, size):
        self.size = size
        self.positions = []
        self.hits = [False] * size
        self.orientation = 0  

    def is_sunk(self):
        return all(self.hits)
    
    def hit(self, index):
        if 0 <= index < self.size:
            self.hits[index] = True