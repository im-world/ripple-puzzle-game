# Configuration constants for Ripple game

# Physics constants
RIPPLE_LIFETIME = 5.0  # seconds
RIPPLE_PROPAGATION_SPEED = 200.0  # pixels/second
RIPPLE_MAX_AMPLITUDE = 1000.0
RIPPLE_DECAY_RATE = 0.3  # exponential decay constant
BALL_MASS = 1.0
BALL_RADIUS = 20.0  # pixels
BALL_FRICTION = 0.98  # per frame multiplier
BALL_MAX_SPEED = 300.0  # pixels/second
STONE_SIZE_RATIO = 0.75
STONE_FLIGHT_TIME_MIN = 0.3  # Minimum flight time in seconds
STONE_FLIGHT_TIME_MAX = 1.0  # Maximum flight time in seconds

# Catapult constants
CATAPULT_MAX_POWER = 600.0  # initial velocity
CATAPULT_MAX_DISTANCE = 200.0  # pixels for full power

# Game constants
INITIAL_STONES = 10
TARGET_FPS = 60
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
WATER_POOL_RECT = (50, 100, 924, 568)  # x, y, width, height

# Colors (pastel zen theme)
COLOR_WATER_LIGHT = (173, 216, 230)  # Light blue
COLOR_WATER_DARK = (135, 206, 235)  # Sky blue
COLOR_BALL = (255, 228, 196)  # Bisque
COLOR_TARGET = (144, 238, 144)  # Light green
COLOR_START = (255, 182, 193)  # Light pink
COLOR_STONE = (169, 169, 169)  # Dark gray
COLOR_UI_TEXT = (70, 70, 70)  # Dark gray
COLOR_TRAJECTORY = (255, 255, 255, 128)  # Semi-transparent white

# Environment themes (6 color themes)
ENVIRONMENT_THEMES = {
    'forest_green': {
        'water_light': (173, 216, 230),
        'water_dark': (135, 206, 235),
        'background': (200, 220, 240),
        'name': 'Forest Green'
    },
    'zen_garden_pink': {
        'water_light': (255, 220, 230),
        'water_dark': (255, 182, 203),
        'background': (255, 240, 245),
        'name': 'Zen Garden Pink'
    },
    'moonlit_blue': {
        'water_light': (150, 170, 200),
        'water_dark': (100, 130, 180),
        'background': (140, 160, 190),
        'name': 'Moonlit Blue'
    },
    'sunset_orange': {
        'water_light': (255, 200, 150),
        'water_dark': (255, 160, 100),
        'background': (255, 220, 180),
        'name': 'Sunset Orange'
    },
    'misty_gray': {
        'water_light': (200, 210, 220),
        'water_dark': (170, 180, 190),
        'background': (210, 220, 230),
        'name': 'Misty Gray'
    },
    'spring_pastel': {
        'water_light': (220, 240, 200),
        'water_dark': (180, 220, 160),
        'background': (230, 250, 220),
        'name': 'Spring Pastel'
    }
}

# Weather effects
WEATHER_EFFECTS = ['none', 'leaves', 'snow', 'rain', 'fireflies']

# Time of day
TIME_OF_DAY = ['day', 'dusk', 'night']

# High-contrast mode colors (for accessibility)
HIGH_CONTRAST_COLORS = {
    'water_light': (255, 255, 255),  # White
    'water_dark': (230, 230, 230),  # Light gray
    'background': (255, 255, 255),  # White
    'ball': (0, 0, 0),  # Black
    'target': (0, 200, 0),  # Bright green
    'start': (200, 0, 0),  # Bright red
    'stone': (50, 50, 50),  # Dark gray
    'ui_text': (0, 0, 0),  # Black
    'trajectory': (0, 0, 0, 200),  # Black with alpha
    'ripple': (0, 100, 200),  # Blue
    'obstacle': (100, 100, 100),  # Gray
    'wall': (80, 80, 80),  # Dark gray
    'current_zone': (0, 150, 255),  # Bright blue
    'whirlpool': (0, 0, 150)  # Dark blue
}
