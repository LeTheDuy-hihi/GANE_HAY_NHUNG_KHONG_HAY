"""ai_logic.py — BFS, DFS, A* pathfinding + heuristic prediction."""
from collections import deque
import heapq
import math
from constants import TILE_SIZE


DIRS = [(0,-1),(0,1),(-1,0),(1,0)]


def tile(px, py):
    return int(px // TILE_SIZE), int(py // TILE_SIZE)


# ── BFS — shortest path ─────────────────────────────────────────────────────
def bfs_path(start_px, start_py, goal_px, goal_py, game_map):
    """Returns list of (px,py) waypoints (pixel centers). Empty if no path."""
    sx, sy = tile(start_px, start_py)
    gx, gy = tile(goal_px, goal_py)
    if game_map.is_wall(gx, gy):
        return []

    queue   = deque([(sx, sy, [])])
    visited = {(sx, sy)}

    while queue:
        x, y, path = queue.popleft()
        if x == gx and y == gy:
            return [(cx*TILE_SIZE + TILE_SIZE//2, cy*TILE_SIZE + TILE_SIZE//2)
                    for cx, cy in path] + [
                        (gx*TILE_SIZE + TILE_SIZE//2, gy*TILE_SIZE + TILE_SIZE//2)]
        for dx, dy in DIRS:
            nx, ny = x+dx, y+dy
            if (nx, ny) not in visited and not game_map.is_wall(nx, ny):
                visited.add((nx, ny))
                queue.append((nx, ny, path + [(x, y)]))
    return []


# ── DFS — patrol exploration ─────────────────────────────────────────────────
def dfs_patrol_step(current_px, current_py, visited_tiles, game_map, depth=12):
    """Returns next pixel waypoint using DFS exploration. Good for patrolling."""
    sx, sy = tile(current_px, current_py)
    stack   = [(sx, sy, [])]
    seen    = set(visited_tiles) | {(sx, sy)}
    result  = []

    while stack and len(result) < depth:
        x, y, path = stack.pop()
        result = path + [(x, y)]
        for dx, dy in DIRS:
            nx, ny = x+dx, y+dy
            if (nx, ny) not in seen and not game_map.is_wall(nx, ny):
                seen.add((nx, ny))
                stack.append((nx, ny, result))

    if len(result) > 1:
        nx, ny = result[1]
        return nx*TILE_SIZE + TILE_SIZE//2, ny*TILE_SIZE + TILE_SIZE//2
    return current_px, current_py


# ── A* — optimal with heuristic ──────────────────────────────────────────────
def astar_path(start_px, start_py, goal_px, goal_py, game_map):
    """Returns pixel waypoint list using A* (Manhattan heuristic)."""
    sx, sy = tile(start_px, start_py)
    gx, gy = tile(goal_px, goal_py)
    if game_map.is_wall(gx, gy):
        return []

    def h(x, y):
        return abs(x-gx) + abs(y-gy)

    open_set = [(h(sx,sy), 0, sx, sy, [])]
    best_g   = {(sx,sy): 0}

    while open_set:
        f, g, x, y, path = heapq.heappop(open_set)
        if x == gx and y == gy:
            full = path + [(x,y)]
            return [(cx*TILE_SIZE+TILE_SIZE//2, cy*TILE_SIZE+TILE_SIZE//2)
                    for cx,cy in full]
        for dx, dy in DIRS:
            nx, ny = x+dx, y+dy
            if not game_map.is_wall(nx, ny):
                ng = g + 1
                if ng < best_g.get((nx,ny), float('inf')):
                    best_g[(nx,ny)] = ng
                    heapq.heappush(open_set, (ng+h(nx,ny), ng, nx, ny, path+[(x,y)]))
    return []


# ── Heuristic — predict player position ──────────────────────────────────────
def predict_player_pos(player, frames_ahead=45):
    """Predict where player will be in `frames_ahead` frames."""
    spd = math.hypot(player.vx, player.vy)
    if spd < 0.1:
        return player.x, player.y
    return (player.x + player.vx * frames_ahead,
            player.y + player.vy * frames_ahead)


# ── Visibility check ─────────────────────────────────────────────────────────
def has_line_of_sight(x1, y1, x2, y2, game_map, steps=20):
    """Bresenham-style LOS check."""
    for i in range(steps+1):
        t  = i / steps
        px = x1 + (x2-x1)*t
        py = y1 + (y2-y1)*t
        if game_map.is_wall_pixel(px, py):
            return False
    return True
