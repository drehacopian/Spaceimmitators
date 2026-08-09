# effects.py
import pygame
import random
import math
from assets import EXPLOSION_FRAMES, black

from assets import EXPLOSION_FRAMES

# --- Explosion ---
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.images = EXPLOSION_FRAMES[size]  # ✅ Just reuse preloaded list
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0

    def update(self):
        explosion_speed = 3
        self.counter += 1

        if self.counter >= explosion_speed:
            self.counter = 0
            self.index += 1
            if self.index < len(self.images):
                self.image = self.images[self.index]
            else:
                self.kill()


# --- Radiating Explosion (fancy effect) ---
class RadiatingExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y, radius=200, damage=3):
        super().__init__()
        self.center = (x, y)
        self.max_radius = radius
        self.cross_radius = 0
        self.diag_radius = 0
        self.growth_speed = 15
        self.damage = damage
        self.timer = 0

        # Delay before diagonals start
        self.diagonal_delay = 20  # ~1 second
        self.diagonal_active = False

        # Invisible sprite controller
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.center)

        # First explosion
        explosion2_fx.play()
        start_screen_shake(intensity=14, duration=20)

    def update(self):
        self.timer += 1

        # ---- Cross ( + ) always active ----
        self.cross_radius += self.growth_speed
        if self.cross_radius <= self.max_radius and self.timer % 5 == 0:
            cross_offsets = [
                (self.cross_radius, 0), (-self.cross_radius, 0),
                (0, self.cross_radius), (0, -self.cross_radius)
            ]
            for dx, dy in cross_offsets:
                explosion = Explosion(self.center[0] + dx, self.center[1] + dy, 3)
                explosion_group.add(explosion)

        # ---- Start diagonals fresh from center ----
        if self.timer == self.diagonal_delay:
            self.diagonal_active = True
            self.diag_radius = 0  # reset to center
            explosion2_fx.play()
            start_screen_shake(intensity=12, duration=15)

        # ---- Diagonal ( X ) after delay ----
        if self.diagonal_active:
            self.diag_radius += self.growth_speed
            if self.diag_radius <= self.max_radius and self.timer % 5 == 0:
                diag_offsets = [
                    (self.diag_radius, self.diag_radius),
                    (-self.diag_radius, self.diag_radius),
                    (self.diag_radius, -self.diag_radius),
                    (-self.diag_radius, -self.diag_radius)
                ]
                for dx, dy in diag_offsets:
                    explosion = Explosion(self.center[0] + dx, self.center[1] + dy, 3)
                    explosion_group.add(explosion)

        # Kill once both are done
        if self.cross_radius > self.max_radius and self.diag_radius > self.max_radius:
            self.kill()

        # Functional damage
        self.check_collisions()

    def check_collisions(self):
        for alien in pygame.sprite.spritecollide(self, alien_group, True, pygame.sprite.collide_mask):
            explosion_group.add(Explosion(alien.rect.centerx, alien.rect.centery, 2))

        if pygame.sprite.spritecollide(self, boss_group, False, pygame.sprite.collide_mask):
            boss.health_remaining -= self.damage

        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            spaceship.health_remaining -= self.damage
            if spaceship.health_remaining <= 0:
                explosion_group.add(Explosion(spaceship.rect.centerx, spaceship.rect.centery, 3))

        for group in [bullets_group, alien_bullet_group, boss_bullet_group]:
            pygame.sprite.spritecollide(self, group, True, pygame.sprite.collide_mask)

class Star:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.streaking = False
        self.streak_timer = 0
        self.streak_duration = 0

        self.reset(
            random.randint(
                0,
                screen_height
            )
        )

    def reset(self, y=None):
        if y is None:
            y = random.randint(
                -100,
                -10
            )

        self.x = random.randint(
            0,
            self.screen_width
        )

        self.y = y

        self.depth = random.uniform(
            0.25,
            1.0
        )

        self.speed = (
            40
            + self.depth * 170
        )

        self.size = max(
            1,
            int(self.depth * 3)
        )

        self.streaking = False
        self.streak_timer = 0

    def start_streak(self):
        self.streaking = True

        self.streak_duration = random.randint(
            18,
            30
        )

        self.streak_timer = self.streak_duration

    def update(self, dt):
        if self.streaking:
            self.y += self.speed * 10 * dt

            self.streak_timer -= 1

            if self.streak_timer <= 0:
                self.streaking = False

        else:
            self.y += self.speed * dt

        if self.y > self.screen_height + 30:
            self.reset()

    def draw(self, surface):
        brightness = int(
            100
            + self.depth * 155
        )

        color = (
            brightness,
            brightness,
            brightness
        )

        if self.streaking:

            streak_length = int(
                90
                + self.depth * 135
            )

            pygame.draw.line(
                surface,
                color,
                (
                    int(self.x),
                    int(self.y - streak_length)
                ),
                (
                    int(self.x),
                    int(self.y)
                ),
                max(
                    1,
                    self.size // 2
                )
            )

        else:

            pygame.draw.circle(
                surface,
                color,
                (
                    int(self.x),
                    int(self.y)
                ),
                self.size
            )


# --- Thrust ---
class Thrust(pygame.sprite.Sprite):
    def __init__(self, x, y, boss, images):
        super().__init__()

        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))

        self.boss = boss
        self.thrust_counter = 0

    def update(self):
        self.thrust_counter += 1

        frame_index = (self.thrust_counter // 5) % len(self.images)
        self.image = self.images[frame_index]

        self.rect.centerx = self.boss.rect.centerx
        self.rect.bottom = self.boss.rect.top + 10
