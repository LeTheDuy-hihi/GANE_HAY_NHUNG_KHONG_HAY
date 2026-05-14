import random

def generate_symmetric_map(level):
    base_w = 28
    base_h = 31
    
    # Increase map size slightly per level (max out at some point to avoid memory/performance issues)
    w = base_w + (level - 1) * 4
    h = base_h + (level - 1) * 2
    
    if w > 60: w = 60
    if h > 45: h = 45
    
    half_w = w // 2
    
    grid = [['W' for _ in range(half_w)] for _ in range(h)]
    
    # Ghost house geometry
    gh_w = 4 # half width
    gh_h = 5
    cy = h // 2 - 2
    
    for y in range(cy, cy + gh_h):
        for x in range(half_w - gh_w, half_w):
            if y == cy and x == half_w - 2:
                grid[y][x] = '-'
            elif y == cy:
                grid[y][x] = 'W'
            elif y == cy + gh_h - 1:
                grid[y][x] = 'W'
            elif x == half_w - gh_w:
                grid[y][x] = 'W'
            else:
                grid[y][x] = ' ' # Inside house
                
    # Maze Generation (DFS)
    visited = set()
    def in_bounds(x, y):
        # Leave a 1-tile border
        if x <= 0 or x >= half_w or y <= 0 or y >= h - 1:
            return False
        # Avoid ghost house
        if half_w - gh_w - 1 <= x < half_w and cy - 1 <= y <= cy + gh_h:
            return False
        return True
        
    stack = [(1, 1)]
    visited.add((1, 1))
    grid[1][1] = '.'
    
    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in visited:
                neighbors.append((nx, ny, dx//2, dy//2))
                
        if neighbors:
            nx, ny, mx, my = random.choice(neighbors)
            visited.add((nx, ny))
            grid[ny][nx] = '.'
            grid[y + my][x + mx] = '.'
            stack.append((nx, ny))
        else:
            stack.pop()
            
    # Carve loops
    for _ in range(h * w // 15):
        rx = random.randint(1, half_w - 1)
        ry = random.randint(1, h - 2)
        if grid[ry][rx] == 'W' and in_bounds(rx, ry):
            paths = sum(1 for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)] if 0 <= ry+dy < h and 0 <= rx+dx < half_w and grid[ry+dy][rx+dx] == '.')
            if paths >= 2:
                grid[ry][rx] = '.'
                
    # Tunnel removed

    # Construct final full map
    full_map = []
    for y in range(h):
        left_half = grid[y]
        right_half = left_half[::-1]
        
        # Fix ghost gate mirroring
        lh = list(left_half)
        rh = list(right_half)
        if '-' in lh:
            # - is gate. Let's make the 2 center tiles gate
            lh[-1] = '-'
            rh[0] = '-'
            
        row_str = "".join(lh) + "".join(rh)
        full_map.append(row_str)
        
    # Place power pellets
    for rx, ry in [(1,1), (w-2,1), (1,h-2), (w-2,h-2)]:
        # find closest dot
        best_pos = None
        best_d = float('inf')
        for y in range(h):
            for x in range(w):
                if full_map[y][x] == '.':
                    d = abs(x-rx) + abs(y-ry)
                    if d < best_d:
                        best_d = d
                        best_pos = (x, y)
        if best_pos:
            row = list(full_map[best_pos[1]])
            row[best_pos[0]] = 'O'
            full_map[best_pos[1]] = "".join(row)

    # Compute start positions
    starts = {
        "PACMAN": (w // 2, cy + gh_h + 1),
        "BLINKY": (w // 2, cy - 1),
        "PINKY": (w // 2, cy + 2),
        "INKY": (w // 2 - 1, cy + 2),
        "CLYDE": (w // 2 + 1, cy + 2),
    }
    
    # Ensure pacman start is empty
    px, py = starts["PACMAN"]
    if full_map[py][px] == 'W':
        row = list(full_map[py])
        row[px] = ' '
        full_map[py] = "".join(row)
        for dy in range(1, 4):
            if full_map[py+dy][px] != 'W':
                break
            row = list(full_map[py+dy])
            row[px] = ' '
            full_map[py+dy] = "".join(row)

    # Ensure ghost gate exit is clear
    exit_y = cy - 1
    for exit_x in [w//2 - 1, w//2]:
        row = list(full_map[exit_y])
        row[exit_x] = ' '
        full_map[exit_y] = "".join(row)
        # carve upwards until free space
        for dy in range(2, 10):
            check_y = cy - dy
            if check_y < 0: break
            if full_map[check_y][exit_x] != 'W':
                break
            row = list(full_map[check_y])
            row[exit_x] = ' '
            full_map[check_y] = "".join(row)

    # clear house interior
    for gy in range(cy + 1, cy + gh_h - 1):
        for gx in range(w//2 - gh_w + 1, w//2 + gh_w - 1):
            row = list(full_map[gy])
            row[gx] = ' '
            full_map[gy] = "".join(row)
            
    return full_map, starts, w, h
