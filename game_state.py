import random
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
            self.create_carrot()

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
