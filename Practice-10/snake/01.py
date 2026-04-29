import pygame
import random
import time

pygame.init()

WIDTH = 600
HEIGHT = 600


colorWHITE = (255, 255, 255)
colorGRAY = (200, 200, 200)
colorBLACK = (0, 0, 0)
colorRED = (255, 0, 0)
colorGREEN = (0, 255, 0)
colorBLUE = (0, 0, 255)
colorYELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

font_score = pygame.font.SysFont("Verdana", 18)

CELL = 30

def draw_grid():
    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            pygame.draw.rect(screen, colorGRAY, (i * CELL, j * CELL, CELL, CELL), 1)

def draw_grid_chess():
    colors = [colorWHITE, colorGRAY]

    for i in range(HEIGHT // CELL):
        for j in range(WIDTH // CELL):
            pygame.draw.rect(screen, colors[(i + j) % 2], (i * CELL, j * CELL, CELL, CELL))

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x}, {self.y}"

class Snake:
    def __init__(self):
        self.body = [Point(10, 11), Point(10, 12), Point(10, 13)]
        self.dx = 1
        self.dy = 0
        self.score = 0

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].x = self.body[i - 1].x
            self.body[i].y = self.body[i - 1].y

        self.body[0].x += self.dx
        self.body[0].y += self.dy

        # checks the right border
        if self.body[0].x < 0 or self.body[0].x >= WIDTH // CELL or self.body[0].y < 0 or self.body[0].y >= HEIGHT // CELL:
            return False
        return True
    def check_self_collision(self):
        head = self.body[0]
        for segment in self.body[1:]:
            if head.x == segment.x and head.y == segment.y:
                return True
        return False
    def draw(self):
        head = self.body[0]
        pygame.draw.rect(screen, colorRED, (head.x * CELL, head.y * CELL, CELL, CELL))
        for segment in self.body[1:]:
            pygame.draw.rect(screen, colorYELLOW, (segment.x * CELL, segment.y * CELL, CELL, CELL))

    def check_collision(self, food):
        head = self.body[0]
        if head.x == food.pos.x and head.y == food.pos.y:
            print("Got food!")
            self.body.append(Point(head.x, head.y))
            food.generate_random_pos(self)
            self.score+=1    

class Food:
    def __init__(self):
        self.pos = Point(9, 9)

    def draw(self):
        pygame.draw.rect(screen, colorGREEN, (self.pos.x * CELL, self.pos.y * CELL, CELL, CELL))

    def generate_random_pos(self, snake):
        while True:
            x = random.randint(0, WIDTH // CELL - 1)
            y = random.randint(0, HEIGHT // CELL - 1)
            check = True
            for i in snake.body:
                if i.x == x and i.y == y:
                    check = False
                    break

            if check:
                self.pos.x = x
                self.pos.y = y
                break


FPS = 5
clock = pygame.time.Clock()

food = Food()
snake = Snake()

running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if snake.dx != -1:
                    snake.dx = 1
                    snake.dy = 0
            elif event.key == pygame.K_LEFT:
                if snake.dx != 1:
                    snake.dx = -1
                    snake.dy = 0
            elif event.key == pygame.K_DOWN:
                if snake.dy != -1:
                    snake.dx = 0
                    snake.dy = 1
            elif event.key == pygame.K_UP:
                if snake.dy != 1:
                    snake.dx = 0
                    snake.dy = -1

    screen.fill(colorWHITE)

    draw_grid_chess()
    
    
    
    if not snake.move():
        running = False
        game_over = True
    else:
        if snake.check_self_collision():
            running = False
            game_over = True
        else:
            snake.check_collision(food)

    snake.draw()
    food.draw()
    image_score = font_score.render(f"Score: {snake.score}", True, colorBLACK)
    image_level = font_score.render(f"Level: {snake.score//4 + 1}", True, colorBLACK)

    image_score_rect = image_score.get_rect(topright = (WIDTH - 10, 10))
    image_level_rect = image_level.get_rect(topright = (WIDTH - 10, 30))
    
    screen.blit(image_score, image_score_rect)
    screen.blit(image_level, image_level_rect)
    
    pygame.display.flip()
    FPS = 5+snake.score // 4
    clock.tick(FPS)

font = pygame.font.SysFont("Verdana", 60)
font2 = pygame.font.SysFont("Verdana", 28)
image_game_over = font.render("Game Over", True, colorGRAY)
image_score_over = font2.render(f"Your score:{snake.score}", True, colorGRAY)
image_game_over_rect = image_game_over.get_rect(center = (WIDTH // 2, HEIGHT // 2))
image_score_over_rect = image_score_over.get_rect(center = (WIDTH // 2, HEIGHT // 2 + 50))

if game_over:
    screen.fill(colorBLUE)
    screen.blit(image_game_over, image_game_over_rect)
    screen.blit(image_score_over, image_score_over_rect)
    pygame.display.flip()
    time.sleep(3)

pygame.quit()
