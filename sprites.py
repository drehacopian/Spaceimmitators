# sprites.py
import pygame
import math, random
from assets import (
    ships, alien_images, boss_image, low_health_boss_image,
    shield_image, small_shield_image
)
from assets import explosion_fx, explosion2_fx  # sounds for collisions
#from effects import Explosion  # you’ll move Explosion later in Step 3
from effects import Explosion

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

screen_width = 600
screen_height = 800


spaceship_group = None
spaceship = None
explosion_group = None
alien_group = None
shield_group = None
boss_group = None
boss = None
bullets_group = None
alien_bullet_group = None
boss_bullet_group = None
missile_group = None
Charge_Shot_group = None
Boss_Charge_Shot_group = None

def load_animation_row(filename, row, columns=4, total_rows=4):
    sheet = pygame.image.load(filename).convert_alpha()

    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // columns
    frame_height = sheet_height // total_rows

    frames = []

    for col in range(columns):
        frame = sheet.subsurface(
            pygame.Rect(
                col * frame_width,
                row * frame_height,
                frame_width,
                frame_height
            )
        ).copy()

        frames.append(frame)

    return frames

class BackgroundBeamEffect(pygame.sprite.Sprite):
    def __init__(self, ship, scale):
        super().__init__()
        self.ship = ship
        self.scale = scale
        self.start_time = pygame.time.get_ticks()
        self.charge_duration = 900
        self.beam_duration = 700
        self.phase = "charge"

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.fade_after_hit = False
        self.hit_time = 0

    def update(self):
        if not self.ship.alive():
            self.kill()
            return

        elapsed = pygame.time.get_ticks() - self.start_time

        if self.fade_after_hit:
            if pygame.time.get_ticks() - self.hit_time >= 180:
                self.ship.beam_attack_finished = True
                self.kill()
                return

        if elapsed < self.charge_duration:
            self.phase = "charge"
            self.draw_charge(elapsed)

        elif elapsed < self.charge_duration + self.beam_duration:
            self.phase = "beam"
            self.draw_beam(elapsed - self.charge_duration)

        else:
            self.ship.beam_attack_finished = True
            self.kill()

    def draw_charge(self, elapsed):
        pulse = int((elapsed // 70) % 4)
        charge_progress = min(1.0, elapsed / self.charge_duration)
        diameter = max(14, int((18 + charge_progress * 24 + pulse * 2) * self.scale))

        self.image = pygame.Surface((diameter * 3, diameter * 3), pygame.SRCALPHA)
        center = self.image.get_width() // 2

        pygame.draw.circle(
            self.image,
            (40, 120, 255, 60),
            (center, center),
            diameter
        )

        pygame.draw.circle(
            self.image,
            (80, 180, 255, 150),
            (center, center),
            max(4, diameter // 2)
        )

        pygame.draw.circle(
            self.image,
            (230, 250, 255, 240),
            (center, center),
            max(2, diameter // 4)
        )

        self.rect = self.image.get_rect(
            centerx=self.ship.rect.centerx,
            bottom=self.ship.rect.top + int(8 * self.scale)
        )

    def draw_beam(self, elapsed):
        pulse = int((elapsed // 60) % 3)
        beam_width = max(16, int((28 + pulse * 3) * self.scale))
        beam_height = max(1, self.ship.rect.top)

        self.image = pygame.Surface(
            (beam_width * 3, beam_height),
            pygame.SRCALPHA
        )

        center_x = self.image.get_width() // 2

        outer_points = [
            (center_x - beam_width, beam_height),
            (center_x - beam_width // 2, 0),
            (center_x + beam_width // 2, 0),
            (center_x + beam_width, beam_height)
        ]

        middle_points = [
            (center_x - beam_width // 2, beam_height),
            (center_x - beam_width // 4, 0),
            (center_x + beam_width // 4, 0),
            (center_x + beam_width // 2, beam_height)
        ]

        pygame.draw.polygon(
            self.image,
            (40, 100, 255, 90),
            outer_points
        )

        pygame.draw.polygon(
            self.image,
            (80, 190, 255, 190),
            middle_points
        )

        pygame.draw.line(
            self.image,
            (240, 255, 255, 255),
            (center_x, beam_height),
            (center_x, 0),
            max(2, beam_width // 4)
        )

        self.rect = self.image.get_rect(
            centerx=self.ship.rect.centerx,
            bottom=self.ship.rect.top
        )

class BackgroundShip(pygame.sprite.Sprite):
    def __init__(self, image, x, y, scale=0.5):
        super().__init__()

        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)

        self.image = pygame.transform.smoothscale(image, (width, height))
        self.rect = self.image.get_rect(center=(x, y))

        self.normal_centerx = self.rect.centerx
        self.active_beam_effect = None

        self.speed = 6.5
        self.scale = scale

        self.uses_beam_attack = random.random() < 0.25
        self.beam_attack_started = False
        self.beam_attack_finished = False
        self.spawn_time = pygame.time.get_ticks()

        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 700

    def update(self, bullet_group, alien_group, beam_effect_group):
        self.rect.y -= self.speed
        current_time = pygame.time.get_ticks()

        if (
            self.uses_beam_attack
            and not self.beam_attack_started
            and alien_group
            and self.rect.top < pygame.display.get_surface().get_height() - 140
        ):
            beam_effect = BackgroundBeamEffect(self, self.scale)
            beam_effect.start_time = pygame.time.get_ticks()
            beam_effect_group.add(beam_effect)

            self.active_beam_effect = beam_effect
            self.beam_attack_started = True

        if (
            alien_group
            and not self.uses_beam_attack
            and current_time - self.last_shot >= self.shoot_delay
        ):
            bullet = BackgroundBullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = current_time

        self.rect.centerx = self.normal_centerx

        if (
            self.active_beam_effect
            and self.active_beam_effect.alive()
            and self.active_beam_effect.phase == "charge"
        ):
            self.rect.centerx += random.randint(-3, 3)

        if self.rect.bottom < 0:
            self.kill()

class OverheadFlyover(pygame.sprite.Sprite):
    def __init__(self, image, screen_width, screen_height):
        super().__init__()

        scale = random.uniform(1.8, 2.6)

        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)

        self.image = pygame.transform.smoothscale(image, (width, height))
        self.original_image = self.image

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.direction = random.choice(["left_to_right", "right_to_left"])

        if self.direction == "left_to_right":
            self.rect = self.image.get_rect(
                right=-50,
                centery=random.randint(
                    screen_height // 4,
                    screen_height * 3 // 4
                )
            )

            self.speed_x = random.uniform(10, 15)

        else:
            self.image = pygame.transform.flip(self.image, True, False)

            self.rect = self.image.get_rect(
                left=screen_width + 50,
                centery=random.randint(
                    screen_height // 4,
                    screen_height * 3 // 4
                )
            )

            self.speed_x = random.uniform(-15, -10)

        self.speed_y = random.uniform(-1.5, 1.5)

        self.position_x = float(self.rect.x)
        self.position_y = float(self.rect.y)

    def update(self):
        self.position_x += self.speed_x
        self.position_y += self.speed_y

        self.rect.x = int(self.position_x)
        self.rect.y = int(self.position_y)

        if (
            self.rect.left > self.screen_width + 150
            or self.rect.right < -150
        ):
            self.kill()


class BackgroundAlien(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=0.75):
        super().__init__()

        self.alien_number = random.randint(1, 5)
        sheet_name = f"alien{self.alien_number}.png"

        self.frames = load_animation_row(
            sheet_name,
            row=0,
            columns=4,
            total_rows=4
        )

        self.frames = [
            pygame.transform.smoothscale(
                frame,
                (
                    int(frame.get_width() * scale),
                    int(frame.get_height() * scale)
                )
            )
            for frame in self.frames
        ]

        self.frame_index = random.randint(0, len(self.frames) - 1)
        self.animation_speed = 0.12
        self.image = self.frames[int(self.frame_index)]

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.health = random.randint(1, 4)

    def update(self):
        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        old_center = self.rect.center

        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=old_center)

        self.rect.y -= self.speed

        if self.rect.bottom < 0:
            self.kill()

class BackgroundBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface((5, 18), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 255, 120), self.image.get_rect())

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed

        if self.rect.bottom < 0:
            self.kill()

class BackgroundExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.frames = []
        for radius in (8, 14, 20, 26):
            image = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(image, (255, 220, 80), (30, 30), radius)
            self.frames.append(image)

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.last_update = pygame.time.get_ticks()
        self.frame_delay = 70

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update >= self.frame_delay:
            self.frame_index += 1
            self.last_update = current_time

            if self.frame_index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.frame_index]

# --- Spaceship ---
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health, ship):
        super().__init__()
        self.image_orig = ships[ship]
        self.image = self.image_orig
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.last_missile_shot = pygame.time.get_ticks()
        self.last_charge_shot = pygame.time.get_ticks()
        self.charge_counter = 0
        self.charging = False
        self.charge_fired = False
        self.charge_start_y = y
        self.charge_start_x = x

    def rotate(self, angle):
        self.angle += angle
        self.image = pygame.transform.rotate(self.image_orig, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.mask = pygame.mask.from_surface(self.image)

# --- Aliens ---
class Aliens(pygame.sprite.Sprite):
    def __init__(
        self,
        formation,
        col,
        row,
        x,
        y,
        move_counter,
        move_direction,
        level_direction_toggle
    ):
        super().__init__()

        # Pick alien sprite sheet 1 through 5
        self.alien_number = random.randint(1, 5)
        sheet_name = f"alien{self.alien_number}.png"

        # Four rows in each sprite sheet
        self.idle_frames = load_animation_row(
            sheet_name,
            row=0,
            columns=4,
            total_rows=4
        )

        self.celebrate_frames = load_animation_row(
            sheet_name,
            row=1,
            columns=4,
            total_rows=4
        )

        self.point_frames = load_animation_row(
            sheet_name,
            row=2,
            columns=4,
            total_rows=4
        )[:3]

        self.spin_frames = load_animation_row(
            sheet_name,
            row=3,
            columns=4,
            total_rows=4
        )

        # Start with idle animation
        self.frames = self.idle_frames
        self.frame_index = random.randint(0, len(self.frames) - 1)
        self.animation_speed = 0.12
        self.image = self.frames[int(self.frame_index)]

        self.rect = self.image.get_rect(center=(x, y))

        # Keep current constructor compatibility
        self.formation = formation
        self.row = row
        self.col = col
        self.move_counter = move_counter
        self.move_direction = move_direction
        self.level_direction_toggle = level_direction_toggle

        # Keep these for later formation attacks
        self.attack = False
        self.returning = False
        self.return_time = 0
        self.attack_start_x = x
        self.original_y = y

    def update(self):
        # Animate
        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        old_center = self.rect.center

        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=old_center)

        # Simple horizontal movement
        self.rect.x += self.move_direction
        self.move_counter += 1

        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= -1

        self.mask = pygame.mask.from_surface(self.image)

    def idle(self):
        self.frames = self.idle_frames
        self.frame_index = 0

    def celebrate(self):
        self.frames = self.celebrate_frames
        self.frame_index = 0

    def point(self):
        self.frames = self.point_frames
        self.frame_index = 0

    def spin(self):
        self.frames = self.spin_frames
        self.frame_index = 0

# --- Boss ---
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self.base_image = boss_image
        self.low_health_image = low_health_boss_image
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(x, y))
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.charge_counter = 0   # ✅ added back

# --- Bullets ---
class Bullets(pygame.sprite.Sprite):
    base_image = pygame.image.load("bullet.png")  # already preloaded in assets

    def __init__(self, x, y, angle, speed=10):
        super().__init__()
        self.original_image = Bullets.base_image
        self.image = pygame.transform.rotate(self.original_image, angle - 90)
        self.rect = self.image.get_rect(center=(x, y))

        self.angle = angle
        theta_rad = math.radians(self.angle)
        self.speed = speed
        self.velocity_x = self.speed * math.cos(theta_rad)
        self.velocity_y = -self.speed * math.sin(theta_rad)

        self.size_multiplier = 1.0
        self.pulsate_speed = 0.1
        self.base_size = self.rect.size

    def pulsate(self):
        self.size_multiplier = 1.0 + 0.2 * math.sin(pygame.time.get_ticks() * self.pulsate_speed)
        scaled_size = (
            int(self.base_size[0] * self.size_multiplier),
            int(self.base_size[1] * self.size_multiplier)
        )
        self.image = pygame.transform.scale(self.original_image, scaled_size)

    def move(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        if self.rect.bottom < 0:
            self.kill()

    def handle_collisions(self, groups):
        (
            alien_bullet_group, boss_group, shield_group,
            alien_group, boss_bullet_group, Boss_Charge_Shot_group,
            explosion_group, boss, shield
        ) = groups

        if pygame.sprite.spritecollide(self, alien_bullet_group, True, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
            return

        collision_groups = [
            (boss_group, True),
            (shield_group, False),
            (alien_group, True),
            (boss_bullet_group, False),
            (Boss_Charge_Shot_group, False)
        ]

        for group, kill_on_hit in collision_groups:
            if pygame.sprite.spritecollide(self, group, kill_on_hit):
                self.trigger_explosion(explosion_group)
                if group == boss_group:
                    boss.health_remaining -= 0.5
                elif group == shield_group:
                    shield.health_remaining -= 1
                break

    def trigger_explosion(self, explosion_group):
        self.kill()
        explosion_fx.play()
        explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
        explosion_group.add(explosion)

    def update(self, groups=None):
        self.pulsate()
        self.move()
        if groups:
            self.handle_collisions(groups)

# --- Missiles ---
class Missiles(pygame.sprite.Sprite):
    def __init__(self, x, y, image, speed=8):
        super().__init__()

        self.image = image.copy()
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = speed

    def update(self):
        # Move straight upward
        self.rect.y -= self.speed

        if self.rect.bottom < 0:
            self.kill()
            return

        # Hit normal alien
        if pygame.sprite.spritecollide(
            self,
            alien_group,
            True,
            pygame.sprite.collide_mask
        ):
            self.kill()
            explosion_fx.play()

            explosion = Explosion(
                self.rect.centerx,
                self.rect.centery,
                2
            )
            explosion_group.add(explosion)
            return

        # Hit boss
        if pygame.sprite.spritecollide(
            self,
            boss_group,
            False,
            pygame.sprite.collide_mask
        ):
            self.kill()
            explosion_fx.play()

            explosion = Explosion(
                self.rect.centerx,
                self.rect.centery,
                3
            )
            explosion_group.add(explosion)

            boss.health_remaining -= 10
            return

        # Hit boss shield
        if pygame.sprite.spritecollide(
            self,
            shield_group,
            False,
            pygame.sprite.collide_mask
        ):
            self.kill()
            explosion_fx.play()

            explosion = Explosion(
                self.rect.centerx,
                self.rect.centery,
                3
            )
            explosion_group.add(explosion)

            shield.health_remaining -= 10
            return

        # Hit boss projectile
        if pygame.sprite.spritecollide(
            self,
            boss_bullet_group,
            True,
            pygame.sprite.collide_mask
        ):
            self.kill()
            explosion_fx.play()

            explosion = Explosion(
                self.rect.centerx,
                self.rect.centery,
                2
            )
            explosion_group.add(explosion)

# --- Shields ---
class Shield(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self.image = shield_image
        self.rect = self.image.get_rect(center=(x, y))
        self.health_start = health
        self.health_remaining = health

class SmallShield(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self.image = small_shield_image
        self.rect = self.image.get_rect(center=(x, y))
        self.health_start = health
        self.health_remaining = health

class Charge_Shot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        base_image = pygame.image.load("bullet.png").convert_alpha()
        self.base_image = base_image

        # Main damaging projectile only
        self.image = pygame.transform.smoothscale(
            base_image,
            (52, 52)
        )

        self.rect = self.image.get_rect(
            midtop=(x, y)
        )

        self.speed = 10

    def move(self):
        self.rect.y -= self.speed

        if self.rect.bottom < 0:
            self.kill()

    def handle_alien_collision(self):
        if pygame.sprite.spritecollide(
            self,
            alien_group,
            True
        ):
            explosion_fx.play()

            explosion = Explosion(
                self.rect.centerx,
                self.rect.top + 30,
                2
            )
            explosion_group.add(explosion)

    def handle_boss_collision(self):
        if pygame.sprite.spritecollide(
            self,
            boss_group,
            False
        ):
            self.kill()
            explosion_fx.play()

            explosion = Explosion(
                self.rect.centerx,
                self.rect.top + 30,
                3
            )
            explosion_group.add(explosion)

            boss.health_remaining -= 1

    def handle_shield_collision(self):
        if pygame.sprite.spritecollide(
            self,
            shield_group,
            False
        ):
            self.kill()
            explosion_fx.play()

            explosion = Explosion(
                self.rect.centerx,
                self.rect.top + 30,
                3
            )
            explosion_group.add(explosion)

            shield.health_remaining -= 2

    def handle_boss_bullet_collision(self):
        if pygame.sprite.spritecollide(
            self,
            boss_bullet_group,
            True
        ):
            explosion_fx.play()

            explosion = Explosion(
                self.rect.centerx,
                self.rect.top + 30,
                2
            )
            explosion_group.add(explosion)

    def handle_missile_collision(self):
        if pygame.sprite.spritecollide(
            self,
            missile_group,
            False
        ):
            self.kill()
            explosion_fx.play()

    def handle_boss_charge_collision(self):
        if pygame.sprite.spritecollide(
            self,
            Boss_Charge_Shot_group,
            False
        ):
            self.kill()
            explosion_fx.play()

            explosion = Explosion(
                self.rect.centerx,
                self.rect.top + 30,
                3
            )
            explosion_group.add(explosion)

    def draw_glow(self, surface):

        glow_sizes = [70, 64, 58]

        glow_alpha = [35, 55, 90]

        for size, alpha in zip(glow_sizes, glow_alpha):
            glow = pygame.transform.smoothscale(
                self.base_image,
                (size, size)
            )

            glow.set_alpha(alpha)

            glow_rect = glow.get_rect(
                center=self.rect.center
            )

            surface.blit(glow, glow_rect)

    def update(self):
        self.move()
        self.handle_alien_collision()
        self.handle_boss_collision()
        self.handle_shield_collision()
        self.handle_boss_bullet_collision()
        self.handle_missile_collision()
        self.handle_boss_charge_collision()

class Charge_Trail(pygame.sprite.Sprite):
    def __init__(self, x, y, size, delay, owner, speed=10):
        super().__init__()

        base_image = pygame.image.load("bullet.png").convert_alpha()

        self.image = pygame.transform.smoothscale(
            base_image,
            (size, size)
        )

        self.rect = self.image.get_rect(
            midtop=(x, y)
        )

        self.speed = speed
        self.delay = delay
        self.spawn_time = pygame.time.get_ticks()
        self.active = False
        self.owner = owner

        # Invisible until its delay finishes
        self.image.set_alpha(0)

    def update(self):
        # If the main charge shot no longer exists,
        # this trail should disappear immediately.
        if not self.owner.alive():
            self.kill()
            return
        current_time = pygame.time.get_ticks()

        if not self.active:
            if current_time - self.spawn_time >= self.delay:
                self.active = True
                self.image.set_alpha(255)
            else:
                return

        self.rect.y -= self.speed

        if self.rect.bottom < 0:
            self.kill()

class Boss_Charge_Shot(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x=None, target_y=None):
        super().__init__()
        self.original_image = pygame.image.load("alien_bullet.png")
        self.original_image = pygame.transform.scale(self.original_image, (100, 100))
        self.image = pygame.transform.rotate(self.original_image, 180)
        self.rect = self.image.get_rect(center=(x, y))

        # Movement setup (angled if target given)
        if target_x is not None and target_y is not None:
            dx, dy = target_x - x, target_y - y
            angle = math.degrees(math.atan2(dy, dx))
            speed = 10
            self.velocity_x = speed * math.cos(math.radians(angle))
            self.velocity_y = speed * math.sin(math.radians(angle))
            self.image = pygame.transform.rotate(self.original_image, -angle)
        else:
            self.velocity_x = 0
            self.velocity_y = 10

    def move(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        if self.rect.top > screen_height:
            self.kill()

    def handle_spaceship_collision(self):
        if pygame.sprite.spritecollide(self, spaceship_group, True, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining = 0
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)

    def handle_charge_shot_collision(self):
        # Overrides player's charge shot
        if pygame.sprite.spritecollide(self, Charge_Shot_group, True, pygame.sprite.collide_mask):
            explosion2_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

    def handle_missile_collision(self):
        if pygame.sprite.spritecollide(self, missile_group, True, pygame.sprite.collide_mask):
            # Cancel both
            self.kill()
            explosion_fx.play()

            # Twice as big blast
            big_explosion = RadiatingExplosion(
                self.rect.centerx, self.rect.centery,
                radius=400, damage=3  # doubled radius from 200 → 400
            )
            explosion_group.add(big_explosion)

    def update(self):
        self.move()
        self.handle_spaceship_collision()
        self.handle_charge_shot_collision()
        self.handle_missile_collision()

class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("alien_bullet.png")
        self.rect = self.image.get_rect(center=(x, y))

    def move(self):
        self.rect.y += 10
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def handle_spaceship_collision(self):
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            global time_last_hit
            time_last_hit = pygame.time.get_ticks()
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            if spaceship.health_remaining <= 0:
                explosion2 = Explosion(spaceship.rect.centerx, spaceship.rect.centery, 3)
                explosion_group.add(explosion2)

    def handle_charge_shot_collision(self):
        if pygame.sprite.spritecollide(self, Charge_Shot_group, False, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

    def handle_player_bullet_collision(self):
        if pygame.sprite.spritecollide(self, bullets_group, True, pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            # smaller explosion for bullet cancel
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

    def update(self):
        self.move()
        self.handle_spaceship_collision()
        self.handle_charge_shot_collision()
        self.handle_player_bullet_collision()

class Boss_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("alien_bullet.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.image = pygame.transform.rotate(self.image, 180)
        self.rect = self.image.get_rect(center=(x, y))

    def move(self):
        self.rect.y += 10
        if self.rect.top > screen_height:
            self.kill()

    def handle_spaceship_collision(self):
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            global time_last_hit
            time_last_hit = pygame.time.get_ticks()
            self.kill()
            explosion2_fx.play()
            spaceship.health_remaining -= 2
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            if spaceship.health_remaining <= 0:
                explosion2 = Explosion(spaceship.rect.centerx, spaceship.rect.centery, 3)
                explosion_group.add(explosion2)

    def handle_charge_shot_collision(self):
        # Boss bullet is stronger → removes Charge_Shot
        if pygame.sprite.spritecollide(self, Charge_Shot_group, True, pygame.sprite.collide_mask):
            explosion2_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)

    def handle_missile_collision(self):
        # Boss bullet overrides missiles → destroys missile, keeps going
        if pygame.sprite.spritecollide(self, missile_group, True, pygame.sprite.collide_mask):
            explosion2_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
            # Boss bullet does NOT self.kill() → keeps flying

    def update(self):
        self.move()
        self.handle_spaceship_collision()
        self.handle_charge_shot_collision()
        self.handle_missile_collision()

#------ cinematics----

