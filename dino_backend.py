__author__ = "Shivam Shekhar"
"""Imports all of the necessary packages"""
import os
import sys
import pygame
import random
from pygame import *
import pyautogui as pag
import numpy as np

pygame.init()
# Sets screen dimensions, colors, sounds, and images.
# Also initializes time/score.
scr_size = (width,height) = (600,150)
FPS = 60
gravity = 0.6

pag.PAUSE = 0

black = (0,0,0)
white = (255,255,255)
background_col = (235,235,235)

high_score = 0

screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("T-Rex Rush")

jump_sound = pygame.mixer.Sound('sprites/jump.wav')
die_sound = pygame.mixer.Sound('sprites/die.wav')
checkPoint_sound = pygame.mixer.Sound('sprites/checkPoint.wav')

# Next, it pulls the sprites to be able to construct the image
# we see on screen.

def load_image(
    name,
    sizex=-1,
    sizey=-1,
    colorkey=None,
    ):

    fullname = os.path.join('sprites', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return (image, image.get_rect())

def load_sprite_sheet(
        sheetname,
        nx,
        ny,
        scalex = -1,
        scaley = -1,
        colorkey = None,
        ):
    fullname = os.path.join('sprites',sheetname)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizex = sheet_rect.width/nx
    sizey = sheet_rect.height/ny

    for i in range(0,ny):
        for j in range(0,nx):
            rect = pygame.Rect((j*sizex,i*sizey,sizex,sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet,(0,0),rect)

            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey,RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image,(scalex,scaley))

            sprites.append(image)

    sprite_rect = sprites[0].get_rect()

    return sprites,sprite_rect

# Game over screen
def disp_gameOver_msg(retbutton_image,gameover_image):
    retbutton_rect = retbutton_image.get_rect()
    retbutton_rect.centerx = width / 2
    retbutton_rect.top = height*0.52

    gameover_rect = gameover_image.get_rect()
    gameover_rect.centerx = width / 2
    gameover_rect.centery = height*0.35

    screen.blit(retbutton_image, retbutton_rect)
    screen.blit(gameover_image, gameover_rect)

# I think this is the loading screen
def extractDigits(number):
    if number > -1:
        digits = []
        i = 0
        while(number/10 != 0):
            digits.append(number%10)
            number = int(number/10)

        digits.append(number%10)
        for i in range(len(digits),5):
            digits.append(0)
        digits.reverse()
        return digits

# Our dino dude(ette). Initializes all of his stats such as life, score, movement,
# and jump speed. It also imports the images of the normal dino and the
# ducking dino.

class Dino():
    def __init__(self,sizex=-1,sizey=-1):
        self.images,self.rect = load_sprite_sheet('dino.png',5,1,sizex,sizey,-1)
        self.images1,self.rect1 = load_sprite_sheet('dino_ducking.png',2,1,59,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width/15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.movement = [0,0]
        self.jumpSpeed = 11.5

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width
    
    def jump(self):
        if self.rect.bottom == int(0.98*height):
            self.isJumping = True
            if pygame.mixer.get_init() != None:
                jump_sound.play()
            self.movement[1] = -1*self.jumpSpeed
        

# Next it draws itself, checks its boundary, defines how to jump, and defines
# how to duck. Finally it checks if its dead. If it isn't, it increases the score.

    def draw(self):
        screen.blit(self.image,self.rect)

    def checkbounds(self):
        if self.rect.bottom > int(0.98*height):
            self.rect.bottom = int(0.98*height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2 + 2

        if self.isDead:
           self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)%2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking == False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() != None:
                    checkPoint_sound.play()

        self.counter = (self.counter + 1)

# This defines the cactus! It puts a cactus randomly between 0 and 3
class Cactus(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('cacti-small.png',3,1,sizex,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0,3)]
        self.movement = [-1*speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        self.dino_distance = self.rect.left - 84

        if self.rect.right < 0:
            self.kill()
            
class Ptera(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('ptera.png',2,1,sizex,sizey,-1)
        # self.ptera_height = [height*0.82,height*0.75,height*0.60]
        self.ptera_height = [height*0.82,height*0.9,height*0.8]
        self.rect.centery = self.ptera_height[random.randrange(0,3)]
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.movement = [-1*speed,0]
        self.index = 0
        self.counter = 0

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        
        self.dino_distance = self.rect.left - 84
        if self.rect.right < 0:
            self.kill()
            
# Yo, this defines the ground, image-wise and movement-wise.
class Ground():
    def __init__(self,speed=-5):
        self.image,self.rect = load_image('ground.png',-1,-1,-1)
        self.image1,self.rect1 = load_image('ground.png',-1,-1,-1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen.blit(self.image,self.rect)
        screen.blit(self.image1,self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right

# Clouds just look pretty. They don't do anything.
class Cloud(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image,self.rect = load_image('cloud.png',int(90*30/42),30,-1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1*self.speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()

# This defines the scoring? I'm a bit confused on this part
class Scoreboard():
    def __init__(self,x=-1,y=-1):
        self.score = 0
        self.tempimages,self.temprect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
        self.image = pygame.Surface((55,int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width*0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height*0.1
        else:
            self.rect.top = y

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self,score):
        score_digits = extractDigits(score)
        self.image.fill(background_col)
        for s in score_digits:
            self.image.blit(self.tempimages[s],self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0

"""This defines the intro screen. It has some backup messages if the game
won't load. Next, it defines the keys that make the dino jump and duck.
Finally, this part starts the game when you press jump!"""
def introscreen(game_start):
    temp_dino = Dino(44,47)
    temp_dino.isBlinking = True
    gameStart = game_start

    callout,callout_rect = load_image('call_out.png',196,45,-1)
    callout_rect.left = width*0.05
    callout_rect.top = height*0.4

    temp_ground,temp_ground_rect = load_sprite_sheet('ground.png',15,1,-1,-1,-1)
    temp_ground_rect.left = width/20
    temp_ground_rect.bottom = height

    logo,logo_rect = load_image('logo.png',240,40,-1)
    logo_rect.centerx = width*0.6
    logo_rect.centery = height*0.6
    while not gameStart:
        if pygame.display.get_surface() == None:
            print("Couldn't load display surface")
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        temp_dino.isJumping = True
                        temp_dino.isBlinking = False
                        temp_dino.movement[1] = -1*temp_dino.jumpSpeed

        temp_dino.update()

        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            screen.blit(temp_ground[0],temp_ground_rect)
            if temp_dino.isBlinking:
                screen.blit(logo,logo_rect)
                screen.blit(callout,callout_rect)
            temp_dino.draw()

            pygame.display.update()

        clock.tick(FPS)
        if temp_dino.isJumping == False and temp_dino.isBlinking == False:
            gameStart = True
# Now we get to the meat of the game. It establishes the placement of the Dino,
# the movement of the ground, and all of the obstacles. Next it establishes the
# game screen.

playerDino = Dino(44,47)
gameOver = False
gameQuit = False
cacti = pygame.sprite.Group()
t = 0
times_played = 1

def gameplay(agent):
    global high_score
    global playerDino
    global gameOver
    global gameQuit
    global t
    gamespeed = 4
    startMenu = False
    new_ground = Ground(-1*gamespeed)
    scb = Scoreboard()
    highsc = Scoreboard(width*0.78)
    episodes = Scoreboard(width*0.1)
    ep_decay = Scoreboard(width*.22)
    DinoHeight = Scoreboard(width*.5)
    counter = 0
    state = GameState(agent)
    cacti_jumped = 0
    is_falling = False
    survived = 0
    state_value = 0
    features = FeatureState()
    global times_played
    high = 0
    best = False

    global cacti
    cacti = pygame.sprite.Group()
    pteras = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    last_obstacle = pygame.sprite.Group()

    Cactus.containers = cacti
    Ptera.containers = pteras
    Cloud.containers = clouds

    retbutton_image,retbutton_rect = load_image('replay_button.png',35,31,-1)
    gameover_image,gameover_rect = load_image('game_over.png',190,11,-1)

    temp_images,temp_rect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
    HI_image = pygame.Surface((22,int(11*6/5)))
    HI_rect = HI_image.get_rect()
    HI_image.fill(background_col)
    HI_image.blit(temp_images[10],temp_rect)
    temp_rect.left += temp_rect.width
    HI_image.blit(temp_images[11],temp_rect)
    HI_rect.top = height*0.1
    HI_rect.left = width*0.73

# Here, the code is for establishing jumping and ducking for the dino.
    while not gameQuit:
        while startMenu:
            pass
        while not gameOver:
            if pygame.display.get_surface() == None:
                print("Couldn't load display surface")
                gameQuit = True
                gameOver = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gameOver = True

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_b:
                            best = True
                        if event.key == pygame.K_v:
                            best = False
                            
                        if event.key == pygame.K_SPACE:
                            playerDino.jump()
                            
                        # if event.key == pygame.K_r:
                        #     gameplay(agent)
                        
                        if event.key == pygame.K_ESCAPE:
                            gameOver = True
                            gameQuit = True

# Now we establish the obstacles. If they hit one, the dino's state changes
# to dead. It populates the game with a random amount of cacti and pteras.
            temp = (epsilon/(1+(np.sqrt(t)/decay)))
            DinoCopy = playerDino
            if full == True:
                if times_played % observe != 0:
                    if temp > epsilon_final:
                        agent.take_action(temp, state, playerDino.isJumping, state_value, gamespeed, features, playerDino.score, DinoCopy)
                        t+=1
                    else: 
                        agent.act_with_best_q(state_value)
                        agent.update_Q(temp, state, playerDino.isJumping, state_value, t, gamespeed, features)
                else: agent.act_with_best_q(state_value)
            else:
                if best == False:
                    agent.take_advanced_action(state, playerDino, temp, features, gamespeed, cacti, pteras)
                    t += 1
                else:
                    state.nearest_on_screen = features.nearest_on_screen
                    state_value = state.get_state(playerDino.rect.bottom, int(playerDino.movement[1]), playerDino.isJumping)
                    # print("else", state_value)
                    agent.act_with_best_q(state_value)
                    t += 1
            
            # if playerDino.rect.bottom != 147: print(playerDino.rect.bottom)
            # agent.act_with_best_q(state_value)
            # print(temp)  
            for c in cacti:
                c.movement[0] = -1*gamespeed
                # if c.dino_distance/gamespeed < 10 and c.dino_distance >0 and playerDino.isJumping != True:
                #     agent.press_jump()
                    
                    
                if pygame.sprite.collide_mask(playerDino,c):
                    playerDino.isDead = True
                    if pygame.mixer.get_init() != None:
                        die_sound.play()
                        
            num_cacti_0 = len(cacti)
            
            for p in pteras:
                p.movement[0] = -1*gamespeed
                if pygame.sprite.collide_mask(playerDino,p):
                    playerDino.isDead = True
                    if pygame.mixer.get_init() != None:
                        die_sound.play()



            if len(cacti) < max_cacti:
                if len(cacti) == 0:
                    last_obstacle.empty()
                    last_obstacle.add(Cactus(gamespeed,40,40))
                else:
                    for l in last_obstacle:
                        if l.rect.right < width*0.7 and random.randrange(0,50) == 10:
                            last_obstacle.empty()
                            last_obstacle.add(Cactus(gamespeed, 40, 40))
                            
            if len(pteras) == 0 and random.randrange(0,200) == 10 and counter > 500 and spawn == True:
                for l in last_obstacle:
                    if l.rect.right < width*0.8:
                        last_obstacle.empty()
                        last_obstacle.add(Ptera(gamespeed, 46, 40))
                            
                                                            
            if len(clouds) < 5 and random.randrange(0,300) == 10:
                Cloud(width,random.randrange(height/5,height/2))
            
            
            high = (int(playerDino.movement[1]))# + 15
             
# After this, it updates all of the states and draws the next screen.
            # print(playerDino.rect.bottom, features.nearest)
            prev_height = playerDino.rect.bottom
            playerDino.update()
            reset = max_score*(times_played+5)
            if playerDino.score == reset: playerDino.isDead = True
            pteras.update()
            cur_height = playerDino.rect.bottom
            if prev_height < cur_height: isfalling = True
            else: isfalling = False
            cacti.update()
            # pteras.update()
            clouds.update()
            new_ground.update()
            scb.update(playerDino.score)
            # scb.update(playerDino.score)
            highsc.update(high_score)
            episodes.update(times_played)
            ep_decay.update(int(10000*temp))
            # print(high, playerDino.isJumping)
            # print(times_played)
            # DinoHeight.update(high)
            # t+=1
            
            ### Cactus jumping
            
            ### Figure out if we have jumped over a cactus previously
            num_cacti_1 = len(cacti)
            # if num_cacti_0 - num_cacti_1 > 0:
            #     survived = True
            survived = num_cacti_0 - num_cacti_1
            cacti_jumped += survived
            
            

            if pygame.display.get_surface() != None:
                screen.fill(background_col)
                new_ground.draw()
                clouds.draw(screen)
                scb.draw()
                episodes.draw()
                ep_decay.draw()
                # DinoHeight.draw()
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image,HI_rect)
                cacti.draw(screen)
                pteras.draw(screen)
                playerDino.draw()

                pygame.display.update()
            clock.tick(FPS)
# Checks if you died.
            if playerDino.isDead:
                gameOver = True
                agent_scores.append(playerDino.score)
                if playerDino.score > high_score:
                    high_score = playerDino.score
# If you didn't, after a certain point, it increases speed
            if counter%700 == 699 and speedup == True:
                new_ground.speed -= 1
                gamespeed += 1

            counter = (counter + 1)
            
            ### Get state for learning on next frame
            features.flatten_sprites(cacti, pteras, gamespeed)
            features.bird_height(pteras, gamespeed)
            state.update(playerDino.rect.bottom, cacti, gamespeed, gameOver, isfalling)
            state_value = state.return_bool_state (playerDino.isJumping, features, gamespeed, playerDino.score)
            ### IF gameOver then we need to store the current game's information?
            

        if gameQuit:
            break
# End credit stuff.
# Allows you to quit the game and get back to the start screen
        while gameOver:
            if pygame.display.get_surface() == None:
                print("Couldn't load display surface")
                gameQuit = True
                gameOver = False
            else:
                #here can use game state to update what we need
                #right now just auto restart for more practice
                # print("gg")
                agent.update_on_gameover(state, features.nearest_on_screen, playerDino.rect.bottom, int(playerDino.movement[1]), playerDino.isJumping, playerDino.score, reset)
                # print(playerDino.isJumping, features.nearest_on_screen)
                times_played += 1
                state.restart()
                playerDino = Dino(44,47)
                gameOver = False
                gameQuit = False
                cacti = pygame.sprite.Group()
                gameplay(agent)
                
            highsc.update(high_score)
            if pygame.display.get_surface() != None:
                disp_gameOver_msg(retbutton_image,gameover_image)
                if high_score != 0:
                    highsc.draw()
                    screen.blit(HI_image,HI_rect)
                pygame.display.update()
            clock.tick(FPS)

    pygame.quit()
    quit()

DinoHeights = [147, 137, 127, 118, 109, 101, 94, 87, 81, 75, 70, 66, 62, 59, 56, 54, 53, 52, 152, 252, 352,
                        -53, -54, -56, -58, -61, -65, -69, -74, -79, -85, -92, -99, -107, -115, -124, -134, -144]

adv_reward = np.zeros((200*38,2))

for i in range(200):
    for j in range(38):
        if i == 0:
            if abs(DinoHeights[j]) > 104 and DinoHeights[j]%100 != 52: adv_reward[j] = [-101,-101]
            elif DinoHeights[j] == -53: adv_reward[j] = [100,100]
        elif i > 182:
            if abs(DinoHeights[j]) > 104 and DinoHeights[j]%100 != 52: adv_reward[38*i + j] = [-101,-101]
adv_reward += [1, -1]

adv_Q = np.zeros(adv_reward.shape)  

adv_e_table = np.zeros(adv_reward.shape)


reward = np.matrix([[1, -1],
                    [1, -1],
                    [-1, 1],
                    [1, -1]])


#add duck reward, with another binary for a t3 height bird
reward = np.matrix([[1, -1],
                    [1, -1],
                    [-1, 1],
                    [1, -1],
                    [-1, 1],
                    [1, -1],
                    [-1, 1],
                    [1, -1],
                    [1, -1],
                    [1, -1],
                    [1, -1],
                    [1, -1],
                    [-1, 1],
                    [1, -1],
                    [-1, 1],
                    [1, -1]])
                    
Q = np.zeros(reward.shape) 

e_table =  np.zeros((len(reward),2))


# Q = np.array([[ 0.83333333, -0.16666667],
#        [ 0.83333333, -0.16666667],
#        [-0.16666667,  0.83333333],
#        [ 0.83333333, -0.16666667]]) 

# output for training on some slow decay [31, 33, 21, 20, 22, 259, 175, 91, 119, 736, 706]
#                                        [33, 142, 20, 158, 452, 517, 179, 94, 522, 20]
# [30, 99, 93, 339, 483, 115, 476, 579, 94, 850, 837, 785, 821, 906, 943, 762, 767, 711, 904, 800, 957, 846, 808, 718, 858, 790, 719, 711, 811]
# [61, 55, 150, 79, 20, 168, 88, 22, 316, 92, 22, 40, 56, 99, 182, 41, 69, 105, 363, 21, 36, 74, 1171, 1187]
# [33, 306, 43, 140, 32, 228, 31, 580, 36, 332, 39, 511, 21, 448, 141, 616, 22, 782, 66, 132, 145, 365, 22] every other
# [21, 155, 20, 468, 304, 46, 36, 66, 120, 458]

# really low Epsilon [1102, 337, 289, 1213, 249, 892, 748, 786, 753, 981, 840, 863, 1206]

trained_Q = np.array([[ 0.83333333, -0.16666667],
       [ 0.83333333, -0.16666667],
       [-0.16666667,  0.83333333],
       [ 0.83333333, -0.16666667],
       [ 0.        ,  0.        ],
       [ 0.        ,  0.        ],
       [-0.16666667,  0.83333333],
       [ 0.83333333, -0.16666667],
       [ 0.        ,  0.        ],
       [ 0.        ,  0.        ],
       [ 0.        ,  0.        ],
       [ 0.        ,  0.        ],
       [ 0.        ,  0.        ],
       [ 0.        ,  0.        ],
       [ 0.        ,  0.        ],
       [ 0.        ,  0.        ]])
# Q = np.array([[ 0.83333333, -0.16666667],
       # [ 0.83333333, -0.16666667],
       # [-0.16666667,  0.83333333],
       # [ 0.83333333, -0.16666667],
       # [ 0.        ,  0.        ],
       # [ 0.        ,  0.        ],
       # [-0.16666667,  0.83333333],
       # [ 0.83333333, -0.16666667],
       # [ 0.        ,  0.        ],
       # [ 0.        ,  0.        ],
       # [ 0.83333333,  0.        ],
       # [ 0.83333333,  0.        ],
       # [ 0.        ,  0.        ],
       # [ 0.        ,  0.        ],
       # [-0.16666667,  0.83333333],
       # [ 0.83333333,  0.        ]])

# trained_Q = np.array([[ 0.10869565, -0.09130435],
#        [ 0.10869565, -0.09130435],
#        [-0.09130435,  0.10869565],
#        [ 0.10869565, -0.09130435]])

# epsilon = .05 decay = 5 epsilon_final = .0004
epsilon = .5
decay = 5
epsilon_final = .001
alpha = .5
gamma = 0.8
observe = 5
agent_scores = []
speedup = False
max_cacti = 1
spawn = False
full = False
max_score = 10


adv_e_table += [epsilon, 1]
e_table += [epsilon, 1]

class Game:
    def __init__(self):
        self.isGameQuit = None
   
    def main(agent, start):
        isGameQuit = introscreen(start)
        if not isGameQuit:
            gameplay(agent)
            

class FeatureState:
    def __init__(self):
        self.nearest = 600
        self.second_nearest = 1200
        self.nearest_on_screen = 150
        self.bird = 0
        
    def flatten_sprites(self, cacti, pteras, gamespeed):
        self.nearest = 600
        self.second_nearest = 1200
        self.nearest_on_screen = 150
        for c in cacti:
            if int(c.dino_distance/gamespeed)< self.nearest_on_screen: self.nearest_on_screen = int(c.dino_distance/gamespeed)
            if c.dino_distance > 0 and int(c.dino_distance/gamespeed) < self.nearest:
                self.second_nearest = self.nearest
                self.nearest = int(c.dino_distance/gamespeed)
        for p in pteras:
            if p.dino_distance > 0:
                if int(p.dino_distance/gamespeed) < self.nearest:
                    self.second_nearest = self.nearest
                    self.nearest = int(p.dino_distance/gamespeed)
                elif int(p.dino_distance/gamespeed) < self.second_nearest:
                    self.second_nearest = int(p.dino_distance/gamespeed)
                    
    def bird_height(self, pteras, gamespeed):
        self.bird = 0
        for p in pteras:
            if int(p.dino_distance/gamespeed) == self.nearest and p.rect.centery == 2:
                self.bird = 1
            
            
# init, determine what type of bird, combine two closest across bird/cactus, interpret, pass to gamestate update

    

class GameState:
    def __init__(self, agent):
        self.agent = agent
        self.bottom = 147
        self.isfalling = False
        # self.nearest = 600
        # self.second_cactus = 1200
        self.isdead = False
        self.state_value = 0
        self.next_state_value = 0
        self.isjumping = False
        self.new_state = 0
        self.height = 147
        self.velocity = 0
        self.fiftytwo = 0
        self.nearest_on_screen = 150
        
    def restart(self):
        #may want something more here to dump replay experience or q-table updates
        #can add a bool that says if we are training or not to initiate or not allow restarts
        pag.press("enter")
        
    def update(self, vertical, features, gamespeed, gameover, isfalling):
        self.isfalling = isfalling
        self.bottom = vertical
        self.isdead = gameover
        # self.nearest = 600
        # self.second_cactus = 1200
        # for c in cacti:
        #     if c.dino_distance > 0 and int(c.dino_distance/gamespeed) < self.nearest:
        #         self.second_cactus = self.nearest
        #         self.nearest = int(c.dino_distance/gamespeed)       
                
    def return_bool_state (self, isjumping, feature, gamespeed, score):
        # tracking = 0
        # if self.nearest < 17: tracking +=2
        # if isjumping == True: tracking +=1
        # return tracking
        scale = 1.2 - (score/5000)
        tracking = 0
        if feature.bird == 1: print("true")
        if feature.second_nearest - feature.nearest-scale*(gamespeed-4) < 17: 
            tracking += 8
            # print("true ")
        if feature.nearest-scale*(gamespeed-4) < 3: tracking += 4
        if feature.nearest-scale*(gamespeed-4) < 17: tracking +=2
        if isjumping == True: tracking +=1
        return tracking
    
    def get_next_state_temp(self, playerDino, action_idx, feature, gamespeed, score, prev_height):
        # get inputs
        self.height = playerDino.rect.bottom
        self.velocity = playerDino.movement[1]
        if playerDino.isJumping == True and self.velocity > 0:
            self.isfalling = True
        else: self.isfalling = False
        
        # calculate next frame
        if playerDino.isJumping == True:
            self.velocity += gravity
    
    def get_state(self, bottom, movement, isjumping):
        self.prev_state = self.state_value
        self.height = bottom
        self.velocity = movement
        self.isjumping = isjumping
        
        if self.height == 52: self.fiftytwo += 1
        else: self.fiftytwo = 0
        
        if movement > 0 and isjumping == True: 
            self.height *= -1
            self.isfalling = True
        else: self.isfalling = False
        
        self.state_value = self.nearest_on_screen*38 + DinoHeights.index(self.height) + self.fiftytwo
        
        return self.state_value
        
    def get_next_state(self, action):
        if action == 0:
            if self.nearest_on_screen != -31:
                if self.isjumping == True:
                    self.next_state_value = (self.nearest_on_screen-1)*38 + ((DinoHeights.index(self.height) + 1 + self.fiftytwo) % 38)
                    if ((DinoHeights.index(self.height) + 1 + self.fiftytwo) % 38) == 0: self.isjumping == False
                    self.nearest_on_screen -=1
                else: 
                    self.next_state_value = (self.nearest_on_screen-1)*38
                    self.nearest_on_screen -=1
            else:
                if self.isjumping == True:
                    self.next_state_value = (150)*38 +  ((DinoHeights.index(self.height) + 1 + self.fiftytwo) % 38)
                    if ((DinoHeights.index(self.height) + 1 + self.fiftytwo) % 38) == 0: self.isjumping == False
                    self.nearest_on_screen = 150
                else: 
                    self.next_state_value = (150)*38
                    self.nearest_on_screen = 150
        else:
            if self.nearest_on_screen != -31:
                if self.isjumping == True:
                    self.next_state_value = (self.nearest_on_screen-1)*38 + ((DinoHeights.index(self.height) + 1 + self.fiftytwo) % 38)
                    if ((DinoHeights.index(self.height) + 1 + self.fiftytwo) % 38) == 0: self.isjumping == False
                    self.nearest_on_screen -= 1
                else: 
                    self.next_state_value = (self.nearest_on_screen-1)*38 + 1
                    self.nearest_on_screen -= 1
            else:
                if self.isjumping == True:
                    self.next_state_value = (150)*38 +  ((DinoHeights.index(self.height) + 1 + self.fiftytwo) % 38)
                    if ((DinoHeights.index(self.height) + 1 + self.fiftytwo) % 38) == 0: self.isjumping == False
                    self.nearest_on_screen = 150
                else: 
                    self.next_state_value = (150)*38 + 1
                    self.nearest_on_screen = 150
        return self.next_state_value
    
    # def get_next_state(self, DinoHeight, isfalling, isjumping, action_idx, feature, gamespeed, score):   
    #     DinoCopy.update() #for some reason updates the playerDino
    #     if action_idx == 1 and DinoCopy.isJumping == False:
    #         DinoCopy.isJumping == True
    #         self.new_state = self.return_bool_state(DinoCopy.isJumping, feature, gamespeed, score)
    #     else: self.new_state = self.return_bool_state(DinoCopy.isJumping, feature, gamespeed, score)
    
    # could make feature and gamespeed part of gamestate
    # then on update in main can update feature there and just take in the new gamespeed,
    # could also check if we will speed up too
    # def get_state(self, actions):
    #     agent.available actions
        
    # sits inside game updates on each frame, talks to agent to find what to do and
    # maybe can make a similarity case function

class Agent:
    def __init__(self, game):
        self.game = game
        self.actions = [0,1]
        self.action_idx = 0
        self.state_value = 0
        self.new_state_value = 0
        self.prev_state = 0
        self.state_action_log = []
        
        self.game.main(self, True)
        
        
    def press_jump(self):
        pag.press("space")
        
    def get_actions(self, state):
        if state.bottom == 147: return [0,1]
        else: return [0]
        
    def take_action(self, epsilon_decay, state, isjumping, state_value, gamespeed, features, score, DinoCopy):
        # print(epsilon_decay)
        state.nearest_on_screen = features.nearest_on_screen
        # print(state.nearest_on_screen)
        if random.random() <= (epsilon_decay):
            self.action_idx = np.random.choice(self.actions)
            if self.action_idx == 1: 
                self.press_jump()
                self.new_state_value = state.return_bool_state(isjumping,features, gamespeed, score)
            # else: self.new_state_value = state_value
        else:
            self.act_with_best_q(state_value)
            # self.action_idx = np.where(Q[state_value,] == np.max(Q[state_value,]))[0][0]
            # if self.action_idx > 1: 
            #     self.press_jump()
            #     self.new_state_value = state.return_bool_state(state, isjumping)
            # else: self.new_state_value = state_value
        self.update_Q(epsilon_decay, state, isjumping, state_value, gamespeed, features)
        # state.get_next_state(DinoCopy, self.action_idx, features, gamespeed, score)
        
    def take_advanced_action(self, state, playerDino, e_decay, features, gamespeed, cacti, birds):
        state.nearest_on_screen = features.nearest_on_screen
        self.prev_state = self.state_value
        self.state_value = state.get_state(playerDino.rect.bottom, int(playerDino.movement[1]), playerDino.isJumping)
        
        # e_state = adv_e_table[self.state_value][0]
        
        if random.random() <= e_decay:
            self.action_idx = np.random.choice(self.actions)
            if self.action_idx == 1: 
                self.press_jump()
        else:
            self.act_with_best_q(self.state_value)
        
        self.state_action_log.append([self.state_value, self.action_idx])    
        self.new_state_value = state.get_next_state(self.action_idx)
        
        if state.isjumping == True:
            if state.nearest_on_screen != -31:
                self.foresight_2 = self.new_state_value - 37
            else: 
                self.foresight_2 = self.new_state_value +150*38 -1
                # for i in range(len(self.state_action_log)-1, len(self.state_action_log)-31, -1):
                #     temp = self.state_action_log[i]
                #     adv_Q[temp[0]][temp[1]] += 10
        else:
            temp_action_idx = np.where(adv_Q[self.new_state_value,] == np.max(adv_Q[self.new_state_value,]))[0][0]
            if temp_action_idx == 1:
                if state.nearest_on_screen != -31:
                    self.foresight_2 = self.new_state_value - 37
                else: 
                    self.foresight_2 = self.new_state_value +150*38 -1
                    for i in range(len(self.state_action_log)-1, len(self.state_action_log)-31, -1):
                        temp = self.state_action_log[i]
                        adv_Q[temp[0]][temp[1]] += 10
            else:
                if state.nearest_on_screen != -31:
                    self.foresight_2 = self.new_state_value - 38
                else: 
                    self.foresight_2 = self.new_state_value +150*38
                    for i in range(len(self.state_action_log)-1, len(self.state_action_log)-31, -1):
                        temp = self.state_action_log[i]
                        adv_Q[temp[0]][temp[1]] += 10
                    
        
        self.adv_update_Q()
        
        # adv_e_table[self.state_value][0] = epsilon/adv_e_table[self.state_value][1]
        # adv_e_table[self.state_value][1] += 1
        
    
    def update_on_gameover(self, state, nearest, bottom, movement, isjumping, score, reset):
        if score != reset:
            if state.isfalling == True:
                for i in range(len(self.state_action_log)-1, len(self.state_action_log)-21, -1):
                    temp = self.state_action_log[i]
                    adv_Q[temp[0]] += [-100,-100]
            else:
                for i in range(len(self.state_action_log)-1, len(self.state_action_log)-4, -1):
                    temp = self.state_action_log[i]
                    adv_Q[temp[0]] += [-100,-100]
            state.nearest_on_screen = nearest
            self.state_value = state.get_state(bottom, movement, isjumping)
            adv_Q[self.state_value] = [-1000,-1000]
            # adv_Q[self.prev_state] = [-1000, -1000]
        
        else:
            for i in range(len(self.state_action_log)):
                    temp = self.state_action_log[i]
                    adv_Q[temp[0]][temp[1]] += score/100
                    
        self.action_log = []
                    
        
    def adv_update_Q(self):
        adv_Q[self.state_value, self.action_idx] += alpha * adv_reward[self.state_value, self.action_idx] + gamma*(np.max(adv_Q[self.new_state_value,:]) + gamma*np.max(adv_Q[self.foresight_2,:])) - adv_Q[self.state_value, self.action_idx]
        
    def update_Q(self, epsilon_decay, state, isjumping, state_value, gamespeed, features):
        Q[state_value, self.action_idx] += alpha * (reward[state_value, self.action_idx] 
                    + gamma*(np.max(Q[self.new_state_value,:])) 
                    + gamma*0)-Q[state_value, self.action_idx]
        
        
    def act_with_best_q(self, state_value):
        # self.action_idx = np.where(trained_Q[state_value,] == np.max(trained_Q[state_value,]))[0][0]
        # self.action_idx = np.where(Q[state_value,] == np.max(Q[state_value,]))[0][0]
        self.action_idx = np.where(adv_Q[state_value,] == np.max(adv_Q[state_value,]))[0][0]
        if self.action_idx == 1: self.press_jump()
  
        
# need similarity function that just gets duck? jump with close behind? jump with duck after?                    
        
#height > cactus then reward if cactus is under
#reward is +num cacti jumped, +.1 for each frame, -100 for dying?
# 
# [85, 437, 232, 894, 814, 865]
# 
# Q
# Out[44]: 
# array([[ 0.83333333, -0.16666667],
#        [ 0.83333333, -0.16666667],
#        [-0.16666667,  0.83333333],
#        [ 0.83333333, -0.16666667],
#        [ 0.        ,  0.        ],
#        [ 0.        ,  0.        ],
#        [-0.16666667,  0.83333333],
#        [ 0.83333333, -0.16666667],
#        [ 0.83333333, -0.16666667],
#        [ 0.83333333,  0.        ],
#        [ 0.83333333,  0.        ],
#        [ 0.83333333,  0.        ],
#        [ 0.        ,  0.        ],
#        [ 0.        ,  0.        ],
#        [-0.16666667,  0.83333333],
#        [ 0.83333333,  0.        ]])


game = Game
agent = Agent(game)
print(agent_scores)  

# [20, 20, 69, 70, 20, 45, 46, 172, 194, 20, 154, 154, 94, 307, 20, 133, 428, 276, 429, 20, 210, 70, 821, 348, 20, 259, 243, 44, 821, 20, 335, 292, 193, 453, 20, 291, 45, 390, 513, 20, 243, 699]
# policy became to jump as close as possible
# [44, 22, 21, 46, 20, 42, 56, 75, 22, 20, 96, 127]
# [20, 44, 20, 45, 22, 20, 210, 21, 44, 114, 94, 291, 227, 545, 524, 242, 21, 134, 275, 45, 226, 69, 21, 115, 376, 210, 46, 114, 45, 45, 307, 259, 193, 173, 21, 70, 133, 404, 404, 404, 453]
# [33, 20, 21, 20, 44, 20, 49, 20, 50, 49, 47, 20, 20, 22, 46, 79, 20, 79, 113, 20, 352, 20, 20, 48, 41, 20, 20, 248, 21, 145]

# balanced jump and no input 20 trials
# [20, 20, 20, 118, 20, 20, 21, 69, 45, 46, 45, 69, 142, 21, 45, 119, 45, 20, 363, 93]

# Bias += [1,0] on reward
# [20, 46, 20, 46, 45, 45, 191, 20, 69, 93, 22, 45, 46, 241, 362, 289, 167, 70, 240, 20, 69, 313, 119, 22, 143, 167, 20, 20, 240, 289]

# same bias as above and one for being at peak over the cactus [0,10]
# [45, 44, 22, 44, 20, 20, 20, 93, 142, 20, 240, 71, 20, 436, 45, 46, 20, 117, 20, 95, 191]

# [44, 20, 20, 68, 21, 21, 44, 118, 20, 69, 69, 22, 93, 21, 265, 117, 20, 20, 364, 44, 143, 93, 166]

# [20, 20, 20, 20, 95, 412, 1510, 411, 289, 583, 535, 44, 119, 899, 582, 264, 828, 46, 22

# [20, 68, 46, 607, 166, 411, 93, 143, 1437, 69, 20, 118, 20]

# [20, 70, 80, 22, 46, 46, 20, 130, 21, 150, 143, 21, 180, 20, 69, 45, 21, 21, 20, 21, 21, 21, 94]

# 
# m=0
# for i in range(len(adv_Q[:,1])): 
#     if adv_Q[:,1][i] > 0:
#         print(i)
#     if adv_Q[:,1][i] > m:
#         m = adv_Q[:,1][i]
#         print(m, i)
#         
# 100
# 0.4 100
# 152
# 0.976 152
# 190
# 380
# 456
# 481
# 594
# 608
# 683
# 758
# 943
# 1026
# 1368
# 1406
# 1418
# 1634
# 1672
# 1710
# 1742
# 1748
# 1862
# 1900
# 1938
# 2090
# 2318
# 2393
# 1.34464 2393
# 2557
# 2642
# 2736
# 2964
# 3002
# 3229
# 1.5805696 3229
# 3382
# 3458
# 3478
# 3625
# 3736
# 3842
# 4180
# 4218
# 4256
# 4674
# 4757
# 4902
# 4978
# 5240
# 6453
# 6490
# 6527
# 6564
# 6601
# 6638
# 6749
# 1.600492544 6749
# 6786
# 6898
# 6935
# 7082
# 7119
# 7156
# 7193
# 7230
# 
# adv_Q[6749]
# Out[35]: array([ 2.10049254,  1.60049254])
# 
# adv_Q[3229]
# Out[36]: array([ 1.6808   ,  1.5805696])
# 
# adv_Q[2393]
# Out[37]: array([ 0.     ,  1.34464])
# 
# 2393 % 38
# Out[38]: 37
# 
# adv_Q[100]
# Out[39]: array([ 0.5,  0.4])
# 
# adv_Q[152]
# Out[40]: array([ 0.9  ,  0.976])
# 
# 152%38
# Out[41]: 0
# 
# 152/38
# Out[42]: 4.0
# 
# 2393/38
# Out[43]: 62.973684210526315
# 
# 2394/38
# Out[44]: 63.0