import pygame

from db import fetch_personal_best, fetch_top_scores, initialize_database, save_game_result
from game import BLACK, GRAY, HEIGHT, WHITE, WIDTH, COLOR_OPTIONS, SnakeGame, load_settings, save_settings
from game import load_sound

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS4 Snake")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Verdana", 34)
font_ui = pygame.font.SysFont("Verdana", 20)
font_small = pygame.font.SysFont("Verdana", 16)

settings = load_settings()
db_ready = initialize_database()
sound_click = load_sound("powerup.wav")

username = ""
state = "menu"
last_result = None
leaderboard_rows = []
draft_settings = settings.copy()


class Button:
    def __init__(self, rect, text, action, color=(220, 220, 220)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        text_image = font_ui.render(self.text, True, BLACK)
        surface.blit(text_image, text_image.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def play_ui_sound():
    if settings["sound"] and sound_click is not None:
        sound_click.play()


menu_buttons = [
    Button((210, 220, 180, 44), "Play", "play", (180, 230, 180)),
    Button((210, 280, 180, 44), "Leaderboard", "leaderboard", (180, 210, 240)),
    Button((210, 340, 180, 44), "Settings", "settings", (240, 220, 180)),
    Button((210, 400, 180, 44), "Quit", "quit", (240, 180, 180)),
]
back_button = Button((225, 520, 150, 42), "Back", "back", (240, 220, 180))
save_back_button = Button((210, 500, 180, 42), "Save & Back", "save_back", (180, 230, 180))
retry_button = Button((140, 430, 140, 42), "Retry", "retry", (180, 230, 180))
menu_button = Button((320, 430, 140, 42), "Main Menu", "menu", (240, 220, 180))


def draw_center(text, y, font, color=BLACK):
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=(WIDTH // 2, y)))


def draw_menu():
    screen.fill(WHITE)
    draw_center("TSIS4 Snake", 110, font_title)
    draw_center("Username", 165, font_ui)
    pygame.draw.rect(screen, GRAY, (150, 185, 300, 34), border_radius=8)
    pygame.draw.rect(screen, BLACK, (150, 185, 300, 34), 2, border_radius=8)
    typed = font_ui.render(username or "_", True, BLACK)
    screen.blit(typed, (160, 191))
    db_text = "Database: Connected" if db_ready else "Database: Not available"
    draw_center(db_text, 485, font_small)
    for button in menu_buttons:
        button.draw(screen)


def draw_leaderboard():
    screen.fill(WHITE)
    draw_center("Leaderboard", 55, font_title)
    headers = ["#", "Username", "Score", "Level", "Date"]
    positions = [20, 60, 220, 310, 390]
    for header, x in zip(headers, positions):
        screen.blit(font_small.render(header, True, BLACK), (x, 105))

    if leaderboard_rows:
        for index, row in enumerate(leaderboard_rows, start=1):
            y = 140 + (index - 1) * 34
            date_text = row[3].strftime("%Y-%m-%d") if hasattr(row[3], "strftime") else str(row[3])[:10]
            values = [str(index), row[0], str(row[1]), str(row[2]), date_text]
            for value, x in zip(values, positions):
                screen.blit(font_small.render(value, True, BLACK), (x, y))
    else:
        draw_center("No leaderboard data", 280, font_ui)

    back_button.draw(screen)


def draw_settings():
    screen.fill(WHITE)
    draw_center("Settings", 70, font_title)

    grid_text = f"Grid: {'ON' if draft_settings['grid'] else 'OFF'}"
    sound_text = f"Sound: {'ON' if draft_settings['sound'] else 'OFF'}"
    color_text = f"Snake Color: {tuple(draft_settings['snake_color'])}"
    texts = [grid_text, sound_text, color_text]
    for index, text in enumerate(texts):
        screen.blit(font_ui.render(text, True, BLACK), (120, 170 + index * 80))

    hint = "G - grid, S - sound, C - color"
    screen.blit(font_small.render(hint, True, BLACK), (165, 430))

    pygame.draw.rect(screen, tuple(draft_settings["snake_color"]), (380, 330, 60, 30))
    pygame.draw.rect(screen, BLACK, (380, 330, 60, 30), 2)
    save_back_button.draw(screen)


def draw_game_over():
    screen.fill(WHITE)
    draw_center("Game Over", 100, font_title)
    draw_center(f"Score: {last_result['score']}", 190, font_ui)
    draw_center(f"Level: {last_result['level']}", 225, font_ui)
    draw_center(f"Personal Best: {last_result['personal_best']}", 260, font_ui)
    retry_button.draw(screen)
    menu_button.draw(screen)


def cycle_color():
    current = draft_settings["snake_color"]
    index = COLOR_OPTIONS.index(current) if current in COLOR_OPTIONS else 0
    draft_settings["snake_color"] = COLOR_OPTIONS[(index + 1) % len(COLOR_OPTIONS)]


def run_game_session():
    global last_result, leaderboard_rows

    personal_best = fetch_personal_best(username) if db_ready else 0
    game = SnakeGame(screen, username, personal_best, settings)
    result = game.run()
    if result["quit"]:
        return "menu"

    if db_ready:
        save_game_result(username, result["score"], result["level"])
        result["personal_best"] = max(result["personal_best"], fetch_personal_best(username))
        leaderboard_rows = fetch_top_scores()

    last_result = result
    return "game_over"


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode and event.unicode.isprintable() and len(username) < 20:
                    username += event.unicode

            for button in menu_buttons:
                if button.is_clicked(event):
                    if button.action == "play" and username.strip():
                        play_ui_sound()
                        state = run_game_session()
                    elif button.action == "leaderboard":
                        play_ui_sound()
                        leaderboard_rows = fetch_top_scores() if db_ready else []
                        state = "leaderboard"
                    elif button.action == "settings":
                        play_ui_sound()
                        draft_settings = settings.copy()
                        state = "settings"
                    elif button.action == "quit":
                        play_ui_sound()
                        running = False

        elif state == "leaderboard":
            if back_button.is_clicked(event):
                play_ui_sound()
                state = "menu"

        elif state == "settings":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    draft_settings["grid"] = not draft_settings["grid"]
                elif event.key == pygame.K_s:
                    draft_settings["sound"] = not draft_settings["sound"]
                elif event.key == pygame.K_c:
                    cycle_color()

            if save_back_button.is_clicked(event):
                play_ui_sound()
                settings = draft_settings.copy()
                save_settings(settings)
                state = "menu"

        elif state == "game_over":
            if retry_button.is_clicked(event) and username.strip():
                play_ui_sound()
                state = run_game_session()
            elif menu_button.is_clicked(event):
                play_ui_sound()
                state = "menu"

    if state == "menu":
        draw_menu()
    elif state == "leaderboard":
        draw_leaderboard()
    elif state == "settings":
        draw_settings()
    elif state == "game_over" and last_result is not None:
        draw_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
