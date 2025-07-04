import pygame
import os
import sys

# It's good practice to initialize pygame.font if you're going to use it.
# This should ideally be done once at the start of the game (e.g., in main.py after pygame.init()).
# However, for AssetManager to be self-contained in creating fallback surfaces,
# we might ensure font is initialized here or rely on main.py having done it.
# For now, let's assume main.py handles pygame.init() and pygame.font.init().
# If not, AssetManager might need its own pygame.font.init() call,
# or font creation might fail.

class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        # Attempt to create a default font for placeholders
        self.placeholder_font = None # Initialize to None
        if hasattr(pygame, 'font'):
            try:
                if not pygame.font.get_init(): # Check if font module is initialized
                    pygame.font.init()
                self.placeholder_font = pygame.font.SysFont(None, 20) # Use default system font, size 20
            except Exception as e:
                print(f"WARNING: Could not initialize font for asset placeholders: {e}")
        else:
            print("WARNING: Pygame font module not available. Placeholders will not have text.")
        
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
            'continue_button': 'images/continue_button.png', # New
            'settings_button': 'images/settings_button.png', # New
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
            try:
                image_path = self._get_path(path)
                self.images[key] = pygame.image.load(image_path).convert_alpha()
            except (pygame.error, FileNotFoundError) as e:
                print(f"WARNING: Could not load image asset '{key}' from '{path}': {e}. Creating placeholder.")
                placeholder_surface = pygame.Surface((100, 50)) # Default size e.g. 100x50
                placeholder_surface.fill((0, 0, 255)) # Blue color for placeholder

                # Temporarily disable text rendering for debugging the KeyError
                # if self.placeholder_font:
                #     try:
                #         text_surface = self.placeholder_font.render(key, True, (255, 255, 255)) # White text
                #         text_rect = text_surface.get_rect(center=(placeholder_surface.get_width() // 2, placeholder_surface.get_height() // 2))
                #         placeholder_surface.blit(text_surface, text_rect)
                #     except Exception as font_e:
                #         print(f"WARNING: Could not render text on placeholder for '{key}': {font_e}")
                # else:
                #     print(f"WARNING: Placeholder font not available for asset '{key}'. Placeholder will be a plain blue rectangle.")

                self.images[key] = placeholder_surface.convert_alpha()
                print(f"DEBUG: Placeholder for '{key}' assigned in self.images. Type: {type(self.images[key])}")
                print(f"DEBUG: Keys in self.images after trying to set '{key}': {list(self.images.keys())}")
            
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
            try:
                sound_file_path = self._get_path(path)
                self.sounds[key] = pygame.mixer.Sound(sound_file_path)
            except pygame.error as e:
                print(f"WARNING: Could not load sound asset '{key}' from '{path}': {e}. Sound will be missing.")
                # Optionally, assign a dummy/silent sound object if the game code expects a Sound object
                # For now, just skipping and it will be missing from self.sounds if load fails
    
    def _get_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, 'Assets', relative_path)
