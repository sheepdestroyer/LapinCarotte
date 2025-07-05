#!/usr/bin/env python3
# main.py
# This is the main executable file for the LapinCarotte game.
# It handles game initialization (Pygame, assets, game state), command-line argument parsing,
# the main game loop, event handling, and transitions between different game states
# (start screen, active game, pause screen, game over). It supports both GUI and CLI modes.
#
# *Ceci est le fichier exécutable principal pour le jeu LapinCarotte.*
# *Il gère l'initialisation du jeu (Pygame, ressources, état du jeu), l'analyse des arguments
# *de la ligne de commande, la boucle de jeu principale, la gestion des événements et les
# *transitions entre les différents états du jeu (écran de démarrage, jeu actif, écran de pause, game over).*
# *Il prend en charge les modes GUI et CLI.*

import os
import argparse
import pygame
import time
import logging
import sys
import random
import math
import config
from asset_manager import AssetManager, DummySound # Import DummySound
from game_entities import Player, Bullet, Carrot, Vampire, Explosion, Collectible, Button
from game_state import GameState
from config import * # Import all constants from config.py / *Importer toutes les constantes de config.py*

def get_asset_path(relative_path):
    """
    Constructs the absolute path to an asset, correctly handling running from source vs. frozen executable.
    This function is duplicated in asset_manager.py; consider centralizing if behavior is identical.
    Args:
        relative_path (str): The path relative to the 'Assets' directory (e.g., 'images/player.png').
                             *Le chemin relatif au répertoire 'Assets' (par ex. 'images/player.png').*
    Returns:
        str: The absolute path to the asset.
             *Le chemin absolu vers la ressource.*

    *Construit le chemin absolu vers une ressource, gérant correctement l'exécution depuis les sources*
    *par rapport à un exécutable figé. Cette fonction est dupliquée dans asset_manager.py ;*
    *envisager de la centraliser si le comportement est identique.*
    *Args:*
        *relative_path (str): Le chemin relatif au répertoire 'Assets' (par ex. 'images/player.png').*
    *Returns:*
        *str: Le chemin absolu vers la ressource.*
    """
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle/frozen executable (e.g., PyInstaller)
        # *Si l'application est exécutée en tant que bundle/exécutable figé (par ex. PyInstaller)*
        base_path = sys._MEIPASS
    else:
        # If run from source code / *Si exécuté depuis le code source*
        base_path = os.path.abspath(".")
    # This version assumes the 'Assets' folder is a subdirectory from where the script is,
    # or where PyInstaller unpacks it. If asset_manager.py's version is different, align them.
    # *Cette version suppose que le dossier 'Assets' est un sous-répertoire de l'emplacement du script,*
    # *ou de l'endroit où PyInstaller le décompresse. Si la version de asset_manager.py est différente, alignez-les.*
    return os.path.join(base_path, 'Assets', relative_path) # Original main.py didn't have 'Assets' here, but AssetManager does.
                                                            # Standardizing to include 'Assets' as per AssetManager's _get_path.
                                                            # *L'original main.py n'avait pas 'Assets' ici, mais AssetManager l'a.*
                                                            # *Standardisation pour inclure 'Assets' conformément à _get_path d'AssetManager.*

# Argument parsing / *Analyse des arguments*
parser = argparse.ArgumentParser(description="LapinCarotte - A game about a rabbit fighting vampire carrots. / *Un jeu sur un lapin combattant des carottes vampires.*")
parser.add_argument("--cli", action="store_true", help="Run the game in Command Line Interface mode (no graphics). / *Exécuter le jeu en mode Interface en Ligne de Commande (sans graphismes).*")
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging output. / *Activer la sortie de journalisation de débogage.*")
args = parser.parse_args()

# Initialize screen and dimensions / *Initialiser l'écran et les dimensions*
screen = None # Pygame screen surface / *Surface de l'écran Pygame*
screen_width, screen_height = 0, 0 # Screen dimensions / *Dimensions de l'écran*

if not args.cli:
    pygame.init() # Initialize all pygame modules needed for GUI mode / *Initialiser tous les modules Pygame nécessaires pour le mode GUI*
    os.environ['SDL_VIDEO_CENTERED'] = '1' # Center the game window / *Centrer la fenêtre de jeu*
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    screen_width, screen_height = screen.get_size()
    pygame.mouse.set_visible(False) # Hide the system mouse cursor / *Masquer le curseur système de la souris*
# else: # This print is handled by initial logging config now / *Ce print est géré par la configuration initiale de journalisation maintenant*
    # logging.info("Running in CLI mode.")
    # logging.info("Exécution en mode CLI.")

asset_manager = AssetManager(cli_mode=args.cli)
asset_manager.load_assets()

if not args.cli and screen and 'icon' in asset_manager.images and hasattr(asset_manager.images['icon'], 'get_rect'): # Check if icon is a surface
    pygame.display.set_icon(asset_manager.images['icon'])

# Set AppUserModelID for Windows to ensure icon is displayed correctly in taskbar
# *Définir AppUserModelID pour Windows pour assurer l'affichage correct de l'icône dans la barre des tâches*
if sys.platform == 'win32' and not args.cli:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('LapinCarotte.LapinCarotte.Game.1.0') # Unique ID for the app / *ID unique pour l'application*
    pygame.display.set_caption("LapinCarotte", "LapinCarotte") # Set window title and icon name / *Définir le titre de la fenêtre et le nom de l'icône*

game_state = GameState(asset_manager, cli_mode=args.cli)

# Graphics-dependent initializations (defaults for CLI)
# *Initialisations dépendantes des graphismes (par défaut pour CLI)*
start_screen_image = None # Surface for the start screen background / *Surface pour l'arrière-plan de l'écran de démarrage*
start_screen_pos = (0,0)  # Top-left position of the start screen image / *Position en haut à gauche de l'image de l'écran de démarrage*

# Rects for button positioning, initialized to default for CLI
# *Rects pour le positionnement des boutons, initialisés par défaut pour CLI*
# These are primarily used to get dimensions if buttons are created before screen size is known,
# or for layout calculations. Actual button instances store their own rects.
# *Ceux-ci sont principalement utilisés pour obtenir les dimensions si les boutons sont créés avant que la taille de l'écran ne soit connue,*
# *ou pour les calculs de mise en page. Les instances réelles des boutons stockent leurs propres rects.*
restart_button_rect = pygame.Rect(0,0,0,0)
exit_button_rect = pygame.Rect(0,0,0,0)
start_button_rect = pygame.Rect(0,0,0,0)
continue_button_rect = pygame.Rect(0,0,0,0)
settings_button_rect = pygame.Rect(0,0,0,0)

# Other image rects, initialized to default for CLI (mostly for potential dimension access if needed early)
# *Autres rects d'image, initialisés par défaut pour CLI (principalement pour un accès potentiel aux dimensions si nécessaire tôt)*
carrot_rect = pygame.Rect(0,0,0,0) # Example, likely not used this way / *Exemple, probablement pas utilisé de cette façon*
vampire_rect = pygame.Rect(0,0,0,0)
hp_rect = pygame.Rect(0,0,0,0)
game_over_rect = pygame.Rect(0,0,0,0)

# Image surfaces for UI drawing in GUI, initialized to None for CLI
# *Surfaces d'image pour le dessin de l'UI en GUI, initialisées à None pour CLI*
grass_image = None        # Single grass tile image / *Image d'une seule tuile d'herbe*
garlic_image = None       # Image for garlic projectile/item (used in main_loop GUI path) / *Image pour projectile/objet ail (utilisée dans le chemin GUI de main_loop)*
hp_image_ui = None        # Image for representing player health in UI / *Image pour représenter la santé du joueur dans l'UI*
game_over_image_ui = None # Background image for game over screen / *Image de fond pour l'écran de game over*

# Button image surfaces (these will be dicts in CLI mode, actual surfaces in GUI)
# Their direct use as surfaces is only in GUI mode.
# *Surfaces d'image des boutons (ce seront des dicts en mode CLI, des surfaces réelles en mode GUI)*
# *Leur utilisation directe en tant que surfaces n'est qu'en mode GUI.*
start_button_img = asset_manager.images.get('start') # Use .get for safety if asset loading fails
exit_button_img = asset_manager.images.get('exit')
restart_button_img = asset_manager.images.get('restart')
continue_button_img = asset_manager.images.get('continue_button')
settings_button_img = asset_manager.images.get('settings_button')

grass_background = None   # Pre-rendered surface of tiled grass for the world background / *Surface pré-rendue d'herbe en tuiles pour l'arrière-plan du monde*


if not args.cli:
    # Load images that are directly used for UI composition or require their rects early
    # *Charger les images qui sont directement utilisées pour la composition de l'UI ou qui nécessitent leurs rects tôt*
    start_screen_image = asset_manager.images.get('start_screen')
    if start_screen_image and hasattr(start_screen_image, 'get_width') and hasattr(start_screen_image, 'get_height'):
        start_screen_pos = (
            (screen_width - start_screen_image.get_width()) // 2,
            (screen_height - start_screen_image.get_height()) // 2
        )

    # Get rects for button dimension/layout if needed, from loaded assets
    # *Obtenir les rects pour les dimensions/mise en page des boutons si nécessaire, à partir des ressources chargées*
    # This assumes the asset_manager.images contains actual Surface objects for these keys in GUI mode
    # *Cela suppose que asset_manager.images contient des objets Surface réels pour ces clés en mode GUI*
    _restart_img_temp = asset_manager.images.get('restart')
    if _restart_img_temp and hasattr(_restart_img_temp, 'get_rect'): restart_button_rect = _restart_img_temp.get_rect()

    _exit_img_temp = asset_manager.images.get('exit')
    if _exit_img_temp and hasattr(_exit_img_temp, 'get_rect'): exit_button_rect = _exit_img_temp.get_rect()

    _start_img_temp = asset_manager.images.get('start')
    if _start_img_temp and hasattr(_start_img_temp, 'get_rect'): start_button_rect = _start_img_temp.get_rect()

    _continue_img_temp = asset_manager.images.get('continue_button')
    if _continue_img_temp and hasattr(_continue_img_temp, 'get_rect'): continue_button_rect = _continue_img_temp.get_rect()

    _settings_img_temp = asset_manager.images.get('settings_button')
    if _settings_img_temp and hasattr(_settings_img_temp, 'get_rect'): settings_button_rect = _settings_img_temp.get_rect()

    # These rects seem to be for placeholder dimensions, actual entities will have their own rects
    # *Ces rects semblent être pour des dimensions de substitution, les entités réelles auront leurs propres rects*
    # _carrot_img_temp = asset_manager.images.get('carrot')
    # if _carrot_img_temp and hasattr(_carrot_img_temp, 'get_rect'): carrot_rect = _carrot_img_temp.get_rect()
    # ... and so on for vampire_rect, hp_rect, game_over_rect if used this way.

    grass_image = asset_manager.images.get('grass')
    if grass_image and hasattr(grass_image, 'get_size'): # Check if it's a surface / *Vérifier si c'est une surface*
        grass_background = pygame.Surface(WORLD_SIZE, pygame.SRCALPHA)
        _grass_w, _grass_h = grass_image.get_size()
        if _grass_w > 0 and _grass_h > 0: # Avoid division by zero if grass asset is invalid / *Éviter la division par zéro si la ressource herbe est invalide*
            for x_g in range(0, WORLD_SIZE[0], _grass_w):
                for y_g in range(0, WORLD_SIZE[1], _grass_h):
                    grass_background.blit(grass_image, (x_g, y_g))
        else:
            logging.warning("Grass asset has invalid dimensions, cannot tile background.")
            # EN: Grass asset has invalid dimensions, cannot tile background.
            # FR: La ressource d'herbe a des dimensions invalides, impossible de carreler l'arrière-plan.
            grass_background.fill((0,100,0)) # Fallback to solid green / *Fallback vers un vert uni*


    garlic_image = asset_manager.images.get('garlic') # Used for garlic shot visuals / *Utilisé pour les visuels du tir d'ail*
    hp_image_ui = asset_manager.images.get('hp')       # Used for drawing health UI / *Utilisé pour dessiner l'UI de santé*
    game_over_image_ui = asset_manager.images.get('game_over') # Background for game over / *Arrière-plan pour game over*

    # Initialize and play intro music / *Initialiser et jouer la musique d'intro*
    if pygame.mixer.get_init(): # Check if mixer is initialized / *Vérifier si le mixeur est initialisé*
        try:
            intro_music_path = asset_manager._get_path(config.MUSIC_INTRO) # Use AssetManager's path getter
                                                                           # *Utiliser le getter de chemin d'AssetManager*
            pygame.mixer.music.load(intro_music_path)
            pygame.mixer.music.play(-1) # Play indefinitely / *Jouer indéfiniment*
        except pygame.error as e:
            logging.warning(f"Could not load or play intro music: {e}")
            # EN: Could not load or play intro music: {e}
            # FR: Impossible de charger ou de jouer la musique d'intro : {e}
    else:
        logging.warning("Pygame mixer not initialized, skipping music.")
        # EN: Pygame mixer not initialized, skipping music.
        # FR: Mixeur Pygame non initialisé, musique ignorée.


# Global variable for current time, updated each frame in GUI mode.
# CLI mode manages its own time for simulated delays if any.
# *Variable globale pour l'heure actuelle, mise à jour à chaque frame en mode GUI.*
# *Le mode CLI gère son propre temps pour les délais simulés, le cas échéant.*
current_time = 0.0

def _play_game_music_and_sound(sound_to_play=None):
    """
    Helper function to switch to main game music and optionally play a sound effect.
    Only active in GUI mode with an initialized mixer.
    Args:
        sound_to_play (str, optional): Key of the sound effect in asset_manager.sounds to play.
                                       *Clé de l'effet sonore dans asset_manager.sounds à jouer.*

    *Fonction utilitaire pour passer à la musique principale du jeu et jouer optionnellement un effet sonore.*
    *Active uniquement en mode GUI avec un mixeur initialisé.*
    *Args:*
        *sound_to_play (str, optionnel): Clé de l'effet sonore dans asset_manager.sounds à jouer.*
    """
    if args.cli or not pygame.mixer.get_init(): return # No sound in CLI or if mixer not ready
                                                       # *Pas de son en CLI ou si le mixeur n'est pas prêt*
    try:
        pygame.mixer.music.stop()
        game_music_path = asset_manager._get_path(config.MUSIC_GAME)
        pygame.mixer.music.load(game_music_path)
        pygame.mixer.music.play(-1) # Loop game music / *Jouer la musique du jeu en boucle*
        if sound_to_play and sound_to_play in asset_manager.sounds:
            sound_effect = asset_manager.sounds[sound_to_play]
            if not isinstance(sound_effect, DummySound): # Ensure it's a real sound object
                                                          # *S'assurer que c'est un véritable objet son*
                 sound_effect.play()
    except pygame.error as e:
        logging.exception(f"Could not load or play game music/sound: {e}")
        # EN: Could not load or play game music/sound: {e}
        # FR: Impossible de charger ou de jouer la musique/le son du jeu : {e}

def start_game():
    """
    Callback function to start the game. Sets game_state.started to True and plays start sound.
    *Fonction de rappel pour démarrer le jeu. Met game_state.started à True et joue le son de démarrage.*
    """
    logging.debug("start_game called.")
    # EN: start_game called.
    # FR: start_game appelé.
    game_state.started = True
    if not args.cli: _play_game_music_and_sound('press_start')
    else: logging.info("Game started (CLI).")
    # EN: Game started (CLI).
    # FR: Jeu démarré (CLI).
    logging.debug(f"game_state.started set to {game_state.started}")
    # EN: game_state.started set to {game_state.started}
    # FR: game_state.started défini sur {game_state.started}


def reset_game():
    """
    Callback function to reset the game state for a new game.
    *Fonction de rappel pour réinitialiser l'état du jeu pour une nouvelle partie.*
    """
    logging.debug("reset_game called.")
    # EN: reset_game called.
    # FR: reset_game appelé.
    game_state.reset()
    if not args.cli: _play_game_music_and_sound('press_start') # Play start sound again on reset
                                                              # *Jouer à nouveau le son de démarrage lors de la réinitialisation*
    else: logging.info("Game reset (CLI).")
    # EN: Game reset (CLI).
    # FR: Jeu réinitialisé (CLI).
    logging.debug("Game state reset by reset_game function.")
    # EN: Game state reset by reset_game function.
    # FR: État du jeu réinitialisé par la fonction reset_game.


def quit_game():
    """
    Callback function to quit the game. Sets the global 'running' flag to False.
    *Fonction de rappel pour quitter le jeu. Met l'indicateur global 'running' à False.*
    """
    logging.debug("quit_game called.")
    # EN: quit_game called.
    # FR: quit_game appelé.
    global running
    running = False
    if args.cli: logging.info("Exiting game (CLI).")
    # EN: Exiting game (CLI).
    # FR: Sortie du jeu (CLI).
    else: logging.info("Exiting game (GUI).")
    # EN: Exiting game (GUI).
    # FR: Sortie du jeu (GUI).
    logging.debug("Global 'running' flag set to False.")
    # EN: Global 'running' flag set to False.
    # FR: Indicateur global 'running' défini sur False.

def resume_game_callback():
    """
    Callback function to resume the game if it was paused.
    *Fonction de rappel pour reprendre le jeu s'il était en pause.*
    """
    logging.debug("resume_game_callback called.")
    # EN: resume_game_callback called.
    # FR: resume_game_callback appelé.
    if game_state.paused:
        logging.debug("Game was paused, calling game_state.resume_game()")
        # EN: Game was paused, calling game_state.resume_game()
        # FR: Le jeu était en pause, appel de game_state.resume_game()
        game_state.resume_game() # GameState handles logging the resume internally
                                 # *GameState gère la journalisation de la reprise en interne*
        if args.cli: logging.info("Game resumed via callback (CLI).")
        # EN: Game resumed via callback (CLI).
        # FR: Jeu repris via rappel (CLI).
    else:
        logging.debug("Game was not paused, resume_game_callback did nothing.")
        # EN: Game was not paused, resume_game_callback did nothing.
        # FR: Le jeu n'était pas en pause, resume_game_callback n'a rien fait.

def open_settings_callback():
    """
    Callback for the settings button. Currently a placeholder.
    *Rappel pour le bouton des paramètres. Actuellement un placeholder.*
    """
    logging.debug("open_settings_callback called.")
    # EN: open_settings_callback called.
    # FR: open_settings_callback appelé.
    logging.info("Settings button clicked - Feature not implemented yet.")
    # EN: Settings button clicked - Feature not implemented yet.
    # FR: Bouton Paramètres cliqué - Fonctionnalité non encore implémentée.

# Create Button instances for different game screens
# *Créer des instances de Button pour différents écrans de jeu*
# These buttons are created once and their visibility/handling is managed by game state in the main loop.
# *Ces boutons sont créés une fois et leur visibilité/gestion est gérée par l'état du jeu dans la boucle principale.*

start_button_start_screen = Button(
    start_screen_pos[0] + START_SCREEN_BUTTON_START_X_OFFSET, # X position
    start_screen_pos[1] + START_SCREEN_BUTTON_START_Y_OFFSET, # Y position
    start_button_img, # Image surface or CLI metadata
    start_game,       # Callback function
    cli_mode=args.cli
)
exit_button_start_screen = Button(
    start_screen_pos[0] + START_SCREEN_BUTTON_EXIT_X_OFFSET,
    start_screen_pos[1] + START_SCREEN_BUTTON_EXIT_Y_OFFSET,
    exit_button_img,
    quit_game,
    cli_mode=args.cli
)
start_screen_buttons = [start_button_start_screen, exit_button_start_screen]

# Game Over screen buttons - positions are relative to screen center
# *Boutons de l'écran Game Over - positions relatives au centre de l'écran*
# Note: restart_button_rect.width might be 0 in CLI if asset wasn't fully processed for rect.
# Button class itself handles this by having a 0-size rect in CLI.
# *Note : restart_button_rect.width peut être 0 en CLI si la ressource n'a pas été entièrement traitée pour le rect.*
# *La classe Button elle-même gère cela en ayant un rect de taille 0 en CLI.*
_restart_width = restart_button_rect.width if not args.cli and restart_button_img and hasattr(restart_button_img, 'get_width') else (DEFAULT_PLACEHOLDER_SIZE[0] if args.cli else 0)
_exit_width = exit_button_rect.width if not args.cli and exit_button_img and hasattr(exit_button_img, 'get_width') else (DEFAULT_PLACEHOLDER_SIZE[0] if args.cli else 0)

restart_button_game_over_screen = Button(
    screen_width / 2 - _restart_width - BUTTON_SPACING / 2 if screen_width > 0 else 0, # Avoid division by zero if screen_width is 0 (e.g. early CLI)
                                                                                         # *Éviter la division par zéro si screen_width est 0 (par ex. CLI précoce)*
    screen_height * 3 / 4 - restart_button_rect.height / 2 if screen_height > 0 else 0,
    restart_button_img,
    reset_game,
    cli_mode=args.cli
)
exit_button_game_over_screen = Button(
    screen_width / 2 + BUTTON_SPACING / 2 if screen_width > 0 else 0,
    screen_height * 3 / 4 - exit_button_rect.height / 2 if screen_height > 0 else 0,
    exit_button_img,
    quit_game,
    cli_mode=args.cli
)
game_over_buttons = [restart_button_game_over_screen, exit_button_game_over_screen]

# Pause screen buttons - positions relative to screen center
# *Boutons de l'écran de Pause - positions relatives au centre de l'écran*
_continue_width = continue_button_rect.width if not args.cli and continue_button_img and hasattr(continue_button_img, 'get_width') else (DEFAULT_PLACEHOLDER_SIZE[0] if args.cli else 0)
_settings_width = settings_button_rect.width if not args.cli and settings_button_img and hasattr(settings_button_img, 'get_width') else (DEFAULT_PLACEHOLDER_SIZE[0] if args.cli else 0)

continue_button_pause_screen = Button(
    screen_width / 2 - _continue_width / 2 if screen_width > 0 else 0,
    screen_height * 0.5 - continue_button_rect.height - BUTTON_SPACING / 2 if screen_height > 0 else 0,
    continue_button_img,
    resume_game_callback,
    cli_mode=args.cli
)
settings_button_pause_screen = Button(
    screen_width / 2 - _settings_width / 2 if screen_width > 0 else 0,
    screen_height * 0.5 + BUTTON_SPACING / 2 if screen_height > 0 else 0,
    settings_button_img,
    open_settings_callback,
    cli_mode=args.cli
)
pause_screen_buttons = [continue_button_pause_screen, settings_button_pause_screen]


def handle_player_death():
    """
    Handles the player's death event. Activates death effect, plays sound.
    Uses the global 'current_time' for timing the death effect.

    *Gère l'événement de la mort du joueur. Active l'effet de mort, joue le son.*
    *Utilise le 'current_time' global pour synchroniser l'effet de mort.*
    """
    global current_time # Ensure access to the global current_time updated by run_gui_mode
                        # *Assurer l'accès au current_time global mis à jour par run_gui_mode*
    if not game_state.game_over and not game_state.player.death_effect_active:
        game_state.player.death_effect_active = True
        game_state.player.death_effect_start_time = current_time # Use the accurately updated current_time
                                                                 # *Utiliser le current_time mis à jour avec précision*
        logging.info("Player death sequence initiated.")
        # EN: Player death sequence initiated.
        # FR: Séquence de mort du joueur initiée.

    if not args.cli and pygame.mixer.get_init(): # Play sound only in GUI with mixer
                                                 # *Jouer le son uniquement en GUI avec mixeur*
        try:
            pygame.mixer.music.stop() # Stop any current music / *Arrêter toute musique en cours*
            death_sound = asset_manager.sounds.get('death')
            if death_sound and not isinstance(death_sound, DummySound):
                death_sound.play()
        except pygame.error as e:
            logging.exception(f"Could not play player death sound: {e}")
            # EN: Could not play player death sound: {e}
            # FR: Impossible de jouer le son de mort du joueur : {e}
    elif args.cli: # Specific log for CLI mode death handling
                   # *Log spécifique pour la gestion de la mort en mode CLI*
        logging.info("Player has died (CLI mode).")
        # EN: Player has died (CLI mode).
        # FR: Le joueur est mort (mode CLI).


running = True # Global flag to control the main game loop / *Indicateur global pour contrôler la boucle de jeu principale*
can_toggle_pause = True # Prevents rapid pause/unpause from single key press / *Empêche pause/reprise rapide à partir d'une seule pression de touche*

# Store current_time globally for functions that need it (e.g. handle_player_death, GUI animations)
# It will be updated primarily by run_gui_mode. CLI mode doesn't use it for its loop timing.
# *Stocker current_time globalement pour les fonctions qui en ont besoin (par ex. handle_player_death, animations GUI)*
# *Il sera mis à jour principalement par run_gui_mode. Le mode CLI ne l'utilise pas pour sa synchronisation de boucle.*
current_time = 0.0 # Initialized, will be set by time.time() in GUI loop / *Initialisé, sera défini par time.time() dans la boucle GUI*

def run_gui_mode():
    """
    Handles the entire game loop, event processing, and rendering for GUI mode.
    This function is called repeatedly by main_loop when not in CLI mode.

    *Gère l'intégralité de la boucle de jeu, le traitement des événements et le rendu pour le mode GUI.*
    *Cette fonction est appelée de manière répétée par main_loop lorsqu'on n'est pas en mode CLI.*
    """
    logging.debug("run_gui_mode: Frame processing started.")
    # EN: run_gui_mode: Frame processing started.
    # FR: run_gui_mode : Traitement de la frame démarré.
    global running, current_time, can_toggle_pause, game_state, asset_manager, screen, args
    # Declare other globals if they are modified here and defined outside, though most are read-only or passed via objects.
    # *Déclarer d'autres globales si elles sont modifiées ici et définies à l'extérieur, bien que la plupart soient en lecture seule ou passées via des objets.*
    # For UI positioning and assets: / *Pour le positionnement de l'UI et les ressources :*
    global screen_width, screen_height
    global start_screen_buttons, pause_screen_buttons, game_over_buttons
    global start_screen_image, start_screen_pos, game_over_image_ui, grass_background, garlic_image, hp_image_ui
    # Note: rects like game_over_rect are used for positioning and come from asset_manager or are calculated
    # *Note : les rects comme game_over_rect sont utilisés pour le positionnement et proviennent d'asset_manager ou sont calculés*

    current_time = time.time() # Update global current_time for this frame / *Mettre à jour current_time global pour cette frame*

    # Event handling loop / *Boucle de gestion des événements*
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logging.info("QUIT event received, shutting down.")
            # EN: QUIT event received, shutting down.
            # FR: Événement QUIT reçu, fermeture en cours.
            running = False # Signal main_loop to exit / *Signaler à main_loop de quitter*
            return # Exit run_gui_mode for this iteration to prevent further processing
                   # *Quitter run_gui_mode pour cette itération afin d'empêcher tout traitement ultérieur*

        # Pause toggle logic (only if game is active)
        # *Logique de basculement de la pause (uniquement si le jeu est actif)*
        if game_state.started and not game_state.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if can_toggle_pause:
                        if game_state.paused:
                            game_state.resume_game()
                        else:
                            game_state.pause_game()
                        can_toggle_pause = False # Prevent re-toggling until key is released
                                                 # *Empêcher un nouveau basculement jusqu'à ce que la touche soit relâchée*
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    can_toggle_pause = True # Allow toggling again / *Permettre à nouveau le basculement*

        # Button event handling based on game state / *Gestion des événements des boutons en fonction de l'état du jeu*
        if not game_state.started: # Start Screen / *Écran de Démarrage*
            for button in start_screen_buttons:
                button.handle_event(event)
        elif game_state.paused: # Pause Screen / *Écran de Pause*
            for button in pause_screen_buttons:
                button.handle_event(event)
        elif not game_state.game_over: # Active game event handling (player actions) / *Gestion des événements du jeu actif (actions du joueur)*
            if event.type == pygame.KEYDOWN:
                # Spacebar for shooting (alternative, mouse click is primary)
                # *Barre d'espace pour tirer (alternative, le clic de souris est principal)*
                if event.key == pygame.K_SPACE and not game_state.player.death_effect_active:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Adjust mouse position by scroll to get world coordinates for target
                    # *Ajuster la position de la souris par le défilement pour obtenir les coordonnées du monde pour la cible*
                    target_world_x = mouse_x + game_state.scroll[0]
                    target_world_y = mouse_y + game_state.scroll[1]
                    game_state.add_bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                          target_world_x, target_world_y,
                                          asset_manager.images['bullet']) # cli_mode is handled by Bullet's init
                                                                          # *cli_mode est géré par l'init de Bullet*
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Left click for shooting bullets / *Clic gauche pour tirer des projectiles*
                if event.button == 1 and not game_state.player.death_effect_active:
                    mouse_pos_screen = pygame.mouse.get_pos() # Screen coordinates / *Coordonnées de l'écran*
                    # Convert screen mouse pos to world coordinates for bullet target
                    # *Convertir la position de la souris à l'écran en coordonnées du monde pour la cible du projectile*
                    target_world_x = mouse_pos_screen[0] + game_state.scroll[0]
                    target_world_y = mouse_pos_screen[1] + game_state.scroll[1]
                    game_state.add_bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                          target_world_x, target_world_y,
                                          asset_manager.images['bullet'])
                # Right click for garlic shot / *Clic droit pour le tir d'ail*
                if event.button == 3 and not game_state.player.death_effect_active and \
                   game_state.player.garlic_count > 0 and game_state.garlic_shot is None:
                    game_state.player.garlic_count -= 1
                    game_state.player.garlic_changed = True # For UI update / *Pour mise à jour UI*

                    game_state.garlic_shot_start_time = current_time # Use accurately updated global current_time
                                                                     # *Utiliser current_time global mis à jour avec précision*
                    mouse_x_screen, mouse_y_screen = pygame.mouse.get_pos()
                    world_mouse_x = mouse_x_screen + game_state.scroll[0]
                    world_mouse_y = mouse_y_screen + game_state.scroll[1]

                    start_x, start_y = game_state.player.rect.centerx, game_state.player.rect.centery
                    dx, dy = world_mouse_x - start_x, world_mouse_y - start_y

                    # Normalize direction vector / *Normaliser le vecteur direction*
                    dist = math.hypot(dx, dy)
                    dx_norm, dy_norm = (dx/dist, dy/dist) if dist > 0 else (0,1) # Default to (0,1) if dist is 0 to avoid error, though unlikely
                                                                                 # *Par défaut (0,1) si dist est 0 pour éviter une erreur, bien que peu probable*
                    angle = math.degrees(math.atan2(-dy_norm, dx_norm)) # Angle for rotation / *Angle pour la rotation*

                    game_state.garlic_shot = {
                        "x": start_x, "y": start_y,
                        "dx": dx_norm, "dy": dy_norm,
                        "angle": angle, "active": True,
                        "rotation_angle": angle # Initial rotation matches direction
                                                # *La rotation initiale correspond à la direction*
                    }
                    game_state.garlic_shot_travel = 0 # Reset travel distance for new shot
                                                      # *Réinitialiser la distance de voyage pour le nouveau tir*
                    logging.debug(f"Garlic shot initiated towards ({world_mouse_x},{world_mouse_y}) with angle {angle:.2f}")
                    # EN: Garlic shot initiated towards ({world_mouse_x},{world_mouse_y}) with angle {angle:.2f}
                    # FR: Tir d'ail initié vers ({world_mouse_x},{world_mouse_y}) avec un angle de {angle:.2f}
        else: # Game over state / *État de Game Over*
            for button in game_over_buttons:
                button.handle_event(event)

    # GUI Drawing Logic / *Logique de dessin GUI*
    if not game_state.started: # Start Screen / *Écran de Démarrage*
        if screen and start_screen_image and hasattr(start_screen_image, 'get_width'): # Check if surface is valid
            screen.blit(start_screen_image, start_screen_pos)
        for button in start_screen_buttons:
            if screen: button.draw(screen) # Button.draw handles cli_mode internally
                                           # *Button.draw gère cli_mode en interne*
    elif game_state.paused: # Pause Screen / *Écran de Pause*
        # Optionally draw current game state dimmed, then pause menu over it
        # *Optionnellement, dessiner l'état actuel du jeu atténué, puis le menu pause par-dessus*
        # For now, reusing game_over_image as placeholder background for pause
        # *Pour l'instant, réutilisation de game_over_image comme arrière-plan de substitution pour la pause*
        if screen and game_over_image_ui and hasattr(game_over_image_ui, 'get_width'):
            game_over_x_pos = (screen_width - game_over_image_ui.get_width()) / 2
            game_over_y_pos = (screen_height - game_over_image_ui.get_height()) / 2
            screen.blit(game_over_image_ui, (game_over_x_pos, game_over_y_pos))
            # TODO: Consider a dedicated "PAUSED" title image or text rendering here
            # *TODO : Envisager une image de titre "PAUSE" dédiée ou un rendu de texte ici*
        for button in pause_screen_buttons:
            if screen: button.draw(screen)
    elif not game_state.game_over: # Active game drawing / *Dessin du jeu actif*
        # Player movement based on pressed keys / *Mouvement du joueur basé sur les touches enfoncées*
        if not game_state.player.death_effect_active:
            dx, dy = 0,0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_q]: dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_z]: dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
            if dx != 0 or dy != 0:
                game_state.player.move(dx, dy, game_state.world_size)

        # Scrolling logic based on player position / *Logique de défilement basée sur la position du joueur*
        # Trigger scrolling if player is near screen edges / *Déclencher le défilement si le joueur est proche des bords de l'écran*
        scroll_margin_x = screen_width * game_state.scroll_trigger
        scroll_margin_y = screen_height * game_state.scroll_trigger

        if game_state.player.rect.left < game_state.scroll[0] + scroll_margin_x:
            game_state.scroll[0] = max(0, game_state.player.rect.left - scroll_margin_x)
        elif game_state.player.rect.right > game_state.scroll[0] + screen_width - scroll_margin_x:
            game_state.scroll[0] = min(game_state.world_size[0] - screen_width, game_state.player.rect.right - screen_width + scroll_margin_x)

        if game_state.player.rect.top < game_state.scroll[1] + scroll_margin_y:
            game_state.scroll[1] = max(0, game_state.player.rect.top - scroll_margin_y)
        elif game_state.player.rect.bottom > game_state.scroll[1] + screen_height - scroll_margin_y:
            game_state.scroll[1] = min(game_state.world_size[1] - screen_height, game_state.player.rect.bottom - screen_height + scroll_margin_y)

        # Ensure scroll does not exceed world boundaries / *S'assurer que le défilement ne dépasse pas les limites du monde*
        game_state.scroll[0] = max(0, min(game_state.scroll[0], game_state.world_size[0] - screen_width))
        game_state.scroll[1] = max(0, min(game_state.scroll[1], game_state.world_size[1] - screen_height))


        try:
            # Update game state (entity movements, collisions, etc.)
            # *Mettre à jour l'état du jeu (mouvements des entités, collisions, etc.)*
            if not game_state.player.death_effect_active: # Don't update game logic if player is in death animation
                                                          # *Ne pas mettre à jour la logique du jeu si le joueur est en animation de mort*
                game_state.update(current_time) # Pass the updated global current_time
                                                # *Passer le current_time global mis à jour*

            # Drawing starts here / *Le dessin commence ici*
            if screen and grass_background and hasattr(grass_background, 'get_width'): # Background / *Arrière-plan*
                screen.blit(grass_background, (-game_state.scroll[0], -game_state.scroll[1]))

            # Draw carrots / *Dessiner les carottes*
            for carrot_enemy in game_state.carrots:
                if carrot_enemy.active and screen: carrot_enemy.draw(screen, game_state.scroll) # Delegate to entity's draw
                                                                                                 # *Déléguer au dessin de l'entité*
            # Draw player with effects / *Dessiner le joueur avec effets*
            player_pos_on_screen = (game_state.player.rect.x - game_state.scroll[0], game_state.player.rect.y - game_state.scroll[1])
            if game_state.player.death_effect_active:
                # Flashing red tint during death animation / *Teinte rouge clignotante pendant l'animation de mort*
                if int((current_time - game_state.player.death_effect_start_time) / 0.1) % 2 == 0:
                    if screen and game_state.player.original_image and hasattr(game_state.player.original_image, 'copy') :
                        tinted_image = game_state.player.original_image.copy()
                        tinted_image.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT) # Red tint / *Teinte rouge*
                        screen.blit(tinted_image, player_pos_on_screen)
            elif game_state.player.invincible and int(current_time * PLAYER_INVINCIBILITY_FLASH_FREQUENCY) % 2 == 1:
                pass # Player flashes by not being drawn every other frame / *Le joueur clignote en n'étant pas dessiné une frame sur deux*
            else: # Normal player drawing / *Dessin normal du joueur*
                if screen: game_state.player.draw(screen, game_state.scroll)

            # Draw bullets / *Dessiner les projectiles*
            for bullet in game_state.bullets:
                if screen and bullet.image: # Ensure bullet has a drawable image (might be None if placeholder failed)
                                            # *S'assurer que le projectile a une image dessinable (peut être None si le substitut a échoué)*
                    rotated_bullet_img = bullet.rotated_image # Get rotated image via property
                                                              # *Obtenir l'image tournée via la propriété*
                    if rotated_bullet_img: # Check if rotated_image is not None
                                           # *Vérifier si rotated_image n'est pas None*
                         screen.blit(rotated_bullet_img, (bullet.rect.x - game_state.scroll[0], bullet.rect.y - game_state.scroll[1]))

            # Draw garlic shot if active / *Dessiner le tir d'ail s'il est actif*
            if game_state.garlic_shot and game_state.garlic_shot["active"]:
                if screen and garlic_image and hasattr(garlic_image, 'get_rect'): # garlic_image is global UI asset
                                                                                  # *garlic_image est une ressource UI globale*
                    rotated_garlic = pygame.transform.rotate(garlic_image, game_state.garlic_shot["rotation_angle"])
                    # Center the rotated image on the garlic_shot's logical position
                    # *Centrer l'image tournée sur la position logique du tir d'ail*
                    rotated_rect = rotated_garlic.get_rect(center=(game_state.garlic_shot["x"], game_state.garlic_shot["y"]))
                    screen.blit(rotated_garlic, (rotated_rect.x - game_state.scroll[0], rotated_rect.y - game_state.scroll[1]))

            # Draw explosions / *Dessiner les explosions*
            for explosion in game_state.explosions:
                if screen: explosion.draw(screen, game_state.scroll)

            # Draw vampire / *Dessiner le vampire*
            if screen: game_state.vampire.draw(screen, game_state.scroll, current_time)

            # Draw UI elements (health, garlic count, etc.) - drawn last, fixed on screen
            # *Dessiner les éléments d'UI (santé, compteur d'ail, etc.) - dessinés en dernier, fixes à l'écran*
            if screen and hp_image_ui and garlic_image: # Check assets are valid surfaces
                                                        # *Vérifier que les ressources sont des surfaces valides*
                game_state.player.draw_ui(screen, hp_image_ui, garlic_image, MAX_GARLIC)

            # Log player stats if they changed (for debugging)
            # *Journaliser les statistiques du joueur si elles ont changé (pour le débogage)*
            if game_state.player.health_changed or game_state.player.garlic_changed or game_state.player.juice_changed:
                logging.debug(f"Player Stats - HP: {game_state.player.health}, Garlic: {game_state.player.garlic_count}, Carrot Juice: {game_state.player.carrot_juice_count}, Vampires Killed: {game_state.vampire_killed_count}")
                # EN: Player Stats - HP: {game_state.player.health}, Garlic: {game_state.player.garlic_count}, Carrot Juice: {game_state.player.carrot_juice_count}, Vampires Killed: {game_state.vampire_killed_count}
                # FR: Stats Joueur - PV : {game_state.player.health}, Ail : {game_state.player.garlic_count}, Jus de Carotte : {game_state.player.carrot_juice_count}, Vampires Tués : {game_state.vampire_killed_count}
                game_state.player.health_changed = False # Reset flags / *Réinitialiser les indicateurs*
                game_state.player.garlic_changed = False
                game_state.player.juice_changed = False

            # Draw collectible items / *Dessiner les objets à collectionner*
            for item in game_state.items:
                if item.active and screen: item.draw(screen, game_state.scroll)

        except Exception as e: # Catch-all for errors during game logic/draw
                               # *Fourre-tout pour les erreurs pendant la logique/le dessin du jeu*
            logging.exception(f"ERROR during game logic/draw: {e}")
            # EN: ERROR during game logic/draw: {e}
            # FR: ERREUR pendant la logique/le dessin du jeu : {e}
            running = False # Signal main_loop to exit on critical error / *Signaler à main_loop de quitter en cas d'erreur critique*
            return

        # Check for player death condition after updates / *Vérifier la condition de mort du joueur après les mises à jour*
        if game_state.player.health <= 0 and not game_state.game_over and not game_state.player.death_effect_active:
            handle_player_death() # Uses the global current_time set at start of run_gui_mode
                                  # *Utilise le current_time global défini au début de run_gui_mode*

        # Transition to game over state if death animation finished
        # *Transition vers l'état game over si l'animation de mort est terminée*
        if game_state.player.death_effect_active:
            time_elapsed_death = current_time - game_state.player.death_effect_start_time
            if time_elapsed_death >= config.PLAYER_DEATH_DURATION:
                game_state.game_over = True
                game_state.player.death_effect_active = False
                logging.info("Player death animation complete. Game Over.")
                # EN: Player death animation complete. Game Over.
                # FR: Animation de mort du joueur terminée. Game Over.
    else: # Game over drawing / *Dessin de Game Over*
        if screen and game_over_image_ui and hasattr(game_over_image_ui, 'get_width'):
            game_over_x_pos = (screen_width - game_over_image_ui.get_width()) / 2
            game_over_y_pos = (screen_height - game_over_image_ui.get_height()) / 2
            screen.blit(game_over_image_ui, (game_over_x_pos, game_over_y_pos))
        for button in game_over_buttons:
            if screen: button.draw(screen)

        # Play game over music if not already playing / *Jouer la musique de game over si elle ne joue pas déjà*
        if pygame.mixer.get_init() and not pygame.mixer.music.get_busy():
            music_path_game_over = asset_manager._get_path(config.MUSIC_GAMEOVER)
            if music_path_game_over: # Check if path resolved correctly
                                     # *Vérifier si le chemin s'est résolu correctement*
                try:
                    pygame.mixer.music.load(music_path_game_over)
                    pygame.mixer.music.play(-1) # Loop game over music / *Jouer la musique de game over en boucle*
                except pygame.error as e:
                    logging.exception(f"Error playing game over music: {e}")
                    # EN: Error playing game over music: {e}
                    # FR: Erreur lors de la lecture de la musique de game over : {e}

    # Draw mouse crosshair last, on top of everything / *Dessiner le réticule de la souris en dernier, par-dessus tout*
    if screen:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        crosshair_img_ref = asset_manager.images.get('crosshair')
        if crosshair_img_ref and hasattr(crosshair_img_ref, 'get_rect'): # Ensure crosshair image is valid
                                                                         # *S'assurer que l'image du réticule est valide*
            crosshair_rect_instance = crosshair_img_ref.get_rect(center=(mouse_x, mouse_y))
            screen.blit(crosshair_img_ref, crosshair_rect_instance)

    pygame.display.flip() # Update the full display / *Mettre à jour l'affichage complet*
    time.sleep(config.FRAME_DELAY) # Control frame rate / *Contrôler la fréquence d'images*
    logging.debug("run_gui_mode: Frame processing ended.")
    # EN: run_gui_mode: Frame processing ended.
    # FR: run_gui_mode : Traitement de la frame terminé.


def run_cli_mode():
    """
    Handles the entire game loop for Command Line Interface (CLI) mode.
    Presents text-based menus and options. Game logic (like entity updates) is minimal or stubbed in CLI.

    *Gère l'intégralité de la boucle de jeu pour le mode Interface en Ligne de Commande (CLI).*
    *Présente des menus et des options textuels. La logique du jeu (comme les mises à jour d'entités) est minimale ou simulée en CLI.*
    """
    global running, game_state, args # Access global state variables / *Accéder aux variables d'état globales*

    logging.debug("run_cli_mode: Iteration started.")
    # EN: run_cli_mode: Iteration started.
    # FR: run_cli_mode : Itération démarrée.

    if not game_state.started: # Start Screen Logic / *Logique de l'Écran de Démarrage*
        logging.debug("run_cli_mode: Game not started, displaying start menu.")
        # EN: run_cli_mode: Game not started, displaying start menu.
        # FR: run_cli_mode : Jeu non démarré, affichage du menu de démarrage.
        logging.info("\n--- LapinCarotte ---")
        logging.info("Start Screen (CLI Mode) / *Écran de Démarrage (Mode CLI)*")
        logging.info("1. Start Game / *Commencer le jeu*")
        logging.info("2. Exit / *Quitter*")
        choice = ""
        try:
            choice = input("Enter choice / *Entrez votre choix*: ").strip()
        except EOFError: # Handle Ctrl+D or piped input ending / *Gérer Ctrl+D ou la fin d'une entrée redirigée*
            logging.info("EOF received on main menu, quitting.")
            # EN: EOF received on main menu, quitting.
            # FR: EOF reçu dans le menu principal, fermeture.
            quit_game()
            return

        if choice == '1':
            start_game()
        elif choice == '2':
            quit_game()
        elif running: # Avoid printing if quit_game was called / *Éviter d'imprimer si quit_game a été appelé*
            logging.warning("Invalid choice on start screen. Please enter 1 or 2.")
            # EN: Invalid choice on start screen. Please enter 1 or 2.
            # FR: Choix invalide sur l'écran de démarrage. Veuillez entrer 1 ou 2.

    elif game_state.paused: # Pause Screen Logic / *Logique de l'Écran de Pause*
        logging.debug("run_cli_mode: Game paused, displaying pause menu.")
        # EN: run_cli_mode: Game paused, displaying pause menu.
        # FR: run_cli_mode : Jeu en pause, affichage du menu pause.
        logging.info("\n--- PAUSED (CLI Mode) / *PAUSE (Mode CLI)* ---")
        logging.info("1. Continue / *Continuer*")
        logging.info("2. Settings (Not Implemented) / *Paramètres (Non implémenté)*")
        logging.info("3. Quit Game / *Quitter le jeu*")
        choice = ""
        try:
            choice = input("Enter choice / *Entrez votre choix*: ").strip()
        except EOFError:
            logging.info("EOF received on pause menu, quitting.")
            # EN: EOF received on pause menu, quitting.
            # FR: EOF reçu dans le menu pause, fermeture.
            quit_game()
            return

        if choice == '1':
            resume_game_callback()
        elif choice == '2':
            open_settings_callback()
        elif choice == '3':
            quit_game()
        elif running:
            logging.warning("Invalid choice on pause menu.")
            # EN: Invalid choice on pause menu.
            # FR: Choix invalide dans le menu pause.

    elif game_state.game_over: # Game Over Screen Logic / *Logique de l'Écran Game Over*
        logging.debug("run_cli_mode: Game over, displaying game over menu.")
        # EN: run_cli_mode: Game over, displaying game over menu.
        # FR: run_cli_mode : Game over, affichage du menu game over.
        logging.info("\n--- GAME OVER (CLI Mode) ---")
        logging.info("1. Restart / *Recommencer*")
        logging.info("2. Exit / *Quitter*")
        choice = ""
        try:
            choice = input("Enter choice / *Entrez votre choix*: ").strip()
        except EOFError:
            logging.info("EOF received on game over menu, quitting.")
            # EN: EOF received on game over menu, quitting.
            # FR: EOF reçu dans le menu game over, fermeture.
            quit_game()
            return

        if choice == '1':
            reset_game()
        elif choice == '2':
            quit_game()
        elif running:
            logging.warning("Invalid choice on game over menu.")
            # EN: Invalid choice on game over menu.
            # FR: Choix invalide dans le menu game over.

    else:  # Game is active (and not paused, not game over) / *Le jeu est actif (et non en pause, non game over)*
        logging.debug("run_cli_mode: Game active, displaying active game options.")
        # EN: run_cli_mode: Game active, displaying active game options.
        # FR: run_cli_mode : Jeu actif, affichage des options du jeu actif.
        logging.info("\n--- Game Active (CLI Mode) / *Jeu Actif (Mode CLI)* ---")
        # Display basic game info. Note: Full game logic (like enemy movement) is not run in CLI.
        # *Afficher les informations de base du jeu. Note : la logique complète du jeu (comme le mouvement des ennemis) n'est pas exécutée en CLI.*
        logging.info(f"Player HP: {game_state.player.health} (Note: Game logic not running in CLI yet / *Note : La logique du jeu ne tourne pas encore en CLI*)")
        logging.info("Options: (esc)ause, (q)uit, (d)ie (simulate death for testing) / *Options : (esc) Pause, (q)uitter, (d)écéder (simuler mort pour test)*")

        cli_action = ""
        try:
            cli_action = input("Action: ").strip().lower()
            logging.debug(f"CLI action received: '{cli_action}'")
            # EN: CLI action received: '{cli_action}'
            # FR: Action CLI reçue : '{cli_action}'
        except EOFError:
            logging.info("EOF received during active game, quitting.")
            # EN: EOF received during active game, quitting.
            # FR: EOF reçu pendant le jeu actif, fermeture.
            quit_game()
            return

        if cli_action == 'esc': # Pause command / *Commande de pause*
            logging.debug("CLI action 'esc' received, pausing game.")
            # EN: CLI action 'esc' received, pausing game.
            # FR: Action CLI 'esc' reçue, mise en pause du jeu.
            game_state.pause_game()
        elif cli_action == 'q': # Quit command / *Commande pour quitter*
            logging.debug("CLI action 'q' received, quitting game.")
            # EN: CLI action 'q' received, quitting game.
            # FR: Action CLI 'q' reçue, fermeture du jeu.
            quit_game()
        elif cli_action == 'd': # Simulate death for testing / *Simuler la mort pour les tests*
            logging.debug("CLI action 'd' received, simulating player death.")
            # EN: CLI action 'd' received, simulating player death.
            # FR: Action CLI 'd' reçue, simulation de la mort du joueur.
            game_state.player.health = 0
            # Directly set game_over for CLI test simplicity. In GUI, this flows from health <= 0.
            # *Définir directement game_over pour la simplicité des tests CLI. En GUI, cela découle de santé <= 0.*
            game_state.game_over = True
            logging.info("Simulating player death for CLI testing... Player HP set to 0, game_over set to True.")
            # EN: Simulating player death for CLI testing... Player HP set to 0, game_over set to True.
            # FR: Simulation de la mort du joueur pour test CLI... PV Joueur mis à 0, game_over mis à True.

    if running and args.cli: # Check 'running' again in case quit_game was called by an action
                             # *Vérifier 'running' à nouveau au cas où quit_game aurait été appelé par une action*
        time.sleep(0.1) # Small delay for CLI loop readability and to prevent busy-waiting
                        # *Petit délai pour la lisibilité de la boucle CLI et pour éviter l'attente active*
    logging.debug("run_cli_mode: Iteration ended.")
    # EN: run_cli_mode: Iteration ended.
    # FR: run_cli_mode : Itération terminée.


def main_loop():
    """
    The main game loop. Alternates between GUI and CLI mode based on arguments.
    Continues as long as the global 'running' flag is True.

    *La boucle de jeu principale. Alterne entre les modes GUI et CLI en fonction des arguments.*
    *Continue tant que l'indicateur global 'running' est True.*
    """
    global running # Controls the loop / *Contrôle la boucle*
    logging.debug("Main loop started.")
    # EN: Main loop started.
    # FR: Boucle principale démarrée.
    while running:
        if not args.cli:
            run_gui_mode()
        else:
            run_cli_mode()
    logging.debug("Main loop ended because 'running' is False.")
    # EN: Main loop ended because 'running' is False.
    # FR: Boucle principale terminée car 'running' est False.

if __name__ == '__main__':
    # Configure logging based on --debug argument
    # *Configurer la journalisation en fonction de l'argument --debug*
    log_level = logging.DEBUG if args.debug else logging.INFO

    # Get the root logger / *Obtenir le logger racine*
    logger = logging.getLogger()
    logger.setLevel(log_level) # Set the level for the root logger / *Définir le niveau pour le logger racine*

    # Clear any existing handlers to avoid duplicate logs if script is re-run in some environments
    # *Effacer tous les gestionnaires existants pour éviter les journaux en double si le script est ré-exécuté dans certains environnements*
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a stream handler for stdout / *Créer un gestionnaire de flux pour stdout*
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level) # Ensure handler respects the same level / *S'assurer que le gestionnaire respecte le même niveau*

    # Create a formatter and set it for the handler / *Créer un formateur et le définir pour le gestionnaire*
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")
    stdout_handler.setFormatter(formatter)

    # Add the handler to the root logger / *Ajouter le gestionnaire au logger racine*
    logger.addHandler(stdout_handler)

    logging.info("Application starting...")
    # EN: Application starting...
    # FR: Démarrage de l'application...
    if args.cli:
        logging.info("CLI mode enabled.")
        # EN: CLI mode enabled.
        # FR: Mode CLI activé.
    if args.debug:
        logging.info("Debug logging enabled.")
        # EN: Debug logging enabled.
        # FR: Journalisation de débogage activée.

    try:
        main_loop()
    finally:
        # Cleanup actions when the game loop finishes or an unhandled exception occurs in main_loop
        # *Actions de nettoyage lorsque la boucle de jeu se termine ou qu'une exception non gérée se produit dans main_loop*
        logging.info("Application shutting down...")
        # EN: Application shutting down...
        # FR: Fermeture de l'application...
        if not args.cli and pygame.get_init(): # Only quit pygame if it was initialized for GUI mode
                                               # *Quitter Pygame uniquement s'il a été initialisé pour le mode GUI*
            pygame.quit()
            logging.info("Pygame quit successfully.")
            # EN: Pygame quit successfully.
            # FR: Pygame quitté avec succès.
        # sys.exit() is not strictly necessary here as the program will exit naturally.
        # It can be used to ensure a specific exit code if needed.
        # *sys.exit() n'est pas strictement nécessaire ici car le programme se terminera naturellement.*
        # *Il peut être utilisé pour assurer un code de sortie spécifique si nécessaire.*
        logging.info("Shutdown complete.")
        # EN: Shutdown complete.
        # FR: Fermeture terminée.
