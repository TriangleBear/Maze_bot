# How to Use Maze Bot

## Setup

1. **Activate your virtual environment** (if you use one):
   ```
   # Windows example
   .\venv\Scripts\activate
   ```
2. **Install requirements**:
   ```
   pip install pygame
   ```

## Running the App

1. Open a terminal and navigate to the project directory:
   ```
   cd d:\Programming\Maze_bot
   ```
2. Run the simulation:
   ```
   python src/drawer.py
   ```

## Controls & UI

- **Start**: Begins the selected pathfinding algorithm.
- **Place Walls**: Toggle wall placement mode. Click on the grid to add (left-click) or remove (right-click) walls. Walls cannot be placed on the start (green) or end (red) cell.
- **Reset**: Resets the maze and clears all paths and walls.
- **Random Walls**: Generates a new maze with random walls.
- **Algorithm Dropdown**: Select BFS, DFS, or A* for the simulation.

## Status Bar

- The gray bar at the bottom displays the current user action and simulation status (e.g., "Simulation Completed", "No path found or path is blocked").

## Notes

- The green cell is the start; the red cell is the end.
- You can only place walls when "Place Walls" mode is active.
- If no path is possible, the status will indicate this.
- To resize the window, adjust `WINDOW_WIDTH` and `WINDOW_HEIGHT` in the code.

---
