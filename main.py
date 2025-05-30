import flet as ft
import random
from queue import Queue
import heapq

GRID_SIZE = 20

WHITE = "#FFFFFF"
BLACK = "#000000"
GREEN = "#00FF00"
RED = "#FF0000"
BLUE = "#0000FF"
GRAY = "#A9A9A9"
LIGHT_GRAY = "#DCDCDC"
YELLOW = "#FFFF00"

ALGO_OPTIONS = ["BFS", "DFS", "A*"]

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = False
        self.wall = False
        self.parent = None
        self.is_path = False

def create_grid():
    return [[Cell(x, y) for y in range(GRID_SIZE)] for x in range(GRID_SIZE)]

def reset_grid(grid):
    for row in grid:
        for cell in row:
            cell.visited = False
            cell.parent = None
            cell.is_path = False

def generate_maze(grid):
    for row in grid:
        for cell in row:
            cell.wall = False
            cell.visited = False
            cell.parent = None
    for _ in range(GRID_SIZE * GRID_SIZE // 3):
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        grid[x][y].wall = True

def get_neighbors(cell, grid):
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

def heuristic(cell, end):
    return abs(cell.x - end.x) + abs(cell.y - end.y)

def reconstruct_path(end):
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = current.parent
    return path[::-1]

def bfs(grid, start, end, update_ui=None):
    reset_grid(grid)
    queue = Queue()
    queue.put(start)
    start.visited = True
    found = False
    while not queue.empty():
        current = queue.get()
        if current == end:
            found = True
            break
        for neighbor in get_neighbors(current, grid):
            if not neighbor.visited and not neighbor.wall:
                neighbor.visited = True
                neighbor.parent = current
                queue.put(neighbor)
        if update_ui:
            update_ui()
    if found:
        current = end
        while current is not None:
            current.is_path = True
            current = current.parent
        return True
    return False

def dfs(grid, start, end, update_ui=None):
    reset_grid(grid)
    stack = [start]
    start.visited = True
    found = False
    while stack:
        current = stack.pop()
        if current == end:
            found = True
            break
        for neighbor in get_neighbors(current, grid):
            if not neighbor.visited and not neighbor.wall:
                neighbor.visited = True
                neighbor.parent = current
                stack.append(neighbor)
        if update_ui:
            update_ui()
    if found:
        current = end
        while current is not None:
            current.is_path = True
            current = current.parent
        return True
    return False

def a_star(grid, start, end, update_ui=None):
    reset_grid(grid)
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
        for neighbor in get_neighbors(current, grid):
            nx, ny = neighbor.x, neighbor.y
            if neighbor.wall or (nx, ny) in closed_set:
                continue
            tentative_g = g_score[(cx, cy)] + 1
            if tentative_g < g_score[(nx, ny)]:
                parent[(nx, ny)] = (cx, cy)
                g_score[(nx, ny)] = tentative_g
                f_score[(nx, ny)] = tentative_g + heuristic(neighbor, end)
                heapq.heappush(open_set, (f_score[(nx, ny)], (nx, ny)))
        if update_ui:
            update_ui()
    if found:
        node = (end.x, end.y)
        while node in parent:
            cell = grid[node[0]][node[1]]
            cell.is_path = True
            node = parent[node]
        grid[start.x][start.y].is_path = True
        return True
    return False

def main(page: ft.Page):
    page.title = "Path Finding Game (Flet)"
    page.bgcolor = WHITE
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    grid = create_grid()
    generate_maze(grid)
    start_cell = grid[0][0]
    end_cell = grid[GRID_SIZE - 1][GRID_SIZE - 1]
    selected_algo = [0]
    simulation_status = ft.Text("Idle", size=16, color=BLACK)
    user_action = ft.Text("Idle", size=16, color=BLACK)
    placing_walls_mode = [False]

    def cell_color(cell):
        if cell == start_cell:
            return GREEN
        elif cell == end_cell:
            return RED
        elif cell.wall:
            return BLACK
        elif cell.is_path:
            return BLUE
        elif cell.visited:
            return YELLOW
        else:
            return WHITE

    def update_grid_ui():
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell_btns[x][y].bgcolor = cell_color(grid[x][y])
        page.update()

    def on_cell_click(e, x, y):
        if placing_walls_mode[0]:
            cell = grid[x][y]
            if cell == start_cell or cell == end_cell:
                return
            cell.wall = not cell.wall
            update_grid_ui()

    def on_algo_change(e):
        selected_algo[0] = int(e.control.value)
        user_action.value = f"{ALGO_OPTIONS[selected_algo[0]]} Algorithm Selected"
        page.update()

    def on_place_walls(e):
        placing_walls_mode[0] = not placing_walls_mode[0]
        user_action.value = "Placing Walls Mode" if placing_walls_mode[0] else "Exit Wall Placement Mode"
        page.update()

    def on_reset(e):
        generate_maze(grid)
        reset_grid(grid)
        user_action.value = "Maze Reset"
        simulation_status.value = "Not Started"
        update_grid_ui()
        page.update()

    def on_random_walls(e):
        generate_maze(grid)
        user_action.value = "Random Walls Mode"
        update_grid_ui()
        page.update()

    def on_start(e):
        reset_grid(grid)
        simulation_status.value = "Simulation Started"
        user_action.value = "Simulation Started"
        update_grid_ui()
        page.update()
        algo = [bfs, dfs, a_star][selected_algo[0]]
        found = algo(grid, start_cell, end_cell, update_grid_ui)
        if found:
            simulation_status.value = "Simulation Completed"
        else:
            simulation_status.value = "No path found or path is blocked"
        update_grid_ui()
        page.update()

    # Build grid UI
    cell_btns = [
        [
            ft.Container(
                width=24, height=24,
                bgcolor=cell_color(grid[x][y]),
                border=ft.border.all(1, BLACK),  # changed from ft.colors.BLACK to BLACK
                on_click=lambda e, x=x, y=y: on_cell_click(e, x, y)
            )
            for y in range(GRID_SIZE)
        ]
        for x in range(GRID_SIZE)
    ]
    grid_row_controls = [ft.Row(cell_btns[x], spacing=0) for x in range(GRID_SIZE)]
    grid_column = ft.Column(grid_row_controls, spacing=0)

    # Controls
    algo_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(str(i), ALGO_OPTIONS[i]) for i in range(len(ALGO_OPTIONS))],
        value="0",
        on_change=on_algo_change,
        width=160,
        color=BLACK
    )
    start_btn = ft.ElevatedButton("Start", on_click=on_start, width=160)
    place_walls_btn = ft.ElevatedButton("Place Walls", on_click=on_place_walls, width=160)
    reset_btn = ft.ElevatedButton("Reset", on_click=on_reset, width=160)
    random_walls_btn = ft.ElevatedButton("Random Walls", on_click=on_random_walls, width=160)

    controls_panel = ft.Column([
        start_btn,
        place_walls_btn,
        reset_btn,
        random_walls_btn,
        ft.Text("Algorithm:", color=BLACK),
        algo_dropdown,
        ft.Divider(),
        ft.Text("User Action:", color=BLACK),
        user_action,
        ft.Text("Simulation Status:", color=BLACK),
        simulation_status,
    ], spacing=10)

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        grid_column,
                        ft.VerticalDivider(width=20),
                        controls_panel
                    ],
                    alignment="center"
                )
            ],
            alignment="center",
            horizontal_alignment="center",
            expand=True
        )
    )

ft.app(target=main)
