# World & Camera
WORLD_SIZE = (4000, 4000)
SCROLL_TRIGGER = 0.2  # 10% screen edge trigger for scrolling

# Player & Entities
PLAYER_SPEED = 5
START_HEALTH = 2
MAX_HEALTH = 3
MAX_GARLIC = 3
MAX_CARROT_JUICE = 999  # Practical "infinite" cap

# Gameplay Mechanics
## Combat
BULLET_SPEED = 4
GARLIC_SHOT_SPEED = 5
GARLIC_SHOT_DURATION = 3  # seconds
GARLIC_SHOT_MAX_TRAVEL = 250  # pixels
GARLIC_ROTATION_SPEED = 5  # degrees per frame

## Carrots
CARROT_COUNT = 5
CARROT_SPEED = 3
CARROT_RESPAWN_DELAY = 3  # seconds
CARROT_DETECTION_RADIUS = 200
CARROT_CHASE_RADIUS = 100
MAX_SPEED_MULTIPLIER = 3  # For carrot speed scaling

## Vampire
VAMPIRE_SPEED = 4

# UI & Visuals
ITEM_SCALE = 0.5
ITEM_WIDTH = 32
ITEM_HEIGHT = 32
BUTTON_SPACING = 20  # pixels between UI elements

# Timing & Animation
FRAME_DELAY = 0.02  # seconds (50 FPS)
EXPLOSION_FLASH_INTERVAL = 0.1  # seconds
EXPLOSION_MAX_FLASHES = 3
VAMPIRE_DEATH_DURATION = 2
VAMPIRE_RESPAWN_TIME = 5
PLAYER_DEATH_DURATION = 2

# Gameplay
ITEM_DROP_GARLIC_CHANCE = 0.5  # 50% chance
GARLIC_SHOT_ROTATION_SPEED = 5
CARROT_SPAWN_SAFE_RATIO = 3  # Minimum distance from player (1/X of world size)

# Music Configuration
MUSIC_INTRO = 'sounds/intro.mp3'
MUSIC_GAME = 'sounds/Pixel_Power.mp3'
MUSIC_GAMEOVER = 'sounds/gameover.mp3'
