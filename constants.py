import arcade

WINDOW_TITLE = "Asteroid Smasher"
STARTING_ASTEROID_COUNT = 5
SCALE = 0.5

# Screen dimensions and limits
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
OFFSCREEN_SPACE = 50

# Control player speed
TURN_SPEED = 5
THRUST_AMOUNT = 0.35
MAX_SPEED = 6.0
DRAG = 0.02

# Asteroid types
ASTEROID_TYPE_BIG = 3
ASTEROID_TYPE_MEDIUM = 2
ASTEROID_TYPE_SMALL = 1

# УРОН от астероидов
ASTEROID_DAMAGE = {
    ASTEROID_TYPE_BIG: 3,
    ASTEROID_TYPE_MEDIUM: 2,
    ASTEROID_TYPE_SMALL: 1,
}

# Background types
BACKGROUND_SPACE = 0
BACKGROUND_NEBULA = 1
BACKGROUND_STARS = 2
BACKGROUND_GALAXY = 3
BACKGROUND_COUNT = 4
BACKGROUND_NAMES = ["🌌 Космос", "🌫️ Туманность", "⭐ Звездное поле", "🌠 Галактика"]
BACKGROUND_COLORS = [
    (0, 0, 0),
    (20, 0, 40),
    (10, 10, 30),
    (40, 20, 60)
]

# Difficulty settings
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2
DIFFICULTY_NAMES = ["🌟 EASY", "⚡ NORMAL", "💀 HARD"]
DIFFICULTY_COLORS = [
    arcade.color.GREEN,
    arcade.color.ORANGE,
    arcade.color.RED
]