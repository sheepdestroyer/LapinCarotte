import pygame
import os
import sys
import logging # Import logging
from config import PLACEHOLDER_TEXT_COLOR, PLACEHOLDER_BG_COLOR, IMAGE_ASSET_CONFIG, SOUND_ASSET_CONFIG, DEFAULT_PLACEHOLDER_SIZE # Import new configs

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
    def __init__(self, cli_mode=False, _test_font_failure=False): # Add cli_mode and test hook
        logging.debug(f"AssetManager initializing. CLI mode: {cli_mode}, TestFontFailure: {_test_font_failure}")
        self.cli_mode = cli_mode
        self.images = {}
        self.sounds = {}
        self.placeholder_font = None

        if not self.cli_mode: # Only attempt font initialization if not in CLI mode
            if hasattr(pygame, 'font'):
                try:
                    if _test_font_failure: # Test hook
                        raise pygame.error("Test-induced font failure")
                    # Assuming pygame.font.init() is called in main.py after pygame.init()
                    if pygame.font.get_init(): # Check if font module is truly initialized
                        self.placeholder_font = pygame.font.SysFont(None, 20)
                        logging.debug("Placeholder font initialized successfully.")
                    else:
                        logging.warning("Pygame font module not initialized. Cannot create placeholder font.")
                except (pygame.error, AttributeError) as e:
                    logging.warning(f"Could not initialize font for asset placeholders: {e}")
            else:
                logging.warning("Pygame font module not available. Placeholders will not have text.")
        logging.debug(f"AssetManager initialized. Placeholder font: {self.placeholder_font}")
        
    def load_assets(self):
        logging.debug("AssetManager.load_assets called.")
        # Image loading using IMAGE_ASSET_CONFIG
        for key, config_entry in IMAGE_ASSET_CONFIG.items():
            logging.debug(f"Attempting to load image asset '{key}' with config: {config_entry}")
            path = config_entry['path']
            size_hint = config_entry.get('size')

            if self.cli_mode:
                # In CLI mode, store metadata or None. For now, just path and size hint.
                self.images[key] = {'path': path, 'size_hint': size_hint, 'type': 'cli_placeholder'}
                logging.debug(f"CLI mode: Stored metadata for image '{key}'.")
                # No actual image loading or Pygame surface creation
            else: # GUI mode
                try:
                    image_path = self._get_path(path)
                    logging.debug(f"GUI mode: Loading image '{key}' from resolved path '{image_path}'.")
                    self.images[key] = pygame.image.load(image_path).convert_alpha()
                    logging.debug(f"Successfully loaded image asset '{key}'.")
                except (pygame.error, FileNotFoundError) as e:
                    logging.warning(f"Could not load image asset '{key}' from '{path}': {e}. Creating placeholder.")
                    logging.debug(f"Entering placeholder creation logic for image '{key}'.")
                    placeholder_size = size_hint if size_hint else DEFAULT_PLACEHOLDER_SIZE
                    placeholder_surface = pygame.Surface(placeholder_size)
                    placeholder_surface.fill(PLACEHOLDER_BG_COLOR)

                    if self.placeholder_font:
                        try:
                            text_surface = self.placeholder_font.render(key, True, PLACEHOLDER_TEXT_COLOR)
                            text_rect = text_surface.get_rect(center=(placeholder_surface.get_width() // 2, placeholder_surface.get_height() // 2))
                            placeholder_surface.blit(text_surface, text_rect)
                        except pygame.error as font_e:
                            logging.warning(f"Could not render text on placeholder for '{key}': {font_e}")
                    else:
                        logging.warning(f"Placeholder font not available for asset '{key}'. Placeholder will be a plain blue rectangle.")

                    self.images[key] = placeholder_surface.convert_alpha()
            
        # Sound loading using SOUND_ASSET_CONFIG
        for key, path in SOUND_ASSET_CONFIG.items():
            logging.debug(f"Attempting to load sound asset '{key}' from path '{path}'.")
            if self.cli_mode or not (hasattr(pygame, 'mixer') and pygame.mixer.get_init()):
                # If in CLI mode, or if mixer is not initialized (e.g. no sound card or init failed)
                if not self.cli_mode: # Only log this specific warning if not in CLI (CLI implies no sound hardware focus)
                    logging.warning(f"Pygame mixer not initialized. Using dummy sound for '{key}'.")
                else:
                    logging.debug(f"CLI mode or mixer not init: Using DummySound for '{key}'.")
                self.sounds[key] = DummySound()
            else: # GUI mode with mixer initialized
                try:
                    sound_file_path = self._get_path(path)
                    logging.debug(f"GUI mode: Loading sound '{key}' from resolved path '{sound_file_path}'.")
                    self.sounds[key] = pygame.mixer.Sound(sound_file_path)
                    logging.debug(f"Successfully loaded sound asset '{key}'.")
                except pygame.error as e:
                    logging.warning(f"Could not load sound asset '{key}' from '{path}': {e}. Using dummy sound.")
                    self.sounds[key] = DummySound() # Moved inside the except block
        logging.debug("AssetManager.load_assets finished.")
    
    def _get_path(self, relative_path):
        logging.debug(f"AssetManager._get_path called with relative_path: '{relative_path}'.")
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, 'Assets', relative_path)
