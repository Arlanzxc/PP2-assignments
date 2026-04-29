import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
DARK_GRAY = (90, 90, 90)
BLUE = (55, 110, 185)
RED = (190, 70, 70)

class Button:
    def __init__(self, rect, text, action, color=GRAY):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.color = color

    def draw(self, surface, font):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        fill_color = DARK_GRAY if is_hovered else self.color
        pygame.draw.rect(surface, fill_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)

        text_image = font.render(self.text, True, WHITE if is_hovered else BLACK)
        text_rect = text_image.get_rect(center=self.rect.center)
        surface.blit(text_image, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

def draw_center_text(surface, text, font, color, center):
    image = font.render(text, True, color)
    rect = image.get_rect(center=center)
    surface.blit(image, rect)

def draw_left_text(surface, text, font, color, pos):
    image = font.render(text, True, color)
    surface.blit(image, pos)

def draw_panel(surface, rect, fill_color=(240, 240, 240)):
    panel_rect = pygame.Rect(rect)
    pygame.draw.rect(surface, fill_color, panel_rect, border_radius=10)
    pygame.draw.rect(surface, BLACK, panel_rect, 2, border_radius=10)

def make_menu_buttons():
    return [
        Button((110, 180, 180, 44), "Play", "play", BLUE),
        Button((110, 240, 180, 44), "Leaderboard", "leaderboard", BLUE),
        Button((110, 300, 180, 44), "Settings", "settings", BLUE),
        Button((110, 360, 180, 44), "Quit", "quit", RED),
    ]
