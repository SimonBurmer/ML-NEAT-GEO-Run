import random
import pygame
from settings import *
vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):

    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        #.rec determine the Height/Widht/Collor of the Object
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        #.rect determine the position of the object
        self.rect = self.image.get_rect()
        self.rect.center = (PLAYER_X, PLAYER_Y)

        #vectors are necessary for the players physic
        self.pos = vec(PLAYER_X, PLAYER_Y)
        #for up force
        self.velocity = vec(0, 0)
        #for garvity
        self.acceleration = vec(0, 0)
        self.jumping = False
        self.jumpCount = 0
    

    def jump(self):
        #jump only if standing on a platform
        self.rect.x += 1 # detect whether something is 1 pixle under the player
        hits = pygame.sprite.collide_rect(self, self.game.ground)
        self.rect.x -= 1
        if hits:
            self.velocity.y = -20


    def update(self):
        self.acceleration = vec(0, PLAYER_GRAV)
        # equations of motion
        self.velocity += self.acceleration
        self.pos += self.velocity + 0.5 * self.acceleration
        self.rect.midbottom = self.pos
    
    def draw(self, surface):
        surface.blit(self.image,self.rect)

