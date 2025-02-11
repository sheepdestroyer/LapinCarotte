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
            'grass': 'images/grass.png',
            'carrot': 'images/carrot.png',
            'rabbit': 'images/rabbit.png',
            'bullet': 'images/bullet.png',
            'explosion': 'images/explosion.png',
            'vampire': 'images/vampire.png',
            'hp': 'images/HP.png',
            'icon': 'images/HP.png',
            'garlic': 'images/garlic.png',
            'game_over': 'images/GameOver.png',
            'restart': 'images/restart.png',
            'exit': 'images/exit.png',
            'start': 'images/start.png',
            'start_screen': 'images/start_screen_final.png',
            'carrot_juice': 'images/carrot_juice.png',
            'crosshair': 'images/crosshair_1.png',
            'digit_0': 'fonts/0.png',
            'digit_1': 'fonts/1.png',
            'digit_2': 'fonts/2.png',
            'digit_3': 'fonts/3.png',
            'digit_4': 'fonts/4.png',
            'digit_5': 'fonts/5.png',
            'digit_6': 'fonts/6.png',
            'digit_7': 'fonts/7.png',
            'digit_8': 'fonts/8.png',
            'digit_9': 'fonts/9.png'
        }
        
        for key, path in assets.items():
            self.images[key] = pygame.image.load(self._get_path(path)).convert_alpha()
            
        # Sound loading
        sound_assets = {
            'explosion': 'sounds/explosion.mp3',
            'press_start': 'sounds/press_start.mp3',
            'hurt': 'sounds/hurt.mp3',
            'get_hp': 'sounds/item_hp.mp3',
            'get_garlic': 'sounds/item_garlic.mp3',
            'death': 'sounds/death.mp3',
            'vampire_death': 'sounds/VampireDeath.mp3'
        }
        
        for key, path in sound_assets.items():
            self.sounds[key] = pygame.mixer.Sound(self._get_path(path))
    
    def _get_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, 'Assets', relative_path)
