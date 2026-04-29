import json
import random
import time
from pathlib import Path

import pygame

WIDTH = 600
HEIGHT = 600
CELL = 30
GRID_W = WIDTH // CELL
GRID_H = HEIGHT // CELL
FOOD_LIFETIME = 5000
POWERUP_FIELD_TIMEOUT = 8000
POWERUP_DURATION = 5000

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_RED = (120, 0, 0)
CYAN = (0, 200, 255)
PURPLE = (150, 80, 255)

SETTINGS_PATH = Path(__file__).resolve().parent / "settings.json"
ASSETS_PATH = Path(__file__).resolve().parent / "assets"
DEFAULT_SETTINGS = {
    "snake_color": [255, 0, 0],
    "grid": True,
    "sound": False,
}
COLOR_OPTIONS = [
    [255, 0, 0],
    [0, 180, 0],
    [0, 0, 255],
    [255, 165, 0],
]


def load_settings():
    if not SETTINGS_PATH.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()

    settings = DEFAULT_SETTINGS.copy()
    settings.update(data)
    return settings


def save_settings(settings):
    with SETTINGS_PATH.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def load_sound(filename):
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        return pygame.mixer.Sound(str(ASSETS_PATH / filename))
    except pygame.error:
        return None


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def as_tuple(self):
        return (self.x, self.y)


class Snake:
    def __init__(self, color):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
        self.score = 0
        self.color = tuple(color)
        self.body_color = YELLOW

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        self.body[0].x += self.dx
        self.body[0].y += self.dy

        if self.body[0].x < 0 or self.body[0].x >= GRID_W or self.body[0].y < 0 or self.body[0].y >= GRID_H:
            return False
        return True

    def check_self_collision(self):
        head = self.body[0]
        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                return True
        return False

    def draw(self, screen):
        head = self.body[0]
        pygame.draw.rect(screen, self.color, (head.x * CELL, head.y * CELL, CELL, CELL))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, self.body_color, (segment.x * CELL, segment.y * CELL, CELL, CELL))

    def grow(self, amount):
        for _ in range(amount):
            tail = self.body[-1]
            self.body.append(Point(tail.x, tail.y))

    def shrink(self, amount):
        for _ in range(amount):
            if self.body:
                self.body.pop()

    def head_tuple(self):
        return self.body[0].as_tuple()


class Food:
    def __init__(self):
        self.pos = Point(9, 9)
        self.weight = 1
        self.color = GREEN
        self.spawn_time = pygame.time.get_ticks()

    def update_params(self):
        self.weight = random.choice([1, 2, 3])
        if self.weight == 1:
            self.color = GREEN
        elif self.weight == 2:
            self.color = BLUE
        else:
            self.color = RED
        self.spawn_time = pygame.time.get_ticks()

    def draw(self, screen):
        margin = 6 - self.weight
        pygame.draw.rect(
            screen,
            self.color,
            (self.pos.x * CELL + margin, self.pos.y * CELL + margin, CELL - margin * 2, CELL - margin * 2),
        )

    def update(self, snake, blocked_positions):
        if pygame.time.get_ticks() - self.spawn_time >= FOOD_LIFETIME:
            self.generate_random_pos(snake, blocked_positions)

    def generate_random_pos(self, snake, blocked_positions):
        occupied = {segment.as_tuple() for segment in snake.body} | set(blocked_positions)
        while True:
            x = random.randint(0, GRID_W - 1)
            y = random.randint(0, GRID_H - 1)
            if (x, y) not in occupied:
                self.pos.x = x
                self.pos.y = y
                self.update_params()
                break


class PoisonFood:
    def __init__(self):
        self.pos = Point(0, 0)
        self.color = DARK_RED

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos.x * CELL + 4, self.pos.y * CELL + 4, CELL - 8, CELL - 8))

    def generate_random_pos(self, snake, blocked_positions):
        occupied = {segment.as_tuple() for segment in snake.body} | set(blocked_positions)
        while True:
            x = random.randint(0, GRID_W - 1)
            y = random.randint(0, GRID_H - 1)
            if (x, y) not in occupied:
                self.pos.x = x
                self.pos.y = y
                break


class PowerUp:
    def __init__(self, kind):
        self.kind = kind
        self.pos = Point(0, 0)
        self.spawn_time = pygame.time.get_ticks()
        self.color = {
            "speed": CYAN,
            "slow": PURPLE,
            "shield": YELLOW,
        }[kind]

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (self.pos.x * CELL + CELL // 2, self.pos.y * CELL + CELL // 2),
            CELL // 2 - 4,
        )

    def generate_random_pos(self, snake, blocked_positions):
        occupied = {segment.as_tuple() for segment in snake.body} | set(blocked_positions)
        while True:
            x = random.randint(0, GRID_W - 1)
            y = random.randint(0, GRID_H - 1)
            if (x, y) not in occupied:
                self.pos.x = x
                self.pos.y = y
                self.spawn_time = pygame.time.get_ticks()
                break


class SnakeGame:
    def __init__(self, screen, username, personal_best, settings):
        self.screen = screen
        self.username = username
        self.personal_best = personal_best
        self.settings = settings
        self.font_score = pygame.font.SysFont("Verdana", 18)
        self.font_big = pygame.font.SysFont("Verdana", 60)
        self.font_mid = pygame.font.SysFont("Verdana", 28)
        self.clock = pygame.time.Clock()
        self.snake = Snake(self.settings["snake_color"])
        self.food = Food()
        self.poison = PoisonFood()
        self.obstacles = set()
        self.powerup = None
        self.active_powerup = None
        self.active_powerup_end = 0
        self.level = 1
        self.base_fps = 5
        self.fps = 5
        self.game_over = False
        self.game_over_reason = ""
        self.sound_food = load_sound("food.wav")
        self.sound_powerup = load_sound("powerup.wav")
        self.sound_game_over = load_sound("game_over.wav")
        self.food.generate_random_pos(self.snake, self.obstacles)
        self.poison.generate_random_pos(self.snake, self.obstacles | {self.food.pos.as_tuple()})

    def play_sound(self, sound):
        if self.settings["sound"] and sound is not None:
            sound.play()

    def draw_grid(self):
        for i in range(HEIGHT // CELL):
            for j in range(WIDTH // CELL):
                pygame.draw.rect(self.screen, GRAY, (i * CELL, j * CELL, CELL, CELL), 1)

    def draw_grid_chess(self):
        colors = [WHITE, GRAY]
        for i in range(HEIGHT // CELL):
            for j in range(WIDTH // CELL):
                pygame.draw.rect(self.screen, colors[(i + j) % 2], (i * CELL, j * CELL, CELL, CELL))

    def draw_obstacles(self):
        for x, y in self.obstacles:
            pygame.draw.rect(self.screen, BLACK, (x * CELL + 3, y * CELL + 3, CELL - 6, CELL - 6))

    def current_blocked_positions(self):
        blocked = set(self.obstacles)
        if self.powerup is not None:
            blocked.add(self.powerup.pos.as_tuple())
        blocked.add(self.poison.pos.as_tuple())
        return blocked

    def spawn_powerup(self):
        if self.powerup is not None or self.active_powerup is not None:
            return
        if random.randint(1, 160) != 1:
            return

        self.powerup = PowerUp(random.choice(["speed", "slow", "shield"]))
        blocked = self.obstacles | {self.food.pos.as_tuple(), self.poison.pos.as_tuple()}
        self.powerup.generate_random_pos(self.snake, blocked)

    def update_powerup_timeout(self):
        if self.powerup is not None and pygame.time.get_ticks() - self.powerup.spawn_time >= POWERUP_FIELD_TIMEOUT:
            self.powerup = None

        if self.active_powerup in ("speed", "slow") and pygame.time.get_ticks() >= self.active_powerup_end:
            self.active_powerup = None

    def apply_powerup(self, kind):
        self.active_powerup = kind
        if kind in ("speed", "slow"):
            self.active_powerup_end = pygame.time.get_ticks() + POWERUP_DURATION
        else:
            self.active_powerup_end = 0

    def consume_shield(self):
        if self.active_powerup == "shield":
            self.active_powerup = None
            self.active_powerup_end = 0
            return True
        return False

    def update_speed(self):
        self.base_fps = 5 + (self.level - 1)
        self.fps = self.base_fps
        if self.active_powerup == "speed":
            self.fps += 3
        elif self.active_powerup == "slow":
            self.fps = max(2, self.fps - 2)

    def generate_obstacles_for_level(self):
        if self.level < 3:
            self.obstacles = set()
            return

        head = self.snake.body[0]
        safe_zone = {
            (head.x, head.y),
            (head.x + 1, head.y),
            (head.x - 1, head.y),
            (head.x, head.y + 1),
            (head.x, head.y - 1),
        }
        occupied = {segment.as_tuple() for segment in self.snake.body}
        count = min(3 + self.level, 10)
        obstacles = set()

        while len(obstacles) < count:
            x = random.randint(1, GRID_W - 2)
            y = random.randint(1, GRID_H - 2)
            if (x, y) in occupied or (x, y) in safe_zone:
                continue
            obstacles.add((x, y))

        self.obstacles = obstacles
        self.food.generate_random_pos(self.snake, self.obstacles | {self.poison.pos.as_tuple()})
        self.poison.generate_random_pos(self.snake, self.obstacles | {self.food.pos.as_tuple()})
        if self.powerup is not None:
            self.powerup.generate_random_pos(self.snake, self.obstacles | {self.food.pos.as_tuple(), self.poison.pos.as_tuple()})

    def update_level(self):
        new_level = self.snake.score // 4 + 1
        if new_level != self.level:
            self.level = new_level
            self.generate_obstacles_for_level()

    def handle_food_collisions(self):
        head = self.snake.body[0]
        if head.x == self.food.pos.x and head.y == self.food.pos.y:
            self.play_sound(self.sound_food)
            self.snake.grow(self.food.weight)
            self.snake.score += self.food.weight
            self.food.generate_random_pos(self.snake, self.obstacles | {self.poison.pos.as_tuple()})
            if self.powerup is not None:
                self.powerup.generate_random_pos(self.snake, self.obstacles | {self.food.pos.as_tuple(), self.poison.pos.as_tuple()})

        if head.x == self.poison.pos.x and head.y == self.poison.pos.y:
            self.play_sound(self.sound_game_over)
            self.snake.shrink(2)
            if len(self.snake.body) <= 1:
                self.game_over = True
                self.game_over_reason = "poison"
                return
            self.poison.generate_random_pos(self.snake, self.obstacles | {self.food.pos.as_tuple()})

        if self.powerup is not None and head.x == self.powerup.pos.x and head.y == self.powerup.pos.y:
            self.play_sound(self.sound_powerup)
            self.apply_powerup(self.powerup.kind)
            self.powerup = None

    def move_or_fail(self):
        moved = self.snake.move()
        if not moved:
            if not self.consume_shield():
                self.play_sound(self.sound_game_over)
                self.game_over = True
                self.game_over_reason = "wall"
                return
            head = self.snake.body[0]
            head.x = max(0, min(head.x, GRID_W - 1))
            head.y = max(0, min(head.y, GRID_H - 1))

        if self.snake.head_tuple() in self.obstacles:
            if not self.consume_shield():
                self.play_sound(self.sound_game_over)
                self.game_over = True
                self.game_over_reason = "obstacle"
                return

        if self.snake.check_self_collision():
            if not self.consume_shield():
                self.play_sound(self.sound_game_over)
                self.game_over = True
                self.game_over_reason = "self"
                return

    def draw_ui(self):
        image_score = self.font_score.render(f"Score: {self.snake.score}", True, BLACK)
        image_level = self.font_score.render(f"Level: {self.level}", True, BLACK)
        image_food = self.font_score.render(f"Food: {self.food.weight}", True, BLACK)
        image_best = self.font_score.render(f"Best: {self.personal_best}", True, BLACK)

        power_text = "Power: None"
        if self.active_powerup == "speed":
            left = max(0, (self.active_powerup_end - pygame.time.get_ticks()) / 1000)
            power_text = f"Power: Speed {left:.1f}s"
        elif self.active_powerup == "slow":
            left = max(0, (self.active_powerup_end - pygame.time.get_ticks()) / 1000)
            power_text = f"Power: Slow {left:.1f}s"
        elif self.active_powerup == "shield":
            power_text = "Power: Shield"

        image_power = self.font_score.render(power_text, True, BLACK)
        self.screen.blit(image_score, image_score.get_rect(topright=(WIDTH - 10, 10)))
        self.screen.blit(image_level, image_level.get_rect(topright=(WIDTH - 10, 30)))
        self.screen.blit(image_food, image_food.get_rect(topright=(WIDTH - 10, 50)))
        self.screen.blit(image_best, image_best.get_rect(topright=(WIDTH - 10, 70)))
        self.screen.blit(image_power, image_power.get_rect(topright=(WIDTH - 10, 90)))

    def draw_scene(self):
        self.screen.fill(WHITE)
        self.draw_grid_chess()
        if self.settings["grid"]:
            self.draw_grid()
        self.draw_obstacles()
        self.food.draw(self.screen)
        self.poison.draw(self.screen)
        if self.powerup is not None:
            self.powerup.draw(self.screen)
        self.snake.draw(self.screen)
        self.draw_ui()

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_RIGHT and self.snake.dx != -1:
            self.snake.dx = 1
            self.snake.dy = 0
        elif event.key == pygame.K_LEFT and self.snake.dx != 1:
            self.snake.dx = -1
            self.snake.dy = 0
        elif event.key == pygame.K_DOWN and self.snake.dy != -1:
            self.snake.dx = 0
            self.snake.dy = 1
        elif event.key == pygame.K_UP and self.snake.dy != 1:
            self.snake.dx = 0
            self.snake.dy = -1

    def run(self):
        self.generate_obstacles_for_level()
        running = True
        while running and not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return {"quit": True}
                self.handle_input(event)

            self.food.update(self.snake, self.obstacles | {self.poison.pos.as_tuple()})
            self.update_powerup_timeout()
            self.spawn_powerup()
            self.update_speed()
            self.move_or_fail()
            if self.game_over:
                break

            self.handle_food_collisions()
            self.update_level()
            self.draw_scene()
            pygame.display.flip()
            self.clock.tick(self.fps)

        time.sleep(0.5)
        return {
            "quit": False,
            "score": self.snake.score,
            "level": self.level,
            "personal_best": max(self.personal_best, self.snake.score),
        }
