# Smart Delivery Robot — Interactive A* Simulation

Course: CF321 — Fundamentals of AI  
Algorithm: A* Search  
Language: Python  
Interface: Pygame

## Features
- Grid map with obstacles
- A* pathfinding using Manhattan distance
- Animated robot following the route
- Click to add/remove obstacles
- Move start and goal
- Live statistics for explored cells and path cost

## Install and run (PowerShell)
Install Pygame using the Python interpreter installed on your computer:

```powershell
python -m pip install pygame
python main.py
```

If `python` is not recognized on Windows, use your actual Python executable path, for example:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe" -m pip install pygame
& "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe" main.py
```

## Controls
- Left-click an empty cell: toggle obstacle
- `S`, then click: move start
- `G`, then click: move goal
- `SPACE`: calculate route and animate robot
- `R`: reset search/robot
- `C`: clear obstacles
- `ESC`: quit

## Problem formulation
- State: `(row, column)`
- Start: `(0, 0)` by default
- Goal: `(14, 19)` by default
- Actions: up, down, left, right
- Step cost: 1
- Heuristic: Manhattan distance, `abs(row-goal_row) + abs(col-goal_col)`

A* prioritizes states using `f(n) = g(n) + h(n)`. With four-direction movement and unit cost, Manhattan distance is admissible.
