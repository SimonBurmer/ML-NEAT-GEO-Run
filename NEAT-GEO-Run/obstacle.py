import random
import pygame
from settings import *

#Represents to obstacles in the game
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #for random sitze of the obstacles 
        x = random.randrange(40, 90)
        y = random.randrange(80, 180)

        self.image = pygame.Surface((x, y))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        #place where obstacle is print first time 
        self.rect.x = WIDTH + random.randrange(0, 200)
        self.rect.y = HEIGHT - self.image.get_height() - GROUNDHEIGHT
    
    def update(self):
        self.rect.x -= 4
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
