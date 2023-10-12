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

# Constants for key codes
KEY_B = 98  # "b" key
KEY_D = 100  # "d" key
KEY_S = 115  # "s" key
KEY_R = 114  # "r" key
KEY_P = 112  # "p" key
KEY_G = 103  # "g" key
KEY_N = 110  # "n" key
KEY_X = 120  # "x" key

# Define the grid size and cell size
GRID_SIZE = 20
CELL_SIZE = 30

simulation_status = "Idle"
user_action = "Idle"
path_cells = []
optimal_path = []  # Initialize optimal_path as an empty list

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Path Finding Game")

# Define fonts
font = pygame.font.Font(None, 36)

# Helper function to draw text on the screen
def draw_text(text, color, x, y):
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

# Create a grid of cells
grid = [[Cell(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]

# Function to generate a maze
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

# Function to reset the grid
def reset_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            grid[x][y].visited = False
            grid[x][y].parent = None
            grid[x][y].is_path = False

# Breadth-First Search Algorithm
def bfs(start, end):
    reset_grid()
    queue = Queue()
    queue.put(start)

    while not queue.empty():
        current = queue.get()
        if current == end:
            while current is not None:
                current.is_path = True
                current = current.parent
            return True
        for neighbor in get_neighbors(current):
            if not neighbor.visited and not neighbor.wall:
                neighbor.visited = True
                neighbor.parent = current
                queue.put(neighbor)
        draw_grid()
        pygame.display.flip()
        time.sleep(0.001)

    return False

# Depth-First Search Algorithm
def dfs(start, end):
    reset_grid()
    stack = [start]

    while stack:
        current = stack.pop()
        if current == end:
            while current is not None:
                current.is_path = True
                current = current.parent
            return True
        for neighbor in get_neighbors(current):
            if not neighbor.visited and not neighbor.wall:
                neighbor.visited = True
                neighbor.parent = current
                stack.append(neighbor)
        draw_grid()
        pygame.display.flip()
        time.sleep(0.001)

    return False

# A* Algorithm
def a_star(start, end):
    reset_grid()
    open_set = [(0, start)]
    heapq.heapify(open_set)
    g_scores = {cell: float('inf') for row in grid for cell in row}
    g_scores[start] = 0
    visited_cells = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == end:
            while current is not None:
                current.is_path = True
                current = current.parent
            return True
        visited_cells.add(current)
        for neighbor in get_neighbors(current):
            tentative_g_score = g_scores[current] + 1
            if tentative_g_score < g_scores[neighbor]:
                neighbor.parent = current
                g_scores[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, end)
                if (f_score, neighbor) not in open_set and neighbor not in visited_cells:
                    heapq.heappush(open_set, (f_score, neighbor))
        draw_grid()
        pygame.display.flip()

    return False

# Function to calculate heuristic value
def heuristic(cell, end):
    return abs(cell.x - end.x) + abs(cell.y - end.y)

# Function to get neighboring cells
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

# Function to draw the grid
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

# Function to reconstruct the path
def reconstruct_path(end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = current.parent
    return path[::-1]

# Algorithm step delay and time limit (in milliseconds)
ALGORITHM_STEP_DELAY = 10
ALGORITHM_TIME_LIMIT = 500

# State constants
STATE_IDLE = 0
STATE_SIMULATING = 1

# Initialize the state
current_state = {"state": STATE_IDLE}

running = True
algorithm = None
result = [False]

# Function to run the algorithm in a separate thread
def run_algorithm(current_state, result):
    algorithm_start_time = pygame.time.get_ticks()
    result[0] = False  # Initialize result to False
    current_state["state"] = STATE_SIMULATING  # Change the state to simulating

    if algorithm:
        while current_state["state"] == STATE_SIMULATING:
            current_time = pygame.time.get_ticks()
            if current_time - algorithm_start_time >= ALGORITHM_TIME_LIMIT:
                # Time limit exceeded, stop the algorithm
                simulation_status = "Time Limit Exceeded"
                current_state["state"] = STATE_IDLE
            else:
                # Continue the algorithm one step at a time with a delay
                if not result[0]:
                    result[0] = algorithm(start_cell, end_cell)
                if result[0]:
                    optimal_path = reconstruct_path(end_cell)
                    simulation_status = "Simulation Completed"
                    current_state["state"] = STATE_IDLE

                # Delay to control the algorithm step rate
                if pygame.time.get_ticks() - algorithm_start_time >= ALGORITHM_STEP_DELAY:
                    algorithm_start_time = pygame.time.get_ticks()
                else:
                    pygame.time.delay(ALGORITHM_STEP_DELAY)  # Use pygame.time.delay for a delay

# Main game loop
generate_maze()
start_cell = grid[0][0]
end_cell = grid[GRID_SIZE - 1][GRID_SIZE - 1]

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == KEY_B:
                user_action = "BFS Algorithm Selected"
                algorithm = bfs
                path_cells = []
            elif event.key == KEY_D:
                user_action = "DFS Algorithm Selected"
                algorithm = dfs
                path_cells = []
            elif event.key == KEY_S:
                if algorithm:
                    user_action = "Simulation Started"
                    simulation_status = "Simulation Started"
                    threading.Thread(target=run_algorithm, args=(current_state, result)).start()
            elif event.key == KEY_R:
                user_action = "Maze Reset"
                simulation_status = "Not Started"
                generate_maze()
                start_cell = grid[0][0]
                end_cell = grid[GRID_SIZE - 1][GRID_SIZE - 1]
                optimal_path = None
                reset_grid()
            elif event.key == KEY_P:
                user_action = "Placing Walls Mode"
                placing_walls_mode = True
            elif event.key == KEY_G:
                user_action = "Random Walls Mode"
                generate_maze()
            elif event.key == KEY_N:
                user_action = "Exit Wall Placement Mode"
                placing_walls_mode = False
            elif event.key == KEY_X:
                if current_state["state"] == STATE_SIMULATING:
                    current_state["state"] = STATE_IDLE
                    simulation_status = "Simulation Stopped"

    draw_grid()
    start_cell.draw(GREEN)
    end_cell.draw(RED)

    if optimal_path:
        for cell in optimal_path:
            if cell != start_cell and cell != end_cell:
                cell.draw(BLUE)

    draw_text(f"User Action: {user_action}", BLACK, 10, WINDOW_HEIGHT - 80)
    draw_text(f"Simulation Status: {simulation_status}", BLACK, 10, WINDOW_HEIGHT - 120)

    pygame.display.flip()

pygame.quit()
sys.exit()
