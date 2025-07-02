import pytest
import pygame
from unittest.mock import MagicMock

@pytest.fixture
def mock_asset_manager():
    manager = MagicMock()

    # Configure mock_image to behave more like a real Surface for get_rect
    def mock_get_rect(**kwargs):
        # Default size, can be overridden by specific tests if needed
        width = kwargs.pop('width', 32)
        height = kwargs.pop('height', 32)

        if 'topleft' in kwargs:
            return pygame.Rect(kwargs['topleft'], (width, height))
        elif 'center' in kwargs:
            # Adjust for center: rect.center = new_center means rect.x = new_center_x - rect.width/2
            return pygame.Rect((kwargs['center'][0] - width // 2, kwargs['center'][1] - height // 2), (width, height))
        return pygame.Rect(0, 0, width, height)

    def create_mock_surface(width=32, height=32):
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.get_rect = MagicMock(side_effect=lambda **kwargs: mock_get_rect(width=width, height=height, **kwargs))
        mock_surface.copy = MagicMock(return_value=mock_surface)
        mock_surface.convert_alpha = MagicMock(return_value=mock_surface)
        mock_surface.get_width = MagicMock(return_value=width)
        mock_surface.get_height = MagicMock(return_value=height)
        mock_surface.fill = MagicMock() # Mock fill method
        return mock_surface

    # Common images
    manager.images = {
        'rabbit': create_mock_surface(32, 32), # Player
        'carrot': create_mock_surface(20, 20), # Carrot
        'vampire': create_mock_surface(40, 40), # Vampire
        'bullet': create_mock_surface(10, 10), # Bullet
        'garlic': create_mock_surface(15, 15), # Garlic item / shot
        'hp': create_mock_surface(15, 15), # HP item
        'explosion': create_mock_surface(50, 50), # Explosion
        'carrot_juice': create_mock_surface(20, 20), # Carrot juice item
        'continue': create_mock_surface(200, 50), # Placeholder for continue_button
        'settings': create_mock_surface(200, 50), # Placeholder for settings_button
    }

    # Digit images for UI
    for i in range(10):
        manager.images[f'digit_{i}'] = create_mock_surface(10, 15) # Example digit size

    # Common sounds
    mock_sound = MagicMock(spec=pygame.mixer.Sound) # Use spec for better mocking
    mock_sound.play = MagicMock()
    manager.sounds = {
        'hurt': mock_sound,
        'get_hp': mock_sound,
        'get_garlic': mock_sound,
        'explosion': mock_sound,
        'vampire_death': mock_sound,
        'shoot': mock_sound, # Assuming a general shoot sound
    }
    return manager

@pytest.fixture(autouse=True)
def mock_pygame_init_and_display(mocker):
    """Mocks essential pygame initializations and display functions."""
    if not pygame.get_init():
        pygame.init() # Ensure pygame is initialized for Surface creation, etc.

    mocker.patch('pygame.display.set_mode', return_value=MagicMock(spec=pygame.Surface))
    mocker.patch('pygame.display.get_surface', return_value=MagicMock(spec=pygame.Surface))

    # Mock font rendering
    mock_font_render_surface = MagicMock(spec=pygame.Surface)
    mock_font_render_surface.get_rect = MagicMock(return_value=pygame.Rect(0,0,50,20))
    mock_font_instance = MagicMock()
    mock_font_instance.render = MagicMock(return_value=mock_font_render_surface)
    mocker.patch('pygame.font.Font', return_value=mock_font_instance)

    # Mock time functions
    mocker.patch('pygame.time.get_ticks', return_value=0) # Start ticks at 0
    mocker.patch('pygame.time.set_timer', return_value=None)
    # time.time is often used, mock it as well if needed globally, or per test with patch
    # For now, let's assume tests will patch time.time specifically when needed for fine-grained control.

@pytest.fixture
def initialized_pygame():
    """Ensure Pygame is initialized for tests that need it (e.g., creating real Surfaces)."""
    if not pygame.get_init():
        pygame.init()
    # Potentially mock display parts if they interfere and aren't covered by mock_pygame_init_and_display
    if not pygame.display.get_init():
         pygame.display.init()
         pygame.display.set_mode((1,1)) # Minimal display
    return pygame

@pytest.fixture
def real_surface_factory(initialized_pygame):
    """A factory to create real pygame.Surface instances for testing."""
    def _create_surface(width, height, fill_color=(255,0,0)):
        surface = pygame.Surface((width, height))
        surface.fill(fill_color)
        return surface
    return _create_surface

# It might be beneficial to also have fixtures for creating specific game entity instances
# For example:
# from game_entities import Player # Assuming top-level import works after project structure adjustment
# from config import START_HEALTH, MAX_HEALTH, PLAYER_SPEED

# @pytest.fixture
# def player_instance(mock_asset_manager, real_surface_factory):
#     player_image = real_surface_factory(32,32)
#     player = Player(100, 100, player_image, mock_asset_manager)
#     return player

# This can be expanded as we develop tests for each entity.
# For now, the mock_asset_manager and pygame mocks are the most crucial common utilities.

# If AGENTS.md instructs to run `pip install -r requirements_dev.txt`
# and that includes `pygame-ce`, then `pygame` should be importable.
# Otherwise, ensure pygame is installed or handle potential import errors.
# For now, assuming pygame is available in the test environment.

print("Common test utilities (test_utils.py) created/updated.")
