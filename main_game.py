import pygame, sys

mainClock = pygame.time.Clock()
from pygame.locals import *

pygame.init()
size = 900, 600
screen = pygame.display.set_mode((size), 0, 32)

font = pygame.font.SysFont(None, 40)


class SecondLavel:
    def __init__(self, font):
        self.click = False
        self.font = font
        self.background = pygame.image.load('assets/water_bg1.jpg')
        self.water = pygame.image.load('assets/water_texture.png')

    def main_menu(self):
        while True:
            screen.fill((0, 0, 0))
            self.draw_text('second level', self.font, (255, 255, 255), screen, 20, 20)
            mx, my = pygame.mouse.get_pos()
            button_1 = pygame.Rect(350, 250, 200, 50)
            if button_1.collidepoint((mx, my)):
                if self.click:
                    self.game()
            pygame.draw.rect(screen, (255, 0, 0), button_1)
            self.draw_text('start', self.font, (255, 255, 255), screen, 415, 260)

            self.click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True

            pygame.display.update()
            mainClock.tick(60)

    def draw_text(self, text, font, color, surface, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def game(self):
        running = True
        self.waterXpos = 0
        while running:
            screen.fill((0, 0, 0))
            screen.blit(self.background, (0, 0))

            def drawFloor():
                screen.blit(self.water, (self.waterXpos, 450))
                screen.blit(self.water, (self.waterXpos + 288, 450))

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            self.waterXpos -= 5  # скорость текстуры воды
            drawFloor()
            if self.waterXpos <= -288:
                self.waterXpos = 0

            pygame.display.update()
            mainClock.tick(60)


try:
    level = SecondLavel(font)
    level.main_menu()
except Exception as e:
    print(e)