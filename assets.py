# assets.py
import pygame

class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, x, y, w, h, colour, rotate, xx, yy):
        image = pygame.Surface((w, h)).convert_alpha()
        image.blit(self.sheet, (0, 0), (x, y, w, h))
        image = pygame.transform.scale(image, (xx, yy))
        image = pygame.transform.rotate(image, rotate)
        image.set_colorkey(colour)
        return image


sprite_sheet_image2 = pygame.image.load("thruster.png")
sprite_sheet2 = SpriteSheet(sprite_sheet_image2)

thruster_sheet = pygame.image.load("thruster.png")



# --- Colors (kept here so assets that need them can import consistently) ---
black = (0, 0, 0)
red   = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

# --- Bullets (player & alien) ---
bullet_base = pygame.image.load("bullet.png")
alien_bullet_base = pygame.image.load("alien_bullet.png")

big_bullet  = pygame.transform.scale(bullet_base, (60, 60))
med1_bullet = pygame.transform.scale(bullet_base, (40, 40))
med2_bullet = pygame.transform.scale(bullet_base, (50, 50))
sm1_bullet  = pygame.transform.scale(bullet_base, (20, 20))
sm2_bullet  = pygame.transform.scale(bullet_base, (30, 30))
small_bullet = pygame.transform.scale(bullet_base, (20, 20))  # alias you already use

big_boss_bullet  = pygame.transform.scale(alien_bullet_base, (90, 90))
med1_boss_bullet = pygame.transform.scale(alien_bullet_base, (60, 60))
med2_boss_bullet = pygame.transform.scale(alien_bullet_base, (75, 75))
sm1_boss_bullet  = pygame.transform.scale(alien_bullet_base, (30, 30))
sm2_boss_bullet  = pygame.transform.scale(alien_bullet_base, (45, 45))
small_boss_bullet = alien_bullet_base  # original size

# --- Explosions (pre-scaled frames by size) ---
EXPLOSION_FRAMES = {
    1: [pygame.transform.scale(pygame.image.load(f"exp{n}.png"), (20, 20))  for n in range(1, 6)],
    2: [pygame.transform.scale(pygame.image.load(f"exp{n}.png"), (40, 40))  for n in range(1, 6)],
    3: [pygame.transform.scale(pygame.image.load(f"exp{n}.png"), (160, 160)) for n in range(1, 6)],
}

# --- Layered red ship ---
layered_ship_sheet = pygame.image.load(
    "spaceship Layered.png"
)

SHIP_LAYER_WIDTH = 154
SHIP_LAYER_HEIGHT = 80

red_ship_layers = []

# Red ship is the left column.
# Use rows 0 through 9.
# Row 10 is the cockpit escape rocket, so we ignore it for now.
for row in range(10):
    layer_rect = pygame.Rect(
        0,
        row * SHIP_LAYER_HEIGHT,
        SHIP_LAYER_WIDTH,
        SHIP_LAYER_HEIGHT
    )

    layer_image = layered_ship_sheet.subsurface(
        layer_rect
    ).copy()

    red_ship_layers.append(layer_image)


# Temporarily assemble all 10 layers into one complete ship.
# This lets the existing game use it without changing Spaceship yet.
red_ship_image = pygame.Surface(
    (SHIP_LAYER_WIDTH, SHIP_LAYER_HEIGHT),
    pygame.SRCALPHA
)

# Layer stacking order from bottom to top
red_ship_layer_order = [
    7,  # Sprite 8 - rocket, underneath sprite 7
    6,  # Sprite 7 - above the rocket

    4,  # Sprite 5
    5,  # Sprite 6

    2,  # Sprite 3 - above sprites 5 and 6
    3,  # Sprite 4 - above sprites 5 and 6

    0,  # Sprite 1
    1,  # Sprite 2
    8,  # Sprite 9
    9   # Sprite 10
]

for layer_index in red_ship_layer_order:
    red_ship_image.blit(
        red_ship_layers[layer_index],
        (0, 0)
    )

# --- Ships, Aliens, Boss, Shields ---
ships = [
    red_ship_image,
    pygame.image.load("spaceship2.png"),
    pygame.image.load("spaceship3.png"),
]
alien_images = [
    pygame.transform.scale(
        pygame.image.load(f"alien{i}.png"),
        (40, 40)
    )
    for i in range(1, 6)
]

boss_image = pygame.transform.scale(pygame.image.load("boss.png"), (120, 120))
low_health_boss_image = pygame.transform.scale(pygame.image.load("lowhealth.png"), (120, 120))

shield_image = pygame.image.load("shield.png")
small_shield_image = pygame.transform.scale(shield_image, (55, 45))

# --- Background ---
bg = pygame.image.load("bg.png")

# --- Sounds (NOTE: import this module after mixer/init) ---
explosion_fx  = pygame.mixer.Sound("explosion.wav");  explosion_fx.set_volume(0.01)
explosion2_fx = pygame.mixer.Sound("explosion2.wav"); explosion2_fx.set_volume(0.01)
laser_fx      = pygame.mixer.Sound("laser.wav");      laser_fx.set_volume(0.01)
