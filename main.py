#!/usr/bin/env python3
import os
import pygame
import time
import sys
import random
import math
import config
from asset_manager import AssetManager
from game_entities import Player, Bullet, Carrot, Vampire, Explosion, Collectible, Button
from game_state import GameState
from config import *

def get_asset_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
screen_width, screen_height = screen.get_size()

asset_manager = AssetManager()
asset_manager.load_assets()
pygame.display.set_icon(asset_manager.images['icon'])
pygame.mouse.set_visible(False)

if sys.platform == 'win32':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('LapinCarotte.1.0')
    pygame.display.set_caption("LapinCarotte", "LapinCarotte")

game_state = GameState(asset_manager)
start_screen_image = asset_manager.images['start_screen']
start_screen_pos = (
    (screen_width - start_screen_image.get_width()) // 2,
    (screen_height - start_screen_image.get_height()) // 2
)

pygame.mixer.music.load(asset_manager._get_path(config.MUSIC_INTRO))
pygame.mixer.music.play(-1)

current_time = 0.0

# Game state modification functions (used as callbacks for buttons)
def _play_game_music_and_sound(sound_to_play=None):
    """Helper function to stop current music, play game music, and an optional sound effect."""
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(asset_manager._get_path(config.MUSIC_GAME))
        pygame.mixer.music.play(-1)
        if sound_to_play and sound_to_play in asset_manager.sounds:
            asset_manager.sounds[sound_to_play].play()
    except pygame.error as e:
        print(f"ERROR: Could not load or play sound: {e}")

def start_game():
    game_state.started = True
    _play_game_music_and_sound('press_start')

def reset_game():
    game_state.reset()
    _play_game_music_and_sound('press_start')

def quit_game():
    global running
    running = False

# Define _rect variables needed by Buttons earlier
# These are used to get width/height for button positioning.
# The actual images are loaded by AssetManager and passed to Button constructor.
# We use the mock from AssetManager in tests, which has get_rect()
restart_button_rect = asset_manager.images['restart'].get_rect()
exit_button_rect = asset_manager.images['exit'].get_rect()
start_button_rect = asset_manager.images['start'].get_rect()


# Button instantiation
start_button_img = asset_manager.images['start']
# exit_button_img is loaded from asset_manager.images['exit'] directly where needed for Button creation.
# No need for a separate global variable if only used once or if clarity is maintained.
# Retaining for now as it was previously defined, but the comment "# Already loaded by AssetManager" is slightly misleading
# as this line IS an assignment from the already loaded dictionary.
exit_button_img = asset_manager.images['exit']

start_button_start_screen = Button(
    start_screen_pos[0] + START_SCREEN_BUTTON_START_X_OFFSET,
    start_screen_pos[1] + START_SCREEN_BUTTON_START_Y_OFFSET,
    start_button_img,
    start_game
)
exit_button_start_screen = Button(
    start_screen_pos[0] + START_SCREEN_BUTTON_EXIT_X_OFFSET,
    start_screen_pos[1] + START_SCREEN_BUTTON_EXIT_Y_OFFSET,
    exit_button_img,
    quit_game
)
start_screen_buttons = [start_button_start_screen, exit_button_start_screen]

# Game Over screen buttons
# restart_button_img is loaded from asset_manager.images['restart'] directly for Button creation.
restart_button_img = asset_manager.images['restart']

restart_button_game_over_screen = Button(
    # Positioned left of center, using its own width (from restart_button_rect) for alignment
    screen_width / 2 - restart_button_rect.width - BUTTON_SPACING / 2,
    screen_height * 3 / 4 - restart_button_rect.height / 2,
    restart_button_img,
    reset_game # Callback for restart
)
exit_button_game_over_screen = Button(
    # Positioned right of center, using BUTTON_SPACING for gap
    screen_width / 2 + BUTTON_SPACING / 2,
    screen_height * 3 / 4 - exit_button_rect.height / 2, # Uses exit_button_rect for its height
    exit_button_img,
    quit_game # Callback for exit
)
game_over_buttons = [restart_button_game_over_screen, exit_button_game_over_screen]


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# These _rect variables are defined once, early, as their .width/.height attributes are used by Button positioning logic
# The variables defined at lines 71-73 are the single source of truth.
# restart_button_rect = asset_manager.images['restart'].get_rect() # Defined at line 71
# exit_button_rect = asset_manager.images['exit'].get_rect()       # Defined at line 72
# start_button_rect = asset_manager.images['start'].get_rect()     # Defined at line 73

# Other rects, not directly used for button positioning logic that needs them *before* this point
carrot_rect = asset_manager.images['carrot'].get_rect()
vampire_rect = asset_manager.images['vampire'].get_rect()
hp_rect = asset_manager.images['hp'].get_rect()
game_over_rect = asset_manager.images['game_over'].get_rect()


grass_image = asset_manager.images['grass']
grass_background = pygame.Surface(WORLD_SIZE, pygame.SRCALPHA)
_grass_w, _grass_h = grass_image.get_size()
for x_g in range(0, WORLD_SIZE[0], _grass_w):
    for y_g in range(0, WORLD_SIZE[1], _grass_h):
        grass_background.blit(grass_image, (x_g, y_g))
        
garlic_image = asset_manager.images['garlic']
hp_image = asset_manager.images['hp']
game_over_image = asset_manager.images['game_over']
restart_button_image = asset_manager.images['restart']
exit_button_image = asset_manager.images['exit']

def handle_player_death():
    global current_time
    if not game_state.game_over and not game_state.player.death_effect_active:
        # print(f"[TRACE] handle_player_death: Called at game time {current_time:.4f}")
        game_state.player.death_effect_active = True
        game_state.player.death_effect_start_time = current_time
        # print(f"[TRACE] handle_player_death: Set death_effect_active=True, death_effect_start_time={game_state.player.death_effect_start_time:.4f}")
    try:
        pygame.mixer.music.stop()
        asset_manager.sounds['death'].play()
    except pygame.error as e:
        print(f"ERROR: Could not load or play sound: {e}")

# This is the main game loop variable
running = True

# The main game loop is not started immediately to allow tests to import and inspect `main.py`
# without automatically running the game. The game execution is wrapped in a function `main_loop()`
# and called only when `__name__ == "__main__"`.

# Callbacks for Pause Screen Buttons
def continue_game():
    game_state.paused = False
    # Potentially resume music or other pause-specific actions here

def open_settings_from_pause():
    game_state.show_settings = True
    # game_state.paused will remain true, settings will overlay pause

# Pause screen buttons (defined globally for access in the loop)
continue_button_img = None # Will be loaded if not already
settings_button_img = None # Will be loaded if not already
pause_screen_buttons = []

def initialize_pause_buttons():
    global continue_button_img, settings_button_img, pause_screen_buttons
    # For now, let's reuse existing button images if possible, or create placeholders
    # Ideally, specific images for "Continue" and "Settings" would be added to AssetManager
    try:
        continue_button_img = asset_manager.images.get('restart', asset_manager.images['start']) # Placeholder
        settings_button_img = asset_manager.images.get('exit', asset_manager.images['start']) # Placeholder
    except KeyError:
        print("Error: Default button images for pause screen not found in asset_manager. Using fallback.")
        # Fallback: Create simple text-based buttons if images are missing (more complex)
        # For now, this will likely cause an error if start/restart/exit are not loaded.
        # This highlights the need for actual assets or more robust fallback.
        pass


    continue_button = Button(
        screen_width / 2 - continue_button_img.get_width() - BUTTON_SPACING / 2,
        screen_height * 2 / 3 - continue_button_img.get_height() / 2, # Position higher than game over buttons
        continue_button_img,
        continue_game
    )
    settings_button = Button(
        screen_width / 2 + BUTTON_SPACING / 2,
        screen_height * 2 / 3 - settings_button_img.get_height() / 2,
        settings_button_img,
        open_settings_from_pause
    )
    pause_screen_buttons = [continue_button, settings_button]

import inspect # For dynamically listing config variables

# Settings screen buttons and layout variables
settings_screen_buttons = []
back_button_img = None
config_vars_layout = [] # To store UI elements for each config variable
font_small = None # For settings text
setting_item_height = 40 # Height for each setting item
setting_start_y = 0 # Initial Y position for the first setting
settings_scroll_offset_y = 0 # For scrolling settings
settings_view_height = 0 # Visible height for settings area
total_settings_content_height = 0 # Total height of all settings items

# Store original config values
original_config_values = {}

def store_original_config():
    global original_config_values
    for name, value in inspect.getmembers(config):
        if not name.startswith('_') and isinstance(value, (int, float, str, bool, tuple)):
            original_config_values[name] = value

def get_default_value(var_name):
    return original_config_values.get(var_name, "N/A")


# --- Callbacks for modifying config values ---
def increase_config_value(var_name, step=1, max_val=None):
    try:
        current_value = getattr(config, var_name)
        new_value = current_value + step
        if isinstance(current_value, float): # Handle float precision if necessary
            new_value = round(new_value, 2)
        if max_val is not None and new_value > max_val:
            new_value = max_val
        setattr(config, var_name, new_value)
        print(f"Increased {var_name} to {getattr(config, var_name)}")
    except Exception as e:
        print(f"Error increasing {var_name}: {e}")

def decrease_config_value(var_name, step=1, min_val=None):
    try:
        current_value = getattr(config, var_name)
        new_value = current_value - step
        if isinstance(current_value, float): # Handle float precision
            new_value = round(new_value, 2)
        if min_val is not None and new_value < min_val:
            new_value = min_val
        setattr(config, var_name, new_value)
        print(f"Decreased {var_name} to {getattr(config, var_name)}")
    except Exception as e:
        print(f"Error decreasing {var_name}: {e}")

def reset_config_value(var_name):
    try:
        default_value = get_default_value(var_name)
        if default_value != "N/A":
            setattr(config, var_name, default_value)
            print(f"Reset {var_name} to default: {getattr(config, var_name)}")
        else:
            print(f"Could not find default value for {var_name}")
    except Exception as e:
        print(f"Error resetting {var_name}: {e}")


def close_settings():
    game_state.show_settings = False
    # Apply changes to live objects if necessary
    # Example for Player speed:
    if hasattr(game_state, 'player') and game_state.player is not None:
        game_state.player.speed = config.PLAYER_SPEED
        print(f"Applied PLAYER_SPEED ({config.PLAYER_SPEED}) to live player object.")

def initialize_settings_ui_elements():
    """Initialize UI elements for the settings screen, including dynamic config vars."""
    global back_button_img, settings_screen_buttons, config_vars_layout, font_small
    global setting_start_y, settings_view_height, total_settings_content_height, settings_scroll_offset_y

    font_small = pygame.font.Font(None, 32) # Smaller font for settings details
    title_bottom_y = screen_height / 4 + 30 # End of title area
    back_button_top_y = screen_height * 0.90 - (asset_manager.images.get('exit', asset_manager.images['start']).get_height() / 2 if asset_manager.images.get('exit') else 20) # Approx top of back button

    setting_start_y = title_bottom_y + 20 # Start Y for settings list
    settings_view_height = back_button_top_y - setting_start_y - 20 # Available height for scrolling list
    settings_scroll_offset_y = 0 # Reset scroll on re-init

    # 1. Back Button
    try:
        back_button_img = asset_manager.images.get('exit', asset_manager.images['start'])
    except KeyError:
        print("Error: Default button image for settings back button not found.")

    if back_button_img:
        back_button = Button(
            screen_width / 2 - back_button_img.get_width() / 2,
            screen_height * 0.90 - back_button_img.get_height() / 2,
            back_button_img,
            close_settings
        )
        settings_screen_buttons = [back_button]
    else:
        settings_screen_buttons = []

    # 2. Dynamic Config Variables UI
    config_vars_layout = []
    current_y_offset = 0 # Relative Y position for items within the scrollable area

    # Define metadata for relevant config variables (name, min, max, step)
    # This should be expanded as per step 5 of the plan
    config_metadata = {
        "PLAYER_SPEED": {"min": 1, "max": 20, "step": 1, "type": "int"},
        "BULLET_SPEED": {"min": 1, "max": 20, "step": 1, "type": "int"},
        "CARROT_SPEED": {"min": 1, "max": 10, "step": 1, "type": "int"},
        "VAMPIRE_SPEED": {"min": 1, "max": 10, "step": 1, "type": "int"},
        "FRAME_DELAY": {"min": 0.005, "max": 0.1, "step": 0.001, "type": "float"},
        # Add more variables here, e.g., START_HEALTH, MAX_HEALTH etc.
    }

    button_width = 40 # Width for +/- buttons
    button_height = font_small.get_height()

    # Create simple text buttons for +/- (could use images later)
    plus_surface = font_small.render("+", True, (0,0,0), (200,200,200)) # Black text on grey bg
    minus_surface = font_small.render("-", True, (0,0,0), (200,200,200))
    reset_surface = font_small.render("R", True, (0,0,0), (200,200,150))


    for name, meta in config_metadata.items():
        if hasattr(config, name):
            var_value = getattr(config, name)

            # Label for the config variable
            label_text = f"{name}:"
            label_surf = font_small.render(label_text, True, (230, 230, 230))
            label_pos_x = screen_width * 0.25 # Align left

            # Value display (updated dynamically)
            # Value display position will be to the right of the label

            # Buttons for + and -
            minus_btn_x = screen_width * 0.55
            plus_btn_x = screen_width * 0.65
            reset_btn_x = screen_width * 0.75

            # Create Button instances for +/-
            # We need to pass the var_name to the callback. functools.partial can help.
            from functools import partial

            decrease_cb = partial(decrease_config_value, name, meta['step'], meta['min'])
            increase_cb = partial(increase_config_value, name, meta['step'], meta['max'])
            reset_cb = partial(reset_config_value, name)

            # Using pygame.Surface directly for +/- buttons for simplicity now
            # Ideally, these would also be Button class instances if complex interaction is needed
            # For now, storing rects and surfaces for drawing and basic click detection
            # Positions are relative to the start of the settings list, adjusted by scroll_offset_y for drawing/events

            item_y_pos_relative = current_y_offset # Relative to the top of the scrollable area

            config_vars_layout.append({
                "name": name,
                "label_surf": label_surf,
                "label_pos_x": label_pos_x, # Store X, Y will be calculated with scroll
                "value_pos_x": screen_width * 0.45,
                "minus_button_rel_rect_base": pygame.Rect(minus_btn_x, item_y_pos_relative, button_width, button_height), # Base relative rect
                "minus_surface": minus_surface,
                "decrease_cb": decrease_cb,
                "plus_button_rel_rect_base": pygame.Rect(plus_btn_x, item_y_pos_relative, button_width, button_height),  # Base relative rect
                "plus_surface": plus_surface,
                "increase_cb": increase_cb,
                "reset_button_rel_rect_base": pygame.Rect(reset_btn_x, item_y_pos_relative, button_width, button_height), # Base relative rect
                "reset_surface": reset_surface,
                "reset_cb": reset_cb,
                "item_y_pos_relative": item_y_pos_relative # Store relative Y for drawing calc
            })
            current_y_offset += setting_item_height

    total_settings_content_height = current_y_offset # Total height of all items
    # Store original config values after everything is set up
    store_original_config()


def main_loop():
    global running # Ensure 'running' can be modified by quit_game
    global current_time # Ensure 'current_time' is updated

    initialize_pause_buttons()
    # initialize_settings_buttons() # This is now part of initialize_settings_ui_elements
    initialize_settings_ui_elements() # Initialize settings UI elements, including config vars

    while running:
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN: # Global key events
                if event.key == pygame.K_ESCAPE:
                    if game_state.started and not game_state.game_over:
                        if game_state.show_settings: # If in settings, ESC closes settings
                            game_state.show_settings = False
                        else: # Otherwise, toggle pause
                            game_state.paused = not game_state.paused
                            if game_state.paused:
                                pass # Actions when pausing (e.g., pause music)
                            else:
                                pass # Actions when unpausing (e.g., resume music)

            if not game_state.started: # Start Screen
                for button in start_screen_buttons:
                    button.handle_event(event)
            elif game_state.game_over: # Game Over Screen
                for button in game_over_buttons:
                    button.handle_event(event)
            elif game_state.paused: # Pause Screen (handles its own events, including settings)
                if game_state.show_settings:
                    for button in settings_screen_buttons: # Handle Back button etc.
                        button.handle_event(event)

                    # Handle clicks on +/- for config vars & scrolling
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: # Left click for buttons
                            mouse_pos = pygame.mouse.get_pos()
                            for item in config_vars_layout:
                                # Calculate actual screen rect for collision, considering scroll
                                actual_minus_rect = item["minus_button_rel_rect_base"].move(0, setting_start_y - settings_scroll_offset_y)
                                actual_plus_rect = item["plus_button_rel_rect_base"].move(0, setting_start_y - settings_scroll_offset_y)
                                actual_reset_rect = item["reset_button_rel_rect_base"].move(0, setting_start_y - settings_scroll_offset_y)

                                if actual_minus_rect.top >= setting_start_y and actual_minus_rect.bottom <= setting_start_y + settings_view_height: # Check if visible
                                    if actual_minus_rect.collidepoint(mouse_pos):
                                        item["decrease_cb"]()
                                        break
                                if actual_plus_rect.top >= setting_start_y and actual_plus_rect.bottom <= setting_start_y + settings_view_height:
                                    if actual_plus_rect.collidepoint(mouse_pos):
                                        item["increase_cb"]()
                                        break
                                if actual_reset_rect.top >= setting_start_y and actual_reset_rect.bottom <= setting_start_y + settings_view_height:
                                    if actual_reset_rect.collidepoint(mouse_pos):
                                        item["reset_cb"]()
                                        break
                        elif event.button == 4: # Scroll Up
                            settings_scroll_offset_y = max(0, settings_scroll_offset_y - setting_item_height)
                        elif event.button == 5: # Scroll Down
                            if total_settings_content_height > settings_view_height:
                                max_scroll = total_settings_content_height - settings_view_height
                                settings_scroll_offset_y = min(max_scroll, settings_scroll_offset_y + setting_item_height)
                else: # Pause screen buttons
                    for button in pause_screen_buttons:
                        button.handle_event(event)
            else: # Active Gameplay (not paused, not game over, started)
                if event.type == pygame.KEYDOWN:
                    # Space for shooting is already handled by general keydown if not paused
                    if event.key == pygame.K_SPACE and not game_state.player.death_effect_active:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        game_state.bullets.append(Bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                                         mouse_x - game_state.player.rect.centerx + game_state.scroll[0],
                                                         mouse_y - game_state.player.rect.centery + game_state.scroll[1],
                                                         asset_manager.images['bullet']))
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not game_state.player.death_effect_active: # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        world_mouse = (mouse_pos[0] + game_state.scroll[0], mouse_pos[1] + game_state.scroll[1])
                        game_state.bullets.append(Bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                                         world_mouse[0], world_mouse[1], asset_manager.images['bullet']))
                    if event.button == 3 and not game_state.player.death_effect_active and game_state.player.garlic_count > 0 and game_state.garlic_shot is None: # Right click
                        game_state.player.garlic_count -= 1
                        game_state.garlic_shot_start_time = current_time
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        world_mouse_x, world_mouse_y = mouse_x + game_state.scroll[0], mouse_y + game_state.scroll[1]
                        start_x, start_y = game_state.player.rect.centerx, game_state.player.rect.centery
                        dx, dy = world_mouse_x - start_x, world_mouse_y - start_y
                        dist = math.hypot(dx, dy)
                        dx_norm, dy_norm = (dx/dist, dy/dist) if dist > 0 else (0,0)
                        angle = math.degrees(math.atan2(-dy_norm, dx_norm)) if dist > 0 else 0
                        game_state.garlic_shot = {"x": start_x, "y": start_y, "dx": dx_norm, "dy": dy_norm, "angle": angle, "active": True, "rotation_angle": angle}


        # Drawing Logic
        if not game_state.started: # Start Screen
            screen.blit(start_screen_image, start_screen_pos)
            for button in start_screen_buttons:
                button.draw(screen)
        elif game_state.game_over: # Game Over Screen
            screen.fill((0, 0, 0))
            game_over_x = (screen_width - game_over_rect.width) / 2
            game_over_y = (screen_height - game_over_rect.height) / 2
            screen.blit(game_over_image, (game_over_x, game_over_y))
            for button in game_over_buttons:
                button.draw(screen)
            if not pygame.mixer.music.get_busy():
                music_path = asset_manager._get_path(config.MUSIC_GAMEOVER)
                if music_path:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play(-1)

        elif game_state.paused: # Pause Screen or Settings Screen
            # Draw the game state as it was when paused
            screen.blit(grass_background, (-game_state.scroll[0], -game_state.scroll[1]))
            for carrot in game_state.carrots:
                if carrot.active: screen.blit(carrot.image, (carrot.rect.x - game_state.scroll[0], carrot.rect.y - game_state.scroll[1]))

            player_pos_on_screen = (game_state.player.rect.x - game_state.scroll[0], game_state.player.rect.y - game_state.scroll[1])
            screen.blit(game_state.player.image, player_pos_on_screen) # Simplified player draw for pause

            for bullet in game_state.bullets:
                screen.blit(bullet.rotated_image, (bullet.rect.x - game_state.scroll[0], bullet.rect.y - game_state.scroll[1]))
            if game_state.garlic_shot and game_state.garlic_shot["active"]:
                rotated_garlic = pygame.transform.rotate(garlic_image, game_state.garlic_shot["rotation_angle"])
                rotated_rect = rotated_garlic.get_rect(center=(game_state.garlic_shot["x"], game_state.garlic_shot["y"]))
                screen.blit(rotated_garlic, (rotated_rect.x - game_state.scroll[0], rotated_rect.y - game_state.scroll[1]))
            for explosion in game_state.explosions: # Draw existing explosions
                if explosion.active: explosion.draw(screen, game_state.scroll)
            game_state.vampire.draw(screen, game_state.scroll, current_time) # Draw vampire in its current state
            game_state.player.draw_ui(screen, hp_image, garlic_image, MAX_GARLIC) # Draw UI

            # Overlay for pause/settings
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) # Semi-transparent black overlay
            screen.blit(overlay, (0,0))

            if game_state.show_settings:
                # Draw Settings Screen
                font = pygame.font.Font(None, 74)
                text_surf = font.render("Settings", True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=(screen_width / 2, screen_height / 4)) # Title
                screen.blit(text_surf, text_rect)

                # Draw dynamic config variables
                if font_small: # Ensure font is loaded
                    # Define a clipping rectangle for the settings items
                    clip_rect = pygame.Rect(0, setting_start_y, screen_width, settings_view_height)
                    screen.set_clip(clip_rect)

                    for item in config_vars_layout:
                        # Calculate actual Y position on the screen based on scroll offset
                        draw_y = setting_start_y + item["item_y_pos_relative"] - settings_scroll_offset_y

                        # Basic check if the item is within the broader visible screen area (clipping will handle specifics)
                        if draw_y + setting_item_height > setting_start_y - setting_item_height and draw_y < setting_start_y + settings_view_height + setting_item_height:

                            # Draw Label
                            screen.blit(item["label_surf"], (item["label_pos_x"], draw_y))

                            # Draw Value (dynamically fetched)
                            current_value = getattr(config, item["name"], "N/A")
                            value_text = f"{current_value}"
                            if isinstance(current_value, float):
                                value_text = f"{current_value:.3f}" # Format float

                            default_val = get_default_value(item['name'])
                            default_text = f"(Default: {default_val})"
                            if isinstance(default_val, float):
                                default_text = f"(Default: {default_val:.3f})"

                            # Add range information from metadata
                            meta = config_metadata.get(item["name"], {})
                            range_text = ""
                            if meta.get("type") in ["int", "float"]:
                                min_val = meta.get("min", "N/A")
                                max_val = meta.get("max", "N/A")
                                range_text = f" [{min_val}-{max_val}]"

                            full_value_text = f"{value_text} {default_text}{range_text}"
                            value_surf = font_small.render(full_value_text, True, (220, 220, 220))
                            value_display_y = draw_y + item["label_surf"].get_height() / 2
                            value_rect = value_surf.get_rect(midleft=(item["value_pos_x"], value_display_y))
                            screen.blit(value_surf, value_rect)

                            # Draw +/-/R Buttons, adjusting their Y position based on scroll
                            minus_draw_rect = item["minus_button_rel_rect_base"].copy()
                            minus_draw_rect.y = draw_y
                            pygame.draw.rect(screen, (200,200,200), minus_draw_rect)
                            screen.blit(item["minus_surface"], minus_draw_rect.topleft)

                            plus_draw_rect = item["plus_button_rel_rect_base"].copy()
                            plus_draw_rect.y = draw_y
                            pygame.draw.rect(screen, (200,200,200), plus_draw_rect)
                            screen.blit(item["plus_surface"], plus_draw_rect.topleft)

                            reset_draw_rect = item["reset_button_rel_rect_base"].copy()
                            reset_draw_rect.y = draw_y
                            pygame.draw.rect(screen, (200,200,150), reset_draw_rect)
                            screen.blit(item["reset_surface"], reset_draw_rect.topleft)
                        # End of the "if draw_y + setting_item_height > ..." block

                    screen.set_clip(None) # Reset clipping

                    # Optional: Add a visual scrollbar indicator
                    if total_settings_content_height > settings_view_height:
                        scrollbar_track_height = settings_view_height
                        scrollbar_height = max(20, scrollbar_track_height * (settings_view_height / total_settings_content_height))

                        # Ensure scrollbar_thumb_y_ratio is not dividing by zero if content height equals view height
                        current_scrollable_height = total_settings_content_height - settings_view_height
                        scrollbar_thumb_y_ratio = 0
                        if current_scrollable_height > 0:
                             scrollbar_thumb_y_ratio = settings_scroll_offset_y / current_scrollable_height

                        scrollbar_thumb_y = setting_start_y + scrollbar_thumb_y_ratio * (scrollbar_track_height - scrollbar_height)

                        pygame.draw.rect(screen, (80, 80, 80),
                                         (screen_width - 25, setting_start_y, 15, scrollbar_track_height)) # Scrollbar Track
                        pygame.draw.rect(screen, (150, 150, 150),
                                         (screen_width - 25, scrollbar_thumb_y, 15, scrollbar_height)) # Scrollbar Thumb

                for button in settings_screen_buttons: # Draw other settings buttons (e.g., Back button)
                    button.draw(screen)

            else: # Pause Screen UI
                font = pygame.font.Font(None, 100) # Larger font for "Paused"
                text_surf = font.render("Paused", True, (255, 255, 255))
                text_rect = text_surf.get_rect(center=(screen_width / 2, screen_height / 3))
                screen.blit(text_surf, text_rect)
                for button in pause_screen_buttons:
                    button.draw(screen)

        else:
            # Player movement and game logic updates only if not paused and not game over
            if not game_state.player.death_effect_active:
                dx, dy = 0,0
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_q]: dx -= 1
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
                if keys[pygame.K_UP] or keys[pygame.K_z]: dy -= 1
                if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
                if dx != 0 or dy != 0:
                    game_state.player.move(dx, dy, game_state.world_size)

            if game_state.player.rect.x < game_state.scroll[0] + screen_width * game_state.scroll_trigger:
                game_state.scroll[0] = max(0, game_state.player.rect.x - screen_width * game_state.scroll_trigger)
            elif game_state.player.rect.x + game_state.player.rect.width > game_state.scroll[0] + screen_width * (1 - game_state.scroll_trigger):
                game_state.scroll[0] = min(game_state.world_size[0] - screen_width, game_state.player.rect.x - screen_width*(1-game_state.scroll_trigger) + game_state.player.rect.width)
            if game_state.player.rect.y < game_state.scroll[1] + screen_height * game_state.scroll_trigger:
                game_state.scroll[1] = max(0, game_state.player.rect.y - screen_height * game_state.scroll_trigger)
            elif game_state.player.rect.y + game_state.player.rect.height > game_state.scroll[1] + screen_height * (1 - game_state.scroll_trigger):
                game_state.scroll[1] = min(game_state.world_size[1] - screen_height, game_state.player.rect.y - screen_height*(1-game_state.scroll_trigger) + game_state.player.rect.height)

            # Inner try...except for game logic and drawing remains
            try:
                # Game logic updates only if not paused, not game over, and player is not in death animation
                if not game_state.paused and not game_state.game_over and not game_state.player.death_effect_active:
                    game_state.update(current_time)

                # Drawing game world (common for active play and for pause background)
                screen.blit(grass_background, (-game_state.scroll[0], -game_state.scroll[1]))
                for carrot in game_state.carrots:
                    if carrot.active: screen.blit(carrot.image, (carrot.rect.x - game_state.scroll[0], carrot.rect.y - game_state.scroll[1]))

                player_pos = (game_state.player.rect.x - game_state.scroll[0], game_state.player.rect.y - game_state.scroll[1])
                if game_state.player.death_effect_active and int((current_time - game_state.player.death_effect_start_time) / 0.1) % 2 == 0:
                    tinted_image = game_state.player.image.copy()
                    tinted_image.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(tinted_image, player_pos)
                # Flash if invincible, but not if already handling death effect tint
                elif not game_state.player.death_effect_active and game_state.player.invincible and int(current_time * PLAYER_INVINCIBILITY_FLASH_FREQUENCY) % 2 == 1:
                    # Don't blit if invincible and it's a "flash off" frame
                    pass
                else:
                    screen.blit(game_state.player.image, player_pos)

                for bullet in game_state.bullets:
                    screen.blit(bullet.rotated_image, (bullet.rect.x - game_state.scroll[0], bullet.rect.y - game_state.scroll[1]))
                if game_state.garlic_shot and game_state.garlic_shot["active"]:
                    rotated_garlic = pygame.transform.rotate(garlic_image, game_state.garlic_shot["rotation_angle"])
                    rotated_rect = rotated_garlic.get_rect(center=(game_state.garlic_shot["x"], game_state.garlic_shot["y"]))
                    screen.blit(rotated_garlic, (rotated_rect.x - game_state.scroll[0], rotated_rect.y - game_state.scroll[1]))
                for explosion in game_state.explosions:
                    if explosion.active: explosion.draw(screen, game_state.scroll)
                game_state.vampire.draw(screen, game_state.scroll, current_time)
                game_state.player.draw_ui(screen, hp_image, garlic_image, MAX_GARLIC)

                if game_state.player.health_changed or game_state.player.garlic_changed or game_state.player.juice_changed:
                    print(f"[DEBUG] Player Stats - HP: {game_state.player.health}, Garlic: {game_state.player.garlic_count}, Carrot Juice: {game_state.player.carrot_juice_count}, Vampires Killed: {game_state.vampire_killed_count}")
                    game_state.player.health_changed = False
                    game_state.player.garlic_changed = False
                    game_state.player.juice_changed = False

                for item in game_state.items:
                    if item.active: screen.blit(item.image, (item.rect.x - game_state.scroll[0], item.rect.y - game_state.scroll[1]))
            except Exception as e:
                print(f"ERROR during game logic/draw: {e}")
                running = False

            # print(f"[TRACE] After inner try-except. HP: {game_state.player.health}, game_over: {game_state.game_over}, death_effect: {game_state.player.death_effect_active}")

            if game_state.player.health <= 0 and not game_state.game_over:
                handle_player_death()

            if game_state.player.death_effect_active:
                time_elapsed = current_time - game_state.player.death_effect_start_time
                if time_elapsed >= config.PLAYER_DEATH_DURATION:
                    # print(f"[TRACE] PLAYER_DEATH_DURATION ({config.PLAYER_DEATH_DURATION}s) reached. Setting game_over = True.")
                    game_state.game_over = True
                    game_state.player.death_effect_active = False

        else:
            screen.fill((0, 0, 0))
            game_over_x = (screen_width - game_over_rect.width) / 2
            game_over_y = (screen_height - game_over_rect.height) / 2
            screen.blit(game_over_image, (game_over_x, game_over_y))
            for button in game_over_buttons:
                button.draw(screen)

            if not pygame.mixer.music.get_busy():
                music_path = asset_manager._get_path(config.MUSIC_GAMEOVER)
                if music_path:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play(-1)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        crosshair_img = asset_manager.images['crosshair']
        crosshair_rect = crosshair_img.get_rect(center=(mouse_x, mouse_y))
        screen.blit(crosshair_img, crosshair_rect)
    
        pygame.display.flip()
    time.sleep(config.FRAME_DELAY)

if __name__ == '__main__':
    try:
        main_loop()
    finally:
        pygame.quit()
        # sys.exit() is not strictly necessary here as the program will exit
        # after the main block finishes. Pygame.quit() is the important cleanup.
        # If sys.exit() is desired, it should ideally be outside the finally
        # if main_loop() could raise SystemExit itself, or if we want to ensure
        # a specific exit code only after pygame.quit().
        # For simplicity and common practice, pygame.quit() is often the last call.
        # The original redundant sys.exit() is removed.
