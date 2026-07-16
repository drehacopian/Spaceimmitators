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

# --- Ships, Aliens, Boss, Shields ---
ships = [
    pygame.image.load("spaceship.png"),
    pygame.image.load("spaceship.png"),  # kept duplicate index for compatibility
    pygame.image.load("spaceship2.png"),
    pygame.image.load("spaceship3.png"),
]

alien_images = [pygame.transform.scale(pygame.image.load(f"alien{i}.png"), (40, 40)) for i in range(1, 6)]

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
