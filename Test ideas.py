import math
import random
import pygame


pygame.init()

WIDTH = 1100
HEIGHT = 750
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Spaceship Effects Test")

clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)

BLACK = (4, 6, 16)
WHITE = (255, 255, 255)
RED = (220, 35, 45)
DARK_RED = (90, 12, 20)
LIGHT_RED = (255, 95, 95)
BLUE = (45, 170, 255)
CYAN = (90, 235, 255)
ORANGE = (255, 125, 30)
YELLOW = (255, 235, 80)
GRAY = (110, 120, 140)


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def rotate_point(point, angle):
    x, y = point
    cosine = math.cos(angle)
    sine = math.sin(angle)

    rotated_x = x * cosine - y * sine
    rotated_y = x * sine + y * cosine

    return rotated_x, rotated_y


def transform_points(points, position, angle=0):
    transformed = []

    for point in points:
        x, y = rotate_point(point, angle)
        transformed.append((position.x + x, position.y + y))

    return transformed


def draw_glowing_circle(surface, position, radius, color):
    radius = int(radius)

    if radius <= 0:
        return

    glow_surface = pygame.Surface(
        (radius * 6, radius * 6),
        pygame.SRCALPHA
    )

    center = radius * 3

    for layer in range(5, 0, -1):
        layer_radius = radius + layer * radius * 0.7
        alpha = int(18 + 14 * (6 - layer))

        pygame.draw.circle(
            glow_surface,
            (*color, alpha),
            (center, center),
            int(layer_radius)
        )

    pygame.draw.circle(
        glow_surface,
        (*color, 255),
        (center, center),
        radius
    )

    surface.blit(
        glow_surface,
        (position[0] - center, position[1] - center)
    )


class Star:
    def __init__(self):
        self.reset(random.randint(0, WIDTH))

    def reset(self, x=None):
        if x is None:
            x = WIDTH + random.randint(0, 100)

        self.position = pygame.Vector2(
            x,
            random.randint(0, HEIGHT)
        )

        self.depth = random.uniform(0.25, 1.0)
        self.speed = 40 + self.depth * 170
        self.size = max(1, int(self.depth * 3))

    def update(self, dt):
        self.position.x -= self.speed * dt

        if self.position.x < -10:
            self.reset()

    def draw(self, surface):
        brightness = int(100 + self.depth * 155)
        color = (brightness, brightness, brightness)

        pygame.draw.circle(
            surface,
            color,
            (int(self.position.x), int(self.position.y)),
            self.size
        )


class Particle:
    def __init__(
        self,
        position,
        velocity,
        color,
        radius,
        lifetime,
        drag=0.96
    ):
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.color = color
        self.radius = radius
        self.lifetime = lifetime
        self.maximum_lifetime = lifetime
        self.drag = drag

    def update(self, dt):
        self.position += self.velocity * dt
        self.velocity *= self.drag ** (dt * 60)
        self.lifetime -= dt
        self.radius *= 0.985 ** (dt * 60)

    def draw(self, surface):
        if self.lifetime <= 0 or self.radius <= 0.5:
            return

        alpha_ratio = self.lifetime / self.maximum_lifetime
        alpha = int(255 * alpha_ratio)

        radius = max(1, int(self.radius))
        size = radius * 6

        particle_surface = pygame.Surface(
            (size, size),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            particle_surface,
            (*self.color, alpha),
            (size // 2, size // 2),
            radius
        )

        surface.blit(
            particle_surface,
            (
                self.position.x - size // 2,
                self.position.y - size // 2
            )
        )

    @property
    def dead(self):
        return self.lifetime <= 0 or self.radius <= 0.5


class Laser:
    def __init__(self, position):
        self.position = pygame.Vector2(position)
        self.speed = 950
        self.length = 42
        self.lifetime = 1.5

    def update(self, dt):
        self.position.x += self.speed * dt
        self.lifetime -= dt

    def draw(self, surface):
        start = self.position
        end = pygame.Vector2(
            self.position.x + self.length,
            self.position.y
        )

        glow_surface = pygame.Surface(
            (self.length + 30, 24),
            pygame.SRCALPHA
        )

        pygame.draw.line(
            glow_surface,
            (20, 125, 255, 55),
            (4, 12),
            (self.length + 4, 12),
            18
        )

        pygame.draw.line(
            glow_surface,
            (60, 220, 255, 130),
            (4, 12),
            (self.length + 4, 12),
            9
        )

        pygame.draw.line(
            glow_surface,
            (255, 255, 255, 255),
            (4, 12),
            (self.length + 4, 12),
            3
        )

        surface.blit(
            glow_surface,
            (start.x - 4, start.y - 12)
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (int(end.x), int(end.y)),
            2
        )

    @property
    def dead(self):
        return self.lifetime <= 0 or self.position.x > WIDTH + 100


class ChargeShot:
    def __init__(self, position, charge_amount):
        self.position = pygame.Vector2(position)
        self.charge_amount = charge_amount

        self.radius = 18 + charge_amount * 24
        self.speed = 650 + charge_amount * 250
        self.lifetime = 3.0

        self.tail_timer = 0
        self.tail_positions = []

    def update(self, dt, particles):
        self.position.x += self.speed * dt
        self.lifetime -= dt

        self.tail_timer -= dt

        if self.tail_timer <= 0:
            self.tail_timer = 0.018

            self.tail_positions.insert(
                0,
                pygame.Vector2(
                    self.position.x - self.radius,
                    self.position.y
                )
            )

            if len(self.tail_positions) > 10:
                self.tail_positions.pop()

        for _ in range(2):
            particles.append(
                Particle(
                    (
                        self.position.x - self.radius,
                        self.position.y + random.uniform(
                            -self.radius * 0.5,
                            self.radius * 0.5
                        )
                    ),
                    (
                        random.uniform(-120, -40),
                        random.uniform(-45, 45)
                    ),
                    random.choice([BLUE, CYAN, WHITE]),
                    random.uniform(1.5, 4),
                    random.uniform(0.15, 0.35)
                )
            )

    def draw(self, surface):
        for index, tail_position in enumerate(self.tail_positions):
            size_ratio = 1 - index / len(self.tail_positions)
            tail_radius = self.radius * size_ratio * 0.75

            if tail_radius > 1:
                draw_glowing_circle(
                    surface,
                    (
                        int(tail_position.x),
                        int(tail_position.y)
                    ),
                    int(tail_radius),
                    CYAN
                )

        glow_surface = pygame.Surface(
            (
                int(self.radius * 7),
                int(self.radius * 7)
            ),
            pygame.SRCALPHA
        )

        center = glow_surface.get_width() // 2

        pygame.draw.circle(
            glow_surface,
            (25, 100, 255, 35),
            (center, center),
            int(self.radius * 2.8)
        )

        pygame.draw.circle(
            glow_surface,
            (35, 175, 255, 75),
            (center, center),
            int(self.radius * 2)
        )

        pygame.draw.circle(
            glow_surface,
            (70, 225, 255, 150),
            (center, center),
            int(self.radius * 1.35)
        )

        pygame.draw.circle(
            glow_surface,
            (180, 250, 255, 255),
            (center, center),
            int(self.radius)
        )

        pygame.draw.circle(
            glow_surface,
            WHITE,
            (
                center + int(self.radius * 0.25),
                center - int(self.radius * 0.25)
            ),
            max(3, int(self.radius * 0.42))
        )

        surface.blit(
            glow_surface,
            (
                self.position.x - center,
                self.position.y - center
            )
        )

    @property
    def dead(self):
        return self.lifetime <= 0 or self.position.x > WIDTH + 200


class Missile:
    def __init__(self, position):
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(400, 0)
        self.maximum_speed = 760
        self.acceleration = 500
        self.lifetime = 4.0
        self.smoke_timer = 0

    def update(self, dt, particles):
        self.velocity.x += self.acceleration * dt
        self.velocity.x = min(self.velocity.x, self.maximum_speed)

        self.position += self.velocity * dt
        self.lifetime -= dt

        self.smoke_timer -= dt

        if self.smoke_timer <= 0:
            self.smoke_timer = 0.025

            particles.append(
                Particle(
                    (
                        self.position.x - 18,
                        self.position.y
                    ),
                    (
                        random.uniform(-130, -60),
                        random.uniform(-30, 30)
                    ),
                    random.choice([
                        (135, 140, 150),
                        (90, 100, 115),
                        (170, 175, 185)
                    ]),
                    random.uniform(4, 8),
                    random.uniform(0.4, 0.8)
                )
            )

            particles.append(
                Particle(
                    (
                        self.position.x - 16,
                        self.position.y
                    ),
                    (
                        random.uniform(-220, -130),
                        random.uniform(-18, 18)
                    ),
                    random.choice([ORANGE, YELLOW, LIGHT_RED]),
                    random.uniform(2, 4),
                    random.uniform(0.15, 0.3)
                )
            )

    def draw(self, surface):
        x = self.position.x
        y = self.position.y

        body = [
            (x - 13, y - 5),
            (x + 8, y - 5),
            (x + 17, y),
            (x + 8, y + 5),
            (x - 13, y + 5)
        ]

        top_fin = [
            (x - 10, y - 5),
            (x - 15, y - 12),
            (x - 3, y - 5)
        ]

        bottom_fin = [
            (x - 10, y + 5),
            (x - 15, y + 12),
            (x - 3, y + 5)
        ]

        pygame.draw.polygon(surface, (200, 205, 215), body)
        pygame.draw.polygon(surface, RED, top_fin)
        pygame.draw.polygon(surface, RED, bottom_fin)

        pygame.draw.line(
            surface,
            WHITE,
            (x - 7, y - 3),
            (x + 8, y - 3),
            2
        )

        draw_glowing_circle(
            surface,
            (int(x - 15), int(y)),
            3,
            ORANGE
        )

    @property
    def dead(self):
        return self.lifetime <= 0 or self.position.x > WIDTH + 100


class Explosion:
    def __init__(self, position, particles):
        for _ in range(55):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(80, 430)

            velocity = pygame.Vector2(
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )

            color = random.choice([
                WHITE,
                YELLOW,
                ORANGE,
                LIGHT_RED,
                RED
            ])

            particles.append(
                Particle(
                    position,
                    velocity,
                    color,
                    random.uniform(2, 7),
                    random.uniform(0.35, 1.0),
                    drag=0.93
                )
            )


class Ship:
    def __init__(self):
        self.position = pygame.Vector2(260, HEIGHT // 2)
        self.velocity = pygame.Vector2()
        self.speed = 420

        self.laser_cooldown = 0
        self.missile_cooldown = 0
        self.engine_timer = 0

        self.charging = False
        self.charge_amount = 0
        self.maximum_charge = 1.8

        self.angle = 0
        self.engine_power = 0.5

    def update(self, dt, keys, particles):
        direction = pygame.Vector2()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        target_velocity = direction * self.speed
        self.velocity = self.velocity.lerp(target_velocity, 0.12)

        self.position += self.velocity * dt

        self.position.x = clamp(self.position.x, 100, WIDTH - 120)
        self.position.y = clamp(self.position.y, 80, HEIGHT - 80)

        target_angle = direction.y * 0.12
        self.angle += (target_angle - self.angle) * 0.12

        self.engine_power = 0.6 + self.velocity.length() / self.speed * 0.7

        if self.charging:
            self.charge_amount += dt
            self.charge_amount = min(
                self.charge_amount,
                self.maximum_charge
            )

            charge_ratio = self.charge_amount / self.maximum_charge

            instability = math.sin(
                pygame.time.get_ticks() * 0.035
            )

            self.angle += instability * charge_ratio * 0.012

        self.laser_cooldown -= dt
        self.missile_cooldown -= dt
        self.engine_timer -= dt

        if self.engine_timer <= 0:
            self.engine_timer = 0.018
            self.create_engine_particles(particles)

    def create_engine_particles(self, particles):
        engine_positions = [
            pygame.Vector2(-45, -18),
            pygame.Vector2(-49, 18)
        ]

        for offset in engine_positions:
            rotated = offset.rotate_rad(self.angle)
            origin = self.position + rotated

            velocity = pygame.Vector2(
                random.uniform(-330, -190) * self.engine_power,
                random.uniform(-35, 35)
            )

            particles.append(
                Particle(
                    origin,
                    velocity,
                    random.choice([BLUE, CYAN, WHITE]),
                    random.uniform(2, 5),
                    random.uniform(0.15, 0.34)
                )
            )

            if random.random() < 0.35:
                particles.append(
                    Particle(
                        origin,
                        (
                            random.uniform(-220, -120),
                            random.uniform(-40, 40)
                        ),
                        ORANGE,
                        random.uniform(1, 3),
                        random.uniform(0.1, 0.22)
                    )
                )

    def fire_lasers(self, lasers):
        if self.laser_cooldown > 0:
            return

        self.laser_cooldown = 0.12

        lasers.append(
            Laser((self.position.x + 60, self.position.y - 18))
        )

        lasers.append(
            Laser((self.position.x + 60, self.position.y + 18))
        )

    def fire_missile(self, missiles):
        if self.missile_cooldown > 0:
            return

        self.missile_cooldown = 0.65

        launch_y = random.choice([-29, 29])

        missiles.append(
            Missile(
                (
                    self.position.x + 20,
                    self.position.y + launch_y
                )
            )
        )

    def start_charging(self):
        self.charging = True

    def release_charge_shot(self, charge_shots):
        if not self.charging:
            return

        minimum_charge = 0.15

        if self.charge_amount >= minimum_charge:
            charge_ratio = self.charge_amount / self.maximum_charge

            charge_shots.append(
                ChargeShot(
                    (
                        self.position.x + 75,
                        self.position.y
                    ),
                    charge_ratio
                )
            )

        self.charging = False
        self.charge_amount = 0

    def draw_engine_glow(self, surface):
        pulse = math.sin(pygame.time.get_ticks() * 0.025) * 3

        engine_positions = [
            pygame.Vector2(-47, -18),
            pygame.Vector2(-51, 18)
        ]

        for offset in engine_positions:
            position = self.position + offset.rotate_rad(self.angle)

            draw_glowing_circle(
                surface,
                (int(position.x), int(position.y)),
                6 + pulse,
                BLUE
            )

            flame_length = random.randint(20, 42)

            flame_points = [
                (-46, -23),
                (-46 - flame_length, -18),
                (-46, -13)
            ]

            if offset.y > 0:
                flame_points = [
                    (-50, 13),
                    (-50 - flame_length, 18),
                    (-50, 23)
                ]

            transformed = transform_points(
                flame_points,
                self.position,
                self.angle
            )

            flame_surface = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            pygame.draw.polygon(
                flame_surface,
                (40, 130, 255, 80),
                transformed
            )

            surface.blit(flame_surface, (0, 0))

    def draw_charge_effect(self, surface):
        if not self.charging:
            return

        charge_ratio = self.charge_amount / self.maximum_charge

        pulse = math.sin(
            pygame.time.get_ticks() * 0.025
        )

        radius = 7 + charge_ratio * 22 + pulse * 2

        charge_position = pygame.Vector2(
            self.position.x + 76,
            self.position.y
        )

        for _ in range(4):
            angle = random.uniform(0, math.tau)
            distance = random.uniform(radius + 5, radius + 18)

            spark_position = (
                charge_position.x + math.cos(angle) * distance,
                charge_position.y + math.sin(angle) * distance
            )

            pygame.draw.line(
                surface,
                random.choice([BLUE, CYAN, WHITE]),
                spark_position,
                charge_position,
                random.randint(1, 2)
            )

        draw_glowing_circle(
            surface,
            (
                int(charge_position.x),
                int(charge_position.y)
            ),
            max(3, int(radius)),
            CYAN
        )

        pygame.draw.circle(
            surface,
            WHITE,
            (
                int(charge_position.x),
                int(charge_position.y)
            ),
            max(2, int(radius * 0.38))
        )

    def draw(self, surface):
        self.draw_engine_glow(surface)

        position = self.position

        outer_wings = [
            (-12, -46),
            (2, -72),
            (21, -79),
            (16, -54),
            (32, -43),
            (18, -38),

            (18, 38),
            (32, 43),
            (16, 54),
            (21, 79),
            (2, 72),
            (-12, 46)
        ]

        transformed_outer_wings = transform_points(
            outer_wings,
            position,
            self.angle
        )

        pygame.draw.polygon(
            surface,
            DARK_RED,
            transformed_outer_wings
        )

        pygame.draw.polygon(
            surface,
            LIGHT_RED,
            transformed_outer_wings,
            3
        )

        wing_shape = [
            (-28, -17),
            (-6, -50),
            (20, -57),
            (10, -22),
            (48, -10),
            (60, 0),
            (48, 10),
            (10, 22),
            (20, 57),
            (-6, 50),
            (-28, 17),
            (-48, 27),
            (-42, 0),
            (-48, -27)
        ]

        transformed_wings = transform_points(
            wing_shape,
            position,
            self.angle
        )

        pygame.draw.polygon(
            surface,
            DARK_RED,
            transformed_wings
        )

        pygame.draw.polygon(
            surface,
            RED,
            transformed_wings,
            3
        )

        body_shape = [
            (-40, -16),
            (-8, -25),
            (40, -12),
            (62, 0),
            (40, 12),
            (-8, 25),
            (-40, 16)
        ]

        transformed_body = transform_points(
            body_shape,
            position,
            self.angle
        )

        pygame.draw.polygon(
            surface,
            RED,
            transformed_body
        )

        inner_body = [
            (-28, -10),
            (2, -16),
            (43, -7),
            (54, 0),
            (43, 7),
            (2, 16),
            (-28, 10)
        ]

        pygame.draw.polygon(
            surface,
            LIGHT_RED,
            transform_points(
                inner_body,
                position,
                self.angle
            )
        )

        cockpit_shape = [
            (-4, -13),
            (21, -8),
            (35, 0),
            (21, 8),
            (-4, 13),
            (-14, 0)
        ]

        cockpit_points = transform_points(
            cockpit_shape,
            position,
            self.angle
        )

        pygame.draw.polygon(
            surface,
            (20, 70, 110),
            cockpit_points
        )

        pygame.draw.polygon(
            surface,
            CYAN,
            cockpit_points,
            2
        )

        highlight_shape = [
            (0, -11),
            (20, -7),
            (29, -2),
            (5, -5)
        ]

        pygame.draw.polygon(
            surface,
            (160, 245, 255),
            transform_points(
                highlight_shape,
                position,
                self.angle
            )
        )

        panel_lines = [
            ((-28, -14), (-10, -22)),
            ((-28, 14), (-10, 22)),
            ((8, -20), (22, -44)),
            ((8, 20), (22, 44)),
            ((32, -10), (45, -7)),
            ((32, 10), (45, 7))
        ]

        for start, end in panel_lines:
            start_point = transform_points(
                [start],
                position,
                self.angle
            )[0]

            end_point = transform_points(
                [end],
                position,
                self.angle
            )[0]

            pygame.draw.line(
                surface,
                DARK_RED,
                start_point,
                end_point,
                3
            )

        gun_positions = [
            pygame.Vector2(48, -18),
            pygame.Vector2(48, 18)
        ]

        for gun_position in gun_positions:
            gun_position = position + gun_position.rotate_rad(self.angle)

            pygame.draw.circle(
                surface,
                GRAY,
                (int(gun_position.x), int(gun_position.y)),
                5
            )

            draw_glowing_circle(
                surface,
                (int(gun_position.x + 4), int(gun_position.y)),
                2,
                CYAN
            )

        center_light = position + pygame.Vector2(-19, 0).rotate_rad(self.angle)

        draw_glowing_circle(
            surface,
            (int(center_light.x), int(center_light.y)),
            3,
            RED
        )

        self.draw_charge_effect(surface)


stars = [Star() for _ in range(150)]
particles = []
lasers = []
missiles = []
charge_shots = []

ship = Ship()

running = True

while running:
    dt = clock.tick(FPS) / 1000
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_x:
                Explosion(
                    (
                        random.randint(WIDTH // 2, WIDTH - 100),
                        random.randint(100, HEIGHT - 100)
                    ),
                    particles
                )

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_c:
                ship.release_charge_shot(charge_shots)

    ship.update(dt, keys, particles)

    if keys[pygame.K_SPACE]:
        ship.fire_lasers(lasers)

    if keys[pygame.K_m]:
        ship.fire_missile(missiles)

    for star in stars:
        star.update(dt)

    for laser in lasers:
        laser.update(dt)

    for missile in missiles:
        missile.update(dt, particles)

    for charge_shot in charge_shots:
        charge_shot.update(dt, particles)

    for particle in particles:
        particle.update(dt)

    lasers = [laser for laser in lasers if not laser.dead]
    missiles = [missile for missile in missiles if not missile.dead]

    charge_shots = [
        charge_shot
        for charge_shot in charge_shots
        if not charge_shot.dead
    ]

    particles = [particle for particle in particles if not particle.dead]

    screen.fill(BLACK)

    for star in stars:
        star.draw(screen)

    for particle in particles:
        particle.draw(screen)

    for missile in missiles:
        missile.draw(screen)

    for laser in lasers:
        laser.draw(screen)

    for charge_shot in charge_shots:
        charge_shot.draw(screen)

    ship.draw(screen)

    instructions = [
        "WASD / Arrow Keys: Move",
        "SPACE: Fire twin lasers",
        "M: Fire missiles",
        "Hold C: Charge shot",
        "Release C: Fire charge shot",
        "X: Test procedural explosion",
        "ESC: Quit"
    ]

    y = 18

    for instruction in instructions:
        text = font.render(instruction, True, (190, 205, 225))
        screen.blit(text, (18, y))
        y += 25

    counter_text = font.render(
        f"Particles: {len(particles)}   "
        f"Lasers: {len(lasers)}   "
        f"Missiles: {len(missiles)}",
        True,
        (120, 150, 180)
    )

    screen.blit(counter_text, (18, HEIGHT - 35))

    pygame.display.flip()

pygame.quit()