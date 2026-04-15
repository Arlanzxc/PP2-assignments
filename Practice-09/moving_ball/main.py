import pygame
from ball import Ball

pygame.init()
# initialize pygame
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Moving Ball")
clock = pygame.time.Clock()
ball = Ball(width, height)
running = True
while running:
    for event in pygame.event.get():
        # stops the program when quit
        if event.type == pygame.QUIT:
            running = False
    # handle key events
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        ball.move(0, -ball.step)
    if keys[pygame.K_DOWN]:
        ball.move(0, ball.step)
    if keys[pygame.K_LEFT]:
        ball.move(-ball.step, 0)
    if keys[pygame.K_RIGHT]:
        ball.move(ball.step, 0)
    # render ball
    screen.fill((255, 255, 255))
    ball.draw(screen)
    # update display
    pygame.display.flip()
    clock.tick(60)
pygame.quit()