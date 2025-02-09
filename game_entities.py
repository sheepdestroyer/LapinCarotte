import pygame
import math
import random
import time
from config import *
from utilities import *

class GameObject:
    """Base class for all game entities"""
    def __init__(self, x, y, image):
        self.original_image = image
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.active = True
        
    def update(self, *args):
        """Update logic to be overridden by subclasses"""
        pass
        
    def draw(self, screen, scroll):
        """Draw the entity with scroll offset"""
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))

class Player(GameObject):
    def __init__(self, x, y, image, asset_manager):
        super().__init__(x, y, image)
        self.flipped = False
        self.last_direction = "right"
        self.health = START_HEALTH
        self.garlic_count = 0
        self.death_effect_active = False
        self.death_effect_start_time = 0
        self.asset_manager = asset_manager

    def move(self, dx, dy, world_bounds):
        speed = PLAYER_SPEED
        self.rect.x = max(0, min(world_bounds[0] - self.rect.width, self.rect.x + dx * speed))
        self.rect.y = max(0, min(world_bounds[1] - self.rect.height, self.rect.y + dy * speed))
        
        if dx < 0 and not self.flipped:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.flipped = True
        elif dx > 0 and self.flipped:
            self.image = self.original_image
            self.flipped = False
            
    def take_damage(self, amount=1):
        self.health = max(0, self.health - amount)
        if self.health > 0:
            self.asset_manager.sounds['hurt'].play()
        
    def reset(self):
        self.health = START_HEALTH
        self.garlic_count = 0
        self.rect.x = 200
        self.rect.y = 200
        
    def draw(self, screen, scroll):
        screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        
    def draw_ui(self, screen, hp_image, garlic_image, max_garlic):
        # Health display
        for i in range(self.health):
            screen.blit(hp_image, (10 + i * (32 + 5), 10))
        
        # Garlic display
        if self.garlic_count > 0:
            garlic_ui_x = screen.get_width() - 10 - max_garlic * (32 + 5)
            for i in range(self.garlic_count):
                screen.blit(garlic_image, (garlic_ui_x + i * (32 + 5), 10))
            
            # Carrot juice counter at bottom right
            if hasattr(self, 'carrot_juice_count') and self.carrot_juice_count > 0:
                juice_image = self.asset_manager.images['carrot_juice']
                screen.blit(juice_image, (screen.get_width() - 50, screen.get_height() - 50))
                font = pygame.font.Font(None, 36)
                text = font.render(str(self.carrot_juice_count), True, (255, 255, 255))
                screen.blit(text, (screen.get_width() - 30, screen.get_height() - 45))

class Bullet(GameObject):
    def __init__(self, x, y, target_x, target_y, image):
        super().__init__(x, y, image)
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
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = CARROT_SPEED
        self.active = True
        self.respawn_timer = 0
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), 
                                           random.uniform(-1, 1)).normalize()
        self.spawn_position = (x, y)  # Store initial spawn position

    def respawn(self, world_size, player_rect):
        """Reset carrot to initial position and state"""
        self.rect.center = self.spawn_position
        self.active = True
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), 
                                           random.uniform(-1, 1)).normalize()

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
    def __init__(self, start_x, start_y, target_x, target_y, image):
        super().__init__(start_x, start_y, image)
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
    def __init__(self, x, y, image, item_type, scale=0.5):
        scaled_image = pygame.transform.scale(image, 
            (int(image.get_width() * scale), 
             int(image.get_height() * scale)))
        super().__init__(x, y, scaled_image)
        self.active = True
        self.item_type = item_type

class Vampire(GameObject):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
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
