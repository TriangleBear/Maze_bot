import React, { useState } from "react";
import Grid from "./Grid";
import { bfs, dfs, astar } from "./algorithms";
import "./App.css";

const GRID_SIZE = 20;
const ALGO_OPTIONS = ["BFS", "DFS", "A*"];

function createEmptyGrid() {
  return Array.from({ length: GRID_SIZE }, (_, x) =>
    Array.from({ length: GRID_SIZE }, (_, y) => ({
      x,
      y,
      wall: false,
      visited: false,
      isPath: false,
    }))
  );
}

function App() {
  const [grid, setGrid] = useState(createEmptyGrid());
  const [start, setStart] = useState({ x: 0, y: 0 });
  const [end, setEnd] = useState({ x: GRID_SIZE - 1, y: GRID_SIZE - 1 });
  const [placingWalls, setPlacingWalls] = useState(false);
  const [selectedAlgo, setSelectedAlgo] = useState(0);
  const [status, setStatus] = useState("Idle");

  const handleCellClick = (x, y) => {
    if (placingWalls) {
      if ((x === start.x && y === start.y) || (x === end.x && y === end.y)) return;
      setGrid((prev) => {
        const newGrid = prev.map((row) => row.map((cell) => ({ ...cell })));
        newGrid[x][y].wall = !newGrid[x][y].wall;
        return newGrid;
      });
    }
  };

  const handleAlgoChange = (e) => {
    setSelectedAlgo(Number(e.target.value));
  };

  const handlePlaceWalls = () => {
    setPlacingWalls((w) => !w);
  };

  const handleReset = () => {
    setGrid(createEmptyGrid());
    setStatus("Maze Reset");
  };

  const handleRandomWalls = () => {
    setGrid((prev) => {
      const newGrid = createEmptyGrid();
      for (let i = 0; i < GRID_SIZE * GRID_SIZE / 3; i++) {
        const x = Math.floor(Math.random() * GRID_SIZE);
        const y = Math.floor(Math.random() * GRID_SIZE);
        if ((x === start.x && y === start.y) || (x === end.x && y === end.y)) continue;
        newGrid[x][y].wall = true;
      }
      return newGrid;
    });
    setStatus("Random Walls Mode");
  };

  const handleStart = () => {
    setStatus("Simulation Started");
    let found = false;
    let newGrid = grid.map((row) => row.map((cell) => ({ ...cell, visited: false, isPath: false })));
    if (selectedAlgo === 0) found = bfs(newGrid, start, end);
    else if (selectedAlgo === 1) found = dfs(newGrid, start, end);
    else if (selectedAlgo === 2) found = astar(newGrid, start, end);
    setGrid(newGrid);
    setStatus(found ? "Simulation Completed" : "No path found or path is blocked");
  };

  return (
    <div className="App">
      <div className="controls">
        <button onClick={handleStart}>Start</button>
        <button onClick={handlePlaceWalls}>{placingWalls ? "Exit Wall Placement" : "Place Walls"}</button>
        <button onClick={handleReset}>Reset</button>
        <button onClick={handleRandomWalls}>Random Walls</button>
        <label>
          Algorithm:
          <select value={selectedAlgo} onChange={handleAlgoChange}>
            {ALGO_OPTIONS.map((algo, i) => (
              <option value={i} key={algo}>{algo}</option>
            ))}
          </select>
        </label>
        <div>Status: {status}</div>
      </div>
      <Grid
        grid={grid}
        start={start}
        end={end}
        onCellClick={handleCellClick}
      />
    </div>
  );
}

export default App;
