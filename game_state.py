class GameState:
    def __init__(self):
        self.scroll = [0, 0]
        self.world_size = (3000, 3000)
        self.game_over = False
        self.started = False
        self.vampire_active = False
        self.vampire_position = (0, 0)
        self.bullets = []
        self.carrots = []
        self.hp_items = []
        self.garlic_items = []
