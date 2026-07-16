import pygame
from pygame import mixer
# from pygame.locals import *
import random
import sys
import time
import threading
import math

# import time
# from os import path
# import json

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

#Screen Dimensions
screen_width = 600
screen_height = 800
win = pygame.display.set_mode((screen_width, screen_height))

# colors----------------------------------------------------
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# define game variables---------------------------------------------------------
rows = 5
columns = 5
number = 1
boss_final = False
paused = False
length = 1
length2 = -1
rate = 3


# Variables to manage text animation
base_size = 35  # Initial size of the text
max_size = 55  # Maximum size when growing
min_size = 35 # Minimum size when shrinking
grow_time = 50  # Number of frames to grow
shrink_time = 50  # Number of frames to shrink

frame = 0  # Frame counter for animation
growing = True  # State to track whether text is growing or shrinking
text_size = base_size  # Initial text size


# time tools------------------------------------------------------------
time_now = 0
func_start = 0
time_last_hit = 0

# number of waves--------------------------------------------------
global waves
waves = 1
global missilex
global missiley
missilex = 0
missiley = 0
paused = False
global field, spawn_x, spawn_y
cooldown = 100

spawn_x = 0
spawn_y = 0

# update1 add reload Flag
is_reloaded = True
is_gameover = True

sayings = ["Are U Afraid of the DARK?", "Cindy, I don't like you using foul language",
           "were friends to the end.... remember?", "Close your eyes and count to seven", "The bodies are pilling up"]
saying = random.choice(sayings)

#Initialize pygame clock
clock = pygame.time.Clock()
fps = 60

#Load images
#try:

alien_cooldown = 1000  # ms
last_alien_shot = pygame.time.get_ticks()
last_boss_shot = pygame.time.get_ticks()


clock.tick(fps)
move_counter = 0
move_direction = 1
adjustment = 0


# SpriteSheet-------------------------------------------------------------------------------
class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, x, y, w, h, colour, rotate, xx, yy):
        image = pygame.Surface((w, h)).convert_alpha()
        image.blit(self.sheet, (0, 0), (x, y, w, h))
        image = pygame.transform.scale(image, (xx, yy))
        image = pygame.transform.rotate(image, rotate)
        image.set_colorkey(colour)

        return image

pygame.display.set_caption('Spritesheets')
sprite_sheet_image = pygame.image.load('missiles.png').convert_alpha()
sprite_sheet_image2 = pygame.image.load('thruster.png').convert_alpha()
sprite_sheet = SpriteSheet(sprite_sheet_image)
scale = 7

# SpriteSheet Grabs  self, x, y, w, h, colour, rotate, xx, yy--------------------------------------
miss1 = sprite_sheet.get_image(0, 0, 350, 80, black, 90, 50, 15)
miss2 = sprite_sheet.get_image(350, 0, 350, 80, black, 90, 50, 15)
miss3 = sprite_sheet.get_image(700, 0, 350, 80, black, 90, 50, 15)
miss4 = sprite_sheet.get_image(1050, 0, 350, 80, black, 90, 50, 15)
miss5 = sprite_sheet.get_image(0, 80, 350, 80, black, 90, 50, 15)
miss6 = sprite_sheet.get_image(350, 80, 350, 80, black, 90, 50, 15)
miss7 = sprite_sheet.get_image(700, 80, 350, 80, black, 90, 50, 15)
miss8 = sprite_sheet.get_image(1050, 80, 350, 80, black, 90, 50, 15)
missileup = [miss1, miss1, miss1, miss2, miss3, miss4, miss5, miss6, miss7, miss8, miss7, miss8]

upgrade_missile = miss1

sprite_sheet2 = SpriteSheet(sprite_sheet_image2)

ships = [pygame.image.load("spaceship.png"), pygame.image.load("spaceship.png"), pygame.image.load("spaceship2.png"),
         pygame.image.load("spaceship3.png")]

# jet thrusters for boss-------------------------------------------------------------------------------------
thrust1 = sprite_sheet2.get_image(0, 0, 204, 287, black, 0, 51, 71)
thrust2 = sprite_sheet2.get_image(0, 287, 204, 287, black, 0, 51, 71)
thrust3 = sprite_sheet2.get_image(0, 574, 204, 287, black, 0, 51, 71)

pygame.display.set_caption("Space Imitators")

big_bullet = pygame.image.load("bullet.png")
big_bullet = pygame.transform.scale(big_bullet, (60, 60))

med1_bullet = pygame.image.load("bullet.png")
med1_bullet = pygame.transform.scale(big_bullet, (40, 40))

med2_bullet = pygame.image.load("bullet.png")
med2_bullet = pygame.transform.scale(big_bullet, (50, 50))

sm1_bullet = pygame.image.load("bullet.png")
sm1_bullet = pygame.transform.scale(big_bullet, (20, 20))

sm2_bullet = pygame.image.load("bullet.png")
sm2_bullet = pygame.transform.scale(big_bullet, (30, 30))

big_boss_bullet = pygame.image.load("alien_bullet.png")
big_boss_bullet = pygame.transform.scale(big_boss_bullet, (90, 90))

med1_boss_bullet = pygame.image.load("alien_bullet.png")
med1_boss_bullet = pygame.transform.scale(big_boss_bullet, (60, 60))

med2_boss_bullet = pygame.image.load("alien_bullet.png")
med2_boss_bullet = pygame.transform.scale(big_boss_bullet, (75, 75))

sm1_boss_bullet = pygame.image.load("alien_bullet.png")
sm1_boss_bullet = pygame.transform.scale(big_boss_bullet, (30, 30))

sm2_boss_bullet = pygame.image.load("alien_bullet.png")
sm2_boss_bullet = pygame.transform.scale(big_boss_bullet, (45, 45))
small_boss_bullet = pygame.image.load("alien_bullet.png")

small_bullet = pygame.image.load("bullet.png")

boss = pygame.image.load("boss.png")

# Funcions...............................................

def charge1(image, x, y):
    win.blit(image, (x - 110, y - 35))
    win.blit(image, (x - 110, y - 95))
    win.blit(image, (x - 110, y - 155))

    win.blit(image, (x + 100, y - 35))
    win.blit(image, (x + 100, y - 95))
    win.blit(image, (x + 100, y - 155))

def charge2(image, x, y):
    win.blit(image, (x - 80, y - 60))
    win.blit(image, (x - 80, y - 95))
    win.blit(image, (x - 80, y - 130))

    win.blit(image, (x + 70, y - 60))
    win.blit(image, (x + 70, y - 95))
    win.blit(image, (x + 70, y - 130))

def charge3(image, x, y):
    win.blit(image, (x - 50, y - 90))
    win.blit(image, (x - 50, y - 95))
    win.blit(image, (x - 50, y - 100))

    win.blit(image, (x + 40, y - 90))
    win.blit(image, (x + 40, y - 95))
    win.blit(image, (x + 40, y - 100))

def pause():
    paused = True

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u and paused == True:
                    paused = False
                    break
                    # paused = False

        # win.fill(white)

def draw_bg():
    win.blit(bg, (0, 0))

# screen moves top down
def moving_screen():
    global y1,y
    speed = 3.0
    y1 += speed  # both control the speed of the screen moving
    y += speed  # both control the speed of the screen moving
    win.blit(bg, (x, round(y)))
    win.blit(bg, (x1, round(y1)))
    if y > h:
        y = -h
    if y1 > h:
        y1 = -h

# moves screen faster for next level
def moving_screen2():
    global y1, y
    speed = 24
    y1 += speed  # both control the speed of the screen moving
    y += speed  # both control the speed of the screen moving
    win.blit(bg, (x, y))
    win.blit(bg, (x1, y1))
    if y > h:
        y = -h
    if y1 > h:
        y1 = -h

# define function for creatin text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    win.blit(img, (x, y))

def draw_text2(text, size, color, x, y):
    font_name = pygame.font.match_font(FONT_NAME)
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    win.blit(text_surface, text_rect)

def animate_text():
    global frame, growing, text_size

    # Text animation logic
    if growing:
        text_size = base_size + (max_size - base_size) * (frame / grow_time)
        if frame >= grow_time:
            growing = False
            frame = 0
    else:
        text_size = max_size - (max_size - min_size) * (frame / shrink_time)
        if frame >= shrink_time:
            growing = True
            frame = 0

    frame += 1
    return int(text_size)

# start screen
def show_start_screen():

    # update2 Move the display background logic to the wait for key
    wait_for_key()

# loop For Start Screen
def wait_for_key():
    waiting = True
    while waiting:
        # update2 add Move the display background logic
        draw_bg()
        moving_screen()
        intro_spaceship_group.add(intro_spaceship, intro_spaceship2, intro_spaceship3)
        intro_boss_group.add(intro_boss)
        # Call animate_text() to get the current animated size
        animated_size = animate_text()

        # Draw the animated text with the new size
        draw_text2("SPACEIMITATORS!!!", animated_size, green, screen_width / 2, screen_height / 4)
        # draw_text2("<  or  > to move, Spacebar to fire", 22, green, screen_width / 2, screen_height / 3)
        if intro_spaceship2.rect.centery < 600:
            draw_text2("Press any key", 22, green, screen_width / 2, screen_height - 150)

        # update
        intro_spaceship_group.update()
        intro_boss_group.update()

        # Draw
        intro_spaceship_group.draw(win)
        intro_boss_group.draw(win)
        pygame.display.update()
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.QUIT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

# Game Over function
def show_go_screen():
    waiting = True
    change = 1
    rate = 1

    while waiting:
        draw_bg()
        moving_screen()
        draw_text2("GAME OVER!!!", 68 + change, red, screen_width / 2, screen_height / 4)
        change += rate
        if change >= 45:
            rate *= -1
        # elif change <= -15:
        # rate *= -1
        # draw_text2("change: " + str(change), 22, red, screen_width / 1 * 3/4, screen_height / 1 * 2/3)
        draw_text2(saying, 22, red, screen_width / 2, screen_height / 2)
        draw_text2("Press Any Key to Play Again", 22, red, screen_width / 2, screen_height * 3 / 4)
        pygame.display.update()
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def create_aliens():
    if waves != 4 and waves != 8 and waves != 12:
        for row in range(rows):
            for item in range(columns):
                alien = Aliens(100 + item * 100, 100 + row * 70, row, item, move_counter, move_direction)
                alien_group.add(alien)
                field[row][item] = 1

# regenerating space invaders within the wave
def regen_invaders():
    if waves != 1 or len(alien_group) > 20:
        return
    # record the location of any invader alive
    # is it plus or minus the spawning area? add or subtract it
    down = random.randint(0, rows - 1)
    across = random.randint(0, columns - 1)
    if field[down][across] == 0:
        _extracted_from_regen_invaders_8(across, down)

# TODO Rename this here and in `regen_invaders`
def _extracted_from_regen_invaders_8(across, down):
    global move_counter
    global move_direction
    global adjustment
    adjustment = (75 + move_counter) * move_direction
    alien = Aliens((100 + adjustment) + across * 100, 100 + down * 70, down, across, move_counter,
                   move_direction)
    alien_group.add(alien)
    field[down][across] = 1

# wave after wave of aliens
def restore_aliens():
    global rate
    if time_now - last_alien_shot > 2.5 * alien_cooldown and len(alien_group) == 0:
        global move_counter
        move_counter = 0
        global waves, is_reloaded
        if is_reloaded:
            # update1  Execute it on a new thread instead
            is_reloaded = False
            thread1 = myThread()
            thread1.start()

# team assist from tiger ship
def missile_assist():
    missile = Missiles(350, 1000)
    missile_group.add(missile)
    spaceship.last_shot = time_now

def screen_blink():
    global rate
    global length

    if time_now - last_alien_shot > 2.5 * alien_cooldown and len(alien_group) == 0:
        rectangle_1 = pygame.draw.rect(win, black, (0, 0, screen_width, length))
        rectangle_2 = pygame.draw.rect(win, black, (0, (800 - length), screen_width, length))
        length += rate

        if length >= (screen_height / 2):
            rate *= -1

        elif length <= 0:
            length = 1
            rate *= 0
    else:
        length = 1
        rate = 3
        length2 = -1

def boss_charge_effect(x1, x2, y1, y2, y3):
    win.blit(small_boss_bullet, (boss.rect.centerx + x1, boss.rect.centery + y1))
    win.blit(small_boss_bullet, (boss.rect.centerx + x1, boss.rect.centery + y2))
    win.blit(small_boss_bullet, (boss.rect.centerx + x1, boss.rect.centery + y3))

    win.blit(small_boss_bullet, (boss.rect.centerx + x2, boss.rect.centery + y1))
    win.blit(small_boss_bullet, (boss.rect.centerx + x2, boss.rect.centery + y2))
    win.blit(small_boss_bullet, (boss.rect.centerx + x2, boss.rect.centery + y3))

# define fonts........................................................
font30 = pygame.font.SysFont
FONT_NAME = 'arial'

# load Sounds
explosion_fx = pygame.mixer.Sound("explosion.wav")
explosion_fx.set_volume(0.01)

explosion2_fx = pygame.mixer.Sound("explosion2.wav")
explosion2_fx.set_volume(0.01)

laser_fx = pygame.mixer.Sound("laser.wav")
laser_fx.set_volume(0.01)
bg = pygame.image.load("bg.png")

speed_list2 = [4, 5, 6]
height_list = [0, 100, 200]
speed = random.choice(speed_list2)
border = random.choice([475, 485, 495])
start_health = 6
hit_cooldown = 10000

background_size = bg.get_size()
background_rect = bg.get_rect()
# win = pygame.display.set_mode(background_size)
w, h = background_size
x = 0
y = 0

x1 = 0
y1 = -h

charge_adjust_x = 0
charge_adjust_y = 0
global angle
angle = 90
ship_angle = 30

# OBJECTS HERE------------------------
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health, ship):
        #pygame.sprite.Sprite.__init__(self)
        #self.image = ships[ship]
        super().__init__()
        global ship_angle
        self.image_orig = ships[ship].convert_alpha()
        self.image = self.image_orig
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.clone = 1
        self.wave = 1
        self.charge_counter = 0
        self.move = True
        self.speed = 8


    def handle_movement(self):
        global angle, ship_angle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0 and self.move:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.left < 520 and self.move:
            self.rect.x += self.speed
        #if keys[pygame.K_z]:
            #angle -= 1
            #ship_angle = ship_angle + 1
        #if keys[pygame.K_x]:
            #angle += 1
            #ship_angle = ship_angle - 1

    #def charge_adjust(self):
        #if self.handle_beam_charge_effect(sm1_bullet, charge1):



    def draw_health_bar(self):
        if self.health_remaining >= 1:
            pygame.draw.rect(win, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 4))
        if self.health_remaining > 0:
            pygame.draw.rect(win, green, (
                self.rect.x, (self.rect.bottom + 10),
                int(self.rect.width * (self.health_remaining / self.health_start)), 4))
        elif self.health_remaining == 0:
            self.kill()
            global game_over
            game_over = True

    def regenerate_health(self):
        global time_last_hit, time_now, start_health, hit_cooldown
        if (
            self.health_remaining < start_health
            and time_now - time_last_hit > hit_cooldown
            and self.health_remaining != 0
        ):
            self.health_remaining += 1
            time_last_hit = time_now

    def handle_shooting(self):
        keys = pygame.key.get_pressed()
        global time_now, cooldown, running, rise, angle

        if keys[pygame.K_SPACE] and time_now - self.last_shot > cooldown * 2:
            self.shoot_bullet()

        if keys[pygame.K_v] and time_now - self.last_shot > cooldown * 5:
            self.shoot_missile()

        if keys[pygame.K_c]:
            self.handle_charge_shot()

        else:
            self.move = True
            self.rect.y = screen_height - 100
            self.charge_counter = 0

    def shoot_bullet(self):
        global laser_fx, bullet_group,angle, spawn_x, spawn_y
        #bullet_speed = 25  # Adjust bullet speed as needed
        bullet_offset_x = 0  # Adjust bullet offset from the center of the spaceship
        bullet_offset_y = 1    # Adjust bullet offset from the center of the spaceship

        # Calculate bullet spawn position based on the spaceship's current angle
        spawn_x = self.rect.centerx + bullet_offset_x * math.cos(math.radians(self.angle))

        spawn_y = self.rect.centery - bullet_offset_y * math.sin(math.radians(self.angle))

        # Create and add the bullet to the bullet group
        bullet = Bullets(spawn_x, spawn_y, self.angle + 90)
        bullet_group.add(bullet)

        # Update the last shot time
        self.last_shot = time_now

    def rotate(self, angle):
        self.angle += angle
        rotated_image = pygame.transform.rotate(self.image_orig, self.angle)
        self.image = pygame.Surface(rotated_image.get_size(), pygame.SRCALPHA)
        self.image.blit(rotated_image, (0, 0))
        self.rect = self.image.get_rect(center=self.rect.center)



    def shoot_missile(self):
        global laser_fx, missile_group
        laser_fx.play()
        missile = Missiles(self.rect.centerx, self.rect.centery)
        missile_group.add(missile)
        self.last_shot = time_now

    def handle_charge_shot(self):
        self.charge_counter += 1
        self.move = False
        global charge_adjust_x,charge_adjust_y

        if 35 < self.charge_counter < 40:
            self.fire_charge_shot()
            self.rect.y = screen_height - 60

        if 5 < self.charge_counter < 9:
            charge_adjust_x = 10
            charge_adjust_y = 90
            self.handle_beam_charge_effect(sm1_bullet, charge1)


        if 9 < self.charge_counter < 14:
            charge_adjust_x = 14
            charge_adjust_y = 95
            self.handle_beam_charge_effect(sm2_bullet, charge2)
            self.rect.x = spaceship.rect.x + 2


        if 15 < self.charge_counter < 19:
            charge_adjust_x = 21
            charge_adjust_y = 100
            self.handle_beam_charge_effect(med1_bullet, charge3)
            self.rect.x = spaceship.rect.x - 2

        # Add similar blocks for other charge levels
        if 20 < self.charge_counter < 24:
            charge_adjust_x = 24
            charge_adjust_y = 105
            self.handle_beam_charge_effect(med2_bullet, charge1)
            self.rect.x = spaceship.rect.x + 2

        if 25 < self.charge_counter < 30:
            charge_adjust_x = 30
            charge_adjust_y = 110
            self.handle_beam_charge_effect(big_bullet, charge2)
            self.rect.x = spaceship.rect.x - 1


        if 31 < self.charge_counter < 35:
            charge3(small_bullet, self.rect.centerx, self.rect.centery)

    def fire_charge_shot(self):
        global Charge_Shot_group
        charge_shot = Charge_Shot(self.rect.centerx - 2, screen_height - 120)
        Charge_Shot_group.add(charge_shot)

    def handle_beam_charge_effect(self, bullet_image, charge_effect):

        win.blit(bullet_image, (self.rect.centerx - charge_adjust_x, self.rect.centery - charge_adjust_y))
        charge_effect(small_bullet, self.rect.centerx, self.rect.centery)



    # Add similar methods for other charge levels

    def update(self):
        global angle
        keys = pygame.key.get_pressed()
        self.handle_movement()
        self.draw_health_bar()
        self.regenerate_health()
        self.update_mask()
        self.handle_shooting()
        self.image

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.image)

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(boss, (120, 120))
        # self.image = pygame.transform.rotate(self.image, 45)

        self.image2 = pygame.transform.scale(pygame.image.load("lowhealth.png"), (120, 120))

        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.move_counter = 0
        self.charge_counter = 0
        self.pass_counter = 0
        self.move_direction = 1  # change back to 1
        self.move = True

    def update(self):
        Speed = 8
        # cool down veriable
        cooldown = 100

        # health bars
        if self.health_remaining >= 1 / 2:
            pygame.draw.rect(win, red, (self.rect.x, (self.rect.top - 10), self.rect.width - 4, 8))
        if self.health_remaining > 0:
            pygame.draw.rect(win, green, (
                self.rect.x, (self.rect.top - 10),
                (int(self.rect.width * (self.health_remaining / self.health_start))) - 4,
                8))

        if self.health_remaining <= 0:
            # self.kill()
            # explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            # explosion_group.add(explosion)
            self.move_direction = 0
            # jet out of there for next time
            self.rect.y += 9
            thrust_group.draw(win)
            # moves screen fast for movement
            # moving_screen2()

        # Shield follows you
        # global shield
        # shield.rect.x = self.rect.center[0] - 87
        # shield.rect.y = self.rect.center[1] - 25

        # update mask
        self.mask = pygame.mask.from_surface(self.image)

        # move
        if self.rect.center[1] <= 100:  # and boss_final == True:
            self.rect.y += 5
            thrust_group.draw(win)
        elif self.rect.center[1] >= 100 and self.health_remaining > 6 and self.move and self.charge_counter == 0:
            self.rect.x += self.move_direction * 8  # change number for speed and
            self.move_counter += 1
            if abs(self.move_counter) > 30:  # and this for side parameters when speed is changed
                self.move_direction *= -1
                self.move_counter *= self.move_direction
                self.pass_counter += 1
        elif self.rect.center[1] < 400 and self.health_remaining <= 6:  # movement on half health, move closer to player
            self.rect.y += 7
            thrust_group.draw(win)
            # moves screen very fast
            # moving_screen2()

        elif 400 <= self.rect.center[1] <= 425 and self.health_remaining <= 6:
            self.rect.x += self.move_direction * 8  # change number for speed and
            self.move_counter += 1
            if abs(self.move_counter) > 37:  # and this for side parameters when speed is changed
                self.move_direction *= -1
                self.move_counter *= self.move_direction
            # moving_screen2()  # moves screen fast while moving left to right and vice versa

        # Charge Shot  #if 3 passes left right left, charge graphic, then shoot, then resume left right left
        if self.pass_counter >= 5 and 295 < self.rect.center[0] < 305 and self.move:
            self.move = False  # Cant Move
            self.charge_counter += 1
        if not self.move:
            self.charge_counter += 1

        # Fire
        if 39 <= self.charge_counter < 44:
            boss_charge_shot = Boss_Charge_Shot(self.rect.centerx, self.rect.centery + 115)
            Boss_Charge_Shot_group.add(boss_charge_shot)

            # push Back

        elif 39 <= self.charge_counter < 48:
            self.rect.y = self.rect.y - 15

        elif 9 < self.charge_counter < 13:
            # Beam charge effect
            # left side
            boss_charge_effect(-110, 100, 35, 95, 155)

        elif 13 < self.charge_counter < 17:
            self.rect.x += 2

            # Beam charge effect
            # left side
            boss_charge_effect(-80, 70, 60, 95, 130)

        elif 17 < self.charge_counter < 21:
            self.rect.x -= 3

            # Beam charge effect
            # left side
            boss_charge_effect(-50, 40, 85, 95, 105)

        elif 21 < self.charge_counter < 25:
            win.blit(sm1_boss_bullet, (self.rect.centerx - 15, self.rect.centery + 85))
            self.rect.x = boss.rect.x + 2
            # Beam charge effect
            # left side
            boss_charge_effect(-110, 100, 35, 95, 155)

        elif 26 < self.charge_counter < 30:
            self.rect.x = boss.rect.x - 3
            win.blit(sm2_boss_bullet, (self.rect.centerx - 22, self.rect.centery + 81))
            # Beam charge effect
            # left side
            boss_charge_effect(-75, 65, 60, 95, 130)

        elif 31 < self.charge_counter < 35:
            self.rect.x = boss.rect.x + 2
            win.blit(med1_boss_bullet, (self.rect.centerx - 30, self.rect.centery + 77))

            # Beam charge effect
            # left side
            boss_charge_effect(-45, 35, 85, 95, 105)

        elif self.charge_counter > 60:
            self.pass_counter = 0
            self.charge_counter = 0
            self.move = True

        # else:
        # resume moving#
        # self.move = True
        # resuming position from push back#
        # self.rect.y = screen_height - 100
        # resetting count#
        # self.charge_counter += 1

        # boss flash when low health 2
        if self.move_counter % 8 == 0 and self.health_remaining <= 6:
            self.image = pygame.transform.scale(pygame.image.load("lowhealth.png"), (120, 120))
        else:
            self.image = pygame.transform.scale(pygame.image.load("boss.png"), (120, 120))

        # leave when dead
        if self.rect.y >= 1000:
            self.kill()
            # self.speed = 0
            self.health_remaining = 12
            self.move_direction = 1
            self.rect.centerx = int(screen_width / 2)

            # boss = Boss(int(screen_width / 2), screen_height - 1200, 20)
            shield = Shield(boss.rect.center[0] - 85, boss.rect.center[1] - 40, 50)
            shield_group.add(shield)
            shield.health_remaining = 12
            self.move_counter = 0

            restore_aliens()
            # self.rect.y = (screen_height - 1200)

class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y, row, item, move_counter, move_direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = move_counter
        self.move_direction = move_direction
        self.row = row
        self.item = item

        # global minishield
        # minishield = SmallShield(self.rect.centerx, self.rect.y + 20, 12)
        # shield_group.add(minishield)

    def update(self):
        global move_counter
        global move_direction
        move_counter = self.move_counter
        move_direction = self.move_direction
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1

            self.move_counter *= self.move_direction

        if pygame.sprite.spritecollide(self, bullet_group, False):
            global field
            field[self.row][self.item] = 0
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            explosion_fx.play()

        # minishield.rect.x = self.rect.x -2
        # minishield.rect.y = self.rect.y + 2

class Aliens2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction * 3
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        pygame.sprite.Sprite.__init__(self)


        self.image = pygame.image.load("bullet.png")
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.image = pygame.transform.rotate(self.image, angle - 90)
        #self.image2 = self.image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        #self.rect.center = [x, y]
        self.angle = angle
        theta_rad = math.radians(self.angle)
        bullet_speed = 10
        self.velocity_x = bullet_speed * math.cos(theta_rad)
        self.velocity_y = -bullet_speed * math.sin(theta_rad)
        self.size_multiplier = 1.0  # Initial size multiplier
        self.pulsate_speed = 0.1  # Adjust pulsate speed as needed
        self.base_size = self.rect.size
        self.center_x, self.center_y = x, y

    def update(self):
        # Adjust size gradually
        #self.image = pygame.transform.scale(self.image,(int(self.rect.width * 2), int(self.rect.height * 2)))

        # Calculate distance from the center of the sprite
        #distance_x = self.rect.centerx - self.center_x
        #distance_y = self.rect.centery - self.center_y
        #distance_from_center = math.sqrt(distance_x ** 2 + distance_y ** 2)

        # Update size based on sine function for pulsating effect
        #self.size_multiplier = 1.0 + 0.2 * math.sin(pygame.time.get_ticks() * self.pulsate_speed)

        # Scale the image based on the size multiplier
        #scaled_size = (int(self.base_size[0] * self.size_multiplier), int(self.base_size[1] * self.size_multiplier))
        #scaled_image = pygame.transform.scale(self.image, scaled_size)

        # Create a mask for the original image
        original_mask = pygame.mask.from_surface(self.image)

        # Apply the original texture to the scaled image using the mask
        #self.image2.fill((0, 0, 0, 0))  # Clear the image
        #self.image2.blit(scaled_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
       #self.image2.blit(self.original_image, self.original_image.get_rect(center=scaled_image.get_rect().center),special_flags=pygame.BLEND_RGBA_MAX)

        # was 5 before change to 25
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        if self.rect.bottom < 0:
            self.kill()
        # if pygame.sprite.spritecollide(self, alien_group, True):

        elif pygame.sprite.spritecollide(self, boss_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            boss.health_remaining -= 1 / 2
        elif pygame.sprite.spritecollide(self, shield_group, False):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            shield_group.draw(win)
            shield.health_remaining -= 1
        elif pygame.sprite.spritecollide(self, boss_bullet_group, False):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
        elif pygame.sprite.spritecollide(self, Boss_Charge_Shot_group, False):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

class Charge_Shot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("bullet.png")
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

        elif pygame.sprite.spritecollide(self, boss_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            boss.health_remaining -= 5
            # True goes through the sprite,     #false means the shot doesnt go through
        elif pygame.sprite.spritecollide(self, shield_group, False):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            shield_group.draw(win)
                # boss.health_remaining += 1
                # shield.health_remaining -= 10
        elif pygame.sprite.spritecollide(self, boss_bullet_group, True):
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
        elif pygame.sprite.spritecollide(self, missile_group, False):
            self.kill
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion = Explosion(self.rect.centerx + 25, self.rect.centery, 3)
            explosion = Explosion(self.rect.centerx - 25, self.rect.centery, 3)
            explosion = Explosion(self.rect.centerx, self.rect.centery - 25, 3)
            explosion = Explosion(self.rect.centerx, self.rect.centery + 25, 3)
            explosion_group.add(explosion)
        elif pygame.sprite.spritecollide(self, Boss_Charge_Shot_group, False):
            self.kill
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            # explosion = Explosion(self.rect.centerx + 25, self.rect.centery,3)
            # explosion = Explosion(self.rect.centerx - 25, self.rect.centery, 3)
            # explosion = Explosion(self.rect.centerx, self.rect.centery - 25, 3)
            # explosion = Explosion(self.rect.centerx, self.rect.centery + 25, 3)
            explosion_group.add(explosion)

class Boss_Charge_Shot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("alien_bullet.png")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.image = pygame.transform.rotate(self.image, 180)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 10
        if self.rect.bottom > 900:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

        # elif pygame.sprite.spritecollide(self, shield_group, True):
        # self.kill()
        # explosion_fx.play()
        # explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
        # explosion_group.add(explosion)
        # boss.health_remaining += 1
        # shield.health_remaining -= 10
        elif pygame.sprite.spritecollide(self, boss_bullet_group, True):
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
        elif pygame.sprite.spritecollide(self, spaceship_group, True):
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining = 0
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
        elif pygame.sprite.spritecollide(self, Charge_Shot_group, True):
            self.kill()
            explosion2_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
        elif pygame.sprite.spritecollide(self, bullet_group, True):
            explosion2_fx.play()

class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 10
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            global time_last_hit
            time_last_hit = pygame.time.get_ticks()
            self.kill()
            explosion2_fx.play
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            if spaceship.health_remaining <= 0:
                explosion2 = Explosion(spaceship.rect.centerx, spaceship.rect.centery, 3)
                explosion_group.add(explosion2)

        if pygame.sprite.spritecollide(self, Charge_Shot_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

        # elif pygame.sprite.spritecollide(self, spaceship2_group, False, pygame.sprite.collide_mask):
        # self.kill()
        # explosion2_fx.play
        # spaceship2.health_remaining  -= 1
        # explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
        # explosion_group.add(explosion)

class Missiles(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = miss1
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.missile_counter = 0
        self.x = x
        self.y = y

    def update(self):
        self.move_counter += 1
        self.missile_counter += 2
        self.rect.y -= self.move_counter * (5 / 10)
        self.image = missileup[self.missile_counter // 15]

        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True, pygame.sprite.collide_mask):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
        elif pygame.sprite.spritecollide(self, boss_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            boss.health_remaining -= 10
        elif pygame.sprite.spritecollide(self, shield_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            shield_group.draw(win)
            shield.health_remaining -= 10
        elif pygame.sprite.spritecollide(self, boss_bullet_group, True, pygame.sprite.collide_mask):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

        # 5 shot missile
        if self.missile_counter > 90 and self.rect.y > (screen_height / 2):
            # global missilex
            # global missiley
            missilex = self.rect.x
            missiley = self.rect.y

            missile = Missiles(missilex, missiley + 10)
            missile_group.add(missile)
            # thisis not working here ###############################################

            missile = Missiles(missilex + 20, missiley + 10)
            missile_group.add(missile)

            missile = Missiles(missilex - 20, missiley + 10)
            missile_group.add(missile)
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

            # 5 missile in different directions

class Shield(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("shield.png")
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = [x, y]
        self.health = health
        self.health_remaining = health

    def update(self):
        # update mask
        self.mask = pygame.mask.from_surface(self.image)
        if self.health_remaining <= 0:
            self.kill()

class SmallShield(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        shield1 = pygame.image.load("shield.png")
        self.image = pygame.transform.scale(shield1, (55, 45))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = [x, y]
        self.health = health
        self.health_remaining = health

    def update(self):
        # update mask
        self.mask = pygame.mask.from_surface(self.image)
        if self.health_remaining <= 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (160, 160))
            # add image to the list
            self.images.append(img)

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        # update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

class Boss_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("alien_bullet.png"), (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        # speed of shot
        self.rect.y += 13
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False):
            time_last_hit
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
        if pygame.sprite.spritecollide(self, Charge_Shot_group, False):
            self.kill()
            explosion2_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
        # elif pygame.sprite.spritecollide(self, spaceship2_group, False, pygame.sprite.collide_mask):
        # self.kill()
        # explosion2_fx.play
        # spaceship2.health_remaining  -= 1
        # explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
        # explosion_group.add(explosion)

class Thrust(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = thrust1
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = [x, y]
        self.thrust_counter = 0

    def update(self):
        # update mask
        self.mask = pygame.mask.from_surface(self.image)
        if boss.rect.y != 100 and boss.rect.y != 400 and boss.rect.y != 1000:
            self.rect.x = boss.rect.centerx - 25
            self.rect.y = boss.rect.y - 60

# Spaceship class for continuous up-down movement with dynamic borders
class Intro_Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health, ship, upper_border, lower_border, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = ships[ship]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.counter = 0
        self.speed = speed  # Speed of movement for the ship
        self.direction = -1  # Start by moving upwards
        self.upper_border = upper_border  # Initial upper limit
        self.lower_border = lower_border  # Initial lower limit
        self.screen_height = 800  # Total screen height

    def update(self):
        # Move the ship in the current direction (up or down)
        self.rect.centery += self.speed * self.direction

        # Reverse direction if the ship hits the upper or lower border
        if self.rect.centery <= self.upper_border:
            self.direction = 1  # Start moving down
            self.set_new_borders()  # Change the borders after hitting the upper border
        elif self.rect.centery >= self.lower_border:
            self.direction = -1  # Start moving up
            self.set_new_borders()  # Change the borders after hitting the lower border

    def set_new_borders(self):
        # Set a new upper border between 0.25 * screen height and the current lower border
        self.upper_border = random.randint(0.25 * self.screen_height, self.lower_border - 50)

        # Set a new lower border between the current upper border and 0.75 * screen height
        self.lower_border = random.randint(self.upper_border + 50, 0.75 * self.screen_height)

class Intro_Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("boss.png"), (120, 120))
        self.image = pygame.transform.rotate(self.image, 180)
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.move_counter = 0
        self.charge_counter = 0
        self.pass_counter = 0
        self.move_direction = 1  # change back to 1
        self.move = True
        self.counter = 0

    def update(self):
        self.rect.centery += 3
        self.counter += .5

        if self.counter > 50 and self.counter < 127:
            self.rect.centery -= 5

        if self.counter > 127:
            self.counter = 0
            self.rect.centerx = random.choice([200, 300, 400, 500])

# update add new Thread
class myThread(threading.Thread):
    def run(self):
        global waves, is_reloaded
        # update1 add sleep Time
        time.sleep(3)
        waves = waves + 1
        create_aliens()
        boss.rect.y = (screen_height - 1200)
        is_reloaded = True


boss = Boss(int(screen_width / 2), screen_height - 1200, 12)
shield = Shield(boss.rect.center[0] - 85, boss.rect.center[1] - 40, 10)
thrust = Thrust(boss.rect.centerx - 25, boss.rect.y - 60)
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, start_health, 1)

# Sprite Groups...................................................................
spaceship_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
boss_bullet_group = pygame.sprite.Group()
Boss_Charge_Shot_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
shield_group = pygame.sprite.Group()
missile_group = pygame.sprite.Group()
Charge_Shot_group = pygame.sprite.Group()
thrust_group = pygame.sprite.Group()
intro_spaceship_group = pygame.sprite.Group()
intro_boss_group = pygame.sprite.Group()
# mini_shield_group = pygame.sprite.Group()

spaceship_group.add(spaceship)
thrust_group.add(thrust)
# adds the 3 intro ships to fly at different speeds
intro_spaceship = Intro_Spaceship(150, screen_height + height_list[0], 3, 2, upper_border=100, lower_border=400, speed=random.choice([2, 2.5, 3, 3.5]))
intro_spaceship2 = Intro_Spaceship(300, screen_height + height_list[1], 3, 1, upper_border=150, lower_border=450, speed=random.choice([2, 2.5, 3, 3.5]))
intro_spaceship3 = Intro_Spaceship(450, screen_height + height_list[2], 3, 3, upper_border=200, lower_border=500, speed=random.choice([2, 2.5, 3, 3.5]))

intro_boss = Intro_Boss(random.choice([200, 300, 400, 500, 600]), -300, 12)

top = spaceship.rect.top
center = spaceship.rect.centery

#radius = (int(str(center)) - int(str(top)))
#x_shot = radius * (math.tan(angle))
#if angle > 0:
    #angle2 = (180 - angle) / 2
#else:
    #angle2 = .001

#xtra = (x_shot) / math.tan(angle2)
#y_shot = radius - (xtra)
#running = spaceship.rect.centerx - (spaceship.rect.centerx - (x_shot))
#rise = spaceship.rect.top - (spaceship.rect.top + (y_shot) / 2)

# to keep track of the space invaders within the wave

field = [[0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0]]

show_start_screen()

create_aliens()

# Game Loop
game_over = False
run = True
while run:


    if game_over == True:
        # time.sleep(3)
        show_go_screen()
        game_over = False
        waves = 0
        spaceship = Spaceship(int(screen_width / 2), screen_height - 100, start_health, 1)
        # spaceship = Spaceship(int(screen_width / 2), screen_height - 100, start_health, 1)
        spaceship_group = pygame.sprite.Group()
        bullet_group = pygame.sprite.Group()
        explosion_group = pygame.sprite.Group()
        alien_group = pygame.sprite.Group()
        boss_group = pygame.sprite.Group()
        shield_group = pygame.sprite.Group()
        boss_bullet_group = pygame.sprite.Group()
        missile_group = pygame.sprite.Group()
        Charge_Shot_group = pygame.sprite.Group()

        spaceship_group.add(spaceship)
        spaceship.health_remaining = spaceship.health_start
        move_counter = 0

    clock.tick(fps)
    key = pygame.key.get_pressed()

    # record current time
    time_now = pygame.time.get_ticks()


    #draw_text2("SPACE IMITATORS!!!", int(text_size), green, screen_width / 2, screen_height / 4)



    # waves of aliens restoring
    if waves != 4 and waves != 8 and waves != 12 and game_over != True:
        screen_blink()
        restore_aliens()

    # boss coming in
    if waves == 4:
        boss_group.add(boss)
        shield_group.add(shield)

    # shoot
    # took this out >>>>> and len(alien_bullet_group) < 5
    if time_now - last_alien_shot > alien_cooldown and len(alien_group) > 0:
        attacking_alien = random.choice(alien_group.sprites())
        alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom + 10)
        alien_bullet_group.add(alien_bullet)
        last_alien_shot = time_now

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # moving the screen(the stars)
    draw_bg()
    moving_screen()
    screen_blink()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_z]:
        spaceship.rotate(2)
        angle -= 2
        ship_angle = ship_angle + 2

    if keys[pygame.K_x]:
        spaceship.rotate(-2)
        angle += 2
        ship_angle = ship_angle - 2

    # if key[pygame.K_q]:
    # waves = 4
    # if key[pygame.K_r]:
    # waves = 7
    if key[pygame.K_a] and time_now - spaceship.last_shot > cooldown * 5:
        missile_assist()
    if key[pygame.K_p] and paused == False:
        pause()

    # Keeping track of counts
    # draw_text2('last hit : ' + str(time_last_hit), 24, green, screen_width / 1.2, screen_height / 1.9)
    # draw_text2('time now : ' + str(time_now), 24, green, screen_width / 1.2, screen_height / 1.7)
    # draw_text2('game over : ' + str(game_over), 24, green, screen_width / 1.2, screen_height / 1.5)
    # draw_text2('invaders  : ' + str(len(alien_group)), 24, green, screen_width / 1.2, screen_height / 1.2)
    # draw_text2('# of aliens : ' + str(field), 16, green, screen_width / 2, screen_height / 1.3)
    draw_text2('# move counter : ' + str(move_counter), 16, green, screen_width / 1.2, screen_height / 1.1)
    draw_text2(' Waves : ' + str(waves), 24, green, screen_width / 1.2, screen_height / 1.5)
    draw_text2(' charge counter : ' + str(boss.charge_counter), 24, green, screen_width / 1.3, screen_height / 1.7)
    #draw_text2(' angle2 : ' + str(angle2), 24, green, screen_width / 1.3, screen_height / 1.8)
    draw_text2(' spawn_x : ' + str(spawn_x), 24, green, screen_width / 1.6, screen_height / 1.4)
    draw_text2(' spawn_y : ' + str(spawn_y), 24, green, screen_width / 2.5, screen_height / 1.6)
    draw_text2(' ship_angle : ' + str(ship_angle), 24, green, screen_width / 1.3, screen_height / 1.9)
    draw_text2(' angle : ' + str(angle), 24, green, screen_width / 1.6, screen_height / 1.5)
    # randomized the speed, height, and counter for intro
    speed = random.choice([7, 6, 8])
    border = random.choice([575, 585, 595])

    # update..............................
    spaceship.update()
    alien_group.update()
    bullet_group.update()
    shield_group.update()
    if waves == 4 or waves == 8 or waves == 12:
        boss_group.update()
    thrust_group.update()
    Boss_Charge_Shot_group.update()
    alien_bullet_group.update()
    Charge_Shot_group.update()
    boss_bullet_group.update()
    explosion_group.update()
    missile_group.update()

    # Draw.....................................
    # win.blit(thrust1, (350, 250))
    missile_group.draw(win)
    spaceship_group.draw(win)
    if waves == 4 or waves == 8 or waves == 12:
        boss_group.draw(win)
    Charge_Shot_group.draw(win)
    Boss_Charge_Shot_group.draw(win)
    alien_group.draw(win)
    bullet_group.draw(win)
    alien_bullet_group.draw(win)
    boss_bullet_group.draw(win)
    explosion_group.draw(win)
    if waves == 4:
        win.blit(upgrade_missile, ((int(screen_width / 2), (screen_height / 2))))
    pygame.display.flip()
    pygame.display.update()

pygame.quit()
