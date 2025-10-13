from game_logic.core import Game
import ui.pygameUI
import pygame

#Здесь будут инициализироваться все части игры

def main():
    pygame.init()
    game = Game()
    UI = ui.pygameUI.PyGameUI(game)
    UI.run()

if __name__ == "__main__":
    main()