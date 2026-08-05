# sprites.py
import pygame
import math, random
from assets import (
    ships, alien_images, boss_image, low_health_boss_image,
    shield_image, small_shield_image, red_ship_layers, red_ship_layer_order
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
ship_debris_group = None
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

        self.original_image = pygame.transform.smoothscale(
            image,
            (width, height)
        )

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.speed_y = 6.5
        self.chase_speed = 2.8
        self.scale = scale

        self.target = None
        self.active_beam_effect = None

        self.uses_beam_attack = random.random() < 0.15
        self.beam_attack_started = False
        self.beam_attack_finished = False

        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(500, 900)

        self.weave_counter = random.uniform(0, math.pi * 2)
        self.weave_speed = random.uniform(0.05, 0.09)

        self.health = 3
        self.max_health = 3

        self.combat_state = "pursuing"

        self.damaged = False
        self.critical = False
        self.retreating = False

        self.hit_flash_until = 0
        self.smoke_timer = 0
        self.smoke_delay = 90

        self.normal_speed_y = self.speed_y
        self.damaged_speed_y = self.speed_y * 0.62
        self.critical_speed_y = self.speed_y * 0.34

        self.dodge_chance = 0.70
        self.dodge_direction = 0
        self.dodge_timer = 0

    def take_damage(self, amount=1):
        self.health -= amount
        self.hit_flash_until = pygame.time.get_ticks() + 120

        if self.health <= 0:
            self.health = 0
            self.combat_state = "destroyed"
            return

        if self.health == 1:
            self.critical = True
            self.damaged = True
            self.retreating = True
            self.combat_state = "retreating"
            self.speed_y = self.critical_speed_y

        elif self.health == 2:
            self.damaged = True
            self.combat_state = "damaged"
            self.speed_y = self.damaged_speed_y

    def choose_target(self, alien_group):
        living_aliens = [
            alien
            for alien in alien_group
            if alien.alive()
        ]

        if not living_aliens:
            self.target = None
            return

        self.target = min(
            living_aliens,
            key=lambda alien: (
                alien.rect.centerx - self.rect.centerx
            ) ** 2 + (
                alien.rect.centery - self.rect.centery
            ) ** 2
        )

    def update(
            self,
            bullet_group,
            alien_group,
            beam_effect_group,
            alien_bullet_group,
            smoke_group,
            explosion_group
    ):
        current_time = pygame.time.get_ticks()

        if self.damaged:
            if current_time - self.smoke_timer >= self.smoke_delay:
                smoke = BackgroundSmoke(
                    self.rect.centerx,
                    self.rect.bottom,
                    self.scale
                )

                smoke_group.add(smoke)
                self.smoke_timer = current_time

                if self.critical:
                    self.smoke_delay = random.randint(45, 75)
                else:
                    self.smoke_delay = random.randint(80, 130)

        if self.health <= 0:
            explosion = BackgroundExplosion(
                self.rect.centerx,
                self.rect.centery
            )

            explosion_group.add(explosion)
            self.kill()
            return

        if self.dodge_timer > 0:
            self.x += self.dodge_direction * 6
            self.dodge_timer -= 1

            if self.dodge_timer == 0:
                self.combat_state = (
                    "retreating"
                    if self.retreating
                    else "pursuing"
                )

        elif not self.critical:
            threatening_bullets = [
                bullet
                for bullet in alien_bullet_group
                if (
                        bullet.rect.centery < self.rect.centery
                        and abs(
                    bullet.rect.centerx
                    - self.rect.centerx
                ) < 45
                        and self.rect.centery
                        - bullet.rect.centery < 180
                )
            ]

            if (
                    threatening_bullets
                    and random.random() < self.dodge_chance
            ):
                nearest_bullet = min(
                    threatening_bullets,
                    key=lambda bullet:
                    abs(
                        bullet.rect.centery
                        - self.rect.centery
                    )
                )

                if nearest_bullet.rect.centerx < self.rect.centerx:
                    self.dodge_direction = 1
                else:
                    self.dodge_direction = -1

                self.dodge_timer = random.randint(8, 14)
                self.combat_state = "dodging"

        if (
            self.target is None
            or not self.target.alive()
        ):
            self.choose_target(alien_group)

        self.y -= self.speed_y

        if self.target:
            distance_x = (
                self.target.rect.centerx
                - self.rect.centerx
            )

            if abs(distance_x) > 8:
                if distance_x > 0:
                    self.x += self.chase_speed
                else:
                    self.x -= self.chase_speed

            self.weave_counter += self.weave_speed
            self.x += math.sin(self.weave_counter) * 0.8

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        screen_width = pygame.display.get_surface().get_width()

        if self.rect.left < 20:
            self.rect.left = 20
            self.x = float(self.rect.x)

        if self.rect.right > screen_width - 20:
            self.rect.right = screen_width - 20
            self.x = float(self.rect.x)

        if (
            self.target
            and self.uses_beam_attack
            and not self.beam_attack_started
            and self.rect.top
            < pygame.display.get_surface().get_height() - 140
        ):
            beam_effect = BackgroundBeamEffect(
                self,
                self.scale
            )

            beam_effect_group.add(beam_effect)

            self.active_beam_effect = beam_effect
            self.beam_attack_started = True

        if (
            self.target
            and not self.uses_beam_attack
            and current_time - self.last_shot
            >= self.shoot_delay
        ):
            horizontal_difference = abs(
                self.target.rect.centerx
                - self.rect.centerx
            )

            if horizontal_difference < 55:
                bullet = BackgroundBullet(
                    self.rect.centerx,
                    self.rect.top
                )

                bullet_group.add(bullet)
                self.last_shot = current_time
                self.shoot_delay = random.randint(500, 900)

        if (
            self.active_beam_effect
            and self.active_beam_effect.alive()
            and self.active_beam_effect.phase == "charge"
        ):
            self.rect.x += random.randint(-3, 3)

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

        self.frame_index = random.randint(
            0,
            len(self.frames) - 1
        )

        self.animation_speed = 0.12
        self.image = self.frames[int(self.frame_index)]

        self.rect = self.image.get_rect(center=(x, y))

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.speed_y = random.uniform(4.7, 5.5)
        self.evade_speed = random.uniform(2.0, 3.2)

        self.health = random.randint(1, 2)

        self.evade_direction = random.choice([-1, 1])
        self.evade_timer = random.randint(20, 60)

        self.weave_counter = random.uniform(
            0,
            math.pi * 2
        )

        self.weave_speed = random.uniform(0.06, 0.11)

        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(800, 1500)

    def update(
            self,
            ship_group,
            alien_bullet_group
    ):
        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        old_center = self.rect.center

        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=old_center)

        self.y -= self.speed_y

        nearest_ship = None

        if ship_group:
            nearest_ship = min(
                ship_group,
                key=lambda ship: (
                    ship.rect.centerx
                    - self.rect.centerx
                ) ** 2 + (
                    ship.rect.centery
                    - self.rect.centery
                ) ** 2
            )

        if nearest_ship:
            horizontal_distance = (
                nearest_ship.rect.centerx
                - self.rect.centerx
            )

            vertical_distance = abs(
                nearest_ship.rect.centery
                - self.rect.centery
            )

            if vertical_distance < 300:
                if horizontal_distance > 0:
                    self.x -= self.evade_speed
                else:
                    self.x += self.evade_speed

        current_time = pygame.time.get_ticks()

        if (
                nearest_ship
                and current_time - self.last_shot
                >= self.shoot_delay
        ):
            horizontal_distance = abs(
                nearest_ship.rect.centerx
                - self.rect.centerx
            )

            vertical_distance = abs(
                nearest_ship.rect.centery
                - self.rect.centery
            )

            if (
                    horizontal_distance < 180
                    and vertical_distance < 350
            ):
                bullet = BackgroundAlienBullet(
                    self.rect.centerx,
                    self.rect.bottom,
                    nearest_ship.rect.centerx,
                    nearest_ship.rect.centery
                )

                alien_bullet_group.add(bullet)

                self.last_shot = current_time
                self.shoot_delay = random.randint(
                    800,
                    1500
                )

        self.evade_timer -= 1

        if self.evade_timer <= 0:
            self.evade_direction *= -1
            self.evade_timer = random.randint(20, 60)

        self.weave_counter += self.weave_speed

        self.x += (
            math.sin(self.weave_counter)
            * self.evade_direction
            * 1.3
        )

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        screen_width = pygame.display.get_surface().get_width()

        if self.rect.left < 20:
            self.rect.left = 20
            self.x = float(self.rect.x)
            self.evade_direction = 1

        if self.rect.right > screen_width - 20:
            self.rect.right = screen_width - 20
            self.x = float(self.rect.x)
            self.evade_direction = -1

        if self.rect.bottom < 0:
            self.kill()

class BackgroundBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface((4, 8), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 255, 120), self.image.get_rect())

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed

        if self.rect.bottom < 0:
            self.kill()

class BackgroundAlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()

        self.image = pygame.Surface(
            (4, 8),
            pygame.SRCALPHA
        )

        pygame.draw.ellipse(
            self.image,
            (255, 90, 90),
            self.image.get_rect()
        )

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)

        if distance == 0:
            distance = 1

        speed = 7

        self.velocity_x = dx / distance * speed
        self.velocity_y = dy / distance * speed

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        screen = pygame.display.get_surface()

        if (
            self.rect.right < 0
            or self.rect.left > screen.get_width()
            or self.rect.bottom < 0
            or self.rect.top > screen.get_height()
        ):
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

class BackgroundSmoke(pygame.sprite.Sprite):
    def __init__(self, x, y, scale=1.0):
        super().__init__()

        size = 10

        self.image = pygame.Surface(
            (size * 2, size * 2),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            self.image,
            (180, 180, 180, 230),
            (size, size),
            size
        )

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.velocity_x = random.uniform(-0.25, 0.25)
        self.velocity_y = random.uniform(0.5, 1.1)

        self.alpha = 150
        self.fade_speed = 2

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.alpha -= self.fade_speed

        if self.alpha <= 0:
            self.kill()
            return

        self.image.set_alpha(self.alpha)

class ShipDebris(pygame.sprite.Sprite):
    def __init__(self, image, x, y, starting_angle=0):
        super().__init__()

        self.original_image = image.copy()
        self.image = pygame.transform.rotate(
            self.original_image,
            starting_angle
        )

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)

        # Random direction and speed
        self.velocity_x = random.uniform(-5.0, 5.0)
        self.velocity_y = random.uniform(-4.0, 3.0)

        # Random spin
        self.angle = starting_angle
        self.rotation_speed = random.uniform(-12, 12)

        # Prevent almost-zero rotation
        if -2 < self.rotation_speed < 2:
            self.rotation_speed = random.choice([-5, 5])

        # Random time before exploding
        self.explode_time = (
            pygame.time.get_ticks()
            + random.randint(700, 1800)
        )

    def damage_part_at_point(
            self,
            hit_x,
            hit_y,
            damage,
            debris_group
    ):
        if self.ship_number != 0:
            return

        # Convert screen position into position
        # inside the 154 x 80 red ship canvas.
        local_x = hit_x - self.rect.left
        local_y = hit_y - self.rect.top

        part_name = None

        # Small left sweep wing
        if (
                30 <= local_x <= 72
                and 28 <= local_y <= 62
        ):
            part_name = "sweep_left_wing"

        # Small right sweep wing
        elif (
                82 <= local_x <= 124
                and 28 <= local_y <= 62
        ):
            part_name = "sweep_right_wing"

        if part_name is None:
            return

        part = self.ship_parts[part_name]

        if not part["attached"]:
            return

        part["health"] -= damage

        print(
            part_name,
            "health:",
            part["health"]
        )

        if part["health"] <= 0:
            self.detach_part(
                part_name,
                debris_group
            )
    def detach_part(self, part_name, debris_group):
        if self.ship_number != 0:
            return

        part = self.ship_parts.get(part_name)

        if part is None:
            return

        if not part["attached"]:
            return

        layer_index = part["layer"]

        # Default values for ordinary parts
        debris_x = self.rect.centerx
        debris_y = self.rect.centery
        starting_angle = 0

        # Small left sweep wing
        if part_name == "sweep_left_wing":
            debris_x = self.rect.left + 72
            debris_y = (
                    self.rect.top
                    + 47
                    + self.wing_offset_y
            )

            starting_angle = self.wing_sweep

        # Small right sweep wing
        elif part_name == "sweep_right_wing":
            debris_x = self.rect.left + 82
            debris_y = (
                    self.rect.top
                    + 47
                    + self.wing_offset_y
            )

            starting_angle = -self.wing_sweep

        part["attached"] = False

        debris = ShipDebris(
            self.ship_layers[layer_index],
            debris_x,
            debris_y,
            starting_angle
        )

        debris_group.add(debris)

        self.rebuild_layered_ship()

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

        self.angle += self.rotation_speed

        self.image = pygame.transform.rotate(
            self.original_image,
            self.angle
        )

        self.rect = self.image.get_rect(
            center=(
                int(self.x),
                int(self.y)
            )
        )

        if pygame.time.get_ticks() >= self.explode_time:
            explosion = Explosion(
                self.rect.centerx,
                self.rect.centery,
                2
            )

            explosion_group.add(explosion)

            explosion_fx.play()

            self.kill()

# --- Spaceship ---
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health, ship):
        super().__init__()
        self.image_orig = ships[ship]
        self.image = self.image_orig
        self.rect = self.image.get_rect(center=(x, y))
        self.ship_number = ship
        # Variable-geometry wing angle for red ship
        self.wing_sweep = 0
        self.wing_offset_y = -4

        # Individual layered parts for the red ship only.
        # Other ships continue using their normal single image.
        if self.ship_number == 0:
            self.ship_layers = [
                layer.copy()
                for layer in red_ship_layers
            ]

            self.ship_layer_order = red_ship_layer_order.copy()
            self.ship_parts = {
                "part_1": {
                    "layer": 0,
                    "attached": True,
                    "health": 2
                },

                "part_2": {
                    "layer": 1,
                    "attached": True,
                    "health": 2
                },

                "rear_left_wing": {
                    "layer": 2,
                    "attached": True,
                    "health": 3
                },

                "rear_right_wing": {
                    "layer": 3,
                    "attached": True,
                    "health": 3
                },

                "sweep_left_wing": {
                    "layer": 4,
                    "attached": True,
                    "health": 2
                },

                "sweep_right_wing": {
                    "layer": 5,
                    "attached": True,
                    "health": 2
                },

                "part_7": {
                    "layer": 6,
                    "attached": True,
                    "health": 3
                },

                "rocket": {
                    "layer": 7,
                    "attached": True,
                    "health": 2
                },

                "part_9": {
                    "layer": 8,
                    "attached": True,
                    "health": 2
                },

                "part_10": {
                    "layer": 9,
                    "attached": True,
                    "health": 2
                }
            }

        else:
            self.ship_layers = None
            self.ship_layer_order = None
        self.angle = 0
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
        self.last_missile_shot = pygame.time.get_ticks()
        self.missiles_remaining = 4
        self.next_missile_mount = 0
        self.last_charge_shot = pygame.time.get_ticks()
        self.charge_counter = 0
        self.charging = False
        self.charge_fired = False
        self.charge_start_y = y
        self.charge_start_x = x

    def get_missile_mounts(self):
        ship_width = self.image_orig.get_width()
        ship_height = self.image_orig.get_height()

        local_mounts = [
            # Left inside
            (-ship_width * 0.11, ship_height * -0.02),

            # Right inside
            (ship_width * 0.11, ship_height * -0.02),

            # Left outside
            (-ship_width * 0.18, ship_height * 0.02),

            # Right outside
            (ship_width * 0.18, ship_height * 0.02)
        ]

        angle_radians = math.radians(self.angle)
        cosine = math.cos(angle_radians)
        sine = math.sin(angle_radians)

        mounts = []

        for offset_x, offset_y in local_mounts:
            rotated_x = (
                    offset_x * cosine
                    + offset_y * sine
            )

            rotated_y = (
                    -offset_x * sine
                    + offset_y * cosine
            )

            mounts.append(
                (
                    self.rect.centerx + rotated_x,
                    self.rect.centery + rotated_y
                )
            )

        return mounts

    def draw_rotated_ship_part(
            self,
            surface,
            layer_image,
            pivot,
            angle,offset_y=0
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

        rotated_pivot_vector = pivot_vector.rotate(-angle)

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

    def layer_is_attached(self, layer_index):
        if self.ship_number != 0:
            return True

        for part in self.ship_parts.values():
            if part["layer"] == layer_index:
                return part["attached"]

        return True

    def rebuild_layered_ship(self):
        if self.ship_number != 0:
            return

        layered_image = pygame.Surface(
            self.image_orig.get_size(),
            pygame.SRCALPHA
        )

        for layer_index in self.ship_layer_order:

            if not self.layer_is_attached(layer_index):
                continue

            # Sprite 5 - small left wing
            if layer_index == 4:
                self.draw_rotated_ship_part(
                    layered_image,
                    self.ship_layers[layer_index],
                    (72, 47),
                    self.wing_sweep,
                    self.wing_offset_y
                )

            # Sprite 6 - small right wing
            elif layer_index == 5:
                self.draw_rotated_ship_part(
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

        self.image = layered_image

        old_center = self.rect.center

        self.rect = self.image.get_rect(
            center=old_center
        )

    def rotate(self, angle):
        self.angle += angle

        if self.ship_number == 0:
            self.rebuild_layered_ship()

        else:
            self.image = pygame.transform.rotate(
                self.image_orig,
                self.angle
            )

            self.rect = self.image.get_rect(
                center=self.rect.center
            )

    def has_part(self, part_name):
        part = self.ship_parts.get(part_name)

        if part is None:
            return True

        return part["attached"]

    def missile_mount_available(self, mount_index):
        if self.ship_number != 0:
            return True

        # Left-side missiles
        if mount_index in (0, 2):
            return self.has_part("sweep_left_wing")

        # Right-side missiles
        if mount_index in (1, 3):
            return self.has_part("sweep_right_wing")

        return True

    def get_turn_strength(self, direction):
        normal_strength = 1.0

        if self.ship_number != 0:
            return normal_strength

        if (
                direction == "left"
                and not self.has_part("sweep_left_wing")
        ):
            return 0.45

        if (
                direction == "right"
                and not self.has_part("sweep_right_wing")
        ):
            return 0.45

        return normal_strength

    def damage_part_at_point(
            self,
            hit_x,
            hit_y,
            damage,
            debris_group
    ):
        if self.ship_number != 0:
            return

        local_x = hit_x - self.rect.left
        local_y = hit_y - self.rect.top

        part_name = None

        # Small left sweep wing
        if (
                30 <= local_x <= 72
                and 28 <= local_y <= 62
        ):
            part_name = "sweep_left_wing"

        # Small right sweep wing
        elif (
                82 <= local_x <= 124
                and 28 <= local_y <= 62
        ):
            part_name = "sweep_right_wing"

        if part_name is None:
            return

        part = self.ship_parts[part_name]

        if not part["attached"]:
            return

        part["health"] -= damage

        print(
            part_name,
            "health:",
            part["health"]
        )

        if part["health"] <= 0:
            self.detach_part(
                part_name,
                debris_group
            )



    def detach_part(self, part_name, debris_group):
        if self.ship_number != 0:
            return

        part = self.ship_parts.get(part_name)

        if part is None:
            return

        if not part["attached"]:
            return

        part["attached"] = False

        layer_index = part["layer"]

        debris = ShipDebris(
            self.ship_layers[layer_index],
            self.rect.centerx,
            self.rect.centery
        )

        debris_group.add(debris)

        self.rebuild_layered_ship()

    def update(self):
        if self.ship_number == 0:
            self.rebuild_layered_ship()

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
        self.rect = self.image.get_rect(
            center=(x, y)
        )
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

            spaceship.damage_part_at_point(
                self.rect.centerx,
                self.rect.centery,
                1,
                ship_debris_group
            )

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
            spaceship.damage_part_at_point(
                self.rect.centerx,
                self.rect.centery,
                2,
                ship_debris_group
            )
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

