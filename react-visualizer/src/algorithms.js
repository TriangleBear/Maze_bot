// BFS, DFS, and A* for the grid
export function bfs(grid, start, end) {
  const queue = [];
  queue.push(grid[start.x][start.y]);
  grid[start.x][start.y].visited = true;
  let found = false;
  while (queue.length) {
    const current = queue.shift();
    if (current.x === end.x && current.y === end.y) {
      found = true;
      break;
    }
    for (const neighbor of getNeighbors(current, grid)) {
      if (!neighbor.visited && !neighbor.wall) {
        neighbor.visited = true;
        neighbor.parent = current;
        queue.push(neighbor);
      }
    }
  }
  if (found) markPath(grid, end);
  return found;
}

export function dfs(grid, start, end) {
  const stack = [];
  stack.push(grid[start.x][start.y]);
  grid[start.x][start.y].visited = true;
  let found = false;
  while (stack.length) {
    const current = stack.pop();
    if (current.x === end.x && current.y === end.y) {
      found = true;
      break;
    }
    for (const neighbor of getNeighbors(current, grid)) {
      if (!neighbor.visited && !neighbor.wall) {
        neighbor.visited = true;
        neighbor.parent = current;
        stack.push(neighbor);
      }
    }
  }
  if (found) markPath(grid, end);
  return found;
}

export function astar(grid, start, end) {
  const openSet = [];
  openSet.push(grid[start.x][start.y]);
  grid[start.x][start.y].g = 0;
  grid[start.x][start.y].f = heuristic(start, end);
  let found = false;
  while (openSet.length) {
    openSet.sort((a, b) => a.f - b.f);
    const current = openSet.shift();
    current.visited = true;
    if (current.x === end.x && current.y === end.y) {
      found = true;
      break;
    }
    for (const neighbor of getNeighbors(current, grid)) {
      if (neighbor.wall) continue;
      const tentative_g = (current.g || 0) + 1;
      if (neighbor.g === undefined || tentative_g < neighbor.g) {
        neighbor.g = tentative_g;
        neighbor.f = tentative_g + heuristic(neighbor, end);
        neighbor.parent = current;
        if (!neighbor.visited) openSet.push(neighbor);
      }
    }
  }
  if (found) markPath(grid, end);
  return found;
}

function getNeighbors(cell, grid) {
  const { x, y } = cell;
  const neighbors = [];
  if (x > 0) neighbors.push(grid[x - 1][y]);
  if (x < grid.length - 1) neighbors.push(grid[x + 1][y]);
  if (y > 0) neighbors.push(grid[x][y - 1]);
  if (y < grid[0].length - 1) neighbors.push(grid[x][y + 1]);
  return neighbors;
}

function heuristic(a, b) {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

function markPath(grid, end) {
  let current = grid[end.x][end.y];
  while (current) {
    current.isPath = true;
    current = current.parent;
  }
}
