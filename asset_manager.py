import pygame
import os
import sys

class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        
    def load_assets(self):
        # Image loading
        assets = {
            'grass': 'grass.png',
            'carrot': 'carrot.png',
            'rabbit': 'rabbit.png',
            'bullet': 'bullet.png',
            'explosion': 'explosion.png',
            'vampire': 'vampire.png',
            'hp': 'HP.png',
            'icon': 'HP.png',  # Use PNG format for pygame icon
            'garlic': 'garlic.png',
            'game_over': 'GameOver.png',
            'restart': 'restart.png',
            'exit': 'exit.png',
            'start': 'start.png',
            'start_screen': 'start_screen_final.png'
        }
        
        for key, path in assets.items():
            self.images[key] = pygame.image.load(self._get_path(path)).convert_alpha()
            
        # Sound loading
        sound_assets = {
            'explosion': 'explosion.mp3',
            'press_start': 'press_start.mp3',
            'hurt': 'hurt.mp3',
            'get_hp': 'item_hp.mp3',
            'get_garlic': 'item_garlic.mp3',
            'death': 'death.mp3',
            'vampire_death': 'VampireDeath.mp3'
        }
        
        for key, path in sound_assets.items():
            self.sounds[key] = pygame.mixer.Sound(self._get_path(path))
    
    def _get_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, 'Assets', relative_path)
