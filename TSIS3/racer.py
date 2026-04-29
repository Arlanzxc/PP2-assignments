import random
from pathlib import Path

import pygame

WIDTH = 400
HEIGHT = 600
FPS = 60
COINS_TO_SPEED_UP = 5
ROAD_DISTANCE = {
    "easy": 2800,
    "medium": 3600,
    "hard": 4500,
}
DIFFICULTY_SPEED = {
    "easy": 5,
    "medium": 7,
    "hard": 9,
}
CAR_COLORS = {
    "red": (220, 70, 70),
    "blue": (70, 120, 220),
    "green": (70, 180, 90),
}

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 40, 40)
YELLOW = (255, 220, 40)
GREEN = (40, 180, 40)
BLUE = (40, 100, 220)
ORANGE = (240, 140, 20)
GRAY = (180, 180, 180)

ASSET_DIR = Path(__file__).resolve().parent / "assets"

def load_image(name):
    return pygame.image.load(str(ASSET_DIR / name))

def load_sound(name):
    return pygame.mixer.Sound(str(ASSET_DIR / name))

class Player(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 5
        self.vertical_speed = 3

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        if keys[pygame.K_UP]:
            self.rect.move_ip(0, -self.vertical_speed)
        if keys[pygame.K_DOWN]:
            self.rect.move_ip(0, self.vertical_speed)
        else:
            self.rect.move_ip(0, self.vertical_speed // 2)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def current_lane(self, lanes):
        distances = [abs(self.rect.centerx - lane) for lane in lanes]
        return distances.index(min(distances))

class TrafficCar(pygame.sprite.Sprite):
    def __init__(self, image, lane_x, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midtop=(lane_x, -self.image.get_height()))
        self.speed = speed

    def move(self):
        self.rect.move_ip(0, self.speed)

class Coin(pygame.sprite.Sprite):
    def __init__(self, image, lane_x):
        super().__init__()
        self.base_image = image
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.weight = 1
        self.value = 10
        self.spawn(lane_x)

    def spawn(self, lane_x):
        self.weight = random.choice([1, 2, 3])
        size = 30 + self.weight * 10
        self.value = self.weight * 10
        self.image = pygame.transform.scale(self.base_image, (size, size))
        self.rect = self.image.get_rect(midtop=(lane_x, -random.randint(80, 180)))

    def move(self, speed):
        self.rect.move_ip(0, speed)

class RoadObject(pygame.sprite.Sprite):
    def __init__(self, lane_x, top, kind, color, width=64, height=36, speed=0):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midtop=(lane_x, top))
        self.base_speed = speed
        self.direction = random.choice([-1, 1])
        self.fill_image(color)

    def fill_image(self, color):
        if self.kind in ("barrier", "moving_barrier"):
            pygame.draw.rect(self.image, color, (0, 0, self.rect.w, self.rect.h), border_radius=6)
            pygame.draw.rect(self.image, BLACK, (0, 0, self.rect.w, self.rect.h), 2, border_radius=6)
        elif self.kind in ("oil",):
            pygame.draw.ellipse(self.image, color, (0, 8, self.rect.w, self.rect.h - 8))
        elif self.kind in ("pothole",):
            pygame.draw.ellipse(self.image, color, (5, 5, self.rect.w - 10, self.rect.h - 10))
            pygame.draw.ellipse(self.image, BLACK, (5, 5, self.rect.w - 10, self.rect.h - 10), 2)
        elif self.kind == "speed_bump":
            pygame.draw.rect(self.image, color, (0, 10, self.rect.w, self.rect.h - 10), border_radius=8)
        elif self.kind == "nitro_strip":
            pygame.draw.rect(self.image, color, (0, 0, self.rect.w, self.rect.h), border_radius=8)
            pygame.draw.line(self.image, WHITE, (10, 5), (self.rect.w - 10, self.rect.h - 5), 4)

    def move(self, road_speed, lanes):
        self.rect.move_ip(0, road_speed + self.base_speed)

        if self.kind == "moving_barrier":
            self.rect.move_ip(self.direction * 2, 0)
            if self.rect.centerx < lanes[0] - 30 or self.rect.centerx > lanes[-1] + 30:
                self.direction *= -1

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, lane_x, top, kind):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((34, 34), pygame.SRCALPHA)
        self.rect = self.image.get_rect(midtop=(lane_x, top))
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 4500
        self.draw_icon()

    def draw_icon(self):
        color_map = {
            "nitro": BLUE,
            "shield": GREEN,
            "repair": ORANGE,
        }
        pygame.draw.circle(self.image, color_map[self.kind], (17, 17), 16)
        pygame.draw.circle(self.image, WHITE, (17, 17), 16, 2)
        label = self.kind[0].upper()
        font = pygame.font.SysFont("Verdana", 18)
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=(17, 17))
        self.image.blit(text, text_rect)

    def move(self, speed):
        self.rect.move_ip(0, speed)

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time >= self.lifetime

class RacerGame:
    def __init__(self, screen, settings, username):
        self.screen = screen
        self.settings = settings
        self.username = username or "Player"
        self.clock = pygame.time.Clock()

        self.lanes = [80, 200, 320]
        self.base_speed = DIFFICULTY_SPEED[self.settings["difficulty"]]
        self.road_speed = self.base_speed
        self.target_distance = ROAD_DISTANCE[self.settings["difficulty"]]
        self.background_y = 0
        self.background_y2 = -HEIGHT
        self.distance = 0.0
        self.coin_score = 0
        self.power_bonus = 0
        self.coins_collected = 0
        self.finish_reason = "crash"
        self.active_power = None
        self.active_power_end = 0
        self.shield_ready = False
        self.nitro_strip_end = 0

        self.last_traffic_spawn = 0
        self.last_hazard_spawn = 0
        self.last_event_spawn = 0
        self.last_powerup_spawn = 0

        self.image_background = load_image("AnimatedStreet.png")
        self.image_enemy = load_image("Enemy.png")
        self.image_coin = load_image("Tenge.png")
        self.sound_crash = load_sound("crash.wav")
        self.sound_coin = load_sound("money.wav")
        self.sound_bip = load_sound("bip.wav")

        player_image = load_image("Player.png").convert_alpha()
        tint_surface = pygame.Surface(player_image.get_size(), pygame.SRCALPHA)
        tint_surface.fill(CAR_COLORS[self.settings["car_color"]] + (255,))
        player_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.player = Player(player_image)

        self.traffic = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.font_small = pygame.font.SysFont("Verdana", 18)
        self.font_title = pygame.font.SysFont("Verdana", 30)

        self.spawn_coin(force=True)

    def play_sound(self, sound):
        if self.settings["sound"]:
            sound.play()

    def score(self):
        return int(self.coin_score + self.distance // 10 + self.power_bonus)

    def progress_level(self):
        return int(self.distance // 700)

    def road_speed_with_effects(self):
        speed = self.base_speed + self.progress_level()

        if self.active_power == "nitro" and pygame.time.get_ticks() < self.active_power_end:
            speed += 4
        if pygame.time.get_ticks() < self.nitro_strip_end:
            speed += 3
        return speed

    def choose_lane(self, avoid_player=True):
        player_lane = self.player.current_lane(self.lanes)
        choices = self.lanes[:]
        if avoid_player and len(choices) > 1:
            choices = [lane for index, lane in enumerate(self.lanes) if index != player_lane]
        return random.choice(choices)

    def safe_to_spawn(self, lane_x):
        player_lane_x = self.lanes[self.player.current_lane(self.lanes)]
        return abs(lane_x - player_lane_x) > 15

    def spawn_coin(self, force=False):
        if self.coins and not force:
            return

        lane_x = self.choose_lane(avoid_player=False)
        coin = Coin(self.image_coin, lane_x)
        self.coins.add(coin)

    def spawn_traffic(self):
        now = pygame.time.get_ticks()
        interval = max(650, 1500 - self.progress_level() * 120)
        if now - self.last_traffic_spawn < interval:
            return

        lane_x = self.choose_lane(avoid_player=True)
        if not self.safe_to_spawn(lane_x):
            return

        car = TrafficCar(self.image_enemy, lane_x, self.base_speed + 1 + self.progress_level())
        self.traffic.add(car)
        self.last_traffic_spawn = now

    def spawn_lane_hazards(self):
        now = pygame.time.get_ticks()
        interval = max(900, 1800 - self.progress_level() * 100)
        if now - self.last_hazard_spawn < interval:
            return

        safe_lane = random.choice(self.lanes)
        for lane_x in self.lanes:
            if lane_x == safe_lane:
                continue
            kind = random.choice(["barrier", "oil", "pothole"])
            color = {
                "barrier": RED,
                "oil": BLACK,
                "pothole": GRAY,
            }[kind]
            hazard = RoadObject(lane_x, -60, kind, color)
            self.hazards.add(hazard)

        self.last_hazard_spawn = now

    def spawn_dynamic_event(self):
        now = pygame.time.get_ticks()
        if now - self.last_event_spawn < 2600:
            return

        lane_x = random.choice(self.lanes)
        event_kind = random.choice(["moving_barrier", "speed_bump", "nitro_strip"])
        if event_kind == "moving_barrier":
            obj = RoadObject(lane_x, -80, event_kind, YELLOW, width=72, height=22)
        elif event_kind == "speed_bump":
            obj = RoadObject(lane_x, -40, event_kind, ORANGE, width=68, height=18)
        else:
            obj = RoadObject(lane_x, -50, event_kind, BLUE, width=68, height=20)

        self.hazards.add(obj)
        self.last_event_spawn = now

    def spawn_powerup(self):
        now = pygame.time.get_ticks()
        if self.active_power is not None or self.powerups:
            return
        if now - self.last_powerup_spawn < 7000:
            return

        lane_x = self.choose_lane(avoid_player=True)
        if not self.safe_to_spawn(lane_x):
            return

        powerup = PowerUp(lane_x, -40, random.choice(["nitro", "shield", "repair"]))
        self.powerups.add(powerup)
        self.last_powerup_spawn = now

    def apply_powerup(self, powerup):
        if powerup.kind == "nitro":
            self.active_power = "nitro"
            self.active_power_end = pygame.time.get_ticks() + 4000
            self.power_bonus += 40
        elif powerup.kind == "shield":
            self.active_power = "shield"
            self.active_power_end = 0
            self.shield_ready = True
            self.power_bonus += 30
        elif powerup.kind == "repair":
            self.clear_nearest_hazard()
            self.power_bonus += 25

        self.play_sound(self.sound_bip)

    def clear_nearest_hazard(self):
        candidates = list(self.hazards) + list(self.traffic)
        if not candidates:
            return
        nearest = min(candidates, key=lambda obj: abs(obj.rect.centery - self.player.rect.centery))
        nearest.kill()

    def consume_protection(self):
        if self.active_power == "shield" and self.shield_ready:
            self.shield_ready = False
            self.active_power = None
            return True
        return False

    def update_power_state(self):
        if self.active_power == "nitro" and pygame.time.get_ticks() >= self.active_power_end:
            self.active_power = None

    def handle_collisions(self):
        traffic_hit = pygame.sprite.spritecollideany(self.player, self.traffic)
        if traffic_hit:
            if self.consume_protection():
                traffic_hit.kill()
            else:
                self.finish_reason = "traffic"
                self.play_sound(self.sound_crash)
                return False

        for hazard in list(self.hazards):
            if self.player.rect.colliderect(hazard.rect):
                if hazard.kind in ("barrier", "moving_barrier"):
                    if self.consume_protection():
                        hazard.kill()
                    else:
                        self.finish_reason = "obstacle"
                        self.play_sound(self.sound_crash)
                        return False
                elif hazard.kind in ("oil", "pothole", "speed_bump"):
                    self.distance = max(0, self.distance - 20)
                    self.power_bonus = max(0, self.power_bonus - 5)
                    hazard.kill()
                elif hazard.kind == "nitro_strip":
                    self.nitro_strip_end = pygame.time.get_ticks() + 2500
                    hazard.kill()

        for coin in list(self.coins):
            if self.player.rect.colliderect(coin.rect):
                self.play_sound(self.sound_coin)
                self.coin_score += coin.value
                self.coins_collected += 1
                if self.coins_collected % COINS_TO_SPEED_UP == 0:
                    self.base_speed += 1
                coin.kill()

        for powerup in list(self.powerups):
            if self.player.rect.colliderect(powerup.rect):
                self.apply_powerup(powerup)
                powerup.kill()

        return True

    def update_objects(self):
        self.road_speed = self.road_speed_with_effects()
        self.distance += self.road_speed / 6

        self.background_y += self.road_speed
        self.background_y2 += self.road_speed
        if self.background_y >= HEIGHT:
            self.background_y = -HEIGHT
        if self.background_y2 >= HEIGHT:
            self.background_y2 = -HEIGHT

        self.player.move()

        for car in list(self.traffic):
            car.move()
            car.rect.move_ip(0, self.road_speed - self.base_speed)
            if car.rect.top > HEIGHT:
                car.kill()

        for coin in list(self.coins):
            coin.move(self.road_speed)
            if coin.rect.top > HEIGHT:
                coin.kill()

        for hazard in list(self.hazards):
            hazard.move(self.road_speed, self.lanes)
            if hazard.rect.top > HEIGHT:
                hazard.kill()

        for powerup in list(self.powerups):
            powerup.move(self.road_speed)
            if powerup.rect.top > HEIGHT or powerup.is_expired():
                powerup.kill()

        self.update_power_state()
        self.spawn_traffic()
        self.spawn_lane_hazards()
        self.spawn_dynamic_event()
        self.spawn_powerup()
        self.spawn_coin()

    def draw_objects(self):
        self.screen.blit(self.image_background, (0, self.background_y))
        self.screen.blit(self.image_background, (0, self.background_y2))

        for lane_x in self.lanes:
            pygame.draw.line(self.screen, WHITE, (lane_x, 0), (lane_x, HEIGHT), 1)

        for group in (self.coins, self.hazards, self.traffic, self.powerups):
            for obj in group:
                self.screen.blit(obj.image, obj.rect)

        self.screen.blit(self.player.image, self.player.rect)

    def draw_ui(self):
        remaining = max(0, int(self.target_distance - self.distance))
        power_text = "None"
        if self.active_power == "nitro":
            left = max(0, (self.active_power_end - pygame.time.get_ticks()) / 1000)
            power_text = f"Nitro {left:.1f}s"
        elif self.active_power == "shield":
            power_text = "Shield until hit"

        info_lines = [
            f"User: {self.username}",
            f"Score: {self.score()}",
            f"Coins: {self.coins_collected}",
            f"Distance: {int(self.distance)} / {self.target_distance}",
            f"Remaining: {remaining}",
            f"Power: {power_text}",
        ]

        panel = pygame.Rect(10, 10, 210, 132)
        pygame.draw.rect(self.screen, (245, 245, 245), panel, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, panel, 2, border_radius=8)

        for index, line in enumerate(info_lines):
            image = self.font_small.render(line, True, BLACK)
            self.screen.blit(image, (18, 18 + index * 20))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return {"quit": True}

            self.update_objects()
            if not self.handle_collisions():
                running = False

            if self.distance >= self.target_distance:
                self.finish_reason = "finish"
                self.power_bonus += 100
                running = False

            self.draw_objects()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)

        return {
            "quit": False,
            "username": self.username,
            "score": self.score(),
            "distance": int(self.distance),
            "coins": self.coins_collected,
            "reason": self.finish_reason,
        }

def run_game(screen, settings, username):
    game = RacerGame(screen, settings, username)
    return game.run()
