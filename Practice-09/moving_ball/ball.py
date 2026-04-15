import pygame


class Ball:
    def __init__(self, screen_width, screen_height):
        #initialize ball parameters
        self.radius = 25
        self.step = 20
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius)
        self.color = (243, 50, 51)

    def move(self, dx, dy):
        # compute new coordinates
        new_x = self.x + dx
        new_y = self.y + dy
        # handle border collisions
        if self.radius <= new_x and new_x <= self.screen_width-self.radius:
            self.x = new_x
        if self.radius <= new_y and new_y <= self.screen_height-self.radius:
            self.y = new_y

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
