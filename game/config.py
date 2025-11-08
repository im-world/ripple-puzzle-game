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
