# World & Camera
WORLD_SIZE = (3000, 3000)
SCROLL_TRIGGER = 0.1  # 10% screen edge trigger for scrolling

# Player & Entities
PLAYER_SPEED = 5
START_HEALTH = 2
MAX_HEALTH = 3
MAX_GARLIC = 3

# Gameplay Mechanics
## Combat
BULLET_SPEED = 10
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
