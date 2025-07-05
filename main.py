#!/usr/bin/env python3
import os
import argparse # Import argparse
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

# Argument parsing
parser = argparse.ArgumentParser(description="LapinCarotte - A game about a rabbit fighting vampire carrots.")
parser.add_argument("--cli", action="store_true", help="Run the game in Command Line Interface mode (no graphics).")
args = parser.parse_args()

# Initialize screen and dimensions
screen = None
screen_width, screen_height = 0, 0

if not args.cli:
    pygame.init() # Initialize all pygame modules needed for GUI mode
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    screen_width, screen_height = screen.get_size()
    pygame.mouse.set_visible(False)
else:
    print("Running in CLI mode.")

asset_manager = AssetManager(cli_mode=args.cli)
asset_manager.load_assets()

if not args.cli and screen:
    pygame.display.set_icon(asset_manager.images['icon'])

if sys.platform == 'win32' and not args.cli:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('LapinCarotte.1.0')
    pygame.display.set_caption("LapinCarotte", "LapinCarotte")

game_state = GameState(asset_manager, cli_mode=args.cli)

# Graphics-dependent initializations (defaults for CLI)
start_screen_image = None
start_screen_pos = (0,0)
# Rects for button positioning, initialized to default for CLI
restart_button_rect = pygame.Rect(0,0,0,0)
exit_button_rect = pygame.Rect(0,0,0,0)
start_button_rect = pygame.Rect(0,0,0,0)
continue_button_rect = pygame.Rect(0,0,0,0)
settings_button_rect = pygame.Rect(0,0,0,0)
# Other image rects, initialized to default for CLI
carrot_rect = pygame.Rect(0,0,0,0)
vampire_rect = pygame.Rect(0,0,0,0)
hp_rect = pygame.Rect(0,0,0,0)
game_over_rect = pygame.Rect(0,0,0,0)
# Image surfaces for UI drawing in GUI, initialized to None for CLI
grass_image = None
garlic_image = None # Note: garlic_image is used in main_loop GUI path
hp_image_ui = None
game_over_image_ui = None
# Button image surfaces (these will be dicts in CLI mode, actual surfaces in GUI)
# Their direct use as surfaces is only in GUI mode.
start_button_img = asset_manager.images['start']
exit_button_img = asset_manager.images['exit']
restart_button_img = asset_manager.images['restart']
continue_button_img = asset_manager.images['continue_button']
settings_button_img = asset_manager.images['settings_button']
grass_background = None


if not args.cli:
    start_screen_image = asset_manager.images['start_screen']
    if hasattr(start_screen_image, 'get_width') and hasattr(start_screen_image, 'get_height'):
        start_screen_pos = (
            (screen_width - start_screen_image.get_width()) // 2,
            (screen_height - start_screen_image.get_height()) // 2
        )

    if hasattr(asset_manager.images['restart'], 'get_rect'):
        restart_button_rect = asset_manager.images['restart'].get_rect()
    if hasattr(asset_manager.images['exit'], 'get_rect'):
        exit_button_rect = asset_manager.images['exit'].get_rect()
    if hasattr(asset_manager.images['start'], 'get_rect'):
        start_button_rect = asset_manager.images['start'].get_rect()
    if hasattr(asset_manager.images['continue_button'], 'get_rect'):
        continue_button_rect = asset_manager.images['continue_button'].get_rect()
    if hasattr(asset_manager.images['settings_button'], 'get_rect'):
        settings_button_rect = asset_manager.images['settings_button'].get_rect()
    if hasattr(asset_manager.images['carrot'], 'get_rect'):
        carrot_rect = asset_manager.images['carrot'].get_rect()
    if hasattr(asset_manager.images['vampire'], 'get_rect'):
        vampire_rect = asset_manager.images['vampire'].get_rect()
    if hasattr(asset_manager.images['hp'], 'get_rect'):
        hp_rect = asset_manager.images['hp'].get_rect()
    if hasattr(asset_manager.images['game_over'], 'get_rect'):
        game_over_rect = asset_manager.images['game_over'].get_rect()

    grass_image = asset_manager.images['grass']
    if grass_image and hasattr(grass_image, 'get_size'): # Check if it's a surface
        grass_background = pygame.Surface(WORLD_SIZE, pygame.SRCALPHA)
        _grass_w, _grass_h = grass_image.get_size()
        for x_g in range(0, WORLD_SIZE[0], _grass_w):
            for y_g in range(0, WORLD_SIZE[1], _grass_h):
                grass_background.blit(grass_image, (x_g, y_g))

    garlic_image = asset_manager.images['garlic']
    hp_image_ui = asset_manager.images['hp']
    game_over_image_ui = asset_manager.images['game_over'] # Used for actual game over image

    pygame.mixer.music.load(asset_manager._get_path(config.MUSIC_INTRO))
    pygame.mixer.music.play(-1)

current_time = 0.0

def _play_game_music_and_sound(sound_to_play=None):
    if args.cli: return # No sound in CLI
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
    if not args.cli: _play_game_music_and_sound('press_start')
    else: print("Game started (CLI).")


def reset_game():
    game_state.reset()
    if not args.cli: _play_game_music_and_sound('press_start')
    else: print("Game reset (CLI).")


def quit_game():
    global running
    running = False
    if args.cli: print("Exiting game.")

def resume_game_callback():
    if game_state.paused:
        game_state.resume_game()
        if args.cli: print("Game resumed (CLI).")

def open_settings_callback():
    print("Settings button clicked - Not implemented yet.")

start_button_start_screen = Button(
    start_screen_pos[0] + START_SCREEN_BUTTON_START_X_OFFSET,
    start_screen_pos[1] + START_SCREEN_BUTTON_START_Y_OFFSET,
    start_button_img, # This is asset_manager.images['start']
    start_game,
    cli_mode=args.cli
)
exit_button_start_screen = Button(
    start_screen_pos[0] + START_SCREEN_BUTTON_EXIT_X_OFFSET,
    start_screen_pos[1] + START_SCREEN_BUTTON_EXIT_Y_OFFSET,
    exit_button_img, # asset_manager.images['exit']
    quit_game,
    cli_mode=args.cli
)
start_screen_buttons = [start_button_start_screen, exit_button_start_screen]

restart_button_game_over_screen = Button(
    screen_width / 2 - restart_button_rect.width - BUTTON_SPACING / 2,
    screen_height * 3 / 4 - restart_button_rect.height / 2,
    restart_button_img, # asset_manager.images['restart']
    reset_game,
    cli_mode=args.cli
)
exit_button_game_over_screen = Button(
    screen_width / 2 + BUTTON_SPACING / 2,
    screen_height * 3 / 4 - exit_button_rect.height / 2,
    exit_button_img, # asset_manager.images['exit']
    quit_game,
    cli_mode=args.cli
)
game_over_buttons = [restart_button_game_over_screen, exit_button_game_over_screen]

continue_button_pause_screen = Button(
    screen_width / 2 - continue_button_rect.width / 2,
    screen_height * 0.5 - continue_button_rect.height - BUTTON_SPACING / 2,
    continue_button_img, # asset_manager.images['continue_button']
    resume_game_callback,
    cli_mode=args.cli
)
settings_button_pause_screen = Button(
    screen_width / 2 - settings_button_rect.width / 2,
    screen_height * 0.5 + BUTTON_SPACING / 2,
    settings_button_img, # asset_manager.images['settings_button']
    open_settings_callback,
    cli_mode=args.cli
)
pause_screen_buttons = [continue_button_pause_screen, settings_button_pause_screen]

def handle_player_death():
    global current_time
    if not game_state.game_over and not game_state.player.death_effect_active:
        game_state.player.death_effect_active = True
        game_state.player.death_effect_start_time = current_time
    if not args.cli:
        try:
            pygame.mixer.music.stop()
            asset_manager.sounds['death'].play()
        except pygame.error as e:
            print(f"ERROR: Could not load or play sound: {e}")
    else:
        print("Player has died (CLI).")


running = True
can_toggle_pause = True

def main_loop():
    global running
    global current_time
    global can_toggle_pause

    while running:
        if not args.cli: #################### GUI MODE ####################
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

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
                            game_state.bullets.append(Bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                                             mouse_x - game_state.player.rect.centerx + game_state.scroll[0],
                                                             mouse_y - game_state.player.rect.centery + game_state.scroll[1],
                                                             asset_manager.images['bullet'], cli_mode=args.cli))
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1 and not game_state.player.death_effect_active:
                            mouse_pos = pygame.mouse.get_pos()
                            world_mouse = (mouse_pos[0] + game_state.scroll[0], mouse_pos[1] + game_state.scroll[1])
                            game_state.bullets.append(Bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                                             world_mouse[0], world_mouse[1], asset_manager.images['bullet'], cli_mode=args.cli))
                        if event.button == 3 and not game_state.player.death_effect_active and game_state.player.garlic_count > 0 and game_state.garlic_shot is None:
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
                else:
                    for button in game_over_buttons:
                        button.handle_event(event)

            # GUI Drawing Logic
            if not game_state.started:
                if screen and start_screen_image: screen.blit(start_screen_image, start_screen_pos)
                for button in start_screen_buttons:
                    if screen: button.draw(screen)
            elif game_state.paused:
                if screen and game_over_image_ui: # Reusing game_over_image for pause bg
                    game_over_x_pos = (screen_width - game_over_rect.width) / 2
                    game_over_y_pos = (screen_height - game_over_rect.height) / 2
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
                        game_state.player.move(dx, dy, game_state.world_size)

                if game_state.player.rect.x < game_state.scroll[0] + screen_width * game_state.scroll_trigger:
                    game_state.scroll[0] = max(0, game_state.player.rect.x - screen_width * game_state.scroll_trigger)
                elif game_state.player.rect.x + game_state.player.rect.width > game_state.scroll[0] + screen_width * (1 - game_state.scroll_trigger):
                    game_state.scroll[0] = min(game_state.world_size[0] - screen_width, game_state.player.rect.x - screen_width*(1-game_state.scroll_trigger) + game_state.player.rect.width)
                if game_state.player.rect.y < game_state.scroll[1] + screen_height * game_state.scroll_trigger:
                    game_state.scroll[1] = max(0, game_state.player.rect.y - screen_height * game_state.scroll_trigger)
                elif game_state.player.rect.y + game_state.player.rect.height > game_state.scroll[1] + screen_height * (1 - game_state.scroll_trigger):
                    game_state.scroll[1] = min(game_state.world_size[1] - screen_height, game_state.player.rect.y - screen_height*(1-game_state.scroll_trigger) + game_state.player.rect.height)

                try:
                    if not game_state.player.death_effect_active:
                        game_state.update(current_time)

                    if screen and grass_background: screen.blit(grass_background, (-game_state.scroll[0], -game_state.scroll[1]))
                    for carrot in game_state.carrots:
                        if carrot.active and screen and carrot.image: screen.blit(carrot.image, (carrot.rect.x - game_state.scroll[0], carrot.rect.y - game_state.scroll[1]))

                    player_pos = (game_state.player.rect.x - game_state.scroll[0], game_state.player.rect.y - game_state.scroll[1])
                    if game_state.player.death_effect_active and int((current_time - game_state.player.death_effect_start_time) / 0.1) % 2 == 0:
                        if screen and game_state.player.image :
                            tinted_image = game_state.player.image.copy()
                            tinted_image.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
                            screen.blit(tinted_image, player_pos)
                    elif not game_state.player.death_effect_active and game_state.player.invincible and int(current_time * PLAYER_INVINCIBILITY_FLASH_FREQUENCY) % 2 == 1:
                        pass
                    else:
                        if screen and game_state.player.image: screen.blit(game_state.player.image, player_pos)

                    for bullet in game_state.bullets:
                        if screen and bullet.image: screen.blit(bullet.rotated_image, (bullet.rect.x - game_state.scroll[0], bullet.rect.y - game_state.scroll[1]))
                    if game_state.garlic_shot and game_state.garlic_shot["active"]:
                        if screen and garlic_image:
                            rotated_garlic = pygame.transform.rotate(garlic_image, game_state.garlic_shot["rotation_angle"])
                            rotated_rect = rotated_garlic.get_rect(center=(game_state.garlic_shot["x"], game_state.garlic_shot["y"]))
                            screen.blit(rotated_garlic, (rotated_rect.x - game_state.scroll[0], rotated_rect.y - game_state.scroll[1]))
                    for explosion in game_state.explosions:
                        if screen: explosion.draw(screen, game_state.scroll) # Explosion draw handles active check
                    if screen: game_state.vampire.draw(screen, game_state.scroll, current_time)
                    if screen and hp_image_ui and garlic_image: game_state.player.draw_ui(screen, hp_image_ui, garlic_image, MAX_GARLIC)

                    if game_state.player.health_changed or game_state.player.garlic_changed or game_state.player.juice_changed:
                        print(f"[DEBUG] Player Stats - HP: {game_state.player.health}, Garlic: {game_state.player.garlic_count}, Carrot Juice: {game_state.player.carrot_juice_count}, Vampires Killed: {game_state.vampire_killed_count}")
                        game_state.player.health_changed = False
                        game_state.player.garlic_changed = False
                        game_state.player.juice_changed = False

                    for item in game_state.items:
                        if item.active and screen and item.image: screen.blit(item.image, (item.rect.x - game_state.scroll[0], item.rect.y - game_state.scroll[1]))
                except Exception as e:
                    print(f"ERROR during game logic/draw: {e}")
                    running = False

                if game_state.player.health <= 0 and not game_state.game_over:
                    handle_player_death()

                if game_state.player.death_effect_active:
                    time_elapsed = current_time - game_state.player.death_effect_start_time
                    if time_elapsed >= config.PLAYER_DEATH_DURATION:
                        game_state.game_over = True
                        game_state.player.death_effect_active = False
            else:
                if screen and game_over_image_ui:
                    game_over_x_pos = (screen_width - game_over_rect.width) / 2
                    game_over_y_pos = (screen_height - game_over_rect.height) / 2
                    screen.blit(game_over_image_ui, (game_over_x_pos, game_over_y_pos))
                for button in game_over_buttons:
                    if screen: button.draw(screen)

                if not pygame.mixer.music.get_busy():
                    music_path = asset_manager._get_path(config.MUSIC_GAMEOVER)
                    if music_path:
                        try:
                            pygame.mixer.music.load(music_path)
                            pygame.mixer.music.play(-1)
                        except pygame.error as e:
                            print(f"Error playing game over music: {e}")

            if screen: # These are GUI specific last drawing steps
                mouse_x, mouse_y = pygame.mouse.get_pos()
                crosshair_img_ref = asset_manager.images['crosshair']
                if hasattr(crosshair_img_ref, 'get_rect'):
                    crosshair_rect = crosshair_img_ref.get_rect(center=(mouse_x, mouse_y))
                    screen.blit(crosshair_img_ref, crosshair_rect)
            # These must be outside the `if screen:` for crosshair, but still inside `if not args.cli:`
            pygame.display.flip()
            time.sleep(config.FRAME_DELAY)
        else: # #################### CLI MODE ####################
            if not game_state.started:
                print("\n--- LapinCarotte ---")
                print("Start Screen (CLI Mode)")
                print("1. Start Game")
                print("2. Exit")
                choice = ""
                try: choice = input("Enter choice: ").strip()
                except EOFError: quit_game()

                if choice == '1':
                    start_game()
                elif choice == '2':
                    quit_game()
                elif running: # Avoid printing if quit_game was called by EOF
                    print("Invalid choice. Please enter 1 or 2.")
            elif game_state.paused:
                print("\n--- PAUSED (CLI Mode) ---")
                print("1. Continue")
                print("2. Settings (Not Implemented)")
                print("3. Quit Game")
                choice = ""
                try: choice = input("Enter choice: ").strip()
                except EOFError: quit_game()

                if choice == '1':
                    resume_game_callback()
                elif choice == '2':
                    open_settings_callback()
                elif choice == '3':
                    quit_game()
                elif running:
                    print("Invalid choice.")
            elif game_state.game_over:
                print("\n--- GAME OVER (CLI Mode) ---")
                print("1. Restart")
                print("2. Exit")
                choice = ""
                try: choice = input("Enter choice: ").strip()
                except EOFError: quit_game()

                if choice == '1':
                    reset_game()
                elif choice == '2':
                    quit_game()
                elif running:
                    print("Invalid choice.")
            else: # Game is active (and not paused, not game over)
                print("\n--- Game Active (CLI Mode) ---")
                print(f"Player HP: {game_state.player.health} (Note: Game logic not running in CLI yet)")
                print("Options: (p)ause, (q)uit, (d)ie (simulate death for testing)")

                cli_action = ""
                try:
                    cli_action = input("Action: ").strip().lower()
                    print(f"DEBUG: cli_action received: '{cli_action}'"); sys.stdout.flush() # DEBUG + FLUSH
                except EOFError:
                    print("EOF received, quitting."); sys.stdout.flush()
                    quit_game()

                if cli_action == 'p':
                    if can_toggle_pause: # Check flag before pausing
                        game_state.pause_game()
                        print("Game paused (CLI).") # Added feedback
                        can_toggle_pause = False
                    # Removed the 'else resume' from here as 'p' should only pause.
                    # Resume is handled by the PAUSED state menu.
                elif cli_action == 'q':
                    quit_game()
                elif cli_action == 'd': # Simulate death - CORRECTED CONDITION
                    print(f"DEBUG: ENTERING 'd' (die) block. cli_action is '{cli_action}'"); sys.stdout.flush()
                    print(f"DEBUG: game_state.game_over before setting: {game_state.game_over}"); sys.stdout.flush()
                    game_state.player.health = 0 # Ensure health is 0 for any subsequent logic
                    game_state.game_over = True
                    print(f"DEBUG: game_state.game_over after setting: {game_state.game_over}"); sys.stdout.flush()
                    print("Simulating player death for CLI testing..."); sys.stdout.flush() # Test assertion relies on this
                    # No need for "Player died. Game Over." here as the main loop will go to game_over state display

                # Logic for can_toggle_pause for CLI 'p' (pause) action:
                # If 'p' was just pressed and game is now paused, can_toggle_pause is False.
                # If any other action is taken, or if 'p' is pressed while already paused (which CLI state handles separately),
                # then can_toggle_pause should be True for the next "Game Active" input cycle.
                if cli_action != 'p' or not game_state.paused: # Reset if not pausing or if pause failed
                    can_toggle_pause = True


            if running and args.cli:
                time.sleep(0.1) # Small delay for CLI loop readability

if __name__ == '__main__':
    try:
        main_loop()
    finally:
        if not args.cli: # Only quit pygame if it was initialized
            pygame.quit()
        # sys.exit() is not strictly necessary here as the program will exit
        # after the main block finishes. Pygame.quit() is the important cleanup.
        # If sys.exit() is desired, it should ideally be outside the finally
        # if main_loop() could raise SystemExit itself, or if we want to ensure
        # a specific exit code only after pygame.quit().
        # For simplicity and common practice, pygame.quit() is often the last call.
        # The original redundant sys.exit() is removed.
