import pygame
from pygame.locals import *
import sys
import random
from queue import Queue
import heapq
import time
import threading

# Constants for colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (169, 169, 169)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (220, 220, 220)
YELLOW = (255, 255, 0)

# Define the grid size and cell size
GRID_SIZE = 20
CELL_SIZE = 30

simulation_status = "Idle"
user_action = "Idle"
optimal_path = []

# Initialize Pygame
pygame.init()

# Set up the display (make window larger for UI)
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + 200
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + 120
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Path Finding Game")

# UI element positions and sizes
UI_LEFT = GRID_SIZE * CELL_SIZE + 20
UI_TOP = 20
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 40
BUTTON_SPACING = 20

# Dropdown for algorithm selection
ALGO_OPTIONS = ["BFS", "DFS", "A*"]
selected_algo = 0
dropdown_open = False

# Button definitions (reordered: Start, Place Walls, Reset)
buttons = [
    {"label": "Start", "rect": pygame.Rect(UI_LEFT, UI_TOP, BUTTON_WIDTH, BUTTON_HEIGHT)},
    {"label": "Place Walls", "rect": pygame.Rect(UI_LEFT, UI_TOP + (BUTTON_HEIGHT + BUTTON_SPACING), BUTTON_WIDTH, BUTTON_HEIGHT)},
    {"label": "Reset", "rect": pygame.Rect(UI_LEFT, UI_TOP + 2 * (BUTTON_HEIGHT + BUTTON_SPACING), BUTTON_WIDTH, BUTTON_HEIGHT)},
    {"label": "Random Walls", "rect": pygame.Rect(UI_LEFT, UI_TOP + 3 * (BUTTON_HEIGHT + BUTTON_SPACING), BUTTON_WIDTH, BUTTON_HEIGHT)},
]

placing_walls_mode = False

# Create a separate screen for text
text_screen = pygame.Surface((WINDOW_WIDTH, 100))
text_screen.fill(GRAY)

# Define fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

def draw_text(text, color, x, y, screen, font=font):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Cell class
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = False
        self.wall = False
        self.parent = None
        self.is_path = False

    def draw(self, color):
        if self.is_path:
            pygame.draw.rect(screen, BLUE, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        else:
            pygame.draw.rect(screen, color, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

grid = [[Cell(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]

def generate_maze():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            grid[x][y].wall = False
            grid[x][y].visited = False
            grid[x][y].parent = None
    for _ in range(GRID_SIZE * GRID_SIZE // 3):
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        grid[x][y].wall = True

def reset_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            grid[x][y].visited = False
            grid[x][y].parent = None
            grid[x][y].is_path = False

def bfs(start, end):
    reset_grid()
    global optimal_path
    optimal_path = []
    queue = Queue()
    queue.put(start)
    start.visited = True
    found = False
    while not queue.empty():
        current = queue.get()
        if current == end:
            found = True
            break
        for neighbor in get_neighbors(current):
            if not neighbor.visited and not neighbor.wall:
                neighbor.visited = True
                neighbor.parent = current
                queue.put(neighbor)
        draw_grid()
        pygame.display.flip()
        time.sleep(0.001)
    if found:
        current = end
        while current is not None:
            current.is_path = True
            current = current.parent
        return True
    return False

def dfs(start, end):
    reset_grid()
    global optimal_path
    optimal_path = []
    stack = [start]
    start.visited = True
    found = False
    while stack:
        current = stack.pop()
        if current == end:
            found = True
            break
        for neighbor in get_neighbors(current):
            if not neighbor.visited and not neighbor.wall:
                neighbor.visited = True
                neighbor.parent = current
                stack.append(neighbor)
        draw_grid()
        pygame.display.flip()
        time.sleep(0.001)
    if found:
        current = end
        while current is not None:
            current.is_path = True
            current = current.parent
        return True
    return False

def a_star(start, end):
    reset_grid()
    global optimal_path
    optimal_path = []
    open_set = []
    heapq.heappush(open_set, (0, (start.x, start.y)))
    g_score = {(cell.x, cell.y): float('inf') for row in grid for cell in row}
    f_score = {(cell.x, cell.y): float('inf') for row in grid for cell in row}
    g_score[(start.x, start.y)] = 0
    f_score[(start.x, start.y)] = heuristic(start, end)
    parent = {}
    closed_set = set()
    found = False
    while open_set:
        _, (cx, cy) = heapq.heappop(open_set)
        current = grid[cx][cy]
        if (cx, cy) in closed_set:
            continue
        closed_set.add((cx, cy))
        current.visited = True
        if current == end:
            found = True
            break
        for neighbor in get_neighbors(current):
            nx, ny = neighbor.x, neighbor.y
            if neighbor.wall or (nx, ny) in closed_set:
                continue
            tentative_g = g_score[(cx, cy)] + 1
            if tentative_g < g_score[(nx, ny)]:
                parent[(nx, ny)] = (cx, cy)
                g_score[(nx, ny)] = tentative_g
                f_score[(nx, ny)] = tentative_g + heuristic(neighbor, end)
                heapq.heappush(open_set, (f_score[(nx, ny)], (nx, ny)))
        draw_grid()
        pygame.display.flip()
        time.sleep(0.001)
    if found:
        path = []
        node = (end.x, end.y)
        while node in parent:
            cell = grid[node[0]][node[1]]
            cell.is_path = True
            path.append(cell)
            node = parent[node]
        grid[start.x][start.y].is_path = True
        return True
    return False

def heuristic(cell, end):
    return abs(cell.x - end.x) + abs(cell.y - end.y)

def get_neighbors(cell):
    neighbors = []
    x, y = cell.x, cell.y
    if x > 0:
        neighbors.append(grid[x - 1][y])
    if x < GRID_SIZE - 1:
        neighbors.append(grid[x + 1][y])
    if y > 0:
        neighbors.append(grid[x][y - 1])
    if y < GRID_SIZE - 1:
        neighbors.append(grid[x][y + 1])
    return neighbors

def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            cell = grid[x][y]
            if cell.wall:
                cell.draw(BLACK)
            elif cell.visited:
                if cell.is_path:
                    cell.draw(BLUE)
                else:
                    cell.draw(GREEN)
            else:
                cell.draw(WHITE)

def reconstruct_path(end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = current.parent
    return path[::-1]

ALGORITHM_STEP_DELAY = 10
ALGORITHM_TIME_LIMIT = 500

STATE_IDLE = 0
STATE_SIMULATING = 1

current_state = {"state": STATE_IDLE}
running = True
algorithm = None
result = [False]
placing_walls_mode = False

def run_algorithm(current_state, result):
    global simulation_status, optimal_path
    algorithm_start_time = pygame.time.get_ticks()
    result[0] = False
    current_state["state"] = STATE_SIMULATING
    if algorithm:
        while current_state["state"] == STATE_SIMULATING:
            current_time = pygame.time.get_ticks()
            if current_time - algorithm_start_time >= ALGORITHM_TIME_LIMIT:
                simulation_status = "Time Limit Exceeded"
                current_state["state"] = STATE_IDLE
            else:
                if not result[0]:
                    result[0] = algorithm(start_cell, end_cell)
                if result[0]:
                    optimal_path = reconstruct_path(end_cell)
                    simulation_status = "Simulation Completed"
                    current_state["state"] = STATE_IDLE
                elif not result[0] and algorithm is not None:
                    simulation_status = "No path found or path is blocked"
                    current_state["state"] = STATE_IDLE
                if pygame.time.get_ticks() - algorithm_start_time >= ALGORITHM_STEP_DELAY:
                    algorithm_start_time = pygame.time.get_ticks()
                else:
                    pygame.time.delay(ALGORITHM_STEP_DELAY)

generate_maze()
start_cell = grid[0][0]
end_cell = grid[GRID_SIZE - 1][GRID_SIZE - 1]

def draw_dropdown(selected, open_):
    # Place dropdown at the bottom of the button stack
    dropdown_y = UI_TOP + 4 * (BUTTON_HEIGHT + BUTTON_SPACING)
    rect = pygame.Rect(UI_LEFT, dropdown_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, LIGHT_GRAY if open_ else WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    draw_text(f"Algorithm: {ALGO_OPTIONS[selected]}", BLACK, rect.x + 10, rect.y + 5, screen, small_font)
    # Draw dropdown arrow
    pygame.draw.polygon(screen, BLACK, [
        (rect.right - 20, rect.y + 15),
        (rect.right - 10, rect.y + 15),
        (rect.right - 15, rect.y + 25)
    ])
    # Draw options if open
    if open_:
        # Draw a background rectangle behind all options to prevent overlap
        options_rect = pygame.Rect(
            rect.x,
            rect.y + BUTTON_HEIGHT,
            BUTTON_WIDTH,
            BUTTON_HEIGHT * len(ALGO_OPTIONS)
        )
        pygame.draw.rect(screen, WHITE, options_rect)
        pygame.draw.rect(screen, BLACK, options_rect, 2)
        for i, option in enumerate(ALGO_OPTIONS):
            opt_rect = pygame.Rect(rect.x, rect.y + (i + 1) * BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT)
            pygame.draw.rect(screen, YELLOW if i == selected else WHITE, opt_rect)
            pygame.draw.rect(screen, BLACK, opt_rect, 1)
            draw_text(option, BLACK, opt_rect.x + 10, opt_rect.y + 5, screen, small_font)
    return rect

def draw_buttons():
    for btn in buttons:
        pygame.draw.rect(screen, LIGHT_GRAY, btn["rect"])
        pygame.draw.rect(screen, BLACK, btn["rect"], 2)
        draw_text(btn["label"], BLACK, btn["rect"].x + 10, btn["rect"].y + 5, screen, small_font)

while running:
    screen.fill(WHITE)
    draw_grid()
    start_cell.draw(GREEN)
    end_cell.draw(RED)

    # Draw border around the grid
    pygame.draw.rect(
        screen, BLACK,
        (0, 0, GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE),
        3
    )

    # Draw border around the right UI panel
    pygame.draw.rect(
        screen, BLACK,
        (GRID_SIZE * CELL_SIZE, 0, WINDOW_WIDTH - GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE + 4 * (BUTTON_HEIGHT + BUTTON_SPACING) + BUTTON_HEIGHT + 10),
        3
    )

    # Draw UI
    dropdown_rect = draw_dropdown(selected_algo, dropdown_open)
    draw_buttons()

    # Draw text on the text screen
    text_screen.fill(GRAY)
    draw_text(f"User Action: {user_action}", BLACK, 10, 20, text_screen)
    draw_text(f"Simulation Status: {simulation_status}", BLACK, 10, 60, text_screen)
    screen.blit(text_screen, (0, GRID_SIZE * CELL_SIZE + 20))

    # Draw border around the status bar (text area)
    pygame.draw.rect(
        screen, BLACK,
        (0, GRID_SIZE * CELL_SIZE + 20, WINDOW_WIDTH, 100),
        3
    )

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Dropdown logic (use new dropdown_rect position)
            if dropdown_rect.collidepoint(mx, my):
                dropdown_open = not dropdown_open
            elif dropdown_open:
                for i, option in enumerate(ALGO_OPTIONS):
                    opt_rect = pygame.Rect(dropdown_rect.x, dropdown_rect.y + (i + 1) * BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT)
                    if opt_rect.collidepoint(mx, my):
                        selected_algo = i
                        dropdown_open = False
                        user_action = f"{ALGO_OPTIONS[selected_algo]} Algorithm Selected"
                        if selected_algo == 0:
                            algorithm = bfs
                        elif selected_algo == 1:
                            algorithm = dfs
                        elif selected_algo == 2:
                            algorithm = a_star
                        break
                else:
                    dropdown_open = False
            # Button logic (no change needed, order is already correct)
            for idx, btn in enumerate(buttons):
                if btn["rect"].collidepoint(mx, my):
                    if btn["label"] == "Place Walls":
                        placing_walls_mode = not placing_walls_mode
                        user_action = "Placing Walls Mode" if placing_walls_mode else "Exit Wall Placement Mode"
                    elif btn["label"] == "Reset":
                        user_action = "Maze Reset"
                        simulation_status = "Not Started"
                        generate_maze()
                        start_cell = grid[0][0]
                        end_cell = grid[GRID_SIZE - 1][GRID_SIZE - 1]
                        optimal_path = []
                        reset_grid()
                    elif btn["label"] == "Start":
                        if algorithm:
                            user_action = "Simulation Started"
                            simulation_status = "Simulation Started"
                            threading.Thread(target=run_algorithm, args=(current_state, result)).start()
                    elif btn["label"] == "Random Walls":
                        user_action = "Random Walls Mode"
                        generate_maze()
            # Place/remove walls
            if placing_walls_mode and mx < GRID_SIZE * CELL_SIZE and my < GRID_SIZE * CELL_SIZE:
                cell_x = mx // CELL_SIZE
                cell_y = my // CELL_SIZE
                if (cell_x, cell_y) == (start_cell.x, start_cell.y) or (cell_x, cell_y) == (end_cell.x, end_cell.y):
                    continue
                if event.button == 1:
                    grid[cell_x][cell_y].wall = True
                elif event.button == 3:
                    grid[cell_x][cell_y].wall = False

pygame.quit()
sys.exit()
