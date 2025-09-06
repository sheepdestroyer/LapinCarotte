# config.py
# This file centralizes all the game's constants and configuration values.
# Modifying these values can alter game mechanics, UI elements, timings, and asset paths
# without needing to change the core game logic.
#
# *Ce fichier centralise toutes les constantes et valeurs de configuration du jeu.*
# *Modifier ces valeurs peut altérer les mécanismes de jeu, les éléments d'interface,*
# *les timings et les chemins d'accès aux ressources sans avoir à modifier la logique principale du jeu.*

# World & Camera
# *Monde et Caméra*
WORLD_SIZE = (4000, 4000)  # Total size of the game world in pixels / *Taille totale du monde du jeu en pixels*
SCROLL_TRIGGER = 0.2  # Percentage of screen edge to trigger scrolling / *Pourcentage du bord de l'écran pour déclencher le défilement*

# Player & Entities
# *Joueur et Entités*
PLAYER_SPEED = 5  # Player movement speed / *Vitesse de déplacement du joueur*
START_HEALTH = 2  # Initial health of the player / *Santé initiale du joueur*
MAX_HEALTH = 3  # Maximum health the player can have / *Santé maximale que le joueur peut avoir*
MAX_GARLIC = 3  # Maximum garlic items the player can hold / *Nombre maximal d'aulx que le joueur peut tenir*
PLAYER_INVINCIBILITY_DURATION = 1  # Duration of invincibility after taking damage, in seconds / *Durée de l'invincibilité après avoir subi des dégâts, en secondes*
MAX_CARROT_JUICE = 999  # Practical cap for carrot juice collected / *Limite pratique pour le jus de carotte collecté*

# Gameplay Mechanics
# *Mécanismes de Jeu*
## Combat
BULLET_SPEED = 4  # Speed of player's bullets / *Vitesse des projectiles du joueur*
GARLIC_SHOT_SPEED = 5  # Speed of the garlic special attack / *Vitesse de l'attaque spéciale à l'ail*
GARLIC_SHOT_DURATION = 3  # Duration the garlic shot stays active, in seconds / *Durée pendant laquelle le tir d'ail reste actif, en secondes*
GARLIC_SHOT_MAX_TRAVEL = 250  # Maximum distance the garlic shot can travel, in pixels / *Distance maximale que le tir d'ail peut parcourir, en pixels*
GARLIC_ROTATION_SPEED = 5  # Rotation speed of the garlic shot, in degrees per frame / *Vitesse de rotation du tir d'ail, en degrés par frame*

## Carrots
# *Carottes (Ennemis)*
CARROT_COUNT = 5  # Number of carrot enemies in the game / *Nombre de carottes ennemies dans le jeu*
CARROT_SPEED = 3  # Base speed of carrot enemies / *Vitesse de base des carottes ennemies*
CARROT_RESPAWN_DELAY = 3  # Delay before a carrot respawns after being defeated, in seconds / *Délai avant la réapparition d'une carotte après avoir été vaincue, en secondes*
CARROT_DETECTION_RADIUS = 200  # Radius within which carrots detect the player / *Rayon dans lequel les carottes détectent le joueur*
CARROT_CHASE_RADIUS = 100  # Radius within which carrots will actively chase the player / *Rayon dans lequel les carottes poursuivront activement le joueur*
CARROT_CHASE_RADIUS_SQUARED = CARROT_CHASE_RADIUS ** 2 # Squared chase radius for performance (avoid sqrt) / *Rayon de poursuite au carré pour la performance (éviter sqrt)*
MAX_SPEED_MULTIPLIER = 3  # Maximum speed multiplier for carrots when close to player / *Multiplicateur de vitesse maximal pour les carottes proches du joueur*

## Vampire
# *Vampire (Ennemi Spécial)*
VAMPIRE_SPEED = 4  # Speed of the vampire enemy / *Vitesse de l'ennemi vampire*

# UI & Visuals
# *Interface Utilisateur et Visuels*
ITEM_SCALE = 0.5  # Scale factor for collectible items / *Facteur d'échelle pour les objets collectables*
ITEM_WIDTH = 32  # Default width for item sprites (used for calculations if needed) / *Largeur par défaut des sprites d'objets (utilisée pour les calculs si nécessaire)*
ITEM_HEIGHT = 32 # Default height for item sprites / *Hauteur par défaut des sprites d'objets*
BUTTON_SPACING = 20  # Spacing between UI buttons, in pixels / *Espacement entre les boutons de l'interface utilisateur, en pixels*
START_SCREEN_BUTTON_START_X_OFFSET = 787  # X offset for the Start button on the start screen / *Décalage X pour le bouton Start sur l'écran de démarrage*
START_SCREEN_BUTTON_START_Y_OFFSET = 742  # Y offset for the Start button on the start screen / *Décalage Y pour le bouton Start sur l'écran de démarrage*
START_SCREEN_BUTTON_EXIT_X_OFFSET = 787   # X offset for the Exit button on the start screen / *Décalage X pour le bouton Exit sur l'écran de démarrage*
START_SCREEN_BUTTON_EXIT_Y_OFFSET = 827   # Y offset for the Exit button on the start screen / *Décalage Y pour le bouton Exit sur l'écran de démarrage*

# Timing & Animation
# *Temporisation et Animation*
FRAME_DELAY = 0.02  # Delay per frame, aiming for 50 FPS (1/50 = 0.02) / *Délai par frame, visant 50 FPS (1/50 = 0.02)*
EXPLOSION_FLASH_INTERVAL = 0.1  # Interval between explosion flashes, in seconds / *Intervalle entre les flashs d'explosion, en secondes*
EXPLOSION_MAX_FLASHES = 3  # Number of flashes for an explosion effect / *Nombre de flashs pour un effet d'explosion*
VAMPIRE_DEATH_DURATION = 2  # Duration of the vampire death effect, in seconds / *Durée de l'effet de mort du vampire, en secondes*
VAMPIRE_RESPAWN_TIME = 5  # Time before the vampire respawns, in seconds / *Temps avant la réapparition du vampire, en secondes*
PLAYER_DEATH_DURATION = 2  # Duration of the player death effect, in seconds / *Durée de l'effet de mort du joueur, en secondes*
PLAYER_INVINCIBILITY_FLASH_FREQUENCY = 15 # Frequency of player flashing when invincible, in flashes per second / *Fréquence du clignotement du joueur lorsqu'il est invincible, en flashs par seconde*

# Gameplay
# *Jouabilité (Autres)*
ITEM_DROP_GARLIC_CHANCE = 0.5  # Chance for a defeated enemy to drop a garlic item (0.0 to 1.0) / *Chance qu'un ennemi vaincu laisse tomber un ail (0.0 à 1.0)*
GARLIC_SHOT_ROTATION_SPEED = 5 # Visual rotation speed of the garlic item when shot / *Vitesse de rotation visuelle de l'ail lorsqu'il est tiré*
CARROT_SPAWN_SAFE_RATIO = 3  # Minimum distance from player for carrot spawn (world_size / ratio) / *Distance minimale par rapport au joueur pour l'apparition des carottes (taille_monde / ratio)*

# Music Configuration
# *Configuration de la Musique*
MUSIC_INTRO = 'sounds/intro.mp3'  # Path to intro music file / *Chemin vers le fichier de musique d'introduction*
MUSIC_GAME = 'sounds/Pixel_Power.mp3'  # Path to main game music file / *Chemin vers le fichier de musique principal du jeu*
MUSIC_GAMEOVER = 'sounds/gameover.mp3' # Path to game over music file / *Chemin vers le fichier de musique de game over*

# Image dimensions (loaded at runtime, but constants can be defined if they are fixed)
# *Dimensions des images (chargées à l'exécution, mais des constantes peuvent être définies si elles sont fixes)*
# Assuming garlic image is 32x32 based on ITEM_WIDTH/HEIGHT, adjust if different
# *En supposant que l'image de l'ail est de 32x32 d'après ITEM_WIDTH/HEIGHT, ajustez si différent*
GARLIC_WIDTH = ITEM_WIDTH  # Use ITEM_WIDTH for consistency / *Utiliser ITEM_WIDTH pour la cohérence*
GARLIC_HEIGHT = ITEM_HEIGHT # Use ITEM_HEIGHT for consistency / *Utiliser ITEM_HEIGHT pour la cohérence*

# Asset Fallbacks
# *Ressources de Remplacement (Fallback)*
PLACEHOLDER_TEXT_COLOR = (255, 255, 255) # White color for text on placeholders / *Couleur blanche pour le texte sur les images de remplacement*
PLACEHOLDER_BG_COLOR = (0, 0, 255)     # Blue background color for placeholder images / *Couleur de fond bleue pour les images de remplacement*
DEFAULT_PLACEHOLDER_SIZE = (100, 50)   # Default size for placeholder images if original size is unknown / *Taille par défaut pour les images de remplacement si la taille originale est inconnue*
PLACEHOLDER_FONT_SIZE = 20 # Font size for text on placeholders / *Taille de police de remplacement*

# Asset Configuration: 'path' is mandatory, 'size' (width, height) is optional for placeholders.
# Keys should match what AssetManager and main.py expect for loading.
#
# *Configuration des Ressources : 'path' (chemin) est obligatoire, 'size' (taille : largeur, hauteur) est optionnel pour les images de remplacement.*
# *Les clés doivent correspondre à ce que AssetManager et main.py attendent pour le chargement.*
IMAGE_ASSET_CONFIG = {
    # Backgrounds & UI Elements / *Arrière-plans et Éléments d'UI*
    'grass': {'path': 'images/grass.png'},
    'start_screen': {'path': 'images/start_screen_final.png', 'size': (1920, 1080)}, # Critical for layout / *Crucial pour la mise en page*
    'game_over': {'path': 'images/GameOver.png', 'size': (1920, 1080)}, # Critical for layout / *Crucial pour la mise en page*
    'icon': {'path': 'images/HP.png', 'size': (32, 32)}, # Common icon size / *Taille commune pour une icône*
    'crosshair': {'path': 'images/crosshair_1.png'},

    # Player & Entities (Example sizes, should be verified against actual assets)
    # *Joueur et Entités (Tailles d'exemple, à vérifier par rapport aux ressources réelles)*
    'rabbit': {'path': 'images/rabbit.png', 'size': (72, 72)},
    'carrot': {'path': 'images/carrot.png', 'size': (48, 48)},
    'vampire': {'path': 'images/vampire.png', 'size': (84, 84)},

    # Projectiles & Effects / *Projectiles et Effets*
    'bullet': {'path': 'images/bullet.png'},
    'explosion': {'path': 'images/explosion.png'},

    # Items / *Objets*
    'hp': {'path': 'images/HP.png', 'size': (32,32)}, # Often same as icon / *Souvent identique à l'icône*
    'garlic': {'path': 'images/garlic.png'},
    'carrot_juice': {'path': 'images/carrot_juice.png'},

    # Buttons - using existing keys from AssetManager's old dict
    # *Boutons - utilisant les clés existantes de l'ancien dictionnaire d'AssetManager*
    'restart': {'path': 'images/restart.png'},
    'exit': {'path': 'images/exit.png'},
    'start': {'path': 'images/start.png'},
    'continue_button': {'path': 'images/continue_button.png'}, # New button / *Nouveau bouton*
    'settings_button': {'path': 'images/settings_button.png'}, # New button / *Nouveau bouton*

    # Fonts (Digits treated as images)
    # *Polices (Chiffres traités comme des images)*
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
# *Configuration des Ressources Sonores (chemin uniquement pour l'instant)*
SOUND_ASSET_CONFIG = {
    'explosion': 'sounds/explosion.mp3',
    'press_start': 'sounds/press_start.mp3',
    'hurt': 'sounds/hurt.mp3',
    'get_hp': 'sounds/item_hp.mp3',
    'get_garlic': 'sounds/item_garlic.mp3',
    'death': 'sounds/death.mp3',
    'vampire_death': 'sounds/VampireDeath.mp3'
}
