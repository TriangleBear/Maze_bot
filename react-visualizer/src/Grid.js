import React from "react";
import "./App.css";

const CELL_SIZE = 24;

function Grid({ grid, start, end, onCellClick }) {
  return (
    <div className="grid">
      {grid.map((row, x) => (
        <div className="grid-row" key={x}>
          {row.map((cell, y) => {
            let className = "cell";
            if (x === start.x && y === start.y) className += " start";
            else if (x === end.x && y === end.y) className += " end";
            else if (cell.wall) className += " wall";
            else if (cell.isPath) className += " path";
            else if (cell.visited) className += " visited";
            return (
              <div
                key={y}
                className={className}
                style={{ width: CELL_SIZE, height: CELL_SIZE }}
                onClick={() => onCellClick(x, y)}
              />
            );
          })}
        </div>
      ))}
    </div>
  );
}

export default Grid;
