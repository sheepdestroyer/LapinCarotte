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
from config import (
    MAX_HEALTH, MAX_GARLIC, ITEM_SCALE, CARROT_COUNT,
    WORLD_SIZE, CARROT_RESPAWN_DELAY
)

def get_asset_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Initialize Pygame
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Create maximized window immediately
#screen = pygame.display.set_mode((0, 0), pygame.WINDOWMAXIMIZED)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
screen_width, screen_height = screen.get_size()

# Initialize game systems
asset_manager = AssetManager()
asset_manager.load_assets()
game_state = GameState(asset_manager)

# Calculate centered position for start screen
start_screen_image = asset_manager.images['start_screen']
start_screen_pos = (
    (screen_width - start_screen_image.get_width()) // 2,
    (screen_height - start_screen_image.get_height()) // 2
)
pygame.display.set_caption("LapinCarotte")

# Initialize game state and variables
game_state = GameState(asset_manager)

# Play intro music
asset_manager.sounds['intro'].play(-1)

# Function to calculate distance between objects
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Get the image sizes for boundary detection
carrot_rect = asset_manager.images['carrot'].get_rect()
carrot_width = carrot_rect.width
carrot_height = carrot_rect.height

# Get the rabbit size for boundary detection and calculations
rabbit_rect = asset_manager.images['rabbit'].get_rect()
rabbit_width = rabbit_rect.width
rabbit_height = rabbit_rect.height

# Get the bullet size for calculations
bullet_rect = asset_manager.images['bullet'].get_rect()
bullet_width = bullet_rect.width
bullet_height = bullet_rect.height

# Get the explosion size
explosion_rect = asset_manager.images['explosion'].get_rect()
explosion_width = explosion_rect.width
explosion_height = explosion_rect.height

# Get the vampire size for boundary detection and calculations
vampire_rect = asset_manager.images['vampire'].get_rect()
vampire_width = vampire_rect.width
vampire_height = vampire_rect.height

# Get the HP image size
hp_rect = asset_manager.images['hp'].get_rect()
hp_width = hp_rect.width
hp_height = hp_rect.height

# Get the Garlic image size
garlic_rect = asset_manager.images['garlic'].get_rect()
garlic_width = garlic_rect.width
garlic_height = garlic_rect.height

# Get the GameOver image size
game_over_rect = asset_manager.images['game_over'].get_rect()
game_over_width = game_over_rect.width
game_over_height = game_over_rect.height

# Get the button image sizes
restart_button_rect = asset_manager.images['restart'].get_rect()
restart_button_width = restart_button_rect.width
restart_button_height = restart_button_rect.height
exit_button_rect = asset_manager.images['exit'].get_rect()
exit_button_width = exit_button_rect.width
exit_button_height = exit_button_rect.height
start_button_rect = asset_manager.images['start'].get_rect()
start_button_width = start_button_rect.width
start_button_height = start_button_rect.height

# Flag to track if the rabbit is flipped
rabbit_flipped = False  # Initial value set to false
# Variable to store the last direction (up, down, left, right)
last_direction = "right"

# Item management (HP drops)
item_scale = 0.5
item_width = int(hp_width * item_scale)  # 50% smaller
item_height = int(hp_height * item_scale)  # 50% smaller
hp_items = []  # List to store the dropped HP items
garlic_items = []  # List to store the dropped Garlic items

# Initialize vampire
game_state.vampire = Vampire(
    random.randint(0, config.WORLD_SIZE[0] - vampire_width),
    random.randint(0, config.WORLD_SIZE[1] - vampire_height),
    asset_manager.images['vampire']
)

# Initialize carrots
for _ in range(CARROT_COUNT):
    game_state.create_carrot(asset_manager)

# Get commonly used images
grass_image = asset_manager.images['grass']
garlic_image = asset_manager.images['garlic']
hp_image = asset_manager.images['hp']
game_over_image = asset_manager.images['game_over']
restart_button_image = asset_manager.images['restart']
exit_button_image = asset_manager.images['exit']

# Function to reset the game state
def reset_game():
    # Reset game state
    game_state.player.reset()
    game_state.scroll = [0, 0]

    # Reset vampire properly
    game_state.vampire.respawn(
        random.randint(0, game_state.world_size[0] - vampire_width),
        random.randint(0, game_state.world_size[1] - vampire_height)
    )

    # Reset bullets
    bullets = []

    # Reset game state
    game_state.game_over = False
    pygame.mixer.music.stop()
    pygame.mixer.music.load(asset_manager._get_path('Pixel_Power.mp3'))
    pygame.mixer.music.play(-1)
    
    # Clear all items
    game_state.items.clear()
    
    # Recreate carrots
    game_state.carrots.clear()
    for _ in range(CARROT_COUNT):
        game_state.create_carrot(asset_manager)


# Function to start the game
def start_game():
    game_state.started = True
    pygame.mixer.music.load(asset_manager._get_path('Pixel_Power.mp3'))
    pygame.mixer.music.play(-1)  # -1 makes the music loop continuously

# Game loop
running = True
while running:
    current_time = time.time()  # Time for checking collision and duration of explosion

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_state.started:
            # Check for start screen button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Start button
                if (787 <= mouse_x - start_screen_pos[0] <= 787 + start_button_width and 
                    742 <= mouse_y - start_screen_pos[1] <= 742 + start_button_height):
                    asset_manager.sounds['intro'].stop()
                    asset_manager.sounds['press_start'].play()
                    start_game()
                # Exit button
                elif (787 <= mouse_x - start_screen_pos[0] <= 787 + exit_button_width and 
                      827 <= mouse_y - start_screen_pos[1] <= 827 + exit_button_height):
                    running = False
        elif not game_state.game_over:
            # Handle shooting with space bar or left mouse button
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Create new bullet at rabbit's center
                    bullet_x = game_state.player.rect.centerx
                    bullet_y = game_state.player.rect.centery
                    # Store the bullet position and direction for that shot
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    bullet_dx = mouse_x - game_state.player.rect.centerx + game_state.scroll[0]
                    bullet_dy = mouse_y - game_state.player.rect.centery + game_state.scroll[1]
                    game_state.bullets.append(Bullet(bullet_x, bullet_y, bullet_dx, bullet_dy, asset_manager.images['bullet']))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    world_mouse = (
                        mouse_pos[0] + game_state.scroll[0],
                        mouse_pos[1] + game_state.scroll[1]
                    )
                    game_state.bullets.append(
                        Bullet(
                            game_state.player.rect.centerx,
                            game_state.player.rect.centery,
                            world_mouse[0],
                            world_mouse[1],
                            asset_manager.images['bullet']
                        )
                    )

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and game_state.player.garlic_count > 0 and game_state.garlic_shot is None:
                    game_state.player.garlic_count -= 1
                    game_state.garlic_shot_start_time = current_time
                    game_state.garlic_shot_travel = 0

                    # Get world coordinates of mouse at time of firing
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_mouse_x = mouse_x + game_state.scroll[0]
                    world_mouse_y = mouse_y + game_state.scroll[1]

                    # Calculate direction vector once at firing
                    start_x = game_state.player.rect.centerx
                    start_y = game_state.player.rect.centery
                    dx = world_mouse_x - start_x
                    dy = world_mouse_y - start_y
                    dist = math.hypot(dx, dy)
                    
                    if dist > 0:
                        dx_normalized = dx/dist
                        dy_normalized = dy/dist
                    else:
                        dx_normalized = 0
                        dy_normalized = 0

                    # Calculate initial rotation angle
                    angle = math.degrees(math.atan2(-dy, dx))

                    game_state.garlic_shot = {
                        "x": start_x,
                        "y": start_y,
                        "dx": dx_normalized,
                        "dy": dy_normalized,
                        "angle": angle,
                        "active": True,
                        "rotation_angle": 0  # Add dedicated rotation property
                    }


        else: # Game is over, check for button clicks
          # Calculate button positions
          restart_button_x = screen_width / 2 - restart_button_width - 20
          restart_button_y = screen_height * 3 / 4 - restart_button_height / 2
          exit_button_x = screen_width / 2 + 20
          exit_button_y = screen_height * 3 / 4 - exit_button_height / 2
          
          mouse_x, mouse_y = pygame.mouse.get_pos()
          if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
            # Check if restart button is clicked
              if (restart_button_x <= mouse_x <= restart_button_x + restart_button_width and \
                   restart_button_y <= mouse_y <= restart_button_y + restart_button_height):
                  asset_manager.sounds['press_start'].play()  # Play the sound effect
                  reset_game()

              # Check if exit button is clicked
              elif (exit_button_x <= mouse_x <= exit_button_x + exit_button_width and \
                   exit_button_y <= mouse_y <= exit_button_y + exit_button_height):
                  running = False

    if not game_state.started:
        screen.blit(start_screen_image, start_screen_pos)
        # Draw buttons relative to centered image position
        screen.blit(asset_manager.images['start'], (start_screen_pos[0] + 787, start_screen_pos[1] + 742))
        screen.blit(asset_manager.images['exit'], (start_screen_pos[0] + 787, start_screen_pos[1] + 827))
    elif not game_state.game_over:
        # Handle keyboard input for player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_q]: dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_z]: dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
        game_state.player.move(dx, dy, game_state.world_size)
            
        # Scrolling logic
        if game_state.player.rect.x < game_state.scroll[0] + screen_width * game_state.scroll_trigger:
            game_state.scroll[0] = max(0, game_state.player.rect.x - screen_width * game_state.scroll_trigger)
        elif game_state.player.rect.x + game_state.player.rect.width > game_state.scroll[0] + screen_width * (1 - game_state.scroll_trigger):
            game_state.scroll[0] = min(game_state.world_size[0] - screen_width,
                                     game_state.player.rect.x - screen_width*(1-game_state.scroll_trigger) + game_state.player.rect.width)

        if game_state.player.rect.y < game_state.scroll[1] + screen_height * game_state.scroll_trigger:
            game_state.scroll[1] = max(0, game_state.player.rect.y - screen_height * game_state.scroll_trigger)
        elif game_state.player.rect.y + game_state.player.rect.height > game_state.scroll[1] + screen_height * (1 - game_state.scroll_trigger):
            game_state.scroll[1] = min(game_state.world_size[1] - screen_height,
                                     game_state.player.rect.y - screen_height*(1-game_state.scroll_trigger) + game_state.player.rect.height)

        # Update carrot logic
        for carrot in game_state.carrots:
            if carrot.active:
                # Calculate direction using vector
                rabbit_center = pygame.math.Vector2(game_state.player.rect.center)
                carrot_center = pygame.math.Vector2(carrot.rect.center)
                direction = carrot_center - rabbit_center
                dist = direction.length()
                
                # Calculate speed multiplier
                max_distance = config.CARROT_DETECTION_RADIUS
                speed_multiplier = min(max(1, 1 + (max_distance - dist)/max_distance * 
                                    (config.MAX_SPEED_MULTIPLIER - 1)), 
                                    config.MAX_SPEED_MULTIPLIER)
                
                # Update movement vector
                if dist < 100:
                    if dist > 0:
                        direction.normalize_ip()
                        carrot.direction = direction
                else:
                    # Add random wander
                    carrot.direction += pygame.math.Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))
                    carrot.direction.normalize_ip()
                
                # Apply movement
                movement = carrot.direction * carrot.speed * speed_multiplier
                carrot.rect.x += movement.x
                carrot.rect.y += movement.y
                
                # Keep within world bounds
                carrot.rect.x = max(0, min(game_state.world_size[0] - carrot.rect.width, carrot.rect.x))
                carrot.rect.y = max(0, min(game_state.world_size[1] - carrot.rect.height, carrot.rect.y))

        # Update bullets and handle collisions
        for bullet in game_state.bullets[:]:
            bullet.update()
            
            # Remove off-screen bullets
            if (bullet.rect.right < 0 or bullet.rect.left > game_state.world_size[0] or
                bullet.rect.bottom < 0 or bullet.rect.top > game_state.world_size[1]):
                game_state.bullets.remove(bullet)
                continue
            
            # Check collisions with carrots
            for carrot in game_state.carrots:
                if carrot.active and bullet.rect.colliderect(carrot.rect):
                    game_state.explosions.append(Explosion(
                        carrot.rect.centerx,
                        carrot.rect.centery,
                        asset_manager.images['explosion']
                    ))
                    carrot.active = False
                    carrot.respawn_timer = current_time
                    asset_manager.sounds['explosion'].play()
                    game_state.bullets.remove(bullet)
                    break

        # Respawn carrots after delay
        for carrot in game_state.carrots:
            if not carrot.active and current_time - carrot.respawn_timer > CARROT_RESPAWN_DELAY:
                carrot.respawn_timer = 0  # Reset timer
                carrot.respawn(game_state.world_size, game_state.player.rect)
        
        # Garlic shot logic
        if game_state.garlic_shot and game_state.garlic_shot["active"]:
            if game_state.garlic_shot_travel < config.GARLIC_SHOT_MAX_TRAVEL:
                # Update rotation angle each frame
                game_state.garlic_shot["rotation_angle"] = (game_state.garlic_shot["rotation_angle"] + config.GARLIC_ROTATION_SPEED) % 360
                # Move in the pre-calculated direction
                game_state.garlic_shot["x"] += game_state.garlic_shot["dx"] * game_state.garlic_shot_speed
                game_state.garlic_shot["y"] += game_state.garlic_shot["dy"] * game_state.garlic_shot_speed
                game_state.garlic_shot_travel += game_state.garlic_shot_speed
            else:
                if current_time - game_state.garlic_shot_start_time > game_state.garlic_shot_duration:
                    game_state.garlic_shot["active"] = False
                    game_state.garlic_shot = None

            # Check for collision with vampire
            if game_state.garlic_shot and game_state.vampire.active:
                garlic_rect = pygame.Rect(game_state.garlic_shot["x"], game_state.garlic_shot["y"], garlic_width, garlic_height)
                if garlic_rect.colliderect(game_state.vampire.rect):
                    game_state.vampire.death_effect_active = True
                    game_state.vampire.death_effect_start_time = current_time
                    game_state.vampire.active = False
                    game_state.vampire.respawn_timer = current_time
                    asset_manager.sounds['vampire_death'].play()
                    game_state.garlic_shot = None
        # Update vampire
        game_state.vampire.update(game_state.player, game_state.world_size, current_time)

        # Check collision with player
        if game_state.vampire.active and game_state.player.rect.colliderect(game_state.vampire.rect):
            game_state.player.health -= 1
            asset_manager.sounds['hurt'].play()
            game_state.vampire.active = False
            game_state.vampire.respawn_timer = current_time
            
            if game_state.player.health <= 0:
                game_state.game_over = True
                asset_manager.sounds['background_music'].stop()
                asset_manager.sounds['death'].play()           
        
        # Check item collisions
        for item in game_state.items[:]:
            if game_state.player.rect.colliderect(item.rect):
                if item.item_type == 'hp' and game_state.player.health < MAX_HEALTH:
                    game_state.player.health += 1
                    asset_manager.sounds['get_hp'].play()
                elif item.item_type == 'garlic' and game_state.player.garlic_count < MAX_GARLIC:
                    game_state.player.garlic_count += 1
                    asset_manager.sounds['get_garlic'].play()
                game_state.items.remove(item)


        # Screen tiling code (fill the entire world_width x world_height area)
        grass_width = grass_image.get_width()
        grass_height = grass_image.get_height()
        for x in range(0, game_state.world_size[0], grass_width):
            for y in range(0, game_state.world_size[1], grass_height):
                screen.blit(grass_image, (x - game_state.scroll[0], y - game_state.scroll[1]))

        # Draw the carrots
        for carrot in game_state.carrots:
            if carrot.active:
                screen.blit(carrot.image, (carrot.rect.x - game_state.scroll[0], carrot.rect.y - game_state.scroll[1]))

        # Draw the rabbit using blit
        screen.blit(game_state.player.image, (game_state.player.rect.x - game_state.scroll[0], game_state.player.rect.y - game_state.scroll[1]))

        # Draw bullets
        for bullet in game_state.bullets:
            screen.blit(
                bullet.rotated_image,
                (bullet.rect.x - game_state.scroll[0],
                 bullet.rect.y - game_state.scroll[1])
            )

        # Draw the garlic shot
        if game_state.garlic_shot and game_state.garlic_shot["active"]:
            # Use rotation_angle instead of fixed angle
            rotated_garlic = pygame.transform.rotate(garlic_image, game_state.garlic_shot["rotation_angle"])
            rotated_rect = rotated_garlic.get_rect(center=(game_state.garlic_shot["x"], game_state.garlic_shot["y"]))
            screen.blit(rotated_garlic, (rotated_rect.x - game_state.scroll[0], 
                                       rotated_rect.y - game_state.scroll[1]))

        # Update and draw explosions
        for explosion in game_state.explosions[:]:
            if explosion.update(current_time):
                # Create collectible item
                is_garlic = random.choice([True, False])
                item_image = asset_manager.images['garlic'] if is_garlic else asset_manager.images['hp']
                game_state.items.append(
                    Collectible(
                        explosion.rect.centerx,
                        explosion.rect.centery,
                        item_image,
                        'garlic' if is_garlic else 'hp',
                        ITEM_SCALE
                    )
                )
                game_state.explosions.remove(explosion)
            explosion.draw(screen, game_state.scroll)
        
        # Draw vampire
        game_state.vampire.draw(screen, game_state.scroll, current_time)

        # Draw health points UI
        for i in range(game_state.player.health):
            screen.blit(hp_image, (10 + i * (hp_width + 5), 10))  # 5 pixels spacing
        

        # Draw Garlic count UI
        if game_state.player.garlic_count > 0:  # Only display if player has garlic
            garlic_ui_x = screen_width - 10 - MAX_GARLIC * (garlic_width + 5)
            for i in range(game_state.player.garlic_count):
                screen.blit(garlic_image, (garlic_ui_x + i * (garlic_width + 5), 10))  # 5 pixels spacing

        # Draw all collectible items
        for item in game_state.items:
            if item.active:
                screen.blit(item.image, 
                           (item.rect.x - game_state.scroll[0],
                            item.rect.y - game_state.scroll[1]))

    else: # Game is over, display the game over screen
      # Fill the screen with black (or your background color)
      screen.fill((0, 0, 0))
      # Draw the game over image
      game_over_x = (screen_width - game_over_width) / 2
      game_over_y = (screen_height - game_over_height) / 2
      screen.blit(game_over_image, (game_over_x, game_over_y))

      # Draw the restart button
      restart_button_x = screen_width / 2 - restart_button_width - 20  # 20 pixels spacing
      restart_button_y = screen_height * 3 / 4 - restart_button_height / 2
      screen.blit(restart_button_image, (restart_button_x, restart_button_y))

      # Draw the exit button next to the restart button
      exit_button_x = screen_width / 2 + 20  # 20 pixels spacing
      exit_button_y = screen_height * 3 / 4 - exit_button_height / 2
      screen.blit(exit_button_image, (exit_button_x, exit_button_y))

      if not pygame.mixer.music.get_busy():
          pygame.mixer.music.load(asset_manager._get_path('gameover.mp3'))
          pygame.mixer.music.play(-1)

    # Update the display
    pygame.display.flip()
    time.sleep(config.FRAME_DELAY)

pygame.quit()
sys.exit()
