import pygame
import sys
from game_logic.core import Game
from ui.pygameUI import PyGameUI
from client.client import BattleshipClient

class NetworkConfigDialog:
    def __init__(self):
        self.width = 400
        self.height = 350
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Настройки сетевой игры")
        
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        self.ip_input = "localhost"
        self.port_input = "5555"
        self.active_input = None

        self.connect_button = pygame.Rect(100, 220, 200, 40)
        self.back_button = pygame.Rect(100, 280, 200, 40)
    
    def draw(self):
        self.screen.fill((240, 240, 240))
        title = self.title_font.render("Настройки подключения", True, (0, 0, 139))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))
        ip_label = self.font.render("IP-адрес сервера:", True, (0, 0, 0))
        self.screen.blit(ip_label, (50, 70))
        ip_bg_color = (255, 255, 255) if self.active_input != 'ip' else (220, 220, 255)
        pygame.draw.rect(self.screen, ip_bg_color, (50, 100, 300, 30))
        pygame.draw.rect(self.screen, (0, 0, 0), (50, 100, 300, 30), 2)
        ip_text = self.font.render(self.ip_input, True, (0, 0, 0))
        self.screen.blit(ip_text, (55, 102))
        port_label = self.font.render("Порт:", True, (0, 0, 0))
        self.screen.blit(port_label, (50, 140))
        
        port_bg_color = (255, 255, 255) if self.active_input != 'port' else (220, 220, 255)
        pygame.draw.rect(self.screen, port_bg_color, (50, 170, 300, 30))
        pygame.draw.rect(self.screen, (0, 0, 0), (50, 170, 300, 30), 2)
        
        port_text = self.font.render(self.port_input, True, (0, 0, 0))
        self.screen.blit(port_text, (55, 172))
        
        connect_color = (173, 216, 230)
        pygame.draw.rect(self.screen, connect_color, self.connect_button)
        pygame.draw.rect(self.screen, (0, 0, 0), self.connect_button, 2)
        connect_text = self.font.render("Подключиться", True, (0, 0, 0))
        self.screen.blit(connect_text, (self.width // 2 - connect_text.get_width() // 2, 230))
        
        back_color = (255, 200, 200)
        pygame.draw.rect(self.screen, back_color, self.back_button)
        pygame.draw.rect(self.screen, (0, 0, 0), self.back_button, 2)
        back_text = self.font.render("Назад", True, (0, 0, 0))
        self.screen.blit(back_text, (self.width // 2 - back_text.get_width() // 2, 290))
        
        hint = self.small_font.render("По умолчанию: localhost:5555", True, (100, 100, 100))
        self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 30))
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, None
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    

                    if 50 <= mouse_pos[0] <= 350 and 100 <= mouse_pos[1] <= 130:
                        self.active_input = 'ip'
                    elif 50 <= mouse_pos[0] <= 350 and 170 <= mouse_pos[1] <= 200:
                        self.active_input = 'port'
                    else:
                        self.active_input = None
                    
                    if self.connect_button.collidepoint(mouse_pos):
                        return self.ip_input, self.port_input
                    
                    if self.back_button.collidepoint(mouse_pos):
                        return None, None
                
                if event.type == pygame.KEYDOWN and self.active_input:
                    if event.key == pygame.K_BACKSPACE:
                        if self.active_input == 'ip':
                            self.ip_input = self.ip_input[:-1]
                        else:
                            self.port_input = self.port_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.active_input == 'ip':
                            self.active_input = 'port'
                        else:
                            return self.ip_input, self.port_input
                    else:
                        if self.active_input == 'port':
                            if event.unicode.isdigit():
                                self.port_input += event.unicode
                        else:
                            self.ip_input += event.unicode
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        return None, None

def show_error_message(message):
    """Показывает сообщение об ошибке"""
    error_font = pygame.font.SysFont('Arial', 20)
    error_screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Ошибка")
    
    error_screen.fill((255, 200, 200))
    error_text = error_font.render(message, True, (200, 0, 0))
    error_screen.blit(error_text, (200 - error_text.get_width() // 2, 70))
    
    pygame.display.flip()
    pygame.time.wait(2000)

def main():
    pygame.init()
    
    screen_width, screen_height = 500, 400
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Морской бой")
    
    font = pygame.font.SysFont('Arial', 24)
    title_font = pygame.font.SysFont('Arial', 36, bold=True)
    
    button_width, button_height = 200, 50
    single_player_button = pygame.Rect(
        screen_width // 2 - button_width // 2, 
        120, 
        button_width, 
        button_height
    )
    multi_player_button = pygame.Rect(
        screen_width // 2 - button_width // 2, 
        190, 
        button_width, 
        button_height
    )
    quit_button = pygame.Rect(
        screen_width // 2 - button_width // 2, 
        260, 
        button_width, 
        button_height
    )
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if single_player_button.collidepoint(mouse_pos):
                    print("Запуск локальной игры...")
                    try:
                        game = Game()
                        game.game_state = "placing"
                        game.message = "Игрок 1 расставляет корабли"
                        
                        ui = PyGameUI(game)
                        ui.run()
                        
                        screen = pygame.display.set_mode((screen_width, screen_height))
                        pygame.display.set_caption("Морской бой")
                    except Exception as e:
                        print(f"Ошибка в локальной игре: {e}")
                        show_error_message(f"Ошибка: {e}")
                
                elif multi_player_button.collidepoint(mouse_pos):
                    print("Запуск сетевой игры...")
                    try:
                        config_dialog = NetworkConfigDialog()
                        ip, port = config_dialog.run()
                        
                        if ip and port:
                            port = int(port)
                            client = BattleshipClient(host=ip, port=port)
                            client.run()
                            
                            screen = pygame.display.set_mode((screen_width, screen_height))
                            pygame.display.set_caption("Морской бой")
                    except ValueError:
                        show_error_message("Порт должен быть числом!")
                    except Exception as e:
                        print(f"Ошибка в сетевой игре: {e}")
                        show_error_message(f"Ошибка подключения: {e}")
                
                elif quit_button.collidepoint(mouse_pos):
                    running = False
        
        screen.fill((240, 240, 240))
        
        title = title_font.render("МОРСКОЙ БОЙ", True, (0, 0, 139))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 40))
        
        button_color = (173, 216, 230)
        hover_color = (135, 206, 250)
        mouse_pos = pygame.mouse.get_pos()

        color = hover_color if single_player_button.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, color, single_player_button)
        pygame.draw.rect(screen, (0, 0, 0), single_player_button, 2)
        single_text = font.render("Локальная игра", True, (0, 0, 0))
        screen.blit(single_text, (screen_width // 2 - single_text.get_width() // 2, 135))
        
        color = hover_color if multi_player_button.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, color, multi_player_button)
        pygame.draw.rect(screen, (0, 0, 0), multi_player_button, 2)
        multi_text = font.render("Сетевая игра", True, (0, 0, 0))
        screen.blit(multi_text, (screen_width // 2 - multi_text.get_width() // 2, 205))
        
        color = hover_color if quit_button.collidepoint(mouse_pos) else (255, 150, 150)
        pygame.draw.rect(screen, color, quit_button)
        pygame.draw.rect(screen, (0, 0, 0), quit_button, 2)
        quit_text = font.render("Выход", True, (0, 0, 0))
        screen.blit(quit_text, (screen_width // 2 - quit_text.get_width() // 2, 275))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

