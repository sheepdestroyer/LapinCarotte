#!/usr/bin/env python3
import os
import pygame
import time
import sys
import random
import math
import config
from asset_manager import AssetManager
from game_entities import Player, Bullet, Carrot, Vampire, Explosion, Collectible
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

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

carrot_rect = asset_manager.images['carrot'].get_rect()
vampire_rect = asset_manager.images['vampire'].get_rect()
hp_rect = asset_manager.images['hp'].get_rect()
game_over_rect = asset_manager.images['game_over'].get_rect()
restart_button_rect = asset_manager.images['restart'].get_rect()
exit_button_rect = asset_manager.images['exit'].get_rect()
start_button_rect = asset_manager.images['start'].get_rect()

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
        pygame.mixer.music.stop()
        asset_manager.sounds['death'].play()

def reset_game():
    game_state.reset()
    pygame.mixer.music.stop()
    pygame.mixer.music.load(asset_manager._get_path(config.MUSIC_GAME))
    pygame.mixer.music.play(-1)

def start_game():
    game_state.started = True
    pygame.mixer.music.stop()
    pygame.mixer.music.load(asset_manager._get_path(config.MUSIC_GAME))
    pygame.mixer.music.play(-1)

running = True
while running:
    current_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not game_state.started:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (start_screen_pos[0] + 787 <= mouse_x <= start_screen_pos[0] + 787 + start_button_rect.width and
                    start_screen_pos[1] + 742 <= mouse_y <= start_screen_pos[1] + 742 + start_button_rect.height):
                    asset_manager.sounds['press_start'].play()
                    start_game()
                elif (start_screen_pos[0] + 787 <= mouse_x <= start_screen_pos[0] + 787 + exit_button_rect.width and
                      start_screen_pos[1] + 827 <= mouse_y <= start_screen_pos[1] + 827 + exit_button_rect.height):
                    running = False
        elif not game_state.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_state.player.death_effect_active:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    game_state.bullets.append(Bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                                     mouse_x - game_state.player.rect.centerx + game_state.scroll[0],
                                                     mouse_y - game_state.player.rect.centery + game_state.scroll[1],
                                                     asset_manager.images['bullet']))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_state.player.death_effect_active:
                    mouse_pos = pygame.mouse.get_pos()
                    world_mouse = (mouse_pos[0] + game_state.scroll[0], mouse_pos[1] + game_state.scroll[1])
                    game_state.bullets.append(Bullet(game_state.player.rect.centerx, game_state.player.rect.centery,
                                                     world_mouse[0], world_mouse[1], asset_manager.images['bullet']))
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
             if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    restart_btn_x = screen_width / 2 - restart_button_rect.width - 20
                    restart_btn_y = screen_height * 3 / 4 - restart_button_rect.height / 2
                    exit_btn_x = screen_width / 2 + 20
                    exit_btn_y = screen_height * 3 / 4 - exit_button_rect.height / 2
                    if (restart_btn_x <= mouse_x <= restart_btn_x + restart_button_rect.width and
                        restart_btn_y <= mouse_y <= restart_btn_y + restart_button_rect.height):
                        asset_manager.sounds['press_start'].play()
                        reset_game()
                    elif (exit_btn_x <= mouse_x <= exit_btn_x + exit_button_rect.width and
                          exit_btn_y <= mouse_y <= exit_btn_y + exit_button_rect.height):
                        running = False

    if not game_state.started:
        screen.blit(start_screen_image, start_screen_pos)
        screen.blit(asset_manager.images['start'], (start_screen_pos[0] + 787, start_screen_pos[1] + 742))
        screen.blit(asset_manager.images['exit'], (start_screen_pos[0] + 787, start_screen_pos[1] + 827))
    elif not game_state.game_over:
        try:
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
                else:
                    pass

                screen.blit(grass_background, (-game_state.scroll[0], -game_state.scroll[1]))
                for carrot in game_state.carrots:
                    if carrot.active: screen.blit(carrot.image, (carrot.rect.x - game_state.scroll[0], carrot.rect.y - game_state.scroll[1]))

                if game_state.player.death_effect_active:
                    time_since_death = current_time - game_state.player.death_effect_start_time
                    if int(time_since_death / 0.1) % 2 == 0:
                        tinted_image = game_state.player.image.copy()
                        tinted_image.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
                        screen.blit(tinted_image, (game_state.player.rect.x - game_state.scroll[0], game_state.player.rect.y - game_state.scroll[1]))
                    else:
                        screen.blit(game_state.player.image, (game_state.player.rect.x - game_state.scroll[0], game_state.player.rect.y - game_state.scroll[1]))
                else:
                    screen.blit(game_state.player.image, (game_state.player.rect.x - game_state.scroll[0], game_state.player.rect.y - game_state.scroll[1]))

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
                    game_state.player.health_changed = False; game_state.player.garlic_changed = False; game_state.player.juice_changed = False

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
        finally:
            # print(f"[TRACE] Exiting 'elif not game_state.game_over' block (finally). HP: {game_state.player.health}, game_over: {game_state.game_over}, death_effect: {game_state.player.death_effect_active}")
            pass

    else:
        screen.fill((0, 0, 0))
        game_over_x = (screen_width - game_over_rect.width) / 2
        game_over_y = (screen_height - game_over_rect.height) / 2
        screen.blit(game_over_image, (game_over_x, game_over_y))
        restart_btn_x = screen_width / 2 - restart_button_rect.width - 20
        restart_btn_y = screen_height * 3 / 4 - restart_button_rect.height / 2
        screen.blit(restart_button_image, (restart_btn_x, restart_btn_y))
        exit_btn_x = screen_width / 2 + 20
        exit_btn_y = screen_height * 3 / 4 - exit_button_rect.height / 2
        screen.blit(exit_button_image, (exit_btn_x, exit_btn_y))

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

pygame.quit()
sys.exit()
```

Les lignes `print(f"[TRACE] After inner try-except...")` et `print(f"[TRACE] Exiting 'elif not game_state.game_over' block (finally)...")` ont été commentées. Les autres logs `[TRACE]` plus spécifiques à l'intérieur de `handle_player_death` ou de la condition `PLAYER_DEATH_DURATION` sont conservés (mais commentés) pour un débogage futur si nécessaire.

J'ai également réactivé les sons dans `handle_player_death` car l'étape suivante du plan est de les tester. Si cela réintroduit le bug, nous saurons que les sons sont le problème. Sinon, ils devraient fonctionner maintenant que la logique de jeu principale est suspendue pendant l'animation de mort.
Correction : je vais laisser les sons commentés pour cette étape de nettoyage de logs, et les réactiver à l'étape suivante explicitement.

```python
