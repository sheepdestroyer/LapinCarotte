# World & Camera
WORLD_SIZE = (4000, 4000)
SCROLL_TRIGGER = 0.2  # 10% screen edge trigger for scrolling

# Player & Entities
PLAYER_SPEED = 5
START_HEALTH = 2
MAX_HEALTH = 3
MAX_GARLIC = 3
PLAYER_INVINCIBILITY_DURATION = 1  # seconds
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
CARROT_CHASE_RADIUS_SQUARED = CARROT_CHASE_RADIUS ** 2
MAX_SPEED_MULTIPLIER = 3  # For carrot speed scaling

## Vampire
VAMPIRE_SPEED = 4

# UI & Visuals
ITEM_SCALE = 0.5
ITEM_WIDTH = 32
ITEM_HEIGHT = 32
BUTTON_SPACING = 20  # pixels between UI elements
START_SCREEN_BUTTON_START_X_OFFSET = 787
START_SCREEN_BUTTON_START_Y_OFFSET = 742
START_SCREEN_BUTTON_EXIT_X_OFFSET = 787
START_SCREEN_BUTTON_EXIT_Y_OFFSET = 827

# Timing & Animation
FRAME_DELAY = 0.02  # seconds (50 FPS)
EXPLOSION_FLASH_INTERVAL = 0.1  # seconds
EXPLOSION_MAX_FLASHES = 3
VAMPIRE_DEATH_DURATION = 2
VAMPIRE_RESPAWN_TIME = 5
PLAYER_DEATH_DURATION = 2
PLAYER_INVINCIBILITY_FLASH_FREQUENCY = 15 # Flashes per second

# Gameplay
ITEM_DROP_GARLIC_CHANCE = 0.5  # 50% chance
GARLIC_SHOT_ROTATION_SPEED = 5
CARROT_SPAWN_SAFE_RATIO = 3  # Minimum distance from player (1/X of world size)

# Music Configuration
MUSIC_INTRO = 'sounds/intro.mp3'
MUSIC_GAME = 'sounds/Pixel_Power.mp3'
MUSIC_GAMEOVER = 'sounds/gameover.mp3'

# Image dimensions (loaded at runtime, but constants can be defined if they are fixed)
# Assuming garlic image is 32x32 based on ITEM_WIDTH/HEIGHT, adjust if different
GARLIC_WIDTH = 32
GARLIC_HEIGHT = 32

# Asset Fallbacks
PLACEHOLDER_TEXT_COLOR = (255, 255, 255) # White
DEFAULT_PLACEHOLDER_SIZE = (100, 50)

# Asset Configuration: 'path' is mandatory, 'size' (width, height) is optional for placeholders
# Keys should match what AssetManager and main.py expect.
IMAGE_ASSET_CONFIG = {
    # Backgrounds & UI Elements
    'grass': {'path': 'images/grass.png'},
    'start_screen': {'path': 'images/start_screen_final.png', 'size': (1920, 1080)}, # Critical for layout
    'game_over': {'path': 'images/GameOver.png', 'size': (1920, 1080)}, # Critical for layout
    'icon': {'path': 'images/HP.png', 'size': (32, 32)}, # Common icon size
    'crosshair': {'path': 'images/crosshair_1.png'},

    # Player & Entities (Example sizes, should be verified against actual assets)
    'rabbit': {'path': 'images/rabbit.png', 'size': (72, 72)},
    'carrot': {'path': 'images/carrot.png', 'size': (48, 48)},
    'vampire': {'path': 'images/vampire.png', 'size': (84, 84)},

    # Projectiles & Effects
    'bullet': {'path': 'images/bullet.png'},
    'explosion': {'path': 'images/explosion.png'},

    # Items
    'hp': {'path': 'images/HP.png', 'size': (32,32)}, # Often same as icon
    'garlic': {'path': 'images/garlic.png'},
    'carrot_juice': {'path': 'images/carrot_juice.png'},

    # Buttons - using existing keys from AssetManager's old dict
    'restart': {'path': 'images/restart.png'},
    'exit': {'path': 'images/exit.png'},
    'start': {'path': 'images/start.png'},
    'continue_button': {'path': 'images/continue_button.png'}, # New button
    'settings_button': {'path': 'images/settings_button.png'}, # New button

    # Fonts (Digits treated as images)
    'digit_0': {'path': 'fonts/0.png'},
    'digit_1': {'path': 'fonts/1.png'},
    'digit_2': {'path': 'fonts/2.png'},
    'digit_3': {'path': 'fonts/3.png'},
    'digit_4': {'path': 'fonts/4.png'},
    'digit_5': {'path': 'fonts/5.png'},
    'digit_6': {'path': 'fonts/6.png'},
    'digit_7': {'path': 'fonts/7.png'},
    'digit_8': {'path': 'fonts/8.png'},
    'digit_9': {'path': 'fonts/9.png'},
}

# Sound Asset Configuration (path only for now)
SOUND_ASSET_CONFIG = {
    'explosion': 'sounds/explosion.mp3',
    'press_start': 'sounds/press_start.mp3',
    'hurt': 'sounds/hurt.mp3',
    'get_hp': 'sounds/item_hp.mp3',
    'get_garlic': 'sounds/item_garlic.mp3',
    'death': 'sounds/death.mp3',
    'vampire_death': 'sounds/VampireDeath.mp3'
}
