import pygame, sys
import random

mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
size = 900, 600
screen = pygame.display.set_mode(size)


class Let(pygame.sprite.Sprite):
    def __init__(self, x, speed, filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect(center=(x, random.randint(0, 500)))
        self.speed = speed

    def update(self, *args):
        if self.rect.x > args[0]:
            self.rect.x -= self.speed
        else:
            self.kill()


class SecondLevel:
    def __init__(self):
        self.water = pygame.image.load('assets/water_texture.png')
        self.background1 = pygame.image.load('assets/list.jpg')
        self.ship = pygame.image.load('assets/ship_png.png')
        self.ship = pygame.transform.scale(self.ship, (240, 150))
        self.shipYpos = 0
        self.ship_rect = self.ship.get_rect(center=(10, self.shipYpos))
        pygame.time.set_timer(pygame.USEREVENT, 4000)

    def game(self):
        running = True
        self.waterXpos = 0
        gravity = 2
        W = -200
        group = pygame.sprite.Group()
        group.add(Let(800, random.randint(1, 4), 'assets/island.png'))
        print(len(group))

        def draw_water():
            screen.blit(self.water, (self.waterXpos, 445))
            screen.blit(self.water, (self.waterXpos + 288, 445))

        while running:
            screen.fill((0, 0, 0))
            screen.blit(self.background1, (0, 0))
            screen.blit(self.ship, (10, self.shipYpos))
            group.draw(screen)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.shipYpos -= 70
                if event.type == pygame.USEREVENT:
                    group.add(Let(900, random.randint(1, 4), 'assets/island.png'))
            if self.shipYpos > 310:
                self.shipYpos = 320
            else:
                self.shipYpos += gravity
            self.waterXpos -= 5  # скорость текстуры воды
            draw_water()
            if self.waterXpos <= -288:
                self.waterXpos = 0

            pygame.display.update()
            mainClock.tick(60)
            group.update(W)


level = SecondLevel()
level.game()