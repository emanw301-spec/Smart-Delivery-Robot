import heapq
import itertools
import math
import pygame

# Smart Delivery Robot — CF321 Fundamentals of AI
# Install: python -m pip install pygame
# Run: python main.py
# Controls: left-click wall toggle; S then click = move start; G then click = move goal;
# SPACE = find path/start robot; R = reset; C = clear obstacles; ESC = quit.

ROWS, COLS = 15, 20
CELL = 42
PANEL_W, TOP_H, BOTTOM_H = 300, 76, 38
WIDTH, HEIGHT = COLS * CELL + PANEL_W, TOP_H + ROWS * CELL + BOTTOM_H
FPS, ROBOT_STEP_MS = 60, 150

START, GOAL = (0, 0), (14, 19)
OBSTACLES = {
    *((r, 5) for r in range(1, 11) if r != 4),
    *((r, 10) for r in range(4, 14) if r != 9),
    *((r, 15) for r in range(0, 10) if r != 6),
    (3, 2), (3, 3), (8, 7), (8, 8), (11, 12), (12, 12),
}
OBSTACLES.discard(START)
OBSTACLES.discard(GOAL)

BG = (18, 24, 35)
PANEL = (27, 35, 49)
GRID = (205, 214, 226)
FREE = (245, 247, 250)
OBSTACLE = (54, 61, 72)
EXPLORED = (255, 211, 107)
PATH = (65, 190, 145)
START_C = (42, 132, 214)
GOAL_C = (238, 82, 91)
ROBOT_C = (130, 95, 230)
WHITE = (245, 248, 255)
MUTED = (165, 177, 195)
ACCENT = (77, 166, 255)
BUTTON = (48, 62, 82)
BUTTON_HOVER = (65, 83, 108)
SUCCESS = (76, 210, 145)
WARNING = (255, 190, 80)

pygame.init()
pygame.display.set_caption("Smart Delivery Robot | A* Search")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("segoeui", 18)
small = pygame.font.SysFont("segoeui", 14)
tiny = pygame.font.SysFont("segoeui", 12)
title_font = pygame.font.SysFont("segoeui", 25, bold=True)
big_font = pygame.font.SysFont("segoeui", 22, bold=True)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(cell):
    r, c = cell
    candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
    return [p for p in candidates if 0 <= p[0] < ROWS and 0 <= p[1] < COLS and p not in OBSTACLES]


def astar(start, goal):
    tie = itertools.count()
    frontier = [(manhattan(start, goal), next(tie), start)]
    came_from, g_score, closed = {}, {start: 0}, set()
    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in closed:
            continue
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path, closed | {goal}
        closed.add(current)
        for nxt in neighbors(current):
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(nxt, math.inf):
                came_from[nxt] = current
                g_score[nxt] = tentative_g
                heapq.heappush(frontier, (tentative_g + manhattan(nxt, goal), next(tie), nxt))
    return [], closed


path, explored = [], set()
robot_index, running_robot, last_step = 0, False, 0
status, mode, total_cost = "Ready — press FIND PATH", "obstacle", None


def reset_search():
    global path, explored, robot_index, running_robot, status, total_cost
    path, explored = [], set()
    robot_index, running_robot, total_cost = 0, False, None
    status = "Map changed — find a new path"


def find_path():
    global path, explored, robot_index, running_robot, status, total_cost
    OBSTACLES.discard(START)
    OBSTACLES.discard(GOAL)
    path, explored = astar(START, GOAL)
    robot_index = 0
    running_robot = bool(path)
    total_cost = len(path) - 1 if path else None
    status = "Robot is delivering..." if path else "No route found — edit obstacles"


def cell_rect(cell):
    r, c = cell
    return pygame.Rect(c * CELL, TOP_H + r * CELL, CELL, CELL)


def cell_from_mouse(pos):
    x, y = pos
    if 0 <= x < COLS * CELL and TOP_H <= y < TOP_H + ROWS * CELL:
        return ((y - TOP_H) // CELL, x // CELL)
    return None


def draw_text(text, x, y, color=WHITE, f=font):
    screen.blit(f.render(text, True, color), (x, y))


def draw_button(label, rect, active=False):
    color = ACCENT if active else (BUTTON_HOVER if rect.collidepoint(pygame.mouse.get_pos()) else BUTTON)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (85, 103, 129), rect, width=1, border_radius=8)
    screen.blit(font.render(label, True, WHITE), font.render(label, True, WHITE).get_rect(center=rect.center))


def draw_header():
    pygame.draw.rect(screen, BG, (0, 0, WIDTH, TOP_H))
    draw_text("SMART DELIVERY ROBOT", 20, 12, WHITE, title_font)
    draw_text("A* pathfinding • obstacle avoidance • live simulation", 22, 47, MUTED, small)


def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            cell = (r, c)
            rect = cell_rect(cell)
            color = FREE
            if cell in OBSTACLES:
                color = OBSTACLE
            elif cell in explored:
                color = EXPLORED
            if cell in path:
                color = PATH
            if cell == START:
                color = START_C
            if cell == GOAL:
                color = GOAL_C
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID, rect, width=1)
    for cell, label in ((START, "S"), (GOAL, "G")):
        txt = big_font.render(label, True, WHITE)
        screen.blit(txt, txt.get_rect(center=cell_rect(cell).center))
    if path:
        rect = cell_rect(path[min(robot_index, len(path) - 1)]).inflate(-10, -10)
        pygame.draw.ellipse(screen, ROBOT_C, rect)
        pygame.draw.ellipse(screen, WHITE, rect, width=2)
        pygame.draw.circle(screen, WHITE, rect.center, 3)


def draw_panel():
    x, px = COLS * CELL, COLS * CELL + 18
    pygame.draw.rect(screen, PANEL, (x, TOP_H, PANEL_W, ROWS * CELL))
    draw_text("CONTROL PANEL", px, TOP_H + 16, WHITE, big_font)
    find_rect = pygame.Rect(px, TOP_H + 58, PANEL_W - 36, 40)
    reset_rect = pygame.Rect(px, TOP_H + 108, (PANEL_W - 44) // 2, 36)
    clear_rect = pygame.Rect(reset_rect.right + 8, TOP_H + 108, (PANEL_W - 44) // 2, 36)
    start_rect = pygame.Rect(px, TOP_H + 154, (PANEL_W - 44) // 2, 36)
    goal_rect = pygame.Rect(start_rect.right + 8, TOP_H + 154, (PANEL_W - 44) // 2, 36)
    draw_button("FIND PATH / START", find_rect, running_robot)
    draw_button("RESET", reset_rect)
    draw_button("CLEAR MAP", clear_rect)
    draw_button("MOVE START", start_rect, mode == "start")
    draw_button("MOVE GOAL", goal_rect, mode == "goal")

    y = TOP_H + 210
    draw_text("LIVE STATISTICS", px, y, WHITE, big_font)
    y += 34
    stats = [("Algorithm", "A* Search"), ("Grid", f"{ROWS} x {COLS}"),
             ("Obstacles", str(len(OBSTACLES))), ("Explored cells", str(len(explored))),
             ("Path cost", str(total_cost) if total_cost is not None else "—"),
             ("Path cells", str(len(path)) if path else "—")]
    for label, value in stats:
        draw_text(label, px, y, MUTED, small)
        val = small.render(value, True, WHITE)
        screen.blit(val, (x + PANEL_W - 18 - val.get_width(), y))
        y += 25
    y += 8
    draw_text("STATUS", px, y, WHITE, big_font)
    y += 32
    words, line = status.split(), ""
    for word in words:
        candidate = (line + " " + word).strip()
        if small.size(candidate)[0] > PANEL_W - 36:
            draw_text(line, px, y, SUCCESS if "completed" in status.lower() else WARNING, small)
            y += 20
            line = word
        else:
            line = candidate
    if line:
        draw_text(line, px, y, SUCCESS if "completed" in status.lower() else WARNING, small
                  )
    y += 45
    draw_text("HOW TO USE", px, y, WHITE, big_font)
    y += 30
    for tip in ["Click cell: toggle wall", "S then click: move start", "G then click: move goal",
                "SPACE: find path / run", "R: reset • C: clear walls"]:
        draw_text(tip, px, y, MUTED, tiny)
        y += 22
    return {"find": find_rect, "reset": reset_rect, "clear": clear_rect, "start": start_rect, "goal": goal_rect}


def draw_footer():
    y = TOP_H + ROWS * CELL
    pygame.draw.rect(screen, BG, (0, y, WIDTH, BOTTOM_H))
    draw_text("Green = route   Yellow = explored   Dark = obstacle   Purple = robot", 12, y + 9, MUTED, small)


def main():
    global running_robot, last_step, robot_index, status, mode, START, GOAL
    alive, buttons = True, {}
    while alive:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                alive = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    alive = False
                elif event.key == pygame.K_SPACE:
                    if not running_robot:
                        find_path()
                        last_step = now
                elif event.key == pygame.K_r:
                    reset_search()
                    status = "Reset — press SPACE to search"
                elif event.key == pygame.K_c:
                    OBSTACLES.clear()
                    reset_search()
                    status = "Obstacles cleared"
                elif event.key == pygame.K_s:
                    mode, status = "start", "Click a free cell to move START"
                elif event.key == pygame.K_g:
                    mode, status = "goal", "Click a free cell to move GOAL"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos, clicked = event.pos, cell_from_mouse(event.pos)
                if clicked is not None:
                    if mode == "start":
                        if clicked not in OBSTACLES and clicked != GOAL:
                            START = clicked
                            mode = "obstacle"
                            reset_search()
                            status = "Start moved — find a new path"
                    elif mode == "goal":
                        if clicked not in OBSTACLES and clicked != START:
                            GOAL = clicked
                            mode = "obstacle"
                            reset_search()
                            status = "Goal moved — find a new path"
                    elif clicked not in (START, GOAL):
                        if clicked in OBSTACLES:
                            OBSTACLES.remove(clicked)
                        else:
                            OBSTACLES.add(clicked)
                        reset_search()
                else:
                    for name, rect in buttons.items():
                        if rect.collidepoint(pos):
                            if name == "find":
                                find_path()
                                last_step = now
                            elif name == "reset":
                                reset_search()
                                status = "Reset — press FIND PATH"
                            elif name == "clear":
                                OBSTACLES.clear()
                                reset_search()
                                status = "Obstacles cleared"
                            elif name == "start":
                                mode, status = "start", "Click a free cell to move START"
                            elif name == "goal":
                                mode, status = "goal", "Click a free cell to move GOAL"
        if running_robot and path and now - last_step >= ROBOT_STEP_MS:
            last_step = now
            if robot_index < len(path) - 1:
                robot_index += 1
            else:
                running_robot = False
                status = "Delivery completed!"
        screen.fill(BG)
        draw_header()
        draw_grid()
        buttons = draw_panel()
        draw_footer()
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
