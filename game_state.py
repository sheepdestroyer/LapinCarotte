from game_entities import Carrot, Vampire, Player
import random
from config import WORLD_SIZE, CARROT_COUNT

class GameState:
    def __init__(self):
        self.scroll = [0, 0]
        self.world_size = WORLD_SIZE
        self.game_over = False
        self.started = False
        self.vampire = None
        self.player = None
        self.bullets = []
        self.carrots = []
        self.explosions = []
        self.garlic_shots = []
        self.items = []

    def reset(self):
        """Reset the game state to initial conditions"""
        self.scroll = [0, 0]
        self.game_over = False
        self.started = False
        self.bullets.clear()
        self.explosions.clear()
        self.garlic_shots.clear()
        self.items.clear()
        
        # Reset entities
        if self.player:
            self.player.reset()
        if self.vampire:
            self.vampire.respawn(
                random.randint(0, self.world_size[0] - self.vampire.rect.width),
                random.randint(0, self.world_size[1] - self.vampire.rect.height)
            )
        
        # Recreate carrots
        self.carrots = []
        for _ in range(CARROT_COUNT):
            self.create_carrot()

    def create_carrot(self, asset_manager):
        """Create a new carrot away from the player"""
        while True:
            x = random.randint(0, self.world_size[0])
            y = random.randint(0, self.world_size[1])
            if not self.player or \
               ((x - self.player.rect.centerx)**2 + 
                (y - self.player.rect.centery)**2 > (min(self.world_size)/3)**2):
                self.carrots.append(Carrot(x, y, asset_manager.images['carrot']))
                break
