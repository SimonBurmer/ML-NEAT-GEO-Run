import os
import pygame
import neat
from settings import *
from obstacle import Obstacle
from player import Player
from ground import Ground
pygame.font.init()

class Game:
    def __init__(self):
        # initialize game window, etc
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dino-Run")
        self.clock = pygame.time.Clock()
        self.speed = 100
        self.gernation = 0

    def eval_genomes(self, genomes, config):

        self.gernation += 1

        """
        runs the simulation of the current population of
        players and sets their fitness based on the distance they
        reach in the game.
        """

        self.score = 0

        self.ground = Ground(*GROUND)
        
        self.obstacles = [Obstacle()]

        # start by creating lists holding the genome itself, the
        # neural network associated with the genome and the
        # bird object that uses that network to play

        #list with neural network of each genum
        self.nets = []
        #list with player
        self.players = []
        #list whit genums
        self.myGenomes = []
        
        for genome_id, genome in genomes: # len(genomes) == 30 because of POP_SITZE = 30 
            genome.fitness = 0  # start with fitness level of 0
            #creat the first version of a neural network for each genum
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            self.players.append(Player(self))
            self.myGenomes.append(genome)
        
        #start Game
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing and len(self.players) > 0: #only run the game is at least one player is alife
            self.clock.tick(self.speed)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game Loop - Update
        self.ground.update()
        for player in self.players:
            player.update()
        for obs in self.obstacles:
            obs.update()
        
        #determine the next obstacle
        for i,obs in enumerate(self.obstacles):
            if obs.rect.right > PLAYER_X:
                nextObstIndex = i
                break

        for x, player in enumerate(self.players):  # give each bird a fitness of 0.1 for each frame it stays alive
            self.myGenomes[x].fitness += 0.1
            
            #Var. for Input layer
            self.nextObs_dis = player.rect.right - self.obstacles[nextObstIndex].rect.left
            self.nextObs_hight = self.obstacles[nextObstIndex].rect.height
            self.nextObs_width = self.obstacles[nextObstIndex].rect.width
            self.player_y = player.rect.bottom

            # send player Y-location, next obstacle distance, next obstacle hight, next obstacle widht
            # determine from network whether to jump or not
            output = self.nets[x].activate((self.player_y, self.nextObs_dis, self.nextObs_hight, self.nextObs_width))
            if output[0] > 0.5:  # i use the tanh activation function so result will be between -1 and 1. if over 0.5 jump
                player.jump()


        # check if a player hits the ground - only if falling
        for player in self.players:
            if player.velocity.y > 0:
                hits = pygame.sprite.collide_rect(player, self.ground)
                # if player hits a ground, put him on the ground
                if hits:
                    player.pos.y = self.ground.rect.y
                    player.velocity.y = 0
        

        # ckeck if a player hits a obstacle 
        for obs in self.obstacles:
            if obs.rect.left < PLAYER_X + 30:
                for i,player in enumerate(self.players):
                    hits = pygame.sprite.collide_rect(player, obs)

                    #if a player collide with an obstacle -> fitness -= 1
                    #he is also deleted from all lists
                    #bad code!! because deleting something from a iterating list 
                    if hits:
                        self.myGenomes[i].fitness -= 1
                        self.nets.pop(i)
                        self.myGenomes.pop(i)
                        self.players.pop(i)

        #kill old obstacles and count up score 
        for i, obs in enumerate(self.obstacles):
            if obs.rect.left < -60:
                self.score += 10
                self.obstacles.pop(i)

                # gives an player reward for passing through a obstical (not required)
                for genome in self.myGenomes:
                    genome.fitness += 5
                

        #only spawn new obstacles when the last one is far enough away
        if self.obstacles[-1].rect.x < 800:
            self.obstacles.append(Obstacle())


    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                    self.playing = False
                    pygame.quit()
                    quit()


    def draw(self):
        # Game Loop - draw
        self.screen.fill(BLACK)
        self.ground.draw(self.screen)
        
        for player in self.players:
            player.draw(self.screen)
        for obs in self.obstacles:
            obs.draw(self.screen)
        
        #drawing important Informations
        self.draw_text("Score: "+str(self.score), 48, WHITE, WIDTH / 2, HEIGHT / 6)
        self.draw_text("Generation: " + str(self.gernation), 30, WHITE, WIDTH / 2, HEIGHT /3.5)
        self.draw_text("Alive: " +str(len(self.players)), 30, WHITE, WIDTH / 2, HEIGHT /3)
        self.draw_text("NextObs_dis: " +str(self.nextObs_dis), 20, WHITE, 100, 20)
        self.draw_text("NextObs_hight: " +str(self.nextObs_hight), 20, WHITE, 100, 40)
        self.draw_text("NextObs_width: " +str(self.nextObs_width), 20, WHITE, 100, 60)
        self.draw_text("Player_Y: " +str(self.player_y), 20, WHITE, 100, 80)

        # *after* drawing everything, flip the display
        pygame.display.flip()

    #for easy text creating 
    def draw_text(self, text, size, color, x, y):
        font = pygame.font.SysFont(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)





def run(config_file):

    #runs the NEAT algorithm to train a neural network.
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation,config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    #eval_genomes is called once per gernation 
    #eval_genomes it the Fitness_Function
    winner = p.run(g.eval_genomes, 50) #50 is the Max. number of gnerations

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    g = Game()
    # Determine path to configuration file. 
    # So that the script will run successfully regardless of the current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'configuration file.txt')
    run(config_path)
