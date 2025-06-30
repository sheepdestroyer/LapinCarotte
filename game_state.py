import random
import pygame # Added for pygame.math.Vector2
import math # Added for math.sqrt
from game_entities import Carrot, Vampire, Player, Bullet, GarlicShot, Explosion, Collectible
from config import *

class GameState:
    def __init__(self, asset_manager):
        self.scroll = [0, 0]
        self.scroll_trigger = SCROLL_TRIGGER
        self.world_size = WORLD_SIZE
        self.game_over = False
        self.started = False
        self.asset_manager = asset_manager
        self.player = Player(200, 200, asset_manager.images['rabbit'], asset_manager)
        self.garlic_shot = None
        self.garlic_shot_start_time = 0
        self.garlic_shot_travel = 0
        self.vampire = Vampire(
            random.randint(0, WORLD_SIZE[0]), 
            random.randint(0, WORLD_SIZE[1]),
            asset_manager.images['vampire']
        )
        self.vampire.active = True
        self.bullets = []
        self.carrots = []
        self.explosions = []
        self.garlic_shots = []
        self.items = []
        self.garlic_shot = None
        self.garlic_shot_travel = 0
        self.garlic_shot_start_time = 0
        self.garlic_shot_speed = GARLIC_SHOT_SPEED
        self.garlic_shot_duration = GARLIC_SHOT_DURATION
        self.vampire_killed_count = 0  # Track vampires killed
        self.last_vampire_death_pos = (0, 0)  # Position tracking for item drops
        
        # Initialize carrots
        for _ in range(CARROT_COUNT):
            self.create_carrot(asset_manager)

    def reset(self):
        """Reset the game state to initial conditions"""
        self.scroll = [0, 0]
        self.game_over = False
        self.started = False
        
        # Completely reset all entity containers
        self.bullets = []
        self.explosions = []
        self.garlic_shots = []
        self.items = []
        self.carrots = []
        
        # Reset garlic shot state
        self.garlic_shot = None
        self.garlic_shot_travel = 0
        self.garlic_shot_start_time = 0
        
        # Reset entities
        if self.player:
            self.player.reset()
            # Clear any bullet rotation state
            if hasattr(self.player, 'bullet_rotation'):
                del self.player.bullet_rotation
        if self.vampire:
            self.vampire.respawn(
                random.randint(0, self.world_size[0] - self.vampire.rect.width),
                random.randint(0, self.world_size[1] - self.vampire.rect.height)
            )
        
        # Hard reset vampires
        if self.vampire:
            self.vampire.active = False
            self.vampire.death_effect_active = False
            self.vampire.respawn_timer = 0
            self.vampire.respawn(
                random.randint(0, self.world_size[0] - self.vampire.rect.width),
                random.randint(0, self.world_size[1] - self.vampire.rect.height)
            )
            
        # Recreate carrots with fresh instances
        self.carrots = []
        for _ in range(CARROT_COUNT):
            self.create_carrot(self.asset_manager) # Pass asset_manager

    def add_bullet(self, start_x, start_y, target_x, target_y, image):
        """Create and add a new bullet"""
        self.bullets.append(Bullet(start_x, start_y, target_x, target_y, image))

    def add_garlic_shot(self, start_x, start_y, target_x, target_y, image):
        """Create and add a new garlic shot"""
        self.garlic_shots.append(GarlicShot(start_x, start_y, target_x, target_y, image))

    def add_explosion(self, x, y, image):
        """Create and add a new explosion"""
        self.explosions.append(Explosion(x, y, image))

    def add_collectible(self, x, y, image, is_garlic=False):
        """Create and add a new collectible item"""
        self.items.append(Collectible(x, y, image, ITEM_SCALE))

    def create_carrot(self, asset_manager):
        """Create a new carrot away from the player"""
        while True:
            x = random.randint(0, self.world_size[0])
            y = random.randint(0, self.world_size[1])
            if not self.player or \
               ((x - self.player.rect.centerx)**2 + 
                (y - self.player.rect.centery)**2 > (min(self.world_size)/CARROT_SPAWN_SAFE_RATIO)**2):
                self.carrots.append(Carrot(x, y, asset_manager.images['carrot']))
                break

    def update(self, current_time):
        # Update player's invincibility state
        self.player.update_invincibility()

        # Update carrot logic
        for carrot in self.carrots:
            if carrot.active:
                # Calculate direction using vector and squared distance
                rabbit_center = pygame.math.Vector2(self.player.rect.center)
                carrot_center = pygame.math.Vector2(carrot.rect.center)
                direction = carrot_center - rabbit_center
                dist_sq = direction.length_squared()

                # Calculate speed multiplier using squared distance
                max_distance = CARROT_DETECTION_RADIUS
                if dist_sq > 0:
                    speed_multiplier = 1 + (max_distance - math.sqrt(dist_sq))/max_distance * (MAX_SPEED_MULTIPLIER - 1)
                    speed_multiplier = min(max(1, speed_multiplier), MAX_SPEED_MULTIPLIER)

                # Update movement vector
                if dist_sq < CARROT_CHASE_RADIUS_SQUARED:  # 100^2
                    if dist_sq > 0:
                        carrot.direction = direction.normalize()
                else:
                    # Add random wander and normalize once
                    carrot.direction += pygame.math.Vector2(random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))
                    if carrot.direction.length_squared() > 0:
                        carrot.direction.normalize_ip()

                # Apply movement
                movement = carrot.direction * carrot.speed * speed_multiplier
                carrot.rect.x += movement.x
                carrot.rect.y += movement.y

                # Keep within world bounds
                carrot.rect.x = max(0, min(self.world_size[0] - carrot.rect.width, carrot.rect.x))
                carrot.rect.y = max(0, min(self.world_size[1] - carrot.rect.height, carrot.rect.y))

        # Update bullets and handle collisions
        for bullet in self.bullets[:]:
            bullet.update()

            # Remove off-screen bullets
            if (bullet.rect.right < 0 or bullet.rect.left > self.world_size[0] or
                bullet.rect.bottom < 0 or bullet.rect.top > self.world_size[1]):
                self.bullets.remove(bullet)
                continue

            # Check collisions with carrots
            for carrot in self.carrots:
                if carrot.active and bullet.rect.colliderect(carrot.rect):
                    self.explosions.append(Explosion(
                        carrot.rect.centerx,
                        carrot.rect.centery,
                        self.asset_manager.images['explosion']
                    ))
                    carrot.active = False
                    carrot.respawn_timer = current_time
                    self.asset_manager.sounds['explosion'].play()
                    self.bullets.remove(bullet)
                    break

        # Respawn carrots after delay
        for carrot in self.carrots:
            if not carrot.active and current_time - carrot.respawn_timer > CARROT_RESPAWN_DELAY:
                carrot.respawn_timer = 0  # Reset timer
                carrot.respawn(self.world_size, self.player.rect)

        # Garlic shot logic
        if self.garlic_shot and self.garlic_shot["active"]:
            if self.garlic_shot_travel < GARLIC_SHOT_MAX_TRAVEL:
                # Update rotation angle each frame
                self.garlic_shot["rotation_angle"] = (self.garlic_shot["rotation_angle"] + GARLIC_SHOT_ROTATION_SPEED) % 360
                # Move in the pre-calculated direction
                self.garlic_shot["x"] += self.garlic_shot["dx"] * self.garlic_shot_speed
                self.garlic_shot["y"] += self.garlic_shot["dy"] * self.garlic_shot_speed
                self.garlic_shot_travel += self.garlic_shot_speed
            else:
                if current_time - self.garlic_shot_start_time > self.garlic_shot_duration:
                    self.garlic_shot["active"] = False
                    self.garlic_shot = None

            # Check for collision with vampire
            if self.garlic_shot and self.vampire.active:
                # Ensure garlic_width and garlic_height are accessible or defined
                # For now, assuming they are available as constants or attributes
                garlic_rect = pygame.Rect(self.garlic_shot["x"], self.garlic_shot["y"], GARLIC_WIDTH, GARLIC_HEIGHT) # Placeholder for actual width/height
                if garlic_rect.colliderect(self.vampire.rect):
                    self.vampire.death_effect_active = True
                    self.vampire.death_effect_start_time = current_time
                    self.vampire.active = False
                    self.vampire.respawn_timer = current_time
                    self.asset_manager.sounds['vampire_death'].play()
                    self.garlic_shot = None
                    self.vampire_killed_count += 1
                    self.last_vampire_death_pos = self.vampire.rect.center  # Store death position
                    print(f"[DEBUG] Vampire killed! Total: {self.vampire_killed_count}")  # Print once per kill

        # Update vampire
        self.vampire.update(self.player, self.world_size, current_time)

        # Handle finished death animations immediately
        if self.vampire.death_effect_active and \
           current_time - self.vampire.death_effect_start_time >= VAMPIRE_DEATH_DURATION:

            self.vampire.death_effect_active = False  # Clear flag immediately

            self.items.append(
                Collectible(
                    self.last_vampire_death_pos[0],
                    self.last_vampire_death_pos[1],
                    self.asset_manager.images['carrot_juice'],
                    'carrot_juice',
                    ITEM_SCALE
                )
            )

        # Check collision with player
        if self.vampire.active and self.player.rect.colliderect(self.vampire.rect):
            self.player.take_damage()
            self.vampire.active = False
            self.vampire.respawn_timer = current_time

        # Update and draw explosions
        for explosion in self.explosions[:]:
            if explosion.update(current_time):
                # Create collectible item
                is_garlic = random.random() < ITEM_DROP_GARLIC_CHANCE
                item_image = self.asset_manager.images['garlic'] if is_garlic else self.asset_manager.images['hp']
                self.items.append(
                    Collectible(
                        explosion.rect.centerx,
                        explosion.rect.centery,
                        item_image,
                        'garlic' if is_garlic else 'hp',
                        ITEM_SCALE
                    )
                )
                self.explosions.remove(explosion)
            # explosion.draw(screen, self.scroll) # Drawing will be handled in main.py

        # Check item collisions
        for item in self.items[:]:
            if self.player.rect.colliderect(item.rect):
                if item.item_type == 'hp' and self.player.health < MAX_HEALTH:
                    self.player.health += 1
                    self.asset_manager.sounds['get_hp'].play()
                elif item.item_type == 'garlic' and self.player.garlic_count < MAX_GARLIC:
                    self.player.garlic_count += 1
                    self.player.garlic_changed = True
                    self.asset_manager.sounds['get_garlic'].play()
                elif item.item_type == 'carrot_juice':
                    if not hasattr(self.player, 'carrot_juice_count'):
                        self.player.carrot_juice_count = 0
                    self.player.carrot_juice_count += 1
                    self.player.juice_changed = True
                    self.asset_manager.sounds['get_hp'].play()  # Reuse existing pickup sound
                self.items.remove(item)
