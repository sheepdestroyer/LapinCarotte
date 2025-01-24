import pygame
import math
import random
import time

class Player:
    def __init__(self, x, y, image):
        self.original_image = image
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.flipped = False
        self.last_direction = "right"
        self.health = 3
        self.garlic_count = 0

    def move(self, dx, dy, world_bounds):
        self.rect.x = max(0, min(world_bounds[0] - self.rect.width, self.rect.x + dx))
        self.rect.y = max(0, min(world_bounds[1] - self.rect.height, self.rect.y + dy))
        
        if dx < 0 and not self.flipped:
            self.image = pygame.transform.flip(self.original_image, True, False)
            self.flipped = True
        elif dx > 0 and self.flipped:
            self.image = self.original_image
            self.flipped = False
            
    def take_damage(self):
        self.health -= 1
        
    def reset(self):
        self.health = 3
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

class Bullet:
    def __init__(self, x, y, target_x, target_y, image):
        self.original_image = image
        self.rect = image.get_rect(center=(x, y))
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        self.velocity = (dx/dist * 10, dy/dist * 10) if dist > 0 else (0, 0)
        self.angle = math.degrees(math.atan2(-dy, dx))
        
    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        
    @property
    def rotated_image(self):
        return pygame.transform.rotate(self.original_image, self.angle)

class Carrot:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = image.get_rect(center=(x, y))  # Center-based position
        self.speed = 3
        self.active = True
        self.respawn_timer = 0
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

    def update(self, player_rect, world_bounds):
        if self.active:
            player_center = pygame.math.Vector2(player_rect.center)
            carrot_center = pygame.math.Vector2(self.rect.center)
            direction = carrot_center - player_center
            dist = direction.length()
            
            max_distance = 200
            speed_multiplier = min(max(1, 1 + (max_distance - dist)/max_distance * (3 - 1)), 3)
            
            if dist < 100 and dist > 0:
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

class GarlicShot:
    def __init__(self, start_x, start_y, target_x, target_y, image):
        self.image = image
        self.rect = image.get_rect(center=(start_x, start_y))
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        self.direction = pygame.math.Vector2(dx/dist, dy/dist) if dist > 0 else pygame.math.Vector2(0, 0)
        self.rotation_angle = 0
        self.speed = 5
        self.max_travel = 250
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
        self.max_flashes = 3
        self.flash_interval = 0.1
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

class Collectible:
    def __init__(self, x, y, image, scale=0.5):
        self.image = pygame.transform.scale(image, 
            (int(image.get_width() * scale), 
             int(image.get_height() * scale)))
        self.rect = self.image.get_rect(center=(x, y))
        self.active = True

class Vampire:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = image.get_rect(center=(x, y))  # Center-based position
        self.active = False
        self.respawn_timer = 0
        self.death_effect_active = False
        self.death_effect_start_time = 0
        self.death_effect_duration = 2  # 2 second death effect
        self.speed = 4

    def update(self, player, world_bounds, current_time):
        if self.active:
            # Movement logic
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)
            
            if distance > 0:
                self.rect.x += dx/distance * self.speed
                self.rect.y += dy/distance * self.speed

            # Boundary check
            self.rect.x = max(0, min(world_bounds[0] - self.rect.width, self.rect.x))
            self.rect.y = max(0, min(world_bounds[1] - self.rect.height, self.rect.y))

            # Death effect check
            if self.death_effect_active and (current_time - self.death_effect_start_time >= self.death_effect_duration):
                self.death_effect_active = False
        else:
            # Respawn check when NOT active
            if (current_time - self.respawn_timer > 5):
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
