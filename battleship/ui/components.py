import pygame

""""""

class Button:
    def __init__(self, x, y, width, height, text, font, color=(173, 216, 230), hover_color=(135, 206, 250)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, x, y):
        return self.rect.collidepoint(x, y)

class BoardRenderer:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.font = pygame.font.SysFont('Arial', 20)
    
    def draw_board(self, screen, board, x, y, show_ships=True):
        for i in range(board.size + 1):
            pygame.draw.line(screen, (0, 0, 0), (x, y + i * self.cell_size), 
                             (x + board.size * self.cell_size, y + i * self.cell_size), 2)
            pygame.draw.line(screen, (0, 0, 0), (x + i * self.cell_size, y), 
                             (x + i * self.cell_size, y + board.size * self.cell_size), 2)
        
        for i in range(board.size):
            letter = self.font.render(chr(65 + i), True, (0, 0, 0))
            number = self.font.render(str(i + 1), True, (0, 0, 0))
            screen.blit(letter, (x + i * self.cell_size + self.cell_size // 2 - 5, y - 30))
            screen.blit(number, (x - 30, y + i * self.cell_size + self.cell_size // 2 - 10))
        
        if show_ships:
            for ship in board.ships:
                for pos in ship.positions:
                    px, py = pos
                    pygame.draw.rect(screen, (0, 0, 139), 
                                    (x + px * self.cell_size + 2, y + py * self.cell_size + 2, 
                                     self.cell_size - 4, self.cell_size - 4))
        
        for i in range(board.size):
            for j in range(board.size):
                if board.shots[j][i]:
                    if board.grid[j][i] == 1:  # Hit
                        pygame.draw.circle(screen, (255, 0, 0), 
                                          (x + i * self.cell_size + self.cell_size // 2, 
                                           y + j * self.cell_size + self.cell_size // 2), 
                                          self.cell_size // 3)
                    else:
                        pygame.draw.circle(screen, (0, 0, 255), 
                                          (x + i * self.cell_size + self.cell_size // 2, 
                                           y + j * self.cell_size + self.cell_size // 2), 
                                          self.cell_size // 6)
    
    def draw_ship_preview(self, screen, ship_size, orientation, x, y, board_x, board_y):
        can_place = True
        if orientation == 0:
            if x + ship_size > 10:
                can_place = False
        else:
            if y + ship_size > 10:
                can_place = False
        
        color = (0, 255, 0) if can_place else (255, 0, 0)
        if orientation == 0:
            pygame.draw.rect(screen, color, 
                            (board_x + x * self.cell_size, board_y + y * self.cell_size, 
                             ship_size * self.cell_size, self.cell_size), 3)
        else:
            pygame.draw.rect(screen, color, 
                            (board_x + x * self.cell_size, board_y + y * self.cell_size, 
                             self.cell_size, ship_size * self.cell_size), 3)