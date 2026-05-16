from collections import deque
import heapq
import random
from constants import Direction

def get_valid_directions(start, game_map, current_dir):
    directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]
    valid_dirs = []
    for d in directions:
        nx, ny = start[0] + d[0], start[1] + d[1]
        # Prevent reversing direction
        if current_dir != Direction.NONE and d == (-current_dir[0], -current_dir[1]):
            continue
        if not game_map.is_wall(nx, ny, is_ghost=True):
            valid_dirs.append(d)
    return valid_dirs

def get_fallback_direction(start, game_map, current_dir):
    directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]
    valid_dirs = []
    for d in directions:
        nx, ny = start[0] + d[0], start[1] + d[1]
        if not game_map.is_wall(nx, ny, is_ghost=True) and d != (-current_dir[0], -current_dir[1]):
            valid_dirs.append(d)
    if valid_dirs:
        return valid_dirs[0]
    return Direction.NONE

def bfs(start, target, game_map, current_dir):
    queue = deque([(start, [])])
    visited = set([start])
    directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]

    while queue:
        current, path = queue.popleft()
        if current == target:
            if len(path) > 0:
                return path[0]
            return current_dir

        for d in directions:
            if len(path) == 0 and current_dir != Direction.NONE and d == (-current_dir[0], -current_dir[1]):
                continue

            nx, ny = current[0] + d[0], current[1] + d[1]
            
            if (nx, ny) not in visited and not game_map.is_wall(nx, ny, is_ghost=True):
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [d]))

    return get_fallback_direction(start, game_map, current_dir)

def dfs(start, target, game_map, current_dir):
    stack = [(start, [])]
    visited = set()
    directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]

    while stack:
        current, path = stack.pop()
        
        if current == target:
            if len(path) > 0:
                return path[0]
            return current_dir

        if current not in visited:
            visited.add(current)
            for d in directions:
                if len(path) == 0 and current_dir != Direction.NONE and d == (-current_dir[0], -current_dir[1]):
                    continue

                nx, ny = current[0] + d[0], current[1] + d[1]
                
                if (nx, ny) not in visited and not game_map.is_wall(nx, ny, is_ghost=True):
                    stack.append(((nx, ny), path + [d]))

    return get_fallback_direction(start, game_map, current_dir)

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def a_star(start, target, game_map, current_dir):
    # Priority Queue elements: (f_score, g_score, current_pos, path)
    pq = [(0, 0, start, [])]
    visited = {} # Keeps track of best g_score to a node
    visited[start] = 0
    directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]

    while pq:
        f, g, current, path = heapq.heappop(pq)

        if current == target:
            if len(path) > 0:
                return path[0]
            return current_dir

        for d in directions:
            if len(path) == 0 and current_dir != Direction.NONE and d == (-current_dir[0], -current_dir[1]):
                continue

            nx, ny = current[0] + d[0], current[1] + d[1]
            
            if not game_map.is_wall(nx, ny, is_ghost=True):
                next_pos = (nx, ny)
                new_g = g + 1
                
                # Only explore if we found a shorter path to next_pos
                if next_pos not in visited or new_g < visited[next_pos]:
                    visited[next_pos] = new_g
                    h = manhattan_distance(next_pos, target)
                    f_score = new_g + h
                    heapq.heappush(pq, (f_score, new_g, next_pos, path + [d]))

    return get_fallback_direction(start, game_map, current_dir)

def bfs_find_pellet(start, game_map, current_dir, ghosts=None):
    from collections import deque
    queue = deque([(start, [start])])
    visited = set([start])
    directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]

    ghost_cells = set()
    if ghosts:
        for g in ghosts:
            ghost_cells.add((g.grid_x, g.grid_y))

    while queue:
        current, path = queue.popleft()
        
        if current in game_map.pellets or current in game_map.power_pellets:
            return path

        for d in directions:
            if len(path) == 1 and current_dir != Direction.NONE and d == (-current_dir[0], -current_dir[1]):
                continue

            nx, ny = current[0] + d[0], current[1] + d[1]
            if nx < 0: nx = len(game_map.grid[0]) - 1
            elif nx >= len(game_map.grid[0]): nx = 0

            if (nx, ny) not in visited and not game_map.is_wall(nx, ny) and (nx, ny) not in ghost_cells:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    # Fallback without avoiding ghosts
    if ghosts:
        return bfs_find_pellet(start, game_map, current_dir, None)
    return []

def dfs_find_pellet(start, game_map, current_dir, ghosts=None):
    stack = [(start, [start])]
    visited = set()
    directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]
    
    ghost_cells = set()
    if ghosts:
        for g in ghosts:
            ghost_cells.add((g.grid_x, g.grid_y))

    while stack:
        current, path = stack.pop()
        
        if current in game_map.pellets or current in game_map.power_pellets:
            return path

        if current not in visited:
            visited.add(current)
            for d in directions:
                if len(path) == 1 and current_dir != Direction.NONE and d == (-current_dir[0], -current_dir[1]):
                    continue

                nx, ny = current[0] + d[0], current[1] + d[1]
                if nx < 0: nx = len(game_map.grid[0]) - 1
                elif nx >= len(game_map.grid[0]): nx = 0

                if (nx, ny) not in visited and not game_map.is_wall(nx, ny) and (nx, ny) not in ghost_cells:
                    stack.append(((nx, ny), path + [(nx, ny)]))

    # Fallback without avoiding ghosts
    if ghosts:
        return dfs_find_pellet(start, game_map, current_dir, None)
    return []

def get_ghost_distances(game_map, ghosts):
    from collections import deque
    distances = {}
    queue = deque()
    directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]
    
    for g in ghosts:
        if getattr(g, 'state', None) != "FRIGHTENED":
            pos = (g.grid_x, g.grid_y)
            queue.append((pos, 0))
            if pos not in distances:
                distances[pos] = 0
                
            if g.direction != Direction.NONE:
                nx, ny = pos[0] + g.direction[0], pos[1] + g.direction[1]
                if not game_map.is_wall(nx, ny):
                    queue.append(((nx, ny), 0))
                    distances[(nx, ny)] = 0
                    
    while queue:
        pos, dist = queue.popleft()
        for d in directions:
            nx, ny = pos[0] + d[0], pos[1] + d[1]
            if nx < 0: nx = len(game_map.grid[0]) - 1
            elif nx >= len(game_map.grid[0]): nx = 0
            
            if not game_map.is_wall(nx, ny):
                if (nx, ny) not in distances or dist + 1 < distances[(nx, ny)]:
                    distances[(nx, ny)] = dist + 1
                    queue.append(((nx, ny), dist + 1))
    return distances

def pacman_auto_ai_logic(start, game_map, current_dir, ghosts, pacman_speed=2, ghost_speed=2, algorithm="BFS"):
    ghost_dist = get_ghost_distances(game_map, ghosts)
    
    # Common initialization
    visited = {start: 0}
    directions = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]
    
    frightened_ghosts = set()
    for g in ghosts:
        if getattr(g, 'state', None) == "FRIGHTENED":
            frightened_ghosts.add((g.grid_x, g.grid_y))
            
    closest_frightened = None
    closest_power_pellet = None
    closest_pellet = None

    if algorithm == "BFS":
        from collections import deque
        collection = deque([(start, [])])
    elif algorithm == "DFS":
        collection = [(start, [])]
    else: # A*
        import heapq
        targets = frightened_ghosts.union(game_map.power_pellets)
        if not targets:
            targets = set(game_map.pellets)
        
        def heuristic(pos):
            if not targets: return 0
            return min(abs(pos[0]-t[0]) + abs(pos[1]-t[1]) for t in targets)
            
        collection = [(heuristic(start), 0, start, [])]

    while collection:
        if algorithm == "BFS":
            pos, path = collection.popleft()
        elif algorithm == "DFS":
            pos, path = collection.pop()
        else:
            import heapq
            _, _, pos, path = heapq.heappop(collection)

        time = len(path)
        pacman_frames = time * 20 / pacman_speed
        ghost_frames = ghost_dist.get(pos, float('inf')) * 20 / ghost_speed
        
        margin_frames = 10
        if time > 5:
            margin_frames = 20
            
        if time > 0 and pacman_frames >= ghost_frames - margin_frames:
            continue
            
        if pos in frightened_ghosts and closest_frightened is None:
            closest_frightened = path
            if algorithm in ["BFS", "A*"]: break
        if pos in game_map.power_pellets and closest_power_pellet is None:
            closest_power_pellet = path
        if pos in game_map.pellets and closest_pellet is None:
            closest_pellet = path
            
        for d in directions:
            if len(path) == 0 and current_dir != Direction.NONE and d == (-current_dir[0], -current_dir[1]):
                continue
                
            nx, ny = pos[0] + d[0], pos[1] + d[1]
            if nx < 0: nx = len(game_map.grid[0]) - 1
            elif nx >= len(game_map.grid[0]): nx = 0
            
            if not game_map.is_wall(nx, ny):
                new_g = time + 1
                if new_g < visited.get((nx, ny), float('inf')):
                    visited[(nx, ny)] = new_g
                    if algorithm == "BFS" or algorithm == "DFS":
                        collection.append(((nx, ny), path + [d]))
                    else:
                        import heapq
                        h = heuristic((nx, ny))
                        heapq.heappush(collection, (new_g + h, new_g, (nx, ny), path + [d]))

    if closest_frightened is not None:
        return closest_frightened[0] if len(closest_frightened) > 0 else current_dir
    if closest_power_pellet is not None:
        return closest_power_pellet[0] if len(closest_power_pellet) > 0 else current_dir
    if closest_pellet is not None:
        return closest_pellet[0] if len(closest_pellet) > 0 else current_dir
                    
    # SURVIVAL FALLBACK
    valid_dirs = []
    for d in directions:
        if current_dir != Direction.NONE and d == (-current_dir[0], -current_dir[1]):
            continue
        nx, ny = start[0] + d[0], start[1] + d[1]
        if nx < 0: nx = len(game_map.grid[0]) - 1
        elif nx >= len(game_map.grid[0]): nx = 0
        if not game_map.is_wall(nx, ny):
            valid_dirs.append(d)
    if not valid_dirs:
        valid_dirs = [(-current_dir[0], -current_dir[1])]
        
    best_d = valid_dirs[0] if valid_dirs else current_dir
    max_d_score = -1
    for d in valid_dirs:
        nx, ny = start[0] + d[0], start[1] + d[1]
        if nx < 0: nx = len(game_map.grid[0]) - 1
        elif nx >= len(game_map.grid[0]): nx = 0
        dist = ghost_dist.get((nx, ny), float('inf'))
        if dist > max_d_score:
            max_d_score = dist
            best_d = d
            
    return best_d
