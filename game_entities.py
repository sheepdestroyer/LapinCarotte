import pygame
import math
import random

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
        self.rect = image.get_rect(topleft=(x, y))
        self.speed = 3
        self.active = True
        self.respawn_timer = 0
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
