class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

# Classic Arcade Colors
BLACK = (0, 0, 0)
CYAN = (25, 25, 255)       # Neon Maze Walls #1919FF
YELLOW = (255, 255, 0)     # Pac-Man
PEACH = (255, 184, 255)    # Pellets
WHITE = (255, 255, 255)    # White (Score, text)
RED = (255, 0, 0)          # Blinky
PINK = (255, 184, 255)     # Pinky
INKY_CYAN = (0, 255, 255)  # Inky
ORANGE = (255, 184, 82)    # Clyde
BLUE_GHOST = (0, 50, 255)  # Frightened State
WHITE_GHOST = (200, 200, 255) # Frightened Flash

# Advanced Ghost Colors
PURPLE = (160, 32, 240)    # Patroller
GRAY = (150, 150, 150)     # Lurker
LEMON = (204, 255, 0)      # Trapper
GREEN = (0, 255, 0)        # Predictor
DARK_GRAY = (80, 80, 80)   # Teleporter
GOLD = (255, 215, 0)       # Commander
DARK_RED = (150, 0, 0)     # Shadow

TILE_SIZE = 20 # Smaller tile to fit 28x31 map on screen
FPS = 60
SCORE_HEIGHT_TOP = 50
SCORE_HEIGHT_BOTTOM = 40

# Arcade Map 28x31
RAW_MAP = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "W............WW............W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "WO...W.WWWWW.WW.WWWWW.W...OW",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W..........................W",
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",
    "W......WW....WW....WW......W",
    "WWWWWW.WWWWW WW WWWWW.WWWWWW",
    "W     .WWWWW WW WWWWW.     W",
    "W     .WW          WW.     W",
    "W     .WW WWW--WWW WW.     W",
    "WWWWWW.WW W      W WW.WWWWWW",
    "W     .   W      W   .     W",
    "WWWWWW.WW W      W WW.WWWWWW",
    "W     .WW WWWWWWWW WW.     W",
    "W     .WW          WW.     W",
    "W     .WW WWWWWWWW WW.     W",
    "WWWWWW.WW WWWWWWWW WW.WWWWWW",
    "W............WW............W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "WO..WW.......  .......WW..OW",
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",
    "W......WW....WW....WW......W",
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",
    "W..........................W",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW"
]

GRID_WIDTH = len(RAW_MAP[0])
GRID_HEIGHT = len(RAW_MAP)
WIDTH = GRID_WIDTH * TILE_SIZE
HEIGHT = GRID_HEIGHT * TILE_SIZE + SCORE_HEIGHT_TOP + SCORE_HEIGHT_BOTTOM

# Speeds
PACMAN_SPEED = 2
GHOST_SPEED = 2
FRIGHTENED_SPEED = 1

# Start positions
PACMAN_START = (13, 23)
BLINKY_START = (13, 11)
PINKY_START = (13, 14)
INKY_START = (11, 14)
CLYDE_START = (15, 14)

# Scatter targets
BLINKY_SCATTER = (25, 1)
PINKY_SCATTER = (2, 1)
INKY_SCATTER = (27, 29)
CLYDE_SCATTER = (0, 29)
