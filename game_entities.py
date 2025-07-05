import pygame
import math
import random
import time
from config import *
from utilities import *

class GameObject:
    """Base class for all game entities"""
    def __init__(self, x, y, image, cli_mode=False): # Added cli_mode
        self.cli_mode = cli_mode
        self.original_image = image # In CLI, this could be metadata dict
        self.image = image         # In CLI, this could be metadata dict

        if not self.cli_mode and hasattr(image, 'get_rect'):
            self.rect = image.get_rect(topleft=(x, y))
        else:
            # For CLI, or if image is not a surface (e.g. placeholder failed even more)
            width, height = 0, 0 # Default size
            if isinstance(image, dict): # Check if it's metadata from AssetManager CLI mode
                size_info = image.get('size_hint') or image.get('size') # Prefer 'size_hint' if available from config
                if size_info:
                    width, height = size_info
            self.rect = pygame.Rect(x, y, width, height)
        self.active = True
        
    def update(self, *args):
        """Update logic to be overridden by subclasses"""
        pass
        
    def draw(self, screen, scroll):
        """Draw the entity with scroll offset"""
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

class Player(GameObject):
    def __init__(self, x, y, image, asset_manager, cli_mode=False): # Added cli_mode
        super().__init__(x, y, image, cli_mode=cli_mode) # Pass cli_mode to super
        self.initial_x = x
        self.initial_y = y
        self.flipped = False
        self.last_direction = "right"
        self.health = START_HEALTH
        self.max_health = MAX_HEALTH
        self.garlic_count = 0
        self.carrot_juice_count = 0  # Initialize counter
        self.invincible = False
        self.last_hit_time = 0
        self.speed = PLAYER_SPEED
        self.death_effect_active = False
        self.death_effect_start_time = 0
        self.asset_manager = asset_manager
        self.health_changed = False
        self.garlic_changed = False
        self.juice_changed = False

    def move(self, dx, dy, world_bounds):
        self.rect.x = max(0, min(world_bounds[0] - self.rect.width, self.rect.x + dx * self.speed))
        self.rect.y = max(0, min(world_bounds[1] - self.rect.height, self.rect.y + dy * self.speed))
        
        if dx < 0 and not self.flipped:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.flipped = True
        elif dx > 0 and self.flipped:
            self.image = self.original_image
            self.flipped = False
            
    def take_damage(self, amount=1):
        if not self.invincible and not self.death_effect_active:
            self.health = max(0, self.health - amount)
            self.health_changed = True
            if self.health > 0:
                self.asset_manager.sounds['hurt'].play()
                self.invincible = True
                self.last_hit_time = time.time()
        
    def update_invincibility(self):
        if self.invincible and (time.time() - self.last_hit_time >= PLAYER_INVINCIBILITY_DURATION):
            self.invincible = False

    def reset(self):
        self.health = START_HEALTH
        self.garlic_count = 0
        self.carrot_juice_count = 0
        self.rect.x = self.initial_x
        self.rect.y = self.initial_y
        self.invincible = False
        self.death_effect_active = False
        self.image = self.original_image # Reset image if flipped
        self.flipped = False
        
    def draw(self, screen, scroll):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        
    def draw_ui(self, screen, hp_image, garlic_image, max_garlic):
        # Health display
        for i in range(self.health):
            screen.blit(hp_image, (10 + i * (hp_image.get_width() + 5), 10))
        
        # Garlic display
        if self.garlic_count > 0:
            screen_width = screen.get_width()
            garlic_width = garlic_image.get_width()
            spacing = 5
            for i in range(self.garlic_count):
                x = screen_width - 10 - (i + 1) * (garlic_width + spacing)
                screen.blit(garlic_image, (x, 10))
        
        # Carrot juice counter at bottom right (always visible when count > 0)
        if self.carrot_juice_count > 0:
            juice_image = self.asset_manager.images['carrot_juice']
            digits = str(self.carrot_juice_count)
            spacing = 5
            original_digit = self.asset_manager.images['digit_0']
            scaled_digit_width = original_digit.get_width() * 5
            scaled_digit_height = original_digit.get_height() * 5
            
            # Calculate total width needed for digits and spacing
            total_width = len(digits) * (scaled_digit_width + spacing)
            
            # Start position (left side of juice image)
            x = screen.get_width() - 10 - juice_image.get_width() - total_width
            y = screen.get_height() - 10 - juice_image.get_height()
            
            # Calculate vertical position to align bottoms
            digit_y = y + juice_image.get_height() - scaled_digit_height
            
            # Draw digits first
            for i, digit in enumerate(digits):
                digit_img = self.asset_manager.images[f'digit_{digit}']
                scaled_digit = pygame.transform.scale(digit_img, (scaled_digit_width, scaled_digit_height))
                screen.blit(scaled_digit, (x + i * (scaled_digit_width + spacing), digit_y))
            
            # Draw juice image to the right of the digits
            screen.blit(juice_image, (x + total_width + spacing, y))

class Bullet(GameObject):
    def __init__(self, x, y, target_x, target_y, image, cli_mode=False): # Added cli_mode
        super().__init__(x, y, image, cli_mode=cli_mode) # Pass cli_mode
        dir_x, dir_y = get_direction_vector(x, y, target_x, target_y)
        self.velocity = (dir_x * BULLET_SPEED, dir_y * BULLET_SPEED)
        self.angle = math.degrees(math.atan2(-dir_y, dir_x))
        
    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        
    @property
    def rotated_image(self):
        return pygame.transform.rotate(self.original_image, self.angle)

class Carrot(GameObject):
    def __init__(self, x, y, image, cli_mode=False): # Added cli_mode
        super().__init__(x, y, image, cli_mode=cli_mode) # Pass cli_mode
        self.speed = CARROT_SPEED
        self.active = True
        self.respawn_timer = 0
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), 
                                           random.uniform(-1, 1)).normalize()
        self.spawn_position = (x, y)  # Store initial spawn position

    def respawn(self, world_size, player_rect):
        """Reset carrot to initial position and state"""
        self.rect.topleft = self.spawn_position # Use topleft as spawn_position is topleft
        self.active = True
        # Ensure new direction is valid (non-zero vector) before normalizing
        new_dir_x = random.uniform(-1, 1)
        new_dir_y = random.uniform(-1, 1)
        # If both are zero (unlikely but possible), default to a direction
        if new_dir_x == 0 and new_dir_y == 0:
            new_dir_x = 1.0
        self.direction = pygame.math.Vector2(new_dir_x, new_dir_y).normalize()

    def update(self, player_rect, world_bounds):
        if self.active:
            player_center = pygame.math.Vector2(player_rect.center)
            carrot_center = pygame.math.Vector2(self.rect.center)
            direction = carrot_center - player_center
            dist = direction.length()
            
            max_distance = CARROT_DETECTION_RADIUS
            speed_multiplier = min(max(1, 1 + (max_distance - dist)/max_distance * (3 - 1)), 3)
            
            if dist < CARROT_CHASE_RADIUS and dist > 0:
                direction.normalize_ip()
                self.direction = direction
            else:
                self.direction += pygame.math.Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))
                self.direction.normalize_ip()
            
            movement = self.direction * self.speed * speed_multiplier
            self.rect.x += movement.x
            self.rect.y += movement.y
            
            self.rect.x = max(0, min(world_bounds[0] - self.rect.width, self.rect.x))
            self.rect.y = max(0, min(world_bounds[1] - self.rect.height, self.rect.y))

class GarlicShot(GameObject):
    def __init__(self, start_x, start_y, target_x, target_y, image, cli_mode=False): # Added cli_mode
        super().__init__(start_x, start_y, image, cli_mode=cli_mode) # Pass cli_mode
        dir_x, dir_y = get_direction_vector(start_x, start_y, target_x, target_y)
        self.direction = pygame.math.Vector2(dir_x, dir_y)
        self.rotation_angle = 0
        self.speed = GARLIC_SHOT_SPEED
        self.max_travel = GARLIC_SHOT_MAX_TRAVEL
        self.traveled = 0
        self.active = True

    def update(self):
        if self.active:
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
            self.traveled += self.speed
            self.rotation_angle = (self.rotation_angle + 5) % 360
            if self.traveled >= self.max_travel:
                self.active = False

class Explosion:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = image.get_rect(center=(x, y))
        self.start_time = time.time()
        self.flash_count = 0
        self.max_flashes = EXPLOSION_MAX_FLASHES
        self.flash_interval = EXPLOSION_FLASH_INTERVAL
        self.active = True

    def update(self, current_time):
        if self.active:
            elapsed = current_time - self.start_time
            if elapsed > self.flash_interval:
                self.flash_count += 1
                self.start_time = current_time
            if self.flash_count >= self.max_flashes:
                self.active = False
                return True
        return False

    def draw(self, screen, scroll):
        """Draw the explosion with scrolling offset"""
        if self.active and (self.flash_count % 2 == 0):
            screen.blit(self.image, 
                       (self.rect.x - scroll[0], 
                        self.rect.y - scroll[1]))

class Collectible(GameObject):
    def __init__(self, x, y, image, item_type, scale=0.5, cli_mode=False): # Added cli_mode
        # In CLI mode, 'image' is metadata, so scaling is not applicable / different.
        # For now, pass original 'image' (metadata) to super if cli_mode.
        # Scaling logic should only apply if not cli_mode and image is a Surface.
        if not cli_mode and hasattr(image, 'get_width') and hasattr(image, 'get_height'):
            scaled_image = pygame.transform.scale(image,
                (int(image.get_width() * scale),
                 int(image.get_height() * scale)))
            super().__init__(x, y, scaled_image, cli_mode=cli_mode) # Pass cli_mode
        else: # CLI mode or image is not a surface
            super().__init__(x, y, image, cli_mode=cli_mode) # Pass original image (metadata) and cli_mode

        # Rect centering might need adjustment if super().__init__ already uses size_hint from metadata
        # If self.rect was already created by super with proper dimensions from metadata, this might be okay.
        # If super created a 0,0 rect in CLI, this re-centering won't use proper width/height.
        # The GameObject.__init__ was updated to use size_hint if image is dict.
        # So, self.rect should be somewhat correct after super call.
        # This line might be redundant or needs care if self.image is not a Surface.
        if not cli_mode and hasattr(self.image, 'get_rect'):
            self.rect = self.image.get_rect(center=(x, y))  # Re-center if it's a surface

        self.active = True
        self.item_type = item_type

class Vampire(GameObject):
    def __init__(self, x, y, image, cli_mode=False):
        super().__init__(x, y, image, cli_mode=cli_mode)
        self.active = False
        self.respawn_timer = 0
        self.death_effect_active = False
        self.death_effect_start_time = 0
        self.death_effect_duration = VAMPIRE_DEATH_DURATION
        self.speed = VAMPIRE_SPEED

    def update(self, player, world_bounds, current_time):
        if self.active:
            # Movement logic
            move_x, move_y = calculate_movement_towards(self.rect, player.rect, self.speed, world_bounds)
            self.rect.x += move_x
            self.rect.y += move_y

            # Boundary check
            self.rect.x = max(0, min(world_bounds[0] - self.rect.width, self.rect.x))
            self.rect.y = max(0, min(world_bounds[1] - self.rect.height, self.rect.y))

            # Death effect check
            if self.death_effect_active and (current_time - self.death_effect_start_time >= self.death_effect_duration):
                self.death_effect_active = False
        else:
            # Respawn check when NOT active
            if (current_time - self.respawn_timer > VAMPIRE_RESPAWN_TIME):
                self.respawn(
                    random.randint(0, world_bounds[0] - self.rect.width),
                    random.randint(0, world_bounds[1] - self.rect.height)
                )

    def respawn(self, x, y):
        self.rect.topleft = (x, y)
        self.active = True
        self.death_effect_active = False
        self.death_flash_count = 0

    def draw(self, screen, scroll, current_time):
        if self.death_effect_active:
            time_since_flash = current_time - self.death_effect_start_time
            if time_since_flash <= self.death_effect_duration:
                if int(time_since_flash / 0.1) % 2 == 0:
                    tinted_image = self.image.copy()
                    tinted_image.fill((0, 255, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(tinted_image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        elif self.active:
            screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

class Button:
    """UI Button class"""
    def __init__(self, x, y, image, callback, cli_mode=False): # Added cli_mode
        self.image = image # In CLI, this might be metadata
        self.callback = callback
        self.cli_mode = cli_mode

        if not self.cli_mode and hasattr(image, 'get_rect'):
            self.rect = self.image.get_rect(topleft=(x,y))
        else:
            # In CLI mode, buttons might not need a rect, or a default one.
            # Or, main.py should not instantiate Button objects with image metadata if not needed.
            # For now, create a default rect to prevent crashes during instantiation.
            # Button positioning logic in main.py might need to be CLI-aware too.
            width, height = 0,0
            if isinstance(image, dict): # Check if it's metadata from AssetManager CLI mode
                size_info = image.get('size_hint') or image.get('size')
                if size_info:
                    width, height = size_info
            self.rect = pygame.Rect(x, y, width, height)


    def draw(self, screen):
        """Draw the button on the screen."""
        screen.blit(self.image, self.rect)

    def handle_event(self, event):
        """Handle a single event. If the button is clicked, execute the callback."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                if self.rect.collidepoint(event.pos):
                    self.callback()
