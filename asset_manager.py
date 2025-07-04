import pygame
import os
import sys
from config import PLACEHOLDER_TEXT_COLOR, IMAGE_ASSET_CONFIG, SOUND_ASSET_CONFIG, DEFAULT_PLACEHOLDER_SIZE # Import new configs

# It's good practice to initialize pygame.font if you're going to use it.
# This should ideally be done once at the start of the game (e.g., in main.py after pygame.init()).
# However, for AssetManager to be self-contained in creating fallback surfaces,
# we might ensure font is initialized here or rely on main.py having done it.
# For now, let's assume main.py handles pygame.init() and pygame.font.init().
# If not, AssetManager might need its own pygame.font.init() call,
# or font creation might fail.

class DummySound:
    """A dummy sound object with a no-op play method."""
    def play(self, *args, **kwargs):
        pass # Does nothing

    def stop(self, *args, **kwargs):
        pass # Does nothing

    def fadeout(self, *args, **kwargs):
        pass # Does nothing

    def set_volume(self, *args, **kwargs):
        pass # Does nothing

    def get_volume(self, *args, **kwargs):
        return 0.0 # Return a default volume

    def get_length(self, *args, **kwargs):
        return 0.0 # Return a default length

    # Add any other methods that might be called on a Sound object to prevent AttributeErrors
    # For now, play() is the most critical.

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
            except (pygame.error, AttributeError) as e: # More specific exceptions
                print(f"WARNING: Could not initialize font for asset placeholders: {e}")
        else:
            print("WARNING: Pygame font module not available. Placeholders will not have text.")
        
    def load_assets(self):
        # Image loading using IMAGE_ASSET_CONFIG
        for key, config_entry in IMAGE_ASSET_CONFIG.items():
            path = config_entry['path']
            size_hint = config_entry.get('size') # Get optional size hint

            try:
                image_path = self._get_path(path)
                self.images[key] = pygame.image.load(image_path).convert_alpha()
            except (pygame.error, FileNotFoundError) as e:
                print(f"WARNING: Could not load image asset '{key}' from '{path}': {e}. Creating placeholder.")

                placeholder_size = size_hint if size_hint else DEFAULT_PLACEHOLDER_SIZE
                placeholder_surface = pygame.Surface(placeholder_size)
                placeholder_surface.fill((0, 0, 255)) # Blue color for placeholder (can be made configurable too)

                if self.placeholder_font:
                    try:
                        text_surface = self.placeholder_font.render(key, True, PLACEHOLDER_TEXT_COLOR)
                        text_rect = text_surface.get_rect(center=(placeholder_surface.get_width() // 2, placeholder_surface.get_height() // 2))
                        placeholder_surface.blit(text_surface, text_rect)
                    except pygame.error as font_e:
                        print(f"WARNING: Could not render text on placeholder for '{key}': {font_e}")
                else:
                    print(f"WARNING: Placeholder font not available for asset '{key}'. Placeholder will be a plain blue rectangle.")

                self.images[key] = placeholder_surface.convert_alpha()
            
        # Sound loading using SOUND_ASSET_CONFIG
        for key, path in SOUND_ASSET_CONFIG.items():
            try:
                sound_file_path = self._get_path(path)
                self.sounds[key] = pygame.mixer.Sound(sound_file_path)
            except pygame.error as e:
                print(f"WARNING: Could not load sound asset '{key}' from '{path}': {e}. Using dummy sound.")
                self.sounds[key] = DummySound()
    
    def _get_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, 'Assets', relative_path)
