import pygame

from persistence import add_leaderboard_entry, load_leaderboard, load_settings, save_settings
from racer import HEIGHT, WIDTH, run_game
from ui import BLACK, BLUE, Button, GRAY, RED, WHITE, draw_center_text, draw_left_text, draw_panel, make_menu_buttons

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Racer")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Verdana", 32)
font_ui = pygame.font.SysFont("Verdana", 20)
font_small = pygame.font.SysFont("Verdana", 16)

settings = load_settings()
leaderboard = load_leaderboard()
username_value = ""
last_username = "Player"
last_result = None
state = "menu"

menu_buttons = make_menu_buttons()
username_buttons = [
    Button((70, 330, 120, 42), "Start", "start", BLUE),
    Button((210, 330, 120, 42), "Back", "back", RED),
]
leaderboard_buttons = [Button((130, 520, 140, 42), "Back", "back", RED)]
game_over_buttons = [
    Button((70, 430, 120, 42), "Retry", "retry", BLUE),
    Button((210, 430, 120, 42), "Main Menu", "menu", RED),
]
settings_buttons = [
    Button((65, 180, 270, 42), "Sound", "sound", BLUE),
    Button((65, 250, 270, 42), "Car Color", "car_color", BLUE),
    Button((65, 320, 270, 42), "Difficulty", "difficulty", BLUE),
    Button((130, 520, 140, 42), "Back", "back", RED),
]

def cycle_setting(name, values):
    current_value = settings[name]
    current_index = values.index(current_value)
    settings[name] = values[(current_index + 1) % len(values)]
    save_settings(settings)

def draw_menu():
    screen.fill((235, 235, 235))
    draw_center_text(screen, "TSIS3 Racer", font_title, BLACK, (WIDTH // 2, 100))
    draw_center_text(screen, "Advanced Driving, Leaderboard & Power-Ups", font_small, BLACK, (WIDTH // 2, 132))
    for button in menu_buttons:
        button.draw(screen, font_ui)

def draw_username():
    screen.fill((235, 235, 235))
    draw_center_text(screen, "Enter Username", font_title, BLACK, (WIDTH // 2, 120))
    draw_panel(screen, (45, 180, 310, 95))
    draw_left_text(screen, "Name:", font_ui, BLACK, (65, 200))
    name_image = font_ui.render(username_value or "_", True, BLACK)
    screen.blit(name_image, (135, 200))
    hint = font_small.render("Press Enter to start or use the Start button", True, BLACK)
    screen.blit(hint, (58, 242))
    for button in username_buttons:
        button.draw(screen, font_ui)

def draw_leaderboard_screen():
    screen.fill((235, 235, 235))
    draw_center_text(screen, "Leaderboard", font_title, BLACK, (WIDTH // 2, 55))
    draw_panel(screen, (20, 95, 360, 400))
    headers = ["#", "Name", "Score", "Distance"]
    header_positions = [35, 80, 210, 305]
    for header, x in zip(headers, header_positions):
        draw_left_text(screen, header, font_ui, BLACK, (x, 110))

    for index, entry in enumerate(leaderboard[:10], start=1):
        y = 140 + (index - 1) * 32
        draw_left_text(screen, str(index), font_small, BLACK, (35, y))
        draw_left_text(screen, entry["name"][:11], font_small, BLACK, (80, y))
        draw_left_text(screen, str(entry["score"]), font_small, BLACK, (210, y))
        draw_left_text(screen, str(entry["distance"]), font_small, BLACK, (305, y))

    if not leaderboard:
        draw_center_text(screen, "No scores yet", font_ui, BLACK, (WIDTH // 2, 250))

    for button in leaderboard_buttons:
        button.draw(screen, font_ui)

def draw_settings_screen():
    screen.fill((235, 235, 235))
    draw_center_text(screen, "Settings", font_title, BLACK, (WIDTH // 2, 90))
    draw_panel(screen, (35, 140, 330, 250))

    labels = [
        f"Sound: {'ON' if settings['sound'] else 'OFF'}",
        f"Car Color: {settings['car_color'].upper()}",
        f"Difficulty: {settings['difficulty'].upper()}",
    ]
    for index, label in enumerate(labels):
        draw_left_text(screen, label, font_ui, BLACK, (65, 155 + index * 70))

    for button in settings_buttons:
        button.text = {
            "sound": "Toggle Sound",
            "car_color": "Change Car Color",
            "difficulty": "Change Difficulty",
            "back": "Back",
        }[button.action]
        button.draw(screen, font_ui)

def draw_game_over():
    screen.fill((235, 235, 235))
    title = "Finished" if last_result["reason"] == "finish" else "Game Over"
    draw_center_text(screen, title, font_title, BLACK, (WIDTH // 2, 90))
    draw_panel(screen, (50, 150, 300, 210))
    draw_left_text(screen, f"Name: {last_result['username']}", font_ui, BLACK, (75, 180))
    draw_left_text(screen, f"Score: {last_result['score']}", font_ui, BLACK, (75, 220))
    draw_left_text(screen, f"Distance: {last_result['distance']}", font_ui, BLACK, (75, 260))
    draw_left_text(screen, f"Coins: {last_result['coins']}", font_ui, BLACK, (75, 300))
    for button in game_over_buttons:
        button.draw(screen, font_ui)

def run_and_store_game():
    global last_result, leaderboard, state

    result = run_game(screen, settings, last_username)
    if result.get("quit"):
        state = "menu"
        return

    last_result = result
    leaderboard = add_leaderboard_entry({
        "name": result["username"],
        "score": result["score"],
        "distance": result["distance"],
    })
    state = "game_over"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif state == "menu":
            for button in menu_buttons:
                if button.is_clicked(event):
                    if button.action == "play":
                        username_value = last_username if last_username != "Player" else ""
                        state = "username"
                    elif button.action == "leaderboard":
                        leaderboard = load_leaderboard()
                        state = "leaderboard"
                    elif button.action == "settings":
                        state = "settings"
                    elif button.action == "quit":
                        running = False

        elif state == "username":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username_value.strip():
                    last_username = username_value.strip()
                    run_and_store_game()
                elif event.key == pygame.K_BACKSPACE:
                    username_value = username_value[:-1]
                elif event.key == pygame.K_ESCAPE:
                    state = "menu"
                elif event.unicode and event.unicode.isprintable() and len(username_value) < 14:
                    username_value += event.unicode

            for button in username_buttons:
                if button.is_clicked(event):
                    if button.action == "start" and username_value.strip():
                        last_username = username_value.strip()
                        run_and_store_game()
                    elif button.action == "back":
                        state = "menu"

        elif state == "leaderboard":
            for button in leaderboard_buttons:
                if button.is_clicked(event):
                    state = "menu"

        elif state == "settings":
            for button in settings_buttons:
                if button.is_clicked(event):
                    if button.action == "sound":
                        settings["sound"] = not settings["sound"]
                        save_settings(settings)
                    elif button.action == "car_color":
                        cycle_setting("car_color", ["red", "blue", "green"])
                    elif button.action == "difficulty":
                        cycle_setting("difficulty", ["easy", "medium", "hard"])
                    elif button.action == "back":
                        state = "menu"

        elif state == "game_over":
            for button in game_over_buttons:
                if button.is_clicked(event):
                    if button.action == "retry":
                        run_and_store_game()
                    elif button.action == "menu":
                        state = "menu"

    if state == "menu":
        draw_menu()
    elif state == "username":
        draw_username()
    elif state == "leaderboard":
        draw_leaderboard_screen()
    elif state == "settings":
        draw_settings_screen()
    elif state == "game_over" and last_result is not None:
        draw_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
