import math
from datetime import datetime
from pathlib import Path

import pygame

WIDTH = 800
HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (255, 255, 255)

BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
GRAY    = (160, 160, 160)
RED     = (255, 0, 0)
GREEN   = (0, 180, 0)
BLUE    = (0, 0, 255)
YELLOW  = (255, 255, 0)
ORANGE  = (255, 165, 0)
PURPLE  = (128, 0, 128)
PINK    = (255, 105, 180)
BROWN   = (139, 69, 19)

BRUSH_SIZE_MAP = {
    pygame.K_F1: 2,
    pygame.K_F2: 5,
    pygame.K_F3: 10,
}

BRUSH_NAME_MAP = {
    2: "SMALL",
    5: "MEDIUM",
    10: "LARGE",
}

COLOR_MAP = {
    pygame.K_0: BLACK,
    pygame.K_1: RED,
    pygame.K_2: GREEN,
    pygame.K_3: BLUE,
    pygame.K_4: YELLOW,
    pygame.K_5: ORANGE,
    pygame.K_6: PURPLE,
    pygame.K_7: PINK,
    pygame.K_8: BROWN,
    pygame.K_9: GRAY,
}

COLOR_NAME_MAP = {
    pygame.K_0: "BLACK",
    pygame.K_1: "RED",
    pygame.K_2: "GREEN",
    pygame.K_3: "BLUE",
    pygame.K_4: "YELLOW",
    pygame.K_5: "ORANGE",
    pygame.K_6: "PURPLE",
    pygame.K_7: "PINK",
    pygame.K_8: "BROWN",
    pygame.K_9: "GRAY",
}

TOOL_NAME_MAP = {
    "pen": "PENCIL",
    "line": "LINE",
    "rect": "RECT",
    "circle": "CIRCLE",
    "square": "SQUARE",
    "right_triangle": "R-TRIANGLE",
    "equilateral_triangle": "E-TRIANGLE",
    "rhombus": "RHOMBUS",
    "fill": "FILL",
    "text": "TEXT",
    "eraser": "ERASER",
}

def calculate_rect(start, end):
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    return pygame.Rect(left, top, width, height)

def draw_circle_by_points(surface, color, start, end, width=0):
    cx, cy = start
    ex, ey = end

    radius = int(math.hypot(ex - cx, ey - cy))

    if radius > 0:
        pygame.draw.circle(surface, color, (cx, cy), radius, width)

def calculate_square(start, end):
    x1, y1 = start
    x2, y2 = end

    side = min(abs(x2 - x1), abs(y2 - y1))
    left = x1 if x2 >= x1 else x1 - side
    top = y1 if y2 >= y1 else y1 - side

    return pygame.Rect(left, top, side, side)

def get_right_triangle_points(start, end):
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]

def get_equilateral_triangle_points(start, end):
    x1, y1 = start
    x2, y2 = end

    side = max(1, abs(x2 - x1))
    height = int(side * math.sqrt(3) / 2)
    direction_x = 1 if x2 >= x1 else -1
    direction_y = 1 if y2 >= y1 else -1

    base_left = (x1, y1)
    base_right = (x1 + direction_x * side, y1)
    top_point = (int(x1 + direction_x * side / 2), int(y1 + direction_y * height))

    return [base_left, base_right, top_point]

def get_rhombus_points(start, end):
    rect = calculate_rect(start, end)
    center_x = rect.left + rect.width / 2
    center_y = rect.top + rect.height / 2

    return [
        (int(center_x), rect.top),
        (rect.right, int(center_y)),
        (int(center_x), rect.bottom),
        (rect.left, int(center_y)),
    ]

def draw_polygon(surface, color, points, width):
    if len(points) >= 3:
        pygame.draw.polygon(surface, color, points, width)

def draw_shape(surface, tool, color, start_pos, current_pos, thickness):
    if tool == "line":
        pygame.draw.line(surface, color, start_pos, current_pos, thickness)
    elif tool == "rect":
        rect = calculate_rect(start_pos, current_pos)
        pygame.draw.rect(surface, color, rect, thickness)
    elif tool == "circle":
        draw_circle_by_points(surface, color, start_pos, current_pos, thickness)
    elif tool == "square":
        rect = calculate_square(start_pos, current_pos)
        pygame.draw.rect(surface, color, rect, thickness)
    elif tool == "right_triangle":
        draw_polygon(surface, color, get_right_triangle_points(start_pos, current_pos), thickness)
    elif tool == "equilateral_triangle":
        draw_polygon(surface, color, get_equilateral_triangle_points(start_pos, current_pos), thickness)
    elif tool == "rhombus":
        draw_polygon(surface, color, get_rhombus_points(start_pos, current_pos), thickness)

def flood_fill(surface, pos, fill_color):
    x, y = pos
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return

    target_color = surface.get_at((x, y))
    replacement_color = pygame.Color(*fill_color)

    if target_color == replacement_color:
        return

    stack = [(x, y)]
    while stack:
        px, py = stack.pop()

        if px < 0 or px >= WIDTH or py < 0 or py >= HEIGHT:
            continue
        if surface.get_at((px, py)) != target_color:
            continue

        surface.set_at((px, py), replacement_color)
        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))

def save_canvas(surface):
    file_dir = Path(__file__).resolve().parent
    filename = datetime.now().strftime("canvas_%Y%m%d_%H%M%S.png")
    file_path = file_dir / filename
    pygame.image.save(surface, str(file_path))
    print(f"Saved {file_path.name}")
