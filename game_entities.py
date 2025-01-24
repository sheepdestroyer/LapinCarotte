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

    def draw(self, screen, scroll):
        if self.death_effect_active:
            time_since_flash = time.time() - self.death_effect_start_time
            if time_since_flash <= self.death_effect_duration:  # Only draw during duration
                if int(time_since_flash / 0.1) % 2 == 0:  # Flash interval
                    # Create green-tinted version
                    tinted_image = self.image.copy()
                    tinted_image.fill((0, 255, 0, 128), special_flags=pygame.BLEND_RGBA_MULT)
                    screen.blit(tinted_image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
        elif self.active:
            screen.blit(self.image, (self.rect.x - scroll[0], self.rect.y - scroll[1]))
