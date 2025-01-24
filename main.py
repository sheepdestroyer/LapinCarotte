#!/usr/bin/env python3
import os
import pygame
import time
import sys
import random
import math
from asset_manager import AssetManager
from game_entities import Player, Bullet, Carrot, Vampire, Explosion, Collectible
from game_state import GameState

def get_asset_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Initialize Pygame and set a minimal display mode first
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Set a minimal display mode before loading assets
pygame.display.set_mode((1, 1))

# Now initialize game systems
asset_manager = AssetManager()
asset_manager.load_assets()
game_state = GameState()

# Set a temporary display mode to get the start screen dimensions
temp_screen = pygame.display.set_mode((0, 0))  # Set a small, temporary display

# Load start screen image
try:
    start_screen_image = pygame.image.load(get_asset_path(os.path.join('Assets', 'start_screen.png'))).convert()
    screen_width, screen_height = start_screen_image.get_size()
except pygame.error as e:
    print(f"Error loading start screen image: {e}")
    sys.exit(1)

# Now, set the actual display mode using the loaded image dimensions
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("LapinCarotte")

# Game constants
max_health_points = 3
max_garlic_count = 3

# Initialize game state and player
game_state = GameState()
player = Player(200, 200, asset_manager.images['rabbit'])

# Get all the images we'll need
grass_image = asset_manager.images['grass']
carrot_image = asset_manager.images['carrot']
rabbit_image = asset_manager.images['rabbit']
original_bullet_image = asset_manager.images['bullet']
garlic_image = asset_manager.images['garlic']
explosion_image = asset_manager.images['explosion']
vampire_image = asset_manager.images['vampire']
hp_image = asset_manager.images['hp']
game_over_image = asset_manager.images['game_over']
restart_button_image = asset_manager.images['restart']
exit_button_image = asset_manager.images['exit']

# Play intro music
asset_manager.sounds['intro'].play(-1)

# Movement constants
carrot_speed = 3  # Base carrot speed
bullet_speed = 10
max_speed_multiplier = 3  # Max speed when rabbit is close

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

# Game timing constants
explosion_flash_interval = 0.1  # Time in seconds between flashes
max_explosion_flashes = 3  # Number of times the explosion will flash
#Respawn timer variables
carrot_respawn_timer = 0
carrot_respawn_delay = 3 # respawn delay in seconds

# Scrolling variables
scroll_x = 0
scroll_y = 0
scroll_trigger = 0.1  # 10% of screen width/height from edge

# Total world size (set to whatever size you want your world to be)
world_width = 3000
world_height = 3000

# Carrot management
num_carrots = 5
carrots = []

# Item management (HP drops)
item_scale = 0.5
item_width = int(hp_width * item_scale)  # 50% smaller
item_height = int(hp_height * item_scale)  # 50% smaller
hp_items = []  # List to store the dropped HP items
garlic_items = []  # List to store the dropped Garlic items



# Initialize vampire
game_state.vampire = Vampire(
    random.randint(0, world_width - vampire_width),
    random.randint(0, world_height - vampire_height),
    asset_manager.images['vampire']
)
game_state.vampire.active = True  # Force initial activation

# Garlic shooting variables
garlic_shot = None
garlic_shot_duration = 3  # seconds
garlic_shot_max_travel = 250  # pixels
garlic_shot_speed = 5
garlic_shot_start_time = 0
garlic_shot_travel = 0

# Garlic rotation variables
garlic_rotation_angle = 0
garlic_rotation_speed = 5  # Degrees per frame


# Game state
game_over = False
game_started = False

# Function to create a new carrot
def create_carrot():
    while True:
        # Create at center coordinates
        new_x = random.randint(carrot_width//2, world_width - carrot_width//2)
        new_y = random.randint(carrot_height//2, world_height - carrot_height//2)
        if distance(new_x, new_y, player.rect.centerx, player.rect.centery) > min(screen_width, screen_height)/3:
            return Carrot(new_x, new_y, asset_manager.images['carrot'])

# Initialize carrots
game_state.carrots = []
for _ in range(num_carrots):
    game_state.carrots.append(create_carrot())

# Function to respawn the vampire
def respawn_vampire():
    global vampire_x, vampire_y, vampire_active, garlic_count
    vampire_x = random.randint(0, world_width - vampire_width)
    vampire_y = random.randint(0, world_height - vampire_height)
    vampire_active = True

# Function to reset the game state
def reset_game():
    global rabbit_x, rabbit_y, health_points, bullets, carrots, game_over, hp_items, garlic_count
    # Reset rabbit position and scrolling
    player.rect.x = 200
    player.rect.y = 200
    game_state.scroll = [0, 0]

    # Reset health points
    player.health = max_health_points

    # Reset vampire properly
    game_state.vampire.respawn(
        random.randint(0, world_width - vampire_width),
        random.randint(0, world_height - vampire_height)
    )

    # Reset bullets
    bullets = []

    # Reset carrots
    carrots = []
    for _ in range(num_carrots):
        carrots.append(create_carrot())

    # Reset game over state
    game_over = False
    asset_manager.sounds['background'].play(-1)  # Restart the background music

    # Reset HP items
    hp_items = []
    
    # Reset garlic items
    garlic_items = []
    player.garlic_count = 0


# Function to start the game
def start_game():
    global game_started, screen_width, screen_height, screen
    game_started = True
    # Update screen size for gameplay
    screen_width = 1280
    screen_height = 1024
    screen = pygame.display.set_mode((screen_width, screen_height))
    asset_manager.sounds['intro'].stop()  # Stop the intro music
    asset_manager.sounds['background'].play(-1)  # -1 makes the music loop continuously

# Game loop
running = True
while running:
    current_time = time.time()  # Time for checking collision and duration of explosion

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_started:
            # Check for start screen button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Start button
                if 787 <= mouse_x <= 787 + start_button_width and 742 <= mouse_y <= 742 + start_button_height:
                    asset_manager.sounds['intro'].stop()
                    asset_manager.sounds['press_start'].play()
                    start_game()
                # Exit button
                elif 787 <= mouse_x <= 787 + exit_button_width and 827 <= mouse_y <= 827 + exit_button_height:
                    running = False
        elif not game_over:
            # Handle shooting with space bar or left mouse button
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Create new bullet at rabbit's center
                    bullet_x = player.rect.centerx
                    bullet_y = player.rect.centery
                    # Store the bullet position and direction for that shot
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    bullet_dx = mouse_x - player.rect.centerx + game_state.scroll[0]
                    bullet_dy = mouse_y - player.rect.centery + game_state.scroll[1]
                    bullets.append([bullet_x, bullet_y, bullet_dx, bullet_dy])

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    world_mouse = (
                        mouse_pos[0] + game_state.scroll[0],
                        mouse_pos[1] + game_state.scroll[1]
                    )
                    game_state.bullets.append(
                        Bullet(
                            player.rect.centerx,
                            player.rect.centery,
                            world_mouse[0],
                            world_mouse[1],
                            asset_manager.images['bullet']
                        )
                    )

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and player.garlic_count > 0 and garlic_shot is None:
                    player.garlic_count -= 1
                    garlic_shot_start_time = current_time
                    garlic_shot_travel = 0

                    # Get world coordinates of mouse at time of firing
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_mouse_x = mouse_x + game_state.scroll[0]
                    world_mouse_y = mouse_y + game_state.scroll[1]

                    # Calculate direction vector once at firing
                    start_x = player.rect.centerx
                    start_y = player.rect.centery
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

                    garlic_shot = {
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

    if not game_started:
        screen.blit(start_screen_image, (0, 0))
        # Draw start button
        screen.blit(asset_manager.images['start'], (787, 742))
        # Draw exit button
        screen.blit(asset_manager.images['exit'], (787, 827))
    elif not game_over:
        # Handle keyboard input for player movement
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_q]: dx -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 5
        if keys[pygame.K_UP] or keys[pygame.K_z]: dy -= 5
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 5
        player.move(dx, dy, game_state.world_size)
            
        # Scrolling logic
        if player.rect.x < game_state.scroll[0] + screen_width * scroll_trigger:
            game_state.scroll[0] = max(0, player.rect.x - screen_width * scroll_trigger)
        elif player.rect.x + player.rect.width > game_state.scroll[0] + screen_width * (1 - scroll_trigger):
            game_state.scroll[0] = min(game_state.world_size[0] - screen_width,
                                     player.rect.x - screen_width*(1-scroll_trigger) + player.rect.width)

        if player.rect.y < game_state.scroll[1] + screen_height * scroll_trigger:
            game_state.scroll[1] = max(0, player.rect.y - screen_height * scroll_trigger)
        elif player.rect.y + player.rect.height > game_state.scroll[1] + screen_height * (1 - scroll_trigger):
            game_state.scroll[1] = min(game_state.world_size[1] - screen_height,
                                     player.rect.y - screen_height*(1-scroll_trigger) + player.rect.height)

        # Update carrot logic
        for carrot in game_state.carrots:
            if carrot.active:
                # Calculate direction using vector
                rabbit_center = pygame.math.Vector2(player.rect.center)
                carrot_center = pygame.math.Vector2(carrot.rect.center)
                direction = carrot_center - rabbit_center
                dist = direction.length()
                
                # Calculate speed multiplier
                max_distance = 200
                speed_multiplier = min(max(1, 1 + (max_distance - dist)/max_distance * (max_speed_multiplier - 1)), max_speed_multiplier)
                
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
                carrot.rect.x = max(0, min(world_width - carrot.rect.width, carrot.rect.x))
                carrot.rect.y = max(0, min(world_height - carrot.rect.height, carrot.rect.y))

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
        for i, carrot in enumerate(game_state.carrots):
            if not carrot.active and current_time - carrot.respawn_timer > carrot_respawn_delay:
                game_state.carrots[i] = create_carrot()
        
        # Garlic shot logic
        if garlic_shot and garlic_shot["active"]:
            if garlic_shot_travel < garlic_shot_max_travel:
                # Update rotation angle each frame
                garlic_shot["rotation_angle"] = (garlic_shot["rotation_angle"] + garlic_rotation_speed) % 360
                # Move in the pre-calculated direction
                garlic_shot["x"] += garlic_shot["dx"] * garlic_shot_speed
                garlic_shot["y"] += garlic_shot["dy"] * garlic_shot_speed
                garlic_shot_travel += garlic_shot_speed
            else:
                if current_time - garlic_shot_start_time > garlic_shot_duration:
                    garlic_shot["active"] = False
                    garlic_shot = None

            # Check for collision with vampire
            if garlic_shot and game_state.vampire.active:
                garlic_rect = pygame.Rect(garlic_shot["x"], garlic_shot["y"], garlic_width, garlic_height)
                if garlic_rect.colliderect(game_state.vampire.rect):
                    game_state.vampire.death_effect_active = True
                    game_state.vampire.death_effect_start_time = current_time
                    game_state.vampire.active = False
                    game_state.vampire.respawn_timer = current_time
                    asset_manager.sounds['vampire_death'].play()
                    garlic_shot = None
        # Update vampire
        game_state.vampire.update(player, game_state.world_size, current_time)

        # Check collision with player
        if game_state.vampire.active and player.rect.colliderect(game_state.vampire.rect):
            player.health -= 1
            asset_manager.sounds['hurt'].play()
            game_state.vampire.active = False
            game_state.vampire.respawn_timer = current_time
            
            if player.health <= 0:
                game_over = True
                asset_manager.sounds['death'].play()
                asset_manager.sounds['background'].stop()
        
        # Check for collisions between rabbit and HP items
        rabbit_rect = player.rect.copy()
        for i, hp_item in enumerate(hp_items[:]):
            hp_item_rect = pygame.Rect(hp_item["x"], hp_item["y"], item_width, item_height)
            if rabbit_rect.colliderect(hp_item_rect):
                if player.health < max_health_points:
                    player.health += 1
                    asset_manager.sounds['get_hp'].play()  # Play the sound effect
                hp_items.pop(i)  # Remove the collected HP item


        # Screen tiling code (fill the entire world_width x world_height area)
        grass_width = grass_image.get_width()
        grass_height = grass_image.get_height()
        for x in range(0, world_width, grass_width):
            for y in range(0, world_height, grass_height):
                screen.blit(grass_image, (x - game_state.scroll[0], y - game_state.scroll[1]))

        # Draw the carrots
        for carrot in game_state.carrots:
            if carrot.active:
                screen.blit(carrot.image, (carrot.rect.x - game_state.scroll[0], carrot.rect.y - game_state.scroll[1]))

        # Draw the rabbit using blit
        screen.blit(player.image, (player.rect.x - game_state.scroll[0], player.rect.y - game_state.scroll[1]))

        # Draw bullets
        for bullet in game_state.bullets:
            screen.blit(
                bullet.rotated_image,
                (bullet.rect.x - game_state.scroll[0],
                 bullet.rect.y - game_state.scroll[1])
            )

        # Draw the garlic shot
        if garlic_shot and garlic_shot["active"]:
            # Use rotation_angle instead of fixed angle
            rotated_garlic = pygame.transform.rotate(garlic_image, garlic_shot["rotation_angle"])
            rotated_rect = rotated_garlic.get_rect(center=(garlic_shot["x"], garlic_shot["y"]))
            screen.blit(rotated_garlic, (rotated_rect.x - game_state.scroll[0], 
                                       rotated_rect.y - game_state.scroll[1]))

        # Update and draw explosions
        for explosion in game_state.explosions[:]:
            if explosion.update(current_time):
                # Handle item drop
                if random.choice([True, False]):
                    game_state.items.append(Collectible(
                        explosion.rect.centerx,
                        explosion.rect.centery,
                        asset_manager.images['hp']
                    ))
                else:
                    game_state.items.append(Collectible(
                        explosion.rect.centerx,
                        explosion.rect.centery,
                        asset_manager.images['garlic']
                    ))
                game_state.explosions.remove(explosion)
            explosion.draw(screen, game_state.scroll)
        
        # Draw vampire
        game_state.vampire.draw(screen, game_state.scroll, current_time)

        # Draw health points UI
        for i in range(player.health):
            screen.blit(hp_image, (10 + i * (hp_width + 5), 10))  # 5 pixels spacing
        
        # Check for collisions between rabbit and Garlic items
        for i, garlic_item in enumerate(garlic_items[:]):
            garlic_item_rect = pygame.Rect(garlic_item["x"], garlic_item["y"], item_width, item_height)
            if rabbit_rect.colliderect(garlic_item_rect):
                if player.garlic_count < max_garlic_count:
                    player.garlic_count += 1
                    asset_manager.sounds['get_garlic'].play()  # Play the sound effect
                garlic_items.pop(i)  # Remove the collected Garlic item

        # Draw Garlic count UI
        if player.garlic_count > 0:  # Only display if player has garlic
            garlic_ui_x = screen_width - 10 - max_garlic_count * (garlic_width + 5)
            for i in range(player.garlic_count):
                screen.blit(garlic_image, (garlic_ui_x + i * (garlic_width + 5), 10))  # 5 pixels spacing

        # Draw the HP items
        item_image_small = pygame.transform.scale(hp_image, (item_width, item_height))
        for hp_item in hp_items:
            screen.blit(pygame.transform.scale(hp_image, (item_width, item_height)), (hp_item["x"] - game_state.scroll[0], hp_item["y"] - game_state.scroll[1]))
        for garlic_item in garlic_items:
            item_image_small = pygame.transform.scale(garlic_image, (item_width, item_height))
            screen.blit(item_image_small, (garlic_item["x"] - game_state.scroll[0], garlic_item["y"] - game_state.scroll[1]))

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

    # Update the display
    pygame.display.flip()
    time.sleep(0.02)

pygame.quit()
sys.exit()
