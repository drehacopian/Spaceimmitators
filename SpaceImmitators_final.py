import pygame
from pygame import mixer
# from pygame.locals import *
import random
import sys
import time
import math

# import time
# from os import path
# import json

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()



from assets import (bg, ships, bullet_base, explosion_fx, explosion2_fx, laser_fx, small_boss_bullet, boss_image, big_bullet, small_bullet, red_ship_layers,
    red_ship_layer_order)
from sprites import (Spaceship, Aliens, Boss, Bullets, Missiles, Shield, SmallShield, Charge_Shot, Charge_Trail, Boss_Charge_Shot, Alien_Bullets, Boss_Bullets, BackgroundShip, BackgroundAlien, BackgroundExplosion, BackgroundAlienBullet, ShipDebris)
from effects import Explosion, RadiatingExplosion, Thrust, Star



#Screen Dimensions
screen_width = 600
screen_height = 800
win = pygame.display.set_mode((screen_width, screen_height))


# define game variables---------------------------------------------------------
rows = 5
columns = 5
number = 1
boss_final = False
paused = False
length = 1
length2 = -1
rate = 3
formation = None
post_boss_transition = False

# colors
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
screen_width = 600
screen_height = 800

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

# Temporary red ship layer viewer
layer_viewer_enabled = False
layer_viewer_index = 0

global field, spawn_x, spawn_y
cooldown = 100
wave_in_progress = False
pending_spawn = False
last_wave_clear_time = 0
blinking = False




spawn_x = 0
spawn_y = 0

# Screen shake globals
screen_shake_intensity = 0
screen_shake_duration = 0

# update1 add reload Flag

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

alien_attack_interval = 3000  # Milliseconds between attacks (3 seconds)
last_attack_time = pygame.time.get_ticks()

clock.tick(fps)
move_counter = 0
move_direction = 1
adjustment = 0
#ships = []

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

PLAYER_MISSILE_SIZE = (8, 22)

player_missile_image = pygame.transform.smoothscale(
    upgrade_missile,
    PLAYER_MISSILE_SIZE
)
sprite_sheet2 = SpriteSheet(sprite_sheet_image2)

# jet thrusters for boss-------------------------------------------------------------------------------------
thrust1 = sprite_sheet2.get_image(0, 0, 204, 287, black, 0, 51, 71)
thrust2 = sprite_sheet2.get_image(0, 287, 204, 287, black, 0, 51, 71)
thrust3 = sprite_sheet2.get_image(0, 574, 204, 287, black, 0, 51, 71)

pygame.display.set_caption("Space Imitators")

level_direction_toggle = True

# ================================
#  ASSET PRELOADING
# ================================

# Thrust
sprite_sheet_image2 = pygame.image.load("thruster.png").convert_alpha()
sprite_sheet2 = SpriteSheet(sprite_sheet_image2)

thrust1 = sprite_sheet2.get_image(0, 0, 204, 287, black, 0, 51, 71)
thrust2 = sprite_sheet2.get_image(0, 287, 204, 287, black, 0, 51, 71)
thrust3 = sprite_sheet2.get_image(0, 574, 204, 287, black, 0, 51, 71)


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

def draw_player_charge_effect():
    if not spaceship.charging or spaceship.charge_fired:
        return

    center_x = spaceship.rect.centerx
    ship_top = spaceship.rect.top
    phase = (spaceship.charge_counter // 5) % 4

    # Grow the charge ball as energy builds
    charge_size = 20 + spaceship.charge_counter

    if charge_size > 60:
        charge_size = 60

    charging_ball = pygame.transform.smoothscale(
        big_bullet,
        (charge_size, charge_size)
    )

    # Flash while charging
    if spaceship.charge_counter // 4 % 2 == 0:
        ball_x = center_x - charging_ball.get_width() // 2
        ball_y = ship_top - charging_ball.get_height() - 5

        win.blit(charging_ball, (ball_x, ball_y))

    # Moving smaller particles
    if phase == 0:
        offsets = [
            (-55, -10),
            (45, -25),
            (-35, -45)
        ]

    elif phase == 1:
        offsets = [
            (-45, -30),
            (35, -5),
            (50, -50)
        ]

    elif phase == 2:
        offsets = [
            (-50, -50),
            (40, -30),
            (-30, -5)
        ]

    else:
        offsets = [
            (-40, -15),
            (45, -45),
            (25, -5)
        ]

    for offset_x, offset_y in offsets:
        win.blit(
            small_bullet,
            (
                center_x + offset_x,
                ship_top + offset_y
            )
        )

def draw_player_missiles():
    if spaceship.missiles_remaining <= 0:
        return

    missile_mounts = spaceship.get_missile_mounts()

    for mount_index in range(
            spaceship.next_missile_mount,
            len(missile_mounts)
    ):

        if not spaceship.missile_mount_available(
                mount_index
        ):
            continue

        mount_x, mount_y = missile_mounts[mount_index]

        mounted_missile = player_missile_image

        missile_rect = mounted_missile.get_rect(
            center=(
                int(mount_x),
                int(mount_y)
            )
        )

        win.blit(
            mounted_missile,
            missile_rect
        )

def draw_intro_missiles(ship):
    ship_width = ship.image.get_width()
    ship_height = ship.image.get_height()

    center_x = ship_width / 2
    center_y = ship_height / 2

    local_mounts = [
        (
            center_x - ship_width * 0.11,
            center_y - ship_height * 0.02
        ),
        (
            center_x + ship_width * 0.11,
            center_y - ship_height * 0.02
        ),
        (
            center_x - ship_width * 0.18,
            center_y + ship_height * 0.02
        ),
        (
            center_x + ship_width * 0.18,
            center_y + ship_height * 0.02
        )
    ]

    for mount_index, mount in enumerate(local_mounts):

        if ship.ship_number == 0:

            if mount_index in (0, 2):
                pivot = pygame.math.Vector2(72, 47)
                wing_angle = ship.wing_sweep

            else:
                pivot = pygame.math.Vector2(82, 47)
                wing_angle = -ship.wing_sweep

            mount_vector = (
                pygame.math.Vector2(mount)
                - pivot
            )

            rotated_mount = (
                pivot
                + mount_vector.rotate(-wing_angle)
            )

            mount_x = (
                ship.rect.left
                + rotated_mount.x
            )

            mount_y = (
                ship.rect.top
                + rotated_mount.y
            )

        else:
            wing_angle = 0

            mount_x = (
                ship.rect.left
                + mount[0]
            )

            mount_y = (
                ship.rect.top
                + mount[1]
            )

        mounted_missile = player_missile_image

        missile_rect = mounted_missile.get_rect(
            center=(
                int(mount_x),
                int(mount_y)
            )
        )

        win.blit(
            mounted_missile,
            missile_rect
        )

def draw_escape_thruster():
    if not spaceship.escape_mode:
        return

    if spaceship.escape_finished:
        return

    frames = [
        thrust1,
        thrust2,
        thrust3
    ]

    frame_index = (
        pygame.time.get_ticks() // 80
    ) % len(frames)

    thruster_image = frames[frame_index]

    thruster_image = pygame.transform.rotate(
        thruster_image,
        180
    )

    # Determine travel direction
    velocity_x = spaceship.escape_velocity_x
    velocity_y = spaceship.escape_velocity_y

    angle = math.degrees(
        math.atan2(
            -velocity_y,
            velocity_x
        )
    )

    # Flame points opposite the direction of travel
    rotation = angle - 90

    thruster_image = pygame.transform.rotate(
        thruster_image,
        rotation
    )

    direction = pygame.math.Vector2(
        velocity_x,
        velocity_y
    )

    if direction.length() == 0:
        direction = pygame.math.Vector2(0, -1)

    direction = direction.normalize()

    # Put flame behind the escaping craft
    thruster_x = (
        spaceship.rect.centerx
        - direction.x * 38
    )

    thruster_y = (
        spaceship.rect.centery
        - direction.y * 38
    )

    thruster_rect = thruster_image.get_rect(
        center=(
            int(thruster_x),
            int(thruster_y)
        )
    )

    win.blit(
        thruster_image,
        thruster_rect
    )

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

def draw_bg(speed=2.0):
    # Just use the scrolling function
    moving_screen(speed)
# screen moves top down
def moving_screen(speed=3.0):
    global y1, y
    y1 += speed
    y += speed
    win.blit(bg, (x, round(y)))
    win.blit(bg, (x1, round(y1)))
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

def draw_layer_viewer():
    if not layer_viewer_enabled:
        return

    layer = red_ship_layers[layer_viewer_index]

    scale = 3

    enlarged_layer = pygame.transform.scale(
        layer,
        (
            layer.get_width() * scale,
            layer.get_height() * scale
        )
    )

    viewer_rect = enlarged_layer.get_rect(
        center=(
            screen_width // 2,
            screen_height // 2
        )
    )

    background_rect = viewer_rect.inflate(30, 70)

    pygame.draw.rect(
        win,
        (15, 15, 15),
        background_rect
    )

    win.blit(
        enlarged_layer,
        viewer_rect
    )

    draw_text2(
        f"Layer {layer_viewer_index} | Sprite {layer_viewer_index + 1}",
        24,
        white,
        screen_width // 2,
        background_rect.top + 5
    )

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

    title_text = "SPACEIMITATORS!!!"
    revealed_chars = 0
    last_reveal_time = pygame.time.get_ticks()
    reveal_delay = 300

    intro_spaceship_group.add(
    intro_spaceship,
    intro_spaceship2,
    intro_spaceship3
    )

    intro_boss_group.add(intro_boss)

    while waiting:
        dt = clock.tick(fps) / 1000

        current_time = pygame.time.get_ticks()

        if current_time - last_reveal_time >= reveal_delay:
            if revealed_chars < len(title_text):
                revealed_chars += 1
                last_reveal_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

        # Update the stars
        for star in stars:
            star.update(dt)

        # Erase the previous frame
        win.fill((4, 6, 16))

        # Draw the starfield
        for star in stars:
            star.draw(win)

        # Update intro ships
        intro_spaceship_group.update()
        intro_boss_group.update()

        # Animate and draw the title
        animated_size = animate_text()

        visible_title = title_text[:revealed_chars]

        draw_text2(
            visible_title,
            animated_size,
            green,
            screen_width / 2,
            screen_height / 4
        )

        if intro_spaceship2.rect.centery < 600:
            draw_text2(
                "Press any key",
                22,
                green,
                screen_width / 2,
                screen_height - 150
            )

        # Draw missiles beneath the main intro ship
        draw_intro_missiles(
            intro_spaceship
        )

        # Draw ships over the missiles
        intro_spaceship_group.draw(win)
        intro_boss_group.draw(win)

        pygame.display.update()

# Game Over function
def show_go_screen():
    waiting = True
    change = 1
    rate = 1

    while waiting:
        dt = clock.tick(fps) / 1000

        for star in stars:
            star.update(dt)

        win.fill((4, 6, 16))

        for star in stars:
            star.draw(win)

        draw_text2(
            "GAME OVER!!!",
            68 + change,
            red,
            screen_width / 2,
            screen_height / 4
        )
        change += rate
        if change >= 45:
            rate *= -1
        # elif change <= -15:
        # rate *= -1
        # draw_text2("change: " + str(change), 22, red, screen_width / 1 * 3/4, screen_height / 1 * 2/3)
        draw_text2(saying, 22, red, screen_width / 2, screen_height / 2)
        draw_text2("Press Any Key to Play Again", 22, red, screen_width / 2, screen_height * 3 / 4)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def create_aliens():
    global level_direction_toggle, formation, move_counter

    move_counter = 0
    move_direction = 1

    if waves not in (4, 8, 12):  # skip boss waves
        for row in range(rows):
            for item in range(columns):
                alien = Aliens(
                    formation,              # ✅ pass shared formation
                    item, row,              # col, row
                    100 + item * 100,       # base x
                    100 + row * 70,         # base y
                    move_counter,
                    move_direction,
                    level_direction_toggle
                )
                alien_group.add(alien)
                field[row][item] = 1

    # flip direction for next wave
    level_direction_toggle = not level_direction_toggle

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
    global move_counter, waves, level_direction_toggle, formation
    global pending_spawn, last_wave_clear_time

    # ✅ skip entirely if this is a boss or post-boss wave
    if waves in (4, 8, 12):
        return

    if pending_spawn and len(alien_group) == 0:
        if time_now - last_wave_clear_time >= 3000:
            move_counter = 0
            pending_spawn = False
            # ❌ don’t increment waves here
            for row in range(rows):
                for item in range(columns):
                    alien = Aliens(formation, item, row, 100 + item * 100, 100 + row * 70, move_counter, 1, level_direction_toggle)
                    alien_group.add(alien)
                    field[row][item] = 1


            level_direction_toggle = not level_direction_toggle

# team assist from tiger ship
def missile_assist():
    missile = Missiles(350, 1000)
    missile_group.add(missile)
    spaceship.last_shot = time_now

def screen_blink():
    global rate, length, post_boss_transition, pending_spawn, last_wave_clear_time

    # scale by real frame time
    dt = clock.get_time() / 16.0   # normalize ~60fps
    length += rate * dt

    # draw bars (AFTER everything else)
    pygame.draw.rect(win, black, (0, 0, screen_width, int(length)))
    pygame.draw.rect(win, black, (0, screen_height - int(length), screen_width, int(length)))

    if length >= (screen_height / 2):
        rate = -abs(rate)
    elif length <= 0:
        length = 0
        rate = abs(rate)
        post_boss_transition = False
        pending_spawn = True
        last_wave_clear_time = pygame.time.get_ticks()

def boss_charge_effect(x1, x2, y1, y2, y3):
    win.blit(small_boss_bullet, (boss.rect.centerx + x1, boss.rect.centery + y1))
    win.blit(small_boss_bullet, (boss.rect.centerx + x1, boss.rect.centery + y2))
    win.blit(small_boss_bullet, (boss.rect.centerx + x1, boss.rect.centery + y3))

    win.blit(small_boss_bullet, (boss.rect.centerx + x2, boss.rect.centery + y1))
    win.blit(small_boss_bullet, (boss.rect.centerx + x2, boss.rect.centery + y2))
    win.blit(small_boss_bullet, (boss.rect.centerx + x2, boss.rect.centery + y3))

def manage_alien_attacks():
    global last_attack_time

    # Check if it's time for an alien to attack
    current_time = pygame.time.get_ticks()
    if current_time - last_attack_time > alien_attack_interval:
        last_attack_time = current_time

        candidates = list(alien_group)
        if candidates:  # only pick if not empty
            attacking_alien = random.choice(candidates)
            attacking_alien.start_attack(spaceship.rect.centerx)

def start_screen_shake(intensity=5, duration=15):
    global screen_shake_intensity, screen_shake_duration
    screen_shake_intensity = intensity
    screen_shake_duration = duration

def apply_screen_shake(surface):
    global screen_shake_intensity, screen_shake_duration
    if screen_shake_duration > 0:
        screen_shake_duration -= 1
        offset_x = random.randint(-screen_shake_intensity, screen_shake_intensity)
        offset_y = random.randint(-screen_shake_intensity, screen_shake_intensity)
        win.blit(surface, (offset_x, offset_y))
    else:
        win.blit(surface, (0, 0))

def handle_events():
    global run, paused, angle, ship_angle
    global layer_viewer_enabled, layer_viewer_index

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.KEYDOWN:

            # Pause
            if event.key == pygame.K_p:
                paused = not paused

            # Turn layer viewer on/off
            if event.key == pygame.K_v:
                layer_viewer_enabled = not layer_viewer_enabled

            # Change displayed layer
            if layer_viewer_enabled:

                # Previous layer
                if event.key == pygame.K_COMMA:
                    layer_viewer_index -= 1

                    if layer_viewer_index < 0:
                        layer_viewer_index = 9

                # Next layer
                if event.key == pygame.K_PERIOD:
                    layer_viewer_index += 1

                    if layer_viewer_index > 9:
                        layer_viewer_index = 0

    # Continuous key holds
    keys = pygame.key.get_pressed()

    # --- Test red ship wing sweep ---
    if keys[pygame.K_LEFTBRACKET]:
        spaceship.wing_sweep -= 1

    if keys[pygame.K_RIGHTBRACKET]:
        spaceship.wing_sweep += 1

    # --- Test breaking off left sweep wing ---
    if keys[pygame.K_1]:
        spaceship.detach_part(
            "sweep_left_wing",
            ship_debris_group
        )

    # --- Test breaking off right sweep wing ---
    if keys[pygame.K_2]:
        spaceship.detach_part(
            "sweep_right_wing",
            ship_debris_group
        )

    spaceship.wing_sweep = max(
        -30,
        min(30, spaceship.wing_sweep)
    )


    # --- Hold C to charge ---
    if (
            keys[pygame.K_c]
            and spaceship.has_part("nose")
    ):


        print("Charging...")

        # First frame of charging
        if not spaceship.charging:
            spaceship.charging = True
            spaceship.charge_counter = 0
            spaceship.charge_fired = False
            spaceship.charge_start_y = spaceship.rect.y
            spaceship.charge_start_x = spaceship.rect.x

        spaceship.charge_counter += 1

        # Rock side to side while the energy becomes unstable
        if not spaceship.charge_fired:
            rock_amount = min(
                1 + spaceship.charge_counter // 10,
                5
            )

            rock_direction = -1 if (spaceship.charge_counter // 3) % 2 == 0 else 1

            spaceship.rect.x = (
                    spaceship.charge_start_x
                    + rock_direction * rock_amount
            )

        # Fire exactly once after 40 frames
        if (
                spaceship.charge_counter >= 40
                and not spaceship.charge_fired
        ):
            charge_shot = Charge_Shot(
                spaceship.rect.centerx,
                spaceship.rect.top
            )

            Charge_Shot_group.add(charge_shot)
            start_screen_shake(intensity=6, duration=8)

            # Smaller energy pieces generated from the firing point
            trail_settings = [
                # size, delay in milliseconds
                (42, 70),
                (33, 140),
                (25, 210),
                (18, 280),
                (11, 350)
            ]

            for size, delay in trail_settings:
                trail_piece = Charge_Trail(
                    spaceship.rect.centerx,
                    spaceship.rect.top,
                    size,
                    delay,
                    charge_shot
                )

                charge_trail_group.add(trail_piece)

            spaceship.charge_fired = True
            spaceship.last_charge_shot = time_now

            # Recoil: push the ship downward
            spaceship.rect.y = min(
                spaceship.charge_start_y + 40,
                screen_height - spaceship.rect.height
            )

    else:
        # C was released
        if spaceship.charging:
            spaceship.rect.x = spaceship.charge_start_x
            spaceship.rect.y = spaceship.charge_start_y

        spaceship.charging = False
        spaceship.charge_counter = 0
        spaceship.charge_fired = False

    # --- Rotation --- took out -------------------------------
    #if keys[pygame.K_z]:
        #spaceship.rotate(2)
        #angle -= 2
        #ship_angle += 2

    #if keys[pygame.K_x]:
        #spaceship.rotate(-2)
        #angle += 2
        #ship_angle -= 2

    # --- Movement is disabled while charging or escaping ---
    if (
            not spaceship.charging
            and not spaceship.escape_mode
    ):

        if keys[pygame.K_LEFT] and spaceship.rect.left > 0:
            spaceship.rect.x -= 5 * spaceship.get_turn_strength("left")

        if keys[pygame.K_RIGHT] and spaceship.rect.right < screen_width:
            spaceship.rect.x += 5 * spaceship.get_turn_strength("right")

        if keys[pygame.K_UP] and spaceship.rect.top > 0:
            spaceship.rect.y -= 5

        if keys[pygame.K_DOWN] and spaceship.rect.bottom < screen_height:
            spaceship.rect.y += 5

    # --- Fire bullet ---
    if (
            keys[pygame.K_SPACE]
            and spaceship.has_part("nose")
            and not spaceship.charging
            and time_now - spaceship.last_shot > cooldown
    ):
        bullet = Bullets(spaceship.rect.centerx, spaceship.rect.top, angle)
        bullets_group.add(bullet)
        spaceship.last_shot = time_now
        laser_fx.play()

    # --- Missile assist ---
    # --- Straight missile shot ---
    if (
            keys[pygame.K_a]
            and not spaceship.charging
            and spaceship.missiles_remaining > 0
            and time_now - spaceship.last_missile_shot > 750
    ):
        missile_mounts = spaceship.get_missile_mounts()

        mount_index = spaceship.next_missile_mount

        # Skip missile mounts that were lost with a wing
        while (
                mount_index < len(missile_mounts)
                and not spaceship.missile_mount_available(
            mount_index
        )
        ):
            mount_index += 1

        # Fire only if a physical missile mount still exists
        if mount_index < len(missile_mounts):
            mount_x, mount_y = missile_mounts[mount_index]

            missile = Missiles(
                int(mount_x),
                int(mount_y),
                player_missile_image
            )

            missile_group.add(missile)

            spaceship.missiles_remaining -= 1
            spaceship.next_missile_mount = mount_index + 1
            spaceship.last_missile_shot = time_now

    # --- Charge shot ---

    if keys[pygame.K_t] and len(alien_group) > 0:
        test_alien = alien_group.sprites()[0]
        test_alien.celebrate()

# define fonts........................................................
font30 = pygame.font.SysFont
FONT_NAME = 'arial'


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
class Formation:
    def __init__(self, speed=1, max_offset=75):
        self.offset_x = 0
        self.direction = 1
        self.speed = speed
        self.max_offset = max_offset

    def update(self):
        self.offset_x += self.direction * self.speed
        if abs(self.offset_x) > self.max_offset:
            self.direction *= -1

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


# Spaceship class for continuous up-down movement with dynamic borders
class Intro_Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health, ship, upper_border, lower_border, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = ships[ship]
        self.ship_number = ship

        if self.ship_number == 0:
            self.ship_layers = [
                layer.copy()
                for layer in red_ship_layers
            ]

            self.ship_layer_order = red_ship_layer_order.copy()

            self.wing_sweep = 0
            self.wing_offset_y = -4


        else:
            self.ship_layers = None
            self.ship_layer_order = None
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

    def draw_rotated_part(
            self,
            surface,
            layer_image,
            pivot,
            angle,
            offset_y=0
    ):
        rotated_image = pygame.transform.rotate(
            layer_image,
            angle
        )

        original_center = pygame.math.Vector2(
            layer_image.get_rect().center
        )

        pivot_vector = (
            pygame.math.Vector2(pivot)
            - original_center
        )

        rotated_pivot_vector = pivot_vector.rotate(
            -angle
        )

        rotated_center = (
            pygame.math.Vector2(pivot)
            - rotated_pivot_vector
        )

        rotated_rect = rotated_image.get_rect(
            center=(
                round(rotated_center.x),
                round(rotated_center.y)
            )
        )

        rotated_rect.y += offset_y

        surface.blit(
            rotated_image,
            rotated_rect
        )

    def rebuild_layered_ship(self):
        if self.ship_number != 0:
            return

        layered_image = pygame.Surface(
            ships[0].get_size(),
            pygame.SRCALPHA
        )

        for layer_index in self.ship_layer_order:

            if layer_index == 4:
                self.draw_rotated_part(
                    layered_image,
                    self.ship_layers[layer_index],
                    (72, 47),
                    self.wing_sweep,
                    self.wing_offset_y
                )

            elif layer_index == 5:
                self.draw_rotated_part(
                    layered_image,
                    self.ship_layers[layer_index],
                    (82, 47),
                    -self.wing_sweep,
                    self.wing_offset_y
                )

            else:
                layered_image.blit(
                    self.ship_layers[layer_index],
                    (0, 0)
                )

        old_center = self.rect.center

        self.image = layered_image

        self.rect = self.image.get_rect(
            center=old_center
        )

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

        if self.ship_number == 0:

            # Moving upward / accelerating forward
            if self.direction == -1:
                if self.wing_sweep < 18:
                    self.wing_sweep += 1.0

            # Moving downward / backing off
            elif self.direction == 1:
                if self.wing_sweep > 0:
                    self.wing_sweep -= 1.0

            self.rebuild_layered_ship()

    def set_new_borders(self):
        # Set a new upper border between 0.25 * screen height and the current lower border
        self.upper_border = random.randint(
            int(0.25 * self.screen_height),
            int(self.lower_border - 50)
        )

        self.lower_border = random.randint(
            int(self.upper_border + 50),
            int(0.75 * self.screen_height)
        )

class Intro_Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.rotate(boss_image, 180)
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

boss = Boss(int(screen_width / 2), screen_height - 1200, 12)

thrust = Thrust(boss.rect.centerx, boss.rect.top, boss, [thrust1, thrust2, thrust3])
spaceship = Spaceship(int(screen_width / 2), screen_height - 100, start_health, 0)
import sprites
sprites.spaceship = spaceship
formation = Formation(speed=1, max_offset=75)

# Sprite Groups...................................................................
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
spaceship_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
boss_bullet_group = pygame.sprite.Group()
Boss_Charge_Shot_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
shield_group = pygame.sprite.Group()
missile_group = pygame.sprite.Group()
Charge_Shot_group = pygame.sprite.Group()
ship_debris_group = pygame.sprite.Group()
charge_trail_group = pygame.sprite.Group()
thrust_group = pygame.sprite.Group()
intro_spaceship_group = pygame.sprite.Group()
intro_boss_group = pygame.sprite.Group()
background_ship_group = pygame.sprite.Group()
background_alien_group = pygame.sprite.Group()
background_bullet_group = pygame.sprite.Group()
background_beam_effect_group = pygame.sprite.Group()
background_explosion_group = pygame.sprite.Group()
background_alien_bullet_group = pygame.sprite.Group()
background_smoke_group = pygame.sprite.Group()

stars = [
    Star(screen_width, screen_height)
    for _ in range(150)
]
# mini_shield_group = pygame.sprite.Group()

import sprites

sprites.spaceship_group = spaceship_group
sprites.alien_group = alien_group
sprites.boss_group = boss_group
sprites.shield_group = shield_group
sprites.explosion_group = explosion_group
sprites.ship_debris_group = ship_debris_group
sprites.bullets_group = bullets_group
sprites.alien_bullet_group = alien_bullet_group
sprites.boss_bullet_group = boss_bullet_group
sprites.missile_group = missile_group
sprites.Charge_Shot_group = Charge_Shot_group
sprites.Boss_Charge_Shot_group = Boss_Charge_Shot_group


spaceship_group.add(spaceship)

background_spawn_delay = random.randint(1800, 4000)
last_background_spawn = pygame.time.get_ticks() - background_spawn_delay
last_background_lane = None

thrust_group.add(thrust)
shield = Shield(boss.rect.center[0] - 85, boss.rect.center[1] - 40, 10)
# adds the 3 intro ships to fly at different speeds
# Adds the 3 intro ships at different positions and speeds
intro_spaceship = Intro_Spaceship(
    150,
    screen_height + height_list[0],
    3,
    0,
    200,
    600,
    4
)

intro_spaceship2 = Intro_Spaceship(
    300,
    screen_height + height_list[1],
    3,
    1,
    200,
    600,
    5
)

intro_spaceship3 = Intro_Spaceship(
    450,
    screen_height + height_list[2],
    3,
    2,
    200,
    600,
    6
)

intro_boss = Intro_Boss(random.choice([200, 300, 400, 500, 600]), -300, 12)

top = spaceship.rect.top
center = spaceship.rect.centery

sprites.boss = boss
sprites.shield = shield

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

    if game_over:
        show_go_screen()
        game_over = False
        waves = 1

        # Reset player
        spaceship = Spaceship(int(screen_width / 2), screen_height - 100, start_health, 1)
        sprites.spaceship = spaceship
        spaceship_group.empty()
        spaceship_group.add(spaceship)
        spaceship.health_remaining = spaceship.health_start
        spaceship.missiles_remaining = 4
        spaceship.next_missile_mount = 0

        # Reset sprite groups (just clear them)
        bullets_group.empty()
        explosion_group.empty()
        alien_group.empty()
        boss_group.empty()
        shield_group.empty()
        boss_bullet_group.empty()
        missile_group.empty()
        Charge_Shot_group.empty()

        # Reset formation
        formation = Formation(speed=1, max_offset=75)

        # Reset counters
        move_counter = 0

    dt = clock.tick(fps) / 1000
    key = pygame.key.get_pressed()
    for star in stars:
        star.update(dt)

    # record current time
    time_now = pygame.time.get_ticks()

    #manage_alien_attacks()

    if len(alien_group) == 0 and not pending_spawn and waves not in (4, 8, 12) and not post_boss_transition:
        if (waves + 1) in (4, 8, 12):
            # Next wave will be a boss
            waves += 1
        else:
            # Normal alien wave progression
            waves += 1
            last_wave_clear_time = time_now
            pending_spawn = True

        overhead_spawned_this_wave = False
        overhead_spawn_time = time_now + random.randint(4000, 9000)


    # waves of aliens restoring
    if waves not in (4, 8, 12) and not game_over:
        restore_aliens()

    # Boss waves
    if waves in (4, 8, 12) and not game_over:
        boss_group.add(boss)
        shield_group.add(shield)

    if post_boss_transition and not game_over:
        screen_blink()



    # shoot
    # took this out >>>>> and len(alien_bullet_group) < 5
    if time_now - last_alien_shot > alien_cooldown and len(alien_group) > 0:
        attacking_alien = random.choice(alien_group.sprites())
        alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom + 10)
        alien_bullet_group.add(alien_bullet)
        last_alien_shot = time_now

    handle_events()
    if paused:
        continue  # skip rest of loop until unpaused

    #draw_bg()
    win.fill((4, 6, 16))

    for star in stars:
        star.draw(win)

    draw_player_charge_effect()

    # Keeping track of counts tools
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
    if spaceship.escape_finished:
        game_over = True
    formation.update()
    current_time = pygame.time.get_ticks()

    if current_time - last_background_spawn >= background_spawn_delay:
        background_lanes = [
            75,
            165,
            255,
            345,
            435,
            525
        ]
        available_lanes = [lane for lane in background_lanes if lane != last_background_lane]
        lane_x = random.choice(available_lanes)
        last_background_lane = lane_x

        battle_size = random.choice([1.0, 0.85, 0.7])
        alien_scale = 0.75 * battle_size
        ship_scale = 0.5 * battle_size

        background_alien = BackgroundAlien(lane_x, screen_height + 40, alien_scale)
        background_alien_group.add(background_alien)

        ship_image = random.choices(
            [ships[0], ships[1], ships[2]],
            weights=[80, 10, 10],
            k=1
        )[0]

        background_ship = BackgroundShip(
            ship_image,
            lane_x,
            screen_height + 450,
            ship_scale
        )
        background_ship_group.add(background_ship)

        last_background_spawn = current_time
        background_spawn_delay = random.randint(1800, 4000)
    background_ship_group.update(
        background_bullet_group,
        background_alien_group,
        background_beam_effect_group,
        background_alien_bullet_group,
        background_smoke_group,
        background_explosion_group
    )
    for beam in background_beam_effect_group:
        if beam.phase != "beam" or beam.fade_after_hit:
            continue

        hit_aliens = pygame.sprite.spritecollide(beam, background_alien_group, False)

        if hit_aliens:
            alien = hit_aliens[0]
            explosion = BackgroundExplosion(alien.rect.centerx, alien.rect.centery)
            background_explosion_group.add(explosion)

            alien.kill()
            beam.fade_after_hit = True
            beam.hit_time = pygame.time.get_ticks()

    background_beam_effect_group.update()
    background_bullet_group.update()
    background_alien_group.update(
        background_ship_group,
        background_alien_bullet_group
    )
    background_alien_bullet_group.update()





    background_explosion_group.update()
    background_hits = pygame.sprite.groupcollide(background_alien_group, background_bullet_group, False, True)

    for alien, bullets in background_hits.items():
        alien.health -= len(bullets)

        if alien.health <= 0:
            explosion = BackgroundExplosion(alien.rect.centerx, alien.rect.centery)
            background_explosion_group.add(explosion)
            alien.kill()
    alien_group.update()
    bullets_group.update((
        alien_bullet_group, boss_group, shield_group, alien_group,
        boss_bullet_group, Boss_Charge_Shot_group, explosion_group,
        boss, shield
    ))

    shield_group.update()
    if waves == 4 or waves == 8 or waves == 12:
        boss_group.update()
    thrust_group.update()
    Boss_Charge_Shot_group.update()
    alien_bullet_group.update()
    Charge_Shot_group.update()
    charge_trail_group.update()
    boss_bullet_group.update()
    background_smoke_group.update()
    explosion_group.update()
    ship_debris_group.update()
    missile_group.update()
    draw_layer_viewer()
    background_ship_hits = pygame.sprite.groupcollide(
        background_ship_group,
        background_alien_bullet_group,
        False,
        True
    )

    for ship, bullets in background_ship_hits.items():
        ship.take_damage(len(bullets))

    background_smoke_group.update()


    # Draw.....................................
    # win.blit(thrust1, (350, 250))
    # Draw.....................................
    # win.blit(thrust1, (350, 250))

    background_smoke_group.draw(win)
    background_ship_group.draw(win)
    background_alien_group.draw(win)
    background_bullet_group.draw(win)
    background_beam_effect_group.draw(win)
    background_explosion_group.draw(win)
    draw_player_missiles()
    draw_escape_thruster()
    spaceship_group.draw(win)
    ship_debris_group.draw(win)
    if post_boss_transition and not game_over:
        screen_blink()

    missile_group.draw(win)
    alien_group.draw(win)
    if waves == 4 or waves == 8 or waves == 12:
        boss_group.draw(win)
    charge_trail_group.draw(win)
    for shot in Charge_Shot_group:
        shot.draw_glow(win)

    Charge_Shot_group.draw(win)
    Boss_Charge_Shot_group.draw(win)
    bullets_group.draw(win)
    alien_bullet_group.draw(win)
    boss_bullet_group.draw(win)
    background_alien_bullet_group.draw(win)
    explosion_group.draw(win)
    if waves == 4:
        win.blit(upgrade_missile, ((int(screen_width / 2), (screen_height / 2))))
    apply_screen_shake(win)
    pygame.display.flip()

pygame.quit()
