import pygame
from pygame import mixer
import math
#from pygame.locals import *
import random
#import time
#from os import path
#import json

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

time_now = 0
func_start = 0

alien_cooldown = 1000  # ms
last_alien_shot = pygame.time.get_ticks()

clock = pygame.time.Clock()
fps = 60

# Fire the Missiles
# missile = pygame.image.load("missile1.png")
# miss1 = missile.copy()
# miss1 = pygame.transform.rotate(miss1, 90)
# miss1 = pygame.transform.scale(miss1, )

# colors
black = (0, 0, 0)
red = (255, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
screen_width = 600
screen_height = 800

win = pygame.display.set_mode((600, 800))

# SpriteSheet
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
sprite_sheet = SpriteSheet(sprite_sheet_image)

def draw_bg():
    win.blit(bg, (0, 0))

pygame.display.set_caption("Space Imitators")

# define fonts
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

sprite_sheet_image2 = pygame.image.load('thruster.png').convert_alpha()
sprite_sheet2 = SpriteSheet(sprite_sheet_image2)

speed_list2 = [6, 7, 8]
height_list = [0, 100, 200]
speed = random.choice(speed_list2)
border = random.choice([575, 585, 595])

def draw_bg():
    win.blit(bg, (0, 0))

background_size = bg.get_size()
background_rect = bg.get_rect()
# win = pygame.display.set_mode(background_size)
w, h = background_size
x = 0
y = 0

x1 = 0
y1 = -h

# screen moves top down
def moving_screen():
    global y1
    global y
    y1 += 3  # both control the speed of the screen moving
    y += 3  # both control the speed of the screen moving
    win.blit(bg, (x, y))
    win.blit(bg, (x1, y1))
    if y > h:
        y = -h
    if y1 > h:
        y1 = -h

#moves screen faster for next level
def moving_screen2():
    global y1
    global y
    y1 += 18  # both control the speed of the screen moving
    y += 18  # both control the speed of the screen moving
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

# OBJECTS HERE
class Intro_Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()

        self.image = pygame.image.load(
            "spaceship.png"
        ).convert_alpha()

        self.rect = self.image.get_rect(center=(x, y))

        # Floating-point coordinates create smoother movement
        self.x = float(x)
        self.y = float(y)

        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

        # Each ship follows a slightly different position behind the boss
        self.chase_offset_x = random.randint(-140, 140)
        self.chase_offset_y = random.randint(90, 170)

        # Gentle independent weaving
        self.weave_time = random.uniform(0, math.tau)
        self.weave_speed = random.uniform(0.025, 0.045)
        self.weave_amount_x = random.randint(10, 25)
        self.weave_amount_y = random.randint(5, 14)

        # Slightly different speed for every ship
        self.base_speed = random.uniform(2.0, 2.8)
        self.current_speed = self.base_speed

        # Prevent abrupt changes in direction
        self.velocity_x = 0.0
        self.velocity_y = -self.base_speed

        # Different response speed for each pilot
        self.steering_strength = random.uniform(0.035, 0.06)

    def update(self):
        print("Intro_Spaceship update running")
        self.rect.x += 100

        self.weave_time += self.weave_speed

        # Point behind the boss that this ship tries to occupy
        target_x = intro_boss.rect.centerx + self.chase_offset_x
        target_y = intro_boss.rect.centery + self.chase_offset_y

        # Stronger side-to-side pursuit movement
        target_x += math.sin(self.weave_time) * self.weave_amount_x

        # Smaller forward-and-back corrections
        target_y += math.sin(
            self.weave_time * 0.65
        ) * self.weave_amount_y

        difference_x = target_x - self.x
        difference_y = target_y - self.y

        distance = math.hypot(
            difference_x,
            difference_y
        )

        if distance > 200:
            desired_speed = self.base_speed * 1.8
        elif distance > 100:
            desired_speed = self.base_speed * 1.3
        else:
            desired_speed = self.base_speed * 0.8

        if distance > 0:
            desired_velocity_x = (
                                         difference_x / distance
                                 ) * desired_speed

            desired_velocity_y = (
                                         difference_y / distance
                                 ) * desired_speed

            self.velocity_x += (
                                       desired_velocity_x - self.velocity_x
                               ) * 0.08

            self.velocity_y += (
                                       desired_velocity_y - self.velocity_y
                               ) * 0.08

        # Add an independent banking drift.
        # This prevents the ship from merely following a straight target line.
        self.velocity_x += (
                math.sin(self.weave_time * 1.4)
                * 0.12
        )

        self.x += self.velocity_x
        self.y += self.velocity_y

        self.rect.center = (
            round(self.x),
            round(self.y)
        )

        if (
                self.rect.right < -200
                or self.rect.left > screen_width + 200
                or self.rect.bottom < -250
                or self.rect.top > screen_height + 250
        ):
            self.kill()

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

random.shuffle(height_list)
#adds the 3 intro ships to fly at different speeds
intro_spaceship = Intro_Spaceship(150, screen_height + height_list[0], 0)
intro_spaceship2 = Intro_Spaceship(300, screen_height + height_list[1], 1)
intro_spaceship3 = Intro_Spaceship(450, screen_height + height_list[2], 2)

intro_boss = Intro_Boss(random.choice([200, 300, 400, 500, 600]), -300, 12)

intro_spaceship_group = pygame.sprite.Group()
intro_boss_group = pygame.sprite.Group()

intro_spaceship_group.add(intro_spaceship,intro_spaceship2,intro_spaceship3)
intro_boss_group.add(intro_boss)

def show_start_screen():
    #update2 Move the display background logic to the wait for key
    wait_for_key()

# loop For Start Screen
def wait_for_key():
    waiting = True

    while waiting:
        dt = clock.tick(fps) / 1000

        for star in stars:
            star.update(dt)

        win.fill((4, 6, 16))

        for star in stars:
            star.draw(win)


        intro_spaceship_group.add(intro_spaceship, intro_spaceship2, intro_spaceship3)
        intro_boss_group.add(intro_boss)
        draw_text2("SPACE IMITATORS!!!", 48, green, screen_width / 2, screen_height / 4)
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.QUIT

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

# Game Over function
def show_go_screen():
    draw_bg()
    draw_text2("GAME OVER!!!", 68, red, screen_width / 2, screen_height / 4)
    draw_text2("Are U Afraid of the DARK?", 22, red, screen_width / 2, screen_height / 2)
    draw_text2("Press Any Key to Play Again", 22, red, screen_width / 2, screen_height * 3 / 4)
    pygame.display.update()
    wait_for_key()

import threading
# update1 add reload Flag
is_reloaded = True

show_start_screen()

# Game Loop
game_over = False
run = True
while run:
    if game_over:
        show_go_screen()
        game_over = False
        spaceship = Spaceship(int(screen_width / 2), screen_height - 100, 3)
        boss = Boss(int(screen_width / 2), screen_height - 1200, 12)
        shield = Shield(boss.rect.center[0] - 85, boss.rect.center[1] - 40, 20)

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
        shield_group.add(shield)
        spaceship.health_remaining = spaceship.health_start

    clock.tick(fps)

    key = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # moving the screen(the stars)
    draw_bg()
    moving_screen()


    # record current time
    time_now = pygame.time.get_ticks()

    y1 += 3  # both control the speed of the screen movin
    y += 3  # both control the speed of the screen moving
    win.blit(bg, (x, y))
    win.blit(bg, (x1, y1))
    if y > h:
        y = -h
    if y1 > h:
        y1 = -h

    #randomized the speed, height, and counter for intro
    speed = random.choice([7, 6, 8])
    border = random.choice([575, 585, 595])


    draw_text2("SPACE IMITATORS!!!", 48, green, screen_width / 2, screen_height / 4)
    #draw_text2("<  or  > to move, Spacebar to fire", 22, green, screen_width / 2, screen_height / 3)
    if intro_spaceship2.rect.centery < 600:
        draw_text2("Press any key", 22, green, screen_width / 2, screen_height - 150)
    #draw_text2('counter : ' + str(intro_boss.counter), 24, green, screen_width / 1.2, screen_height / 1.9)
    #draw_text2('speed : ' + str(speed), 24, green, screen_width / 1.2, 750)


    # update
    intro_spaceship_group.update()
    intro_boss_group.update()

    # Draw
    intro_spaceship_group.draw(win)
    intro_boss_group.draw(win)
    pygame.display.update()

pygame.quit()
