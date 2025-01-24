#!/usr/bin/env python3
import os
import pygame
import time
import sys
import random
import math
from asset_manager import AssetManager
from game_entities import Player, Bullet, Carrot
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

# Initialize Pygame and managers
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Initialize game systems
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

# Initialize player
player = Player(200, 200, asset_manager.images['rabbit'])

# Play intro music
asset_manager.sounds['intro'].play(-1)

# Carrot speed
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

# Lists to store bullets
bullets = []

# Explosion variables
explosion_x = 0
explosion_y = 0
explosion_start_time = 0
explosion_duration = 0.1  # in seconds
explosion_active = False
drop_hp_item = False # Flag to indicate if the HP item should be dropped
explosion_flash_count = 0  # Counter for the number of flashes
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



# Vampire and Garlic variables
vampire_x = world_width - vampire_width - 100  # Start from the right edge
vampire_y = random.randint(0, world_height - vampire_height)
vampire_speed = 4
vampire_active = False # the vampire will spawn after the start
vampire_respawn_delay = 5 # delay in seconds before the vampire respawns
vampire_respawn_timer = 0

# Vampire death effect variables
vampire_death_effect_active = False
vampire_death_flash_count = 0
vampire_death_flash_interval = 0.1  # Time in seconds between flashes

# Health Points variables
max_health_points = 3
health_points = max_health_points

# Garlic count variables
max_garlic_count = 3
garlic_count = 0

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
        new_x = random.randint(0, world_width - carrot_width)
        new_y = random.randint(0, world_height - carrot_height)
        if distance(new_x + carrot_width / 2, new_y + carrot_height / 2, rabbit_x + rabbit_width / 2,
                    rabbit_y + rabbit_height / 2) > min(screen_width, screen_height) / 3:
            return {
                "x": new_x,
                "y": new_y,
                "move_x": 0,
                "move_y": 0,
                "speed_multiplier": 1, # initialize speed
                "active": True, # initialize the carrot as being active
                "respawn_timer": 0
            }

# Initialize carrots
for _ in range(num_carrots):
    carrots.append(create_carrot())

# Function to respawn the vampire
def respawn_vampire():
    global vampire_x, vampire_y, vampire_active, garlic_count
    vampire_x = random.randint(0, world_width - vampire_width)
    vampire_y = random.randint(0, world_height - vampire_height)
    vampire_active = True

# Function to reset the game state
def reset_game():
    global rabbit_x, rabbit_y, scroll_x, scroll_y, health_points, vampire_active, vampire_x, vampire_y, bullets, carrots, game_over, hp_items
    # Reset rabbit position and scrolling
    rabbit_x = 200
    rabbit_y = 200
    scroll_x = 0
    scroll_y = 0

    # Reset health points
    health_points = max_health_points

    # Reset vampire
    vampire_active = False
    vampire_x = world_width - vampire_width - 100
    vampire_y = random.randint(0, world_height - vampire_height)

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
    garlic_count = 0


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
                    bullet_x = rabbit_x + rabbit_width / 2 - bullet_width / 2  # Middle of the rabbit
                    bullet_y = rabbit_y + rabbit_height / 2 - bullet_height / 2
                    # Store the bullet position and direction for that shot
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    bullet_dx = mouse_x - rabbit_x - rabbit_width/2 + scroll_x
                    bullet_dy = mouse_y - rabbit_y - rabbit_height/2 + scroll_y
                    bullets.append([bullet_x, bullet_y, bullet_dx, bullet_dy])

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Create new bullet at rabbit's center
                    bullet_x = rabbit_x + rabbit_width / 2 - bullet_width / 2  # Middle of the rabbit
                    bullet_y = rabbit_y + rabbit_height / 2 - bullet_height / 2

                    # Store the bullet position and get direction based on mouse
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    bullet_dx = mouse_x - rabbit_x - rabbit_width/2 + scroll_x
                    bullet_dy = mouse_y - rabbit_y - rabbit_height/2 + scroll_y
                    bullets.append([bullet_x, bullet_y, bullet_dx, bullet_dy])

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and garlic_count > 0 and garlic_shot is None:  # Right mouse button and have garlic
                    garlic_count -= 1
                    garlic_shot_start_time = current_time
                    garlic_shot_travel = 0

                    # Initial position of the garlic shot
                    garlic_shot_angle = 0  # Initialize angle for garlic shot
                    garlic_shot_x = rabbit_x + rabbit_width / 2 - garlic_width / 2
                    garlic_shot_y = rabbit_y

                    # Store the garlic shot data
                    garlic_shot = {
                        "x": garlic_shot_x,
                        "y": garlic_shot_y,
                        "start_x": garlic_shot_x,
                        "start_y": garlic_shot_y,
                        "angle": garlic_shot_angle,  # Store the initial angle
                        "active": True
                    }


        else: # Game is over, check for button clicks
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
        screen.blit(start_button_image, (787, 742))
        # Draw exit button
        screen.blit(exit_button_image, (787, 827))
    elif not game_over:
        # Handle keyboard input for rabbit movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_q]: # Check for both left arrow and 'q' key
            rabbit_x -= 5
            # Flip the image only when moving left
            if not rabbit_flipped:  # Only flip the image once
                rabbit_image = pygame.transform.flip(original_rabbit_image, True, False)
                rabbit_flipped = True
            last_direction = "left"  # set the last direction
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: # Check for both right arrow and 'd' key
            rabbit_x += 5
            # Unflip the image when moving right (or stopping)
            if rabbit_flipped:  # Only unflip if the image is flipped
                rabbit_image = original_rabbit_image
                rabbit_flipped = False
            last_direction = "right"  # set the last direction
        if keys[pygame.K_UP] or keys[pygame.K_z]: # Check for both up arrow and 'z' key
            rabbit_y -= 5
            last_direction = "up"  # set the last direction
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: # Check for both down arrow and 's' key
            rabbit_y += 5
            last_direction = "down"  # set the last direction
            
        # Scrolling logic
        if rabbit_x < scroll_x + screen_width * scroll_trigger:
            scroll_x = max(0, rabbit_x - screen_width * scroll_trigger) # keep scrolling in the world boundaries
        elif rabbit_x + rabbit_width > scroll_x + screen_width * (1 - scroll_trigger):
          scroll_x = min(world_width - screen_width, rabbit_x - screen_width*(1-scroll_trigger) + rabbit_width) # keep scrolling in the world boundaries

        if rabbit_y < scroll_y + screen_height * scroll_trigger:
            scroll_y = max(0, rabbit_y - screen_height * scroll_trigger)
        elif rabbit_y + rabbit_height > scroll_y + screen_height * (1 - scroll_trigger):
            scroll_y = min(world_height - screen_height, rabbit_y - screen_height*(1-scroll_trigger) + rabbit_height)

        # Update coordinates to be inside world bounds
        rabbit_x = max(0, min(world_width - rabbit_width, rabbit_x))
        rabbit_y = max(0, min(world_height - rabbit_height, rabbit_y))

        # Update carrot logic
        for carrot in carrots:
          if carrot["active"]:
            # Calculate direction away from the rabbit (avoidance)
            rabbit_center_x = rabbit_x + rabbit_width / 2
            rabbit_center_y = rabbit_y + rabbit_height / 2
            carrot_center_x = carrot["x"] + carrot_width/2
            carrot_center_y = carrot["y"] + carrot_height/2
            dx = carrot_center_x - rabbit_center_x
            dy = carrot_center_y - rabbit_center_y
            dist = distance(rabbit_center_x, rabbit_center_y, carrot_center_x, carrot_center_y)

            # Calculate the speed multiplier based on distance
            max_distance = 200  # Define a maximum distance where the carrot will reach max speed
            carrot["speed_multiplier"] = min(max(1, 1 + (max_distance - dist) / max_distance * (max_speed_multiplier - 1)),
                                   max_speed_multiplier)  # between 1 and max_speed_multiplier

            # Check for border proximity and change direction if necessary
            if carrot["x"] < 10:
              carrot["move_x"] = random.uniform(0.1, 1)
            if carrot["x"] > world_width - carrot_width - 10:
              carrot["move_x"] = random.uniform(-1, -0.1)
            if carrot["y"] < 10:
              carrot["move_y"] = random.uniform(0.1, 1)
            if carrot["y"] > world_height - carrot_height - 10:
              carrot["move_y"] = random.uniform(-1, -0.1)

            # Carrot movement behavior based on distance
            if dist < 100: # Move away from the rabbit
              if dist > 0:
                carrot["move_x"] = dx / dist
                carrot["move_y"] = dy / dist
            else: # Move randomly
              if carrot["move_x"] == 0 or carrot["move_y"] == 0: # Initialize with random movement
                 carrot["move_x"] = random.uniform(-1, 1)
                 carrot["move_y"] = random.uniform(-1, 1)
              else: # Keep moving in the same general direction, but add some randomness
                 carrot["move_x"] += random.uniform(-0.2, 0.2)
                 carrot["move_y"] += random.uniform(-0.2, 0.2)
            # Update carrot position based on movement variables
            carrot["x"] += carrot["move_x"] * carrot_speed * carrot["speed_multiplier"]
            carrot["y"] += carrot["move_y"] * carrot_speed * carrot["speed_multiplier"]

            # Keep carrot within world bounds
            carrot["x"] = max(0, min(world_width - carrot_width, carrot["x"]))
            carrot["y"] = max(0, min(world_height - carrot_height, carrot["y"]))

        # Update the bullet positions and handle removal
        for bullet in bullets[:]:  # Iterate over a copy to safely delete
            bullet_x = bullet[0]
            bullet_y = bullet[1]
            bullet_dx = bullet[2]
            bullet_dy = bullet[3]
            # Normalize the direction and move using the normalized direction
            bullet_dist = distance(0, 0, bullet_dx, bullet_dy)
            if bullet_dist > 0:
                bullet_x += bullet_dx / bullet_dist * bullet_speed
                bullet_y += bullet_dy / bullet_dist * bullet_speed

                bullet[0] = bullet_x
                bullet[1] = bullet_y

            # Check for a collision between the carrot and the bullets
            for carrot in carrots:
              if carrot["active"]:
                carrot_rect = pygame.Rect(carrot["x"], carrot["y"], carrot_width, carrot_height)
                bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)
                if carrot_rect.colliderect(bullet_rect):
                    # Set variables to render the explosion
                    explosion_x = carrot["x"] - (explosion_width - carrot_width) / 2  # Center the image
                    explosion_y = carrot["y"] - (explosion_height - carrot_height) / 2
                    explosion_start_time = current_time
                    explosion_active = True
                    drop_hp_item = True
                    explosion_flash_count = 0
                    if bullet in bullets: # Prevent trying to remove the bullet when it has already been removed
                      bullets.remove(bullet)  # Remove the bullet
                    
                    
                    carrot["active"] = False  # Set that the carrot has been "destroyed"
                    explosion_sound.play()  # Play the explosion
                    
                    carrot["respawn_timer"] = current_time  # Start the respawn timer
                else:  # Remove bullets that are off the screen
                    if bullet[0] > world_width or bullet[0] < 0 or bullet[1] > world_height or bullet[1] < 0:
                        if bullet in bullets:
                          bullets.remove(bullet)

        # Respawn carrots after delay
        for carrot in carrots:
          if not carrot["active"]:
            if current_time - carrot["respawn_timer"] > carrot_respawn_delay:
              new_carrot = create_carrot()
              carrot.update(new_carrot)
        
        # Garlic shot logic
        if garlic_shot and garlic_shot["active"]:
            if garlic_shot_travel < garlic_shot_max_travel:
                # Calculate direction based on mouse position at the time of the shot
                mouse_x, mouse_y = pygame.mouse.get_pos()
                garlic_dx = mouse_x - garlic_shot["start_x"] + scroll_x
                garlic_dy = mouse_y - garlic_shot["start_y"] + scroll_y
                garlic_dist = distance(0, 0, garlic_dx, garlic_dy)
                garlic_shot["x"] += garlic_dx / garlic_dist * garlic_shot_speed
                garlic_shot["y"] += garlic_dy / garlic_dist * garlic_shot_speed
                garlic_shot_travel += garlic_shot_speed
            else:
                if current_time - garlic_shot_start_time > garlic_shot_duration:
                    garlic_shot["active"] = False
                    garlic_shot = None  # Reset garlic shot

            # Update garlic rotation
            garlic_rotation_angle = (garlic_rotation_angle + garlic_rotation_speed) % 360

            # Check for collision with vampire
            if garlic_shot and vampire_active:
                garlic_rect = pygame.Rect(garlic_shot["x"], garlic_shot["y"], garlic_width, garlic_height)
                if garlic_rect.colliderect(vampire_rect):
                    #vampire_active = False
                    #vampire_respawn_timer = current_time
                    vampire_death_effect_active = True
                    vampire_death_flash_count = 0
                    vampire_active = False
                    vampire_respawn_timer = current_time
                    vampire_death_effect_start_time = current_time
                    vampire_death_sound.play()
                    vampire_death_sound.play()  # Play vampire death sound
                    garlic_shot = None
        # Vampire logic
        if vampire_active:
            # Calculate direction towards the rabbit
            vampire_dx = (rabbit_x + rabbit_width / 2) - (vampire_x + vampire_width / 2)
            vampire_dy = (rabbit_y + rabbit_height / 2) - (vampire_y + vampire_height / 2)
            vampire_dist = distance(rabbit_x, rabbit_y, vampire_x, vampire_y)

            if vampire_dist > 0:
                vampire_dx /= vampire_dist
                vampire_dy /= vampire_dist

            # Move the vampire
            vampire_x += vampire_dx * vampire_speed
            vampire_y += vampire_dy * vampire_speed

            # Keep vampire within world bounds
            vampire_x = max(0, min(world_width - vampire_width, vampire_x))
            vampire_y = max(0, min(world_height - vampire_height, vampire_y))

            # Check for collision with rabbit
            rabbit_rect = pygame.Rect(rabbit_x, rabbit_y, rabbit_width, rabbit_height)
            vampire_rect = pygame.Rect(vampire_x, vampire_y, vampire_width, vampire_height)
            if rabbit_rect.colliderect(vampire_rect):
                health_points -= 1  # Decrease health points
                hurt_sound.play()  # Play hurt sound
                vampire_active = False
                vampire_respawn_timer = current_time
                vampire_death_effect_active = False
                vampire_death_flash_count = 0

                if health_points == 0:
                    game_over = True
                    get_death_sound.play()  # Play death sound
                    background_music.stop()
        else: # Respawn the vampire after a delay if it is not active
          if current_time - vampire_respawn_timer > vampire_respawn_delay:
            respawn_vampire()
        
        # Check for collisions between rabbit and HP items
        rabbit_rect = pygame.Rect(rabbit_x, rabbit_y, rabbit_width, rabbit_height)
        for i, hp_item in enumerate(hp_items[:]):
            hp_item_rect = pygame.Rect(hp_item["x"], hp_item["y"], item_width, item_height)
            if rabbit_rect.colliderect(hp_item_rect):
                if health_points < max_health_points:
                    health_points += 1
                    get_hp_sound.play()  # Play the sound effect
                hp_items.pop(i)  # Remove the collected HP item


        # Screen tiling code (fill the entire world_width x world_height area)
        grass_width = grass_image.get_width()
        grass_height = grass_image.get_height()
        for x in range(0, world_width, grass_width):
            for y in range(0, world_height, grass_height):
                screen.blit(grass_image, (x - scroll_x, y - scroll_y))

        # Draw the carrots
        for carrot in carrots:
          if carrot["active"]:
            screen.blit(carrot_image, (carrot["x"] - scroll_x, carrot["y"] - scroll_y))

        # Draw the rabbit using blit
        screen.blit(rabbit_image, (rabbit_x - scroll_x, rabbit_y - scroll_y))

        # Draw the bullets
        for bullet in bullets:
            bullet_x = bullet[0]
            bullet_y = bullet[1]
            bullet_dx = bullet[2]
            bullet_dy = bullet[3]
            bullet_dist = distance(0, 0, bullet_dx, bullet_dy)

            # Calculate the angle of the bullet
            angle = math.degrees(math.atan2(bullet_dy, bullet_dx))

            # Rotate the bullet
            rotated_bullet = pygame.transform.rotate(original_bullet_image, -angle)
            bullet_rect = rotated_bullet.get_rect(center=(bullet_x, bullet_y))  # We need to also fix the center of the sprite to be where the x and y coordinates are
            screen.blit(rotated_bullet, (bullet_rect.x - scroll_x, bullet_rect.y - scroll_y))

        # Draw the garlic shot
        if garlic_shot and garlic_shot["active"]:
            # Calculate the angle of the garlic shot
            garlic_dx = mouse_x - garlic_shot["start_x"] + scroll_x
            garlic_dy = mouse_y - garlic_shot["start_y"] + scroll_y
            angle = math.degrees(math.atan2(garlic_dy, garlic_dx))
            rotated_garlic = pygame.transform.rotate(garlic_image, garlic_rotation_angle)            
            rotated_garlic_rect = rotated_garlic.get_rect(center = (garlic_shot["x"], garlic_shot["y"]))
            screen.blit(rotated_garlic, (garlic_shot["x"] - scroll_x, garlic_shot["y"] - scroll_y))

        # Check and draw explosion
        if explosion_active:
            time_since_flash_start = current_time - explosion_start_time
            if int(time_since_flash_start / explosion_flash_interval) % 2 == 0:
                screen.blit(explosion_image, (explosion_x - scroll_x, explosion_y - scroll_y))            
            # Drop HP item after the last explosion flash
            if drop_hp_item and explosion_flash_count == max_explosion_flashes -1 and time_since_flash_start > explosion_flash_interval:
                if random.choice([True, False]):  # Randomly drop either HP or Garlic
                    hp_items.append({
                        "x": explosion_x + explosion_width / 2 - item_width / 2,
                        "y": explosion_y + explosion_height / 2 - item_height / 2
                    })
                    drop_hp_item = False
                else:
                    garlic_items.append({
                        "x": explosion_x + explosion_width / 2 - item_width / 2,
                        "y": explosion_y + explosion_height / 2 - item_height / 2
                    })
                    drop_hp_item = False

            
            # Increment flash count
            if time_since_flash_start > explosion_flash_interval:
                explosion_flash_count += 1
                explosion_start_time = current_time  # Reset start time for the next flash

            if explosion_flash_count >= max_explosion_flashes:
                explosion_active = False  # Stop displaying after 3 flashes
        
        # Draw the vampire
        if vampire_active or vampire_death_effect_active:
            if vampire_death_effect_active:
                time_since_flash_start = current_time - vampire_death_effect_start_time

                # Apply dark green alpha layer
                vampire_surface = vampire_image.copy()
                dark_green = (0, 100, 0, 128)  # Dark green with alpha (RGBA)
                for x in range(vampire_surface.get_width()):
                    for y in range(vampire_surface.get_height()):
                        if vampire_surface.get_at((x, y))[3] > 0:  # Check if pixel is not transparent
                            vampire_surface.set_at((x, y), dark_green)

                # Flashing effect
                if int(time_since_flash_start / vampire_death_flash_interval) % 2 == 0:
                    screen.blit(vampire_surface, (vampire_x - scroll_x, vampire_y - scroll_y))
                else:
                    screen.blit(vampire_image, (vampire_x - scroll_x, vampire_y - scroll_y))

                if time_since_flash_start > vampire_death_flash_interval:
                    vampire_death_flash_count += 1
                    vampire_death_effect_start_time = current_time

                if vampire_death_flash_count >= 3:
                    vampire_death_effect_active = False
                    vampire_active = False
                    vampire_respawn_timer = current_time
            else:
                screen.blit(vampire_image, (vampire_x - scroll_x, vampire_y - scroll_y))

        # Draw health points UI
        for i in range(health_points):
            screen.blit(hp_image, (10 + i * (hp_width + 5), 10))  # 5 pixels spacing
        
        # Check for collisions between rabbit and Garlic items
        for i, garlic_item in enumerate(garlic_items[:]):
            garlic_item_rect = pygame.Rect(garlic_item["x"], garlic_item["y"], item_width, item_height)
            if rabbit_rect.colliderect(garlic_item_rect):
                if garlic_count < max_garlic_count:
                    garlic_count += 1
                    get_garlic_sound.play()  # Play the sound effect
                garlic_items.pop(i)  # Remove the collected Garlic item

        # Draw Garlic count UI
        if garlic_count > 0:  # Only display if player has garlic
            garlic_ui_x = screen_width - 10 - max_garlic_count * (garlic_width + 5)
            for i in range(garlic_count):
                screen.blit(garlic_image, (garlic_ui_x + i * (garlic_width + 5), 10))  # 5 pixels spacing

        # Draw the HP items
        item_image_small = pygame.transform.scale(hp_image, (item_width, item_height))
        for hp_item in hp_items:
            screen.blit(pygame.transform.scale(hp_image, (item_width, item_height)), (hp_item["x"] - scroll_x, hp_item["y"] - scroll_y))
        for garlic_item in garlic_items:
            item_image_small = pygame.transform.scale(garlic_image, (item_width, item_height))
            screen.blit(item_image_small, (garlic_item["x"] - scroll_x, garlic_item["y"] - scroll_y))

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
