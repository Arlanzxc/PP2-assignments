import pygame

from tools import BACKGROUND_COLOR, BLACK, BRUSH_NAME_MAP, BRUSH_SIZE_MAP, COLOR_MAP, COLOR_NAME_MAP, FPS, GRAY, HEIGHT, TOOL_NAME_MAP, WHITE, WIDTH, draw_shape, flood_fill, save_canvas

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font_ui = pygame.font.SysFont("Verdana", 20)
font_small = pygame.font.SysFont("Verdana", 16)
font_text = pygame.font.SysFont("Verdana", 24)

tool = "pen"
current_color = BLACK
current_color_name = "BLACK"
thickness = 5

drawing = False
start_pos = None
prev_pos = None
current_pos = None

text_position = None
text_value = ""
text_active = False

base_layer = pygame.Surface((WIDTH, HEIGHT))
base_layer.fill(BACKGROUND_COLOR)

print("--- Instructions ---")
print("W - Pencil")
print("L - Line")
print("R - Rectangle")
print("C - Circle")
print("S - Square")
print("T - Right triangle")
print("Q - Equilateral triangle")
print("H - Rhombus")
print("F - Fill")
print("X - Text")
print("E - Eraser")
print("F1 - 2 px")
print("F2 - 5 px")
print("F3 - 10 px")
print("CTRL+S - Save canvas")
print("SPACE - Clear canvas")
print("------ Colors ------")
print("0 - Black")
print("1 - Red")
print("2 - Green")
print("3 - Blue")
print("4 - Yellow")
print("5 - Orange")
print("6 - Purple")
print("7 - Pink")
print("8 - Brown")
print("9 - Gray")
print("-------------------")

def get_draw_color():
    if tool == "eraser":
        return BACKGROUND_COLOR
    return current_color

def draw_ui():
    panel_rect = pygame.Rect(WIDTH - 240, 10, 220, 150)
    pygame.draw.rect(screen, (235, 235, 235), panel_rect)
    pygame.draw.rect(screen, BLACK, panel_rect, 2)

    tool_text = font_ui.render(f"Tool: {TOOL_NAME_MAP[tool]}", True, BLACK)
    screen.blit(tool_text, (WIDTH - 225, 20))

    thick_text = font_ui.render(f"Brush: {BRUSH_NAME_MAP[thickness]}", True, BLACK)
    screen.blit(thick_text, (WIDTH - 225, 50))

    px_text = font_small.render("F1:2  F2:5  F3:10", True, BLACK)
    screen.blit(px_text, (WIDTH - 225, 75))

    color_text = font_ui.render(f"Color: {current_color_name}", True, BLACK)
    screen.blit(color_text, (WIDTH - 225, 100))

    outer_rect = pygame.Rect(WIDTH - 70, 108, 40, 40)
    inner_rect = pygame.Rect(WIDTH - 65, 113, 30, 30)
    pygame.draw.rect(screen, GRAY, outer_rect)
    pygame.draw.rect(screen, current_color, inner_rect)

def finalize_shape():
    if start_pos and current_pos:
        draw_shape(base_layer, tool, get_draw_color(), start_pos, current_pos, thickness)

def draw_shape_preview():
    if start_pos and current_pos:
        draw_shape(screen, tool, get_draw_color(), start_pos, current_pos, thickness)

def draw_text_preview():
    if not text_active or text_position is None:
        return

    text_surface = font_text.render(text_value, True, current_color)
    screen.blit(text_surface, text_position)

    if pygame.time.get_ticks() % 1000 < 500:
        cursor_x = text_position[0] + text_surface.get_width() + 2
        cursor_rect = pygame.Rect(cursor_x, text_position[1], 2, font_text.get_height())
        pygame.draw.rect(screen, current_color, cursor_rect)

def commit_text():
    global text_active, text_position, text_value

    if text_active and text_value:
        text_surface = font_text.render(text_value, True, current_color)
        base_layer.blit(text_surface, text_position)

    text_active = False
    text_position = None
    text_value = ""

def cancel_text():
    global text_active, text_position, text_value

    text_active = False
    text_position = None
    text_value = ""

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and text_active:
                cancel_text()
                continue

            if event.key == pygame.K_RETURN and text_active:
                commit_text()
                continue

            if text_active:
                if event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]
                elif event.unicode and event.unicode.isprintable():
                    text_value += event.unicode
                continue

            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                save_canvas(base_layer)
            elif event.key == pygame.K_w:
                tool = "pen"
            elif event.key == pygame.K_l:
                tool = "line"
            elif event.key == pygame.K_r:
                tool = "rect"
            elif event.key == pygame.K_c:
                tool = "circle"
            elif event.key == pygame.K_s:
                tool = "square"
            elif event.key == pygame.K_t:
                tool = "right_triangle"
            elif event.key == pygame.K_q:
                tool = "equilateral_triangle"
            elif event.key == pygame.K_h:
                tool = "rhombus"
            elif event.key == pygame.K_f:
                tool = "fill"
            elif event.key == pygame.K_x:
                tool = "text"
            elif event.key == pygame.K_e:
                tool = "eraser"
            elif event.key == pygame.K_SPACE:
                base_layer.fill(BACKGROUND_COLOR)
                cancel_text()
            elif event.key in BRUSH_SIZE_MAP:
                thickness = BRUSH_SIZE_MAP[event.key]
            elif event.key in COLOR_MAP:
                current_color = COLOR_MAP[event.key]
                current_color_name = COLOR_NAME_MAP[event.key]

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                current_pos = event.pos

                if tool == "fill":
                    flood_fill(base_layer, event.pos, current_color)
                elif tool == "text":
                    text_position = event.pos
                    text_value = ""
                    text_active = True
                else:
                    drawing = True
                    start_pos = event.pos
                    prev_pos = event.pos

                    if tool in ("pen", "eraser"):
                        pygame.draw.circle(base_layer, get_draw_color(), event.pos, max(1, thickness // 2))

        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                current_pos = event.pos

                if tool in ("pen", "eraser"):
                    pygame.draw.line(base_layer, get_draw_color(), prev_pos, current_pos, thickness)
                    prev_pos = current_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                current_pos = event.pos

                if tool in ("line", "rect", "circle", "square", "right_triangle", "equilateral_triangle", "rhombus"):
                    finalize_shape()

                drawing = False
                start_pos = None
                prev_pos = None
                current_pos = None

    screen.blit(base_layer, (0, 0))

    if drawing and tool in ("line", "rect", "circle", "square", "right_triangle", "equilateral_triangle", "rhombus"):
        draw_shape_preview()

    draw_text_preview()
    draw_ui()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
