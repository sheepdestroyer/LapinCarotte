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

import argparse
import logging
import math
import os
import random
import sys
import time

import pygame

import config
from asset_manager import AssetManager, DummySound
from game_entities import Button
from game_state import GameState
from utilities import get_asset_path

# Global variables initialized with default/None values
# These will be properly initialized in main_entry_point after args parsing
args = None
screen = None
screen_width, screen_height = 0, 0
asset_manager = None
game_state = None
start_screen_image = None
start_screen_pos = (0,0)
garlic_image = None
hp_image_ui = None
game_over_image_ui = None
grass_background = None
start_screen_buttons = []
game_over_buttons = []
pause_screen_buttons = []

current_time = 0.0
running = True
can_toggle_pause = True

def handle_player_death():
    """
    Handles the player's death event. Activates death effect, plays sound.
    Uses the global 'current_time' for timing the death effect.

    *Gère l'événement de la mort du joueur. Active l'effet de mort, joue le son.*
    *Utilise le 'current_time' global pour synchroniser l'effet de mort.*
    """
    global current_time
    if not game_state.game_over and not game_state.player.death_effect_active:
        game_state.player.death_effect_active = True
        game_state.player.death_effect_start_time = current_time
        logging.info("Player death sequence initiated. / Séquence de mort du joueur initiée.")

    if not args.cli and pygame.mixer.get_init():
        try:
            pygame.mixer.music.stop()
            death_sound = asset_manager.sounds.get('death')
            if death_sound and not isinstance(death_sound, DummySound):
                death_sound.play()
        except pygame.error as e:
            logging.exception(f"Could not play player death sound: {e} / Impossible de jouer le son de mort du joueur : {e}")
    elif args.cli:
        logging.info("Player has died (CLI mode). / Le joueur est mort (mode CLI).")

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
    if args.cli or not pygame.mixer.get_init(): return
    try:
        pygame.mixer.music.stop()
        game_music_path = get_asset_path(config.MUSIC_GAME)
        pygame.mixer.music.load(game_music_path)
        pygame.mixer.music.play(-1)
        if sound_to_play and sound_to_play in asset_manager.sounds:
            sound_effect = asset_manager.sounds[sound_to_play]
            if not isinstance(sound_effect, DummySound):
                 sound_effect.play()
    except pygame.error as e:
        logging.exception(f"Could not load or play game music/sound: {e} / Impossible de charger ou de jouer la musique/le son du jeu : {e}")

def start_game():
    """
    Callback function to start the game. Sets game_state.started to True and plays start sound.
    *Fonction de rappel pour démarrer le jeu. Met game_state.started à True et joue le son de démarrage.*
    """
    logging.debug("start_game called. / start_game appelé.")
    game_state.started = True
    if not args.cli: _play_game_music_and_sound('press_start')
    else: logging.info("Game started (CLI). / Jeu démarré (CLI).")
    logging.debug(f"game_state.started set to {game_state.started} / game_state.started défini sur {game_state.started}")

def reset_game():
    """
    Callback function to reset the game state for a new game.
    *Fonction de rappel pour réinitialiser l'état du jeu pour une nouvelle partie.*
    """
    logging.debug("reset_game called. / reset_game appelé.")
    game_state.reset()
    if not args.cli: _play_game_music_and_sound('press_start')
    else: logging.info("Game reset (CLI). / Jeu réinitialisé (CLI).")
    logging.debug("Game state reset by reset_game function. / État du jeu réinitialisé par la fonction reset_game.")

def quit_game():
    """
    Callback function to quit the game. Sets the global 'running' flag to False.
    *Fonction de rappel pour quitter le jeu. Met l'indicateur global 'running' à False.*
    """
    logging.debug("quit_game called. / quit_game appelé.")
    global running
    running = False
    if args.cli: logging.info("Exiting game (CLI). / Sortie du jeu (CLI).")
    else: logging.info("Exiting game (GUI). / Sortie du jeu (GUI).")
    logging.debug("Global 'running' flag set to False. / Indicateur global 'running' défini sur False.")

def resume_game_callback():
    """
    Callback function to resume the game if it was paused.
    *Fonction de rappel pour reprendre le jeu s'il était en pause.*
    """
    logging.debug("resume_game_callback called. / resume_game_callback appelé.")
    if game_state.paused:
        logging.debug("Game was paused, calling game_state.resume_game() / Le jeu était en pause, appel de game_state.resume_game()")
        game_state.resume_game()
        if args.cli: logging.info("Game resumed via callback (CLI). / Jeu repris via rappel (CLI).")
    else:
        logging.debug("Game was not paused, resume_game_callback did nothing. / Le jeu n'était pas en pause, resume_game_callback n'a rien fait.")

def open_settings_callback():
    """
    Callback for the settings button. Currently a placeholder.
    *Rappel pour le bouton des paramètres. Actuellement un placeholder.*
    """
    logging.debug("open_settings_callback called. / open_settings_callback appelé.")
    logging.info("Settings button clicked - Feature not implemented yet. / Bouton Paramètres cliqué - Fonctionnalité non encore implémentée.")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="LapinCarotte - A game about a rabbit fighting vampire carrots. / *Un jeu sur un lapin combattant des carottes vampires.*")
    parser.add_argument("--cli", action="store_true", help="Run the game in Command Line Interface mode (no graphics). / *Exécuter le jeu en mode Interface en Ligne de Commande (sans graphismes).*")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging output. / *Activer la sortie de journalisation de débogage.*")
    return parser.parse_args()

def setup_logging(args):
    """Configure logging based on command-line arguments."""
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = logging.getLogger()
    logger.setLevel(log_level)
    if logger.hasHandlers():
        logger.handlers.clear()
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    logging.info("Application starting... / Démarrage de l'application...")
    if args.cli:
        logging.info("CLI mode enabled. / Mode CLI activé.")
    if args.debug:
        logging.info("Debug logging enabled. / Journalisation de débogage activée.")

def initialize_pygame(args):
    """Initialize Pygame and the display screen."""
    if args.cli:
        return None, 0, 0
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    screen_width, screen_height = screen.get_size()
    pygame.mouse.set_visible(False)
    return screen, screen_width, screen_height

def load_game_assets(args, asset_manager, screen_width, screen_height):
    """Load all game assets."""
    asset_manager.load_assets()
    assets = {
        'start_button_img': asset_manager.images.get('start'),
        'exit_button_img': asset_manager.images.get('exit'),
        'restart_button_img': asset_manager.images.get('restart'),
        'continue_button_img': asset_manager.images.get('continue_button'),
        'settings_button_img': asset_manager.images.get('settings_button'),
        'start_screen_image': None,
        'grass_background': None,
        'garlic_image': asset_manager.images.get('garlic'),
        'hp_image_ui': asset_manager.images.get('hp'),
        'game_over_image_ui': asset_manager.images.get('game_over'),
        'start_screen_pos': (0, 0)
    }

    if not args.cli:
        if 'icon' in asset_manager.images and hasattr(asset_manager.images['icon'], 'get_rect'):
            pygame.display.set_icon(asset_manager.images['icon'])

        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('LapinCarotte.LapinCarotte.Game.1.0')
            pygame.display.set_caption("LapinCarotte", "LapinCarotte")

        start_screen_image = asset_manager.images.get('start_screen')
        if start_screen_image and hasattr(start_screen_image, 'get_width') and hasattr(start_screen_image, 'get_height'):
            assets['start_screen_image'] = start_screen_image
            assets['start_screen_pos'] = (
                (screen_width - start_screen_image.get_width()) // 2,
                (screen_height - start_screen_image.get_height()) // 2
            )

        grass_image = asset_manager.images.get('grass')
        if grass_image and hasattr(grass_image, 'get_size'):
            grass_background = pygame.Surface(config.WORLD_SIZE, pygame.SRCALPHA)
            _grass_w, _grass_h = grass_image.get_size()
            if _grass_w > 0 and _grass_h > 0:
                for x_g in range(0, config.WORLD_SIZE[0], _grass_w):
                    for y_g in range(0, config.WORLD_SIZE[1], _grass_h):
                        grass_background.blit(grass_image, (x_g, y_g))
            else:
                logging.warning("Grass asset has invalid dimensions, cannot tile background.")
                grass_background.fill((0,100,0))
            assets['grass_background'] = grass_background

        if pygame.mixer.get_init():
            try:
                intro_music_path = get_asset_path(config.MUSIC_INTRO)
                pygame.mixer.music.load(intro_music_path)
                pygame.mixer.music.play(-1)
            except pygame.error as e:
                logging.warning(f"Could not load or play intro music: {e}")
        else:
            logging.warning("Pygame mixer not initialized, skipping music.")

    return assets

def create_buttons(args, screen_width, screen_height, assets, callbacks):
    """Create all UI buttons for the game."""
    start_screen_pos = assets['start_screen_pos']
    start_button_img = assets['start_button_img']
    exit_button_img = assets['exit_button_img']
    restart_button_img = assets['restart_button_img']
    continue_button_img = assets['continue_button_img']
    settings_button_img = assets['settings_button_img']

    # Button Rects - these are needed for positioning calculations
    restart_button_rect = pygame.Rect(0,0,0,0)
    exit_button_rect = pygame.Rect(0,0,0,0)
    start_button_rect = pygame.Rect(0,0,0,0)
    continue_button_rect = pygame.Rect(0,0,0,0)
    settings_button_rect = pygame.Rect(0,0,0,0)

    if not args.cli:
        # Use assets dictionary to get images
        _restart_img_temp = assets.get('restart_button_img')
        if _restart_img_temp and hasattr(_restart_img_temp, 'get_rect'): restart_button_rect = _restart_img_temp.get_rect()

        _exit_img_temp = assets.get('exit_button_img')
        if _exit_img_temp and hasattr(_exit_img_temp, 'get_rect'): exit_button_rect = _exit_img_temp.get_rect()

        _start_img_temp = assets.get('start_button_img')
        if _start_img_temp and hasattr(_start_img_temp, 'get_rect'): start_button_rect = _start_img_temp.get_rect()

        _continue_img_temp = assets.get('continue_button_img')
        if _continue_img_temp and hasattr(_continue_img_temp, 'get_rect'): continue_button_rect = _continue_img_temp.get_rect()

        _settings_img_temp = assets.get('settings_button_img')
        if _settings_img_temp and hasattr(_settings_img_temp, 'get_rect'): settings_button_rect = _settings_img_temp.get_rect()

    start_button_start_screen = Button(
        start_screen_pos[0] + config.START_SCREEN_BUTTON_START_X_OFFSET,
        start_screen_pos[1] + config.START_SCREEN_BUTTON_START_Y_OFFSET,
        start_button_img,
        callbacks['start'],
        cli_mode=args.cli
    )
    exit_button_start_screen = Button(
        start_screen_pos[0] + config.START_SCREEN_BUTTON_EXIT_X_OFFSET,
        start_screen_pos[1] + config.START_SCREEN_BUTTON_EXIT_Y_OFFSET,
        exit_button_img,
        callbacks['quit'],
        cli_mode=args.cli
    )
    start_screen_buttons = [start_button_start_screen, exit_button_start_screen]

    _restart_w = restart_button_rect.width if not args.cli and restart_button_img and hasattr(restart_button_img, 'get_width') else (config.DEFAULT_PLACEHOLDER_SIZE[0] if args.cli else 0)
    _exit_w = exit_button_rect.width if not args.cli and exit_button_img and hasattr(exit_button_img, 'get_width') else (config.DEFAULT_PLACEHOLDER_SIZE[0] if args.cli else 0)

    restart_button_game_over_screen = Button(
        screen_width / 2 - _restart_w - config.BUTTON_SPACING / 2 if screen_width > 0 else 0,
        screen_height * 3 / 4 - restart_button_rect.height / 2 if screen_height > 0 else 0,
        restart_button_img,
        callbacks['reset'],
        cli_mode=args.cli
    )
    exit_button_game_over_screen = Button(
        screen_width / 2 + config.BUTTON_SPACING / 2 if screen_width > 0 else 0,
        screen_height * 3 / 4 - exit_button_rect.height / 2 if screen_height > 0 else 0,
        exit_button_img,
        callbacks['quit'],
        cli_mode=args.cli
    )
    game_over_buttons = [restart_button_game_over_screen, exit_button_game_over_screen]

    _continue_w = continue_button_rect.width if not args.cli and continue_button_img and hasattr(continue_button_img, 'get_width') else (config.DEFAULT_PLACEHOLDER_SIZE[0] if args.cli else 0)
    _settings_w = settings_button_rect.width if not args.cli and settings_button_img and hasattr(settings_button_img, 'get_width') else (config.DEFAULT_PLACEHOLDER_SIZE[0] if args.cli else 0)

    continue_button_pause_screen = Button(
        screen_width / 2 - _continue_w / 2 if screen_width > 0 else 0,
        screen_height * 0.5 - continue_button_rect.height - config.BUTTON_SPACING / 2 if screen_height > 0 else 0,
        continue_button_img,
        callbacks['resume'],
        cli_mode=args.cli
    )
    settings_button_pause_screen = Button(
        screen_width / 2 - _settings_w / 2 if screen_width > 0 else 0,
        screen_height * 0.5 + config.BUTTON_SPACING / 2 if screen_height > 0 else 0,
        settings_button_img,
        callbacks['settings'],
        cli_mode=args.cli
    )
    pause_screen_buttons = [continue_button_pause_screen, settings_button_pause_screen]

    return {
        'start': start_screen_buttons,
        'game_over': game_over_buttons,
        'pause': pause_screen_buttons
    }

def run_gui_mode():
    """
    Handles the entire game loop, event processing, and rendering for GUI mode.
    This function is called repeatedly by main_loop when not in CLI mode.

    *Gère l'intégralité de la boucle de jeu, le traitement des événements et le rendu pour le mode GUI.*
    *Cette fonction est appelée de manière répétée par main_loop lorsqu'on n'est pas en mode CLI.*
    """
    logging.debug("run_gui_mode: Frame processing started. / run_gui_mode : Traitement de la frame démarré.")
    global running, current_time, can_toggle_pause, game_state, asset_manager, screen, args
    global screen_width, screen_height
    global start_screen_buttons, pause_screen_buttons, game_over_buttons
    global start_screen_image, start_screen_pos, game_over_image_ui, grass_background, garlic_image, hp_image_ui

    current_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logging.info("QUIT event received, shutting down. / Événement QUIT reçu, fermeture en cours.")
            running = False
            return

        if game_state.started and not game_state.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if can_toggle_pause:
                        if game_state.paused:
                            game_state.resume_game()
                        else:
                            game_state.pause_game()
                        can_toggle_pause = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    can_toggle_pause = True

        if not game_state.started:
            for button in start_screen_buttons:
                button.handle_event(event)
        elif game_state.paused:
            for button in pause_screen_buttons:
                button.handle_event(event)
        elif not game_state.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_state.player.death_effect_active:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    target_world_x = mouse_x + game_state.scroll[0]
                    target_world_y = mouse_y + game_state.scroll[1]
                    game_state.add_bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                          target_world_x, target_world_y,
                                          asset_manager.images['bullet'])
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_state.player.death_effect_active:
                    mouse_pos_screen = pygame.mouse.get_pos()
                    target_world_x = mouse_pos_screen[0] + game_state.scroll[0]
                    target_world_y = mouse_pos_screen[1] + game_state.scroll[1]
                    game_state.add_bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                          target_world_x, target_world_y,
                                          asset_manager.images['bullet'])
                if event.button == 3 and not game_state.player.death_effect_active and \
                   game_state.player.garlic_count > 0 and game_state.garlic_shot is None:
                    game_state.player.garlic_count -= 1
                    game_state.player.garlic_changed = True

                    game_state.garlic_shot_start_time = current_time
                    mouse_x_screen, mouse_y_screen = pygame.mouse.get_pos()
                    world_mouse_x = mouse_x_screen + game_state.scroll[0]
                    world_mouse_y = mouse_y_screen + game_state.scroll[1]

                    start_x, start_y = game_state.player.rect.centerx, game_state.player.rect.centery
                    dx, dy = world_mouse_x - start_x, world_mouse_y - start_y

                    dist = math.hypot(dx, dy)
                    dx_norm, dy_norm = (dx/dist, dy/dist) if dist > 0 else (0,1)
                    angle = math.degrees(math.atan2(-dy_norm, dx_norm))

                    game_state.garlic_shot = {
                        "x": start_x, "y": start_y,
                        "dx": dx_norm, "dy": dy_norm,
                        "angle": angle, "active": True,
                        "rotation_angle": angle
                    }
                    game_state.garlic_shot_travel = 0
                    logging.debug(f"Garlic shot initiated towards ({world_mouse_x},{world_mouse_y}) with angle {angle:.2f} / Tir d'ail initié vers ({world_mouse_x},{world_mouse_y}) avec un angle de {angle:.2f}")
        else:
            for button in game_over_buttons:
                button.handle_event(event)

    if not game_state.started:
        if screen and start_screen_image and hasattr(start_screen_image, 'get_width'):
            screen.blit(start_screen_image, start_screen_pos)
        for button in start_screen_buttons:
            if screen: button.draw(screen)
    elif game_state.paused:
        if screen and game_over_image_ui and hasattr(game_over_image_ui, 'get_width'):
            game_over_x_pos = (screen_width - game_over_image_ui.get_width()) / 2
            game_over_y_pos = (screen_height - game_over_image_ui.get_height()) / 2
            screen.blit(game_over_image_ui, (game_over_x_pos, game_over_y_pos))
        for button in pause_screen_buttons:
            if screen: button.draw(screen)
    elif not game_state.game_over:
        if not game_state.player.death_effect_active:
            dx, dy = 0,0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_q]: dx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
            if keys[pygame.K_UP] or keys[pygame.K_z]: dy -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
            if dx != 0 or dy != 0:
                game_state.player.move(dx, dy, config.WORLD_SIZE)

        scroll_margin_x = screen_width * game_state.scroll_trigger
        scroll_margin_y = screen_height * game_state.scroll_trigger

        if game_state.player.rect.left < game_state.scroll[0] + scroll_margin_x:
            game_state.scroll[0] = max(0, game_state.player.rect.left - scroll_margin_x)
        elif game_state.player.rect.right > game_state.scroll[0] + screen_width - scroll_margin_x:
            game_state.scroll[0] = min(config.WORLD_SIZE[0] - screen_width, game_state.player.rect.right - screen_width + scroll_margin_x)

        if game_state.player.rect.top < game_state.scroll[1] + scroll_margin_y:
            game_state.scroll[1] = max(0, game_state.player.rect.top - scroll_margin_y)
        elif game_state.player.rect.bottom > game_state.scroll[1] + screen_height - scroll_margin_y:
            game_state.scroll[1] = min(config.WORLD_SIZE[1] - screen_height, game_state.player.rect.bottom - screen_height + scroll_margin_y)

        game_state.scroll[0] = max(0, min(game_state.scroll[0], config.WORLD_SIZE[0] - screen_width))
        game_state.scroll[1] = max(0, min(game_state.scroll[1], config.WORLD_SIZE[1] - screen_height))

        try:
            if not game_state.player.death_effect_active:
                game_state.update(current_time)

            if screen and grass_background and hasattr(grass_background, 'get_width'):
                screen.blit(grass_background, (-game_state.scroll[0], -game_state.scroll[1]))

            for carrot_enemy in game_state.carrots:
                if carrot_enemy.active and screen: carrot_enemy.draw(screen, game_state.scroll)

            player_pos_on_screen = (game_state.player.rect.x - game_state.scroll[0], game_state.player.rect.y - game_state.scroll[1])
            if game_state.player.death_effect_active:
                if int((current_time - game_state.player.death_effect_start_time) / 0.1) % 2 == 0:
                    if screen and game_state.player.original_image and hasattr(game_state.player.original_image, 'copy') :
                        tinted_image = game_state.player.original_image.copy()
                        tinted_image.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
                        screen.blit(tinted_image, player_pos_on_screen)
            elif game_state.player.invincible and int(current_time * config.PLAYER_INVINCIBILITY_FLASH_FREQUENCY) % 2 == 1:
                pass
            else:
                if screen: game_state.player.draw(screen, game_state.scroll)

            for bullet in game_state.bullets:
                if screen and bullet.image:
                    rotated_bullet_img = bullet.rotated_image
                    if rotated_bullet_img:
                         screen.blit(rotated_bullet_img, (bullet.rect.x - game_state.scroll[0], bullet.rect.y - game_state.scroll[1]))

            if game_state.garlic_shot and game_state.garlic_shot["active"]:
                if screen and garlic_image and hasattr(garlic_image, 'get_rect'):
                    rotated_garlic = pygame.transform.rotate(garlic_image, game_state.garlic_shot["rotation_angle"])
                    rotated_rect = rotated_garlic.get_rect(center=(game_state.garlic_shot["x"], game_state.garlic_shot["y"]))
                    screen.blit(rotated_garlic, (rotated_rect.x - game_state.scroll[0], rotated_rect.y - game_state.scroll[1]))

            for explosion in game_state.explosions:
                if screen: explosion.draw(screen, game_state.scroll)

            if screen: game_state.vampire.draw(screen, game_state.scroll, current_time)

            if screen and hp_image_ui and garlic_image:
                game_state.player.draw_ui(screen, hp_image_ui, garlic_image, config.MAX_GARLIC)

            if game_state.player.health_changed or game_state.player.garlic_changed or game_state.player.juice_changed:
                logging.debug(f"Player Stats - HP: {game_state.player.health}, Garlic: {game_state.player.garlic_count}, Carrot Juice: {game_state.player.carrot_juice_count}, Vampires Killed: {game_state.vampire_killed_count} / Stats Joueur - PV : {game_state.player.health}, Ail : {game_state.player.garlic_count}, Jus de Carotte : {game_state.player.carrot_juice_count}, Vampires Tués : {game_state.vampire_killed_count}")
                game_state.player.health_changed = False
                game_state.player.garlic_changed = False
                game_state.player.juice_changed = False

            for item in game_state.items:
                if item.active and screen: item.draw(screen, game_state.scroll)

        except Exception as e:
            logging.exception(f"ERROR during game logic/draw: {e} / ERREUR pendant la logique/le dessin du jeu : {e}")
            running = False
            return

        if game_state.player.health <= 0 and not game_state.game_over and not game_state.player.death_effect_active:
            handle_player_death()

        if game_state.player.death_effect_active:
            time_elapsed_death = current_time - game_state.player.death_effect_start_time
            if time_elapsed_death >= config.PLAYER_DEATH_DURATION:
                game_state.game_over = True
                game_state.player.death_effect_active = False
                logging.info("Player death animation complete. Game Over. / Animation de mort du joueur terminée. Game Over.")
    else:
        if screen and game_over_image_ui and hasattr(game_over_image_ui, 'get_width'):
            game_over_x_pos = (screen_width - game_over_image_ui.get_width()) / 2
            game_over_y_pos = (screen_height - game_over_image_ui.get_height()) / 2
            screen.blit(game_over_image_ui, (game_over_x_pos, game_over_y_pos))
        for button in game_over_buttons:
            if screen: button.draw(screen)

        if pygame.mixer.get_init() and not pygame.mixer.music.get_busy():
            music_path_game_over = get_asset_path(config.MUSIC_GAMEOVER)
            if music_path_game_over:
                try:
                    pygame.mixer.music.load(music_path_game_over)
                    pygame.mixer.music.play(-1)
                except pygame.error as e:
                    logging.exception(f"Error playing game over music: {e} / Erreur lors de la lecture de la musique de game over : {e}")

    if screen:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        crosshair_img_ref = asset_manager.images.get('crosshair')
        if crosshair_img_ref and hasattr(crosshair_img_ref, 'get_rect'):
            crosshair_rect_instance = crosshair_img_ref.get_rect(center=(mouse_x, mouse_y))
            screen.blit(crosshair_img_ref, crosshair_rect_instance)

    pygame.display.flip()
    time.sleep(config.FRAME_DELAY)
    logging.debug("run_gui_mode: Frame processing ended. / run_gui_mode : Traitement de la frame terminé.")


def run_cli_mode():
    """
    Handles the entire game loop for Command Line Interface (CLI) mode.
    Presents text-based menus and options. Game logic (like entity updates) is minimal or stubbed in CLI.

    *Gère l'intégralité de la boucle de jeu pour le mode Interface en Ligne de Commande (CLI).*
    *Présente des menus et des options textuels. La logique du jeu (comme les mises à jour d'entités) est minimale ou simulée en CLI.*
    """
    global running, game_state, args

    logging.debug("run_cli_mode: Iteration started. / run_cli_mode : Itération démarrée.")

    if not game_state.started:
        logging.debug("run_cli_mode: Game not started, displaying start menu. / run_cli_mode : Jeu non démarré, affichage du menu de démarrage.")
        logging.info("\n--- LapinCarotte ---")
        logging.info("Start Screen (CLI Mode) / *Écran de Démarrage (Mode CLI)*")
        logging.info("1. Start Game / *Commencer le jeu*")
        logging.info("2. Exit / *Quitter*")
        choice = ""
        try:
            choice = input("Enter choice / *Entrez votre choix*: ").strip()
        except EOFError:
            logging.info("EOF received on main menu, quitting. / EOF reçu dans le menu principal, fermeture.")
            quit_game()
            return

        if choice == '1':
            start_game()
        elif choice == '2':
            quit_game()
        elif running:
            logging.warning("Invalid choice on start screen. Please enter 1 or 2. / Choix invalide sur l'écran de démarrage. Veuillez entrer 1 ou 2.")

    elif game_state.paused:
        logging.debug("run_cli_mode: Game paused, displaying pause menu. / run_cli_mode : Jeu en pause, affichage du menu pause.")
        logging.info("\n--- PAUSED (CLI Mode) / *PAUSE (Mode CLI)* ---")
        logging.info("1. Continue / *Continuer*")
        logging.info("2. Settings (Not Implemented) / *Paramètres (Non implémenté)*")
        logging.info("3. Quit Game / *Quitter le jeu*")
        choice = ""
        try:
            choice = input("Enter choice / *Entrez votre choix*: ").strip()
        except EOFError:
            logging.info("EOF received on pause menu, quitting. / EOF reçu dans le menu pause, fermeture.")
            quit_game()
            return

        if choice == '1':
            resume_game_callback()
        elif choice == '2':
            open_settings_callback()
        elif choice == '3':
            quit_game()
        elif running:
            logging.warning("Invalid choice on pause menu. / Choix invalide dans le menu pause.")

    elif game_state.game_over:
        logging.debug("run_cli_mode: Game over, displaying game over menu. / run_cli_mode : Game over, affichage du menu game over.")
        logging.info("\n--- GAME OVER (CLI Mode) ---")
        logging.info("1. Restart / *Recommencer*")
        logging.info("2. Exit / *Quitter*")
        choice = ""
        try:
            choice = input("Enter choice / *Entrez votre choix*: ").strip()
        except EOFError:
            logging.info("EOF received on game over menu, quitting. / EOF reçu dans le menu game over, fermeture.")
            quit_game()
            return

        if choice == '1':
            reset_game()
        elif choice == '2':
            quit_game()
        elif running:
            logging.warning("Invalid choice on game over menu. / Choix invalide dans le menu game over.")

    else:
        logging.debug("run_cli_mode: Game active, displaying active game options. / run_cli_mode : Jeu actif, affichage des options du jeu actif.")
        logging.info("\n--- Game Active (CLI Mode) / *Jeu Actif (Mode CLI)* ---")
        logging.info(f"Player HP: {game_state.player.health} (Note: Game logic not running in CLI yet / *Note : La logique du jeu ne tourne pas encore en CLI*)")
        logging.info("Options: (esc)ause, (q)uit, (d)ie (simulate death for testing) / *Options : (esc) Pause, (q)uitter, (d)écéder (simuler mort pour test)*")

        cli_action = ""
        try:
            cli_action = input("Action: ").strip().lower()
            logging.debug(f"CLI action received: '{cli_action}' / Action CLI reçue : '{cli_action}'")
        except EOFError:
            logging.info("EOF received during active game, quitting. / EOF reçu pendant le jeu actif, fermeture.")
            quit_game()
            return

        if cli_action == 'esc':
            logging.debug("CLI action 'esc' received, pausing game. / Action CLI 'esc' reçue, mise en pause du jeu.")
            game_state.pause_game()
        elif cli_action == 'q':
            logging.debug("CLI action 'q' received, quitting game. / Action CLI 'q' reçue, fermeture du jeu.")
            quit_game()
        elif cli_action == 'd':
            logging.debug("CLI action 'd' received, simulating player death. / Action CLI 'd' reçue, simulation de la mort du joueur.")
            game_state.player.health = 0
            game_state.game_over = True
            logging.info("Simulating player death for CLI testing... Player HP set to 0, game_over set to True. / Simulation de la mort du joueur pour test CLI... PV Joueur mis à 0, game_over mis à True.")

    if running and args.cli:
        time.sleep(0.1)
    logging.debug("run_cli_mode: Iteration ended. / run_cli_mode : Itération terminée.")


def main_loop():
    """
    The main game loop. Alternates between GUI and CLI mode based on arguments.
    Continues as long as the global 'running' flag is True.

    *La boucle de jeu principale. Alterne entre les modes GUI et CLI en fonction des arguments.*
    *Continue tant que l'indicateur global 'running' est True.*
    """
    global running
    logging.debug("Main loop started. / Boucle principale démarrée.")
    while running:
        if not args.cli:
            run_gui_mode()
        else:
            run_cli_mode()
    logging.debug("Main loop ended because 'running' is False. / Boucle principale terminée car 'running' est False.")

def main_entry_point():
    global args, screen, screen_width, screen_height, asset_manager, game_state, current_time
    global start_screen_image, start_screen_pos
    global grass_background, garlic_image, hp_image_ui, game_over_image_ui
    global start_screen_buttons, game_over_buttons, pause_screen_buttons
    global running, can_toggle_pause

    args = parse_arguments()
    setup_logging(args)

    screen, screen_width, screen_height = initialize_pygame(args)

    asset_manager = AssetManager(cli_mode=args.cli)
    assets = load_game_assets(args, asset_manager, screen_width, screen_height)

    # Set global variables for run_gui_mode to use
    start_screen_image = assets['start_screen_image']
    start_screen_pos = assets['start_screen_pos']
    grass_background = assets['grass_background']
    garlic_image = assets['garlic_image']
    hp_image_ui = assets['hp_image_ui']
    game_over_image_ui = assets['game_over_image_ui']

    game_state = GameState(asset_manager, cli_mode=args.cli)

    callbacks = {
        'start': start_game,
        'quit': quit_game,
        'reset': reset_game,
        'resume': resume_game_callback,
        'settings': open_settings_callback
    }

    buttons = create_buttons(args, screen_width, screen_height, assets, callbacks)
    start_screen_buttons = buttons['start']
    game_over_buttons = buttons['game_over']
    pause_screen_buttons = buttons['pause']

    current_time = time.time()
    running = True

    try:
        main_loop()
    finally:
        logging.info("Application shutting down... / Fermeture de l'application...")
        if not args.cli and pygame.get_init():
            pygame.quit()
            logging.info("Pygame quit successfully. / Pygame quitté avec succès.")
        logging.info("Shutdown complete. / Fermeture terminée.")

if __name__ == '__main__':
    main_entry_point()
