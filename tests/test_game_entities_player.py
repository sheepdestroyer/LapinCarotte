import pytest
import pygame
from unittest.mock import MagicMock, patch

from config import START_HEALTH, MAX_HEALTH, PLAYER_INVINCIBILITY_DURATION, MAX_GARLIC, PLAYER_SPEED
from game_entities import Player

@pytest.fixture(autouse=True)
def mock_pygame_display_and_font(mocker):
    mocker.patch('pygame.display.set_mode', return_value=MagicMock())
    mocker.patch('pygame.display.get_surface', return_value=MagicMock())
    mock_font_render = MagicMock(return_value=MagicMock(get_rect=MagicMock(return_value=pygame.Rect(0,0,50,20))))
    mocker.patch('pygame.font.Font', return_value=MagicMock(render=mock_font_render))

@pytest.fixture
def mock_asset_manager():
    manager = MagicMock()

    # Configure mock_image to behave more like a real Surface for get_rect
    def mock_get_rect(**kwargs):
        if 'topleft' in kwargs:
            return pygame.Rect(kwargs['topleft'], (32, 32))
        elif 'center' in kwargs:
            return pygame.Rect((0,0), (32,32)).move(kwargs['center'][0] - 16, kwargs['center'][1] - 16) # adjust for center
        return pygame.Rect(0, 0, 32, 32)

    mock_image = MagicMock(spec=pygame.Surface)
    mock_image.get_rect = MagicMock(side_effect=mock_get_rect)
    mock_image.copy = MagicMock(return_value=mock_image) # For Player.reset
    mock_image.convert_alpha = MagicMock(return_value=mock_image) # If used

    # Mock for digit images
    mock_digit_image = MagicMock(spec=pygame.Surface)
    mock_digit_image.get_width = MagicMock(return_value=10) # Example width
    mock_digit_image.get_height = MagicMock(return_value=10) # Example height

    manager.images = {
        'rabbit': mock_image,
        'carrot_juice': mock_image,
    }
    # Add digit images to the mock asset manager
    for i in range(10):
        manager.images[f'digit_{i}'] = mock_digit_image

    mock_sound = MagicMock()
    mock_sound.play = MagicMock()
    manager.sounds = {
        'hurt': mock_sound,
        'get_hp': mock_sound,
        'get_garlic': mock_sound,
    }
    return manager

@pytest.fixture
def player_instance(mock_asset_manager):
    # Create a real minimal surface for testing flip
    # Pygame needs to be initialized for Surface, but display isn't strictly needed for just Surface objects
    if not pygame.get_init(): # Initialize pygame if not already (e.g. by display mock)
        pygame.init()

    real_surface = pygame.Surface((32, 32))
    real_surface.fill((255, 0, 0)) # Fill with a color to make it a valid surface

    # Replace the mocked 'rabbit' image in the asset manager for this player instance
    # OR, more directly, pass this real_surface to Player constructor if asset_manager isn't used for player.image
    mock_asset_manager.images['rabbit'] = real_surface

    player = Player(100, 100, real_surface, mock_asset_manager)
    # Player class copies the passed image to self.original_image and self.image
    # So, player.original_image and player.image should be this real_surface

    # If the Player class makes its own .copy() of the image internally for original_image,
    # ensure that copy also works. The real Surface.copy() will work.
    return player

class TestPlayer:
    def test_player_initialization(self, player_instance, mock_asset_manager):
        assert player_instance.rect.x == 100
        assert player_instance.rect.y == 100
        assert player_instance.health == START_HEALTH
        assert player_instance.max_health == MAX_HEALTH
        assert player_instance.garlic_count == 0
        assert not player_instance.invincible
        assert player_instance.speed == PLAYER_SPEED
        assert not player_instance.death_effect_active
        assert player_instance.asset_manager == mock_asset_manager
        assert player_instance.carrot_juice_count == 0

    def test_take_damage_reduces_health(self, player_instance, mock_asset_manager):
        player_instance.invincible = False # Ensure player is not invincible at start of test
        initial_health = player_instance.health
        with patch('time.time', return_value=123.456):
            player_instance.take_damage()
        assert player_instance.health == initial_health - 1
        assert player_instance.invincible
        assert player_instance.last_hit_time == 123.456
        mock_asset_manager.sounds['hurt'].play.assert_called_once()
        assert player_instance.health_changed

    def test_take_damage_when_invincible(self, player_instance, mock_asset_manager):
        player_instance.invincible = True
        initial_health = player_instance.health
        player_instance.take_damage()
        assert player_instance.health == initial_health
        mock_asset_manager.sounds['hurt'].play.assert_not_called()

    def test_take_damage_when_death_effect_active(self, player_instance, mock_asset_manager):
        player_instance.death_effect_active = True
        initial_health = player_instance.health
        player_instance.take_damage()
        assert player_instance.health == initial_health
        mock_asset_manager.sounds['hurt'].play.assert_not_called()

    def test_take_damage_until_death_effect_not_triggered_by_take_damage(self, player_instance):
        player_instance.invincible = False # Ensure player is not invincible at start
        current_mock_time = 100.0
        for i in range(START_HEALTH):
            with patch('time.time', return_value=current_mock_time):
                player_instance.take_damage()
                # If health became 0, break, no need to check invincibility update then.
                if player_instance.health == 0 and i == START_HEALTH -1: # only break if it's the last expected hit
                    break
            # Simulate time passing for invincibility to wear off before next hit
            current_mock_time += PLAYER_INVINCIBILITY_DURATION + 0.1
            with patch('time.time', return_value=current_mock_time):
                player_instance.update_invincibility()

        assert player_instance.health == 0
        assert not player_instance.death_effect_active

    def test_update_invincibility(self, player_instance):
        # Ensure player is not invincible before taking damage
        player_instance.invincible = False
        player_instance.last_hit_time = 0

        with patch('time.time', return_value=100.0) as mock_time_damage:
            player_instance.take_damage()
        assert player_instance.invincible
        assert player_instance.last_hit_time == 100.0

        # Check still invincible just before duration ends
        with patch('time.time', return_value=100.0 + PLAYER_INVINCIBILITY_DURATION - 0.01) as mock_time_update_1:
            player_instance.update_invincibility()
        assert player_instance.invincible

        # Check becomes vincible exactly when duration ends
        with patch('time.time', return_value=100.0 + PLAYER_INVINCIBILITY_DURATION) as mock_time_update_2:
            player_instance.update_invincibility()
        assert not player_instance.invincible

    def test_reset_player(self, player_instance, mock_asset_manager):
        player_instance.health = 0
        player_instance.garlic_count = 2
        player_instance.invincible = True
        player_instance.death_effect_active = True
        player_instance.carrot_juice_count = 5
        player_instance.rect.x = 50
        player_instance.rect.y = 50
        player_instance.reset()
        assert player_instance.health == START_HEALTH
        assert player_instance.garlic_count == 0
        assert player_instance.carrot_juice_count == 0
        assert not player_instance.invincible
        assert not player_instance.death_effect_active
        assert player_instance.rect.x == player_instance.initial_x
        assert player_instance.rect.y == player_instance.initial_y
        assert player_instance.asset_manager == mock_asset_manager
        assert player_instance.image == player_instance.original_image # Check if image is reset
        assert not player_instance.flipped # Check if flipped status is reset

    def test_move_player(self, player_instance):
        initial_x, initial_y = player_instance.rect.x, player_instance.rect.y
        world_size = (1000, 1000)
        player_instance.move(1, 1, world_size)
        assert player_instance.rect.x == initial_x + player_instance.speed
        assert player_instance.rect.y == initial_y + player_instance.speed
        player_instance.move(-1, -1, world_size)
        assert player_instance.rect.x == initial_x
        assert player_instance.rect.y == initial_y

    def test_move_player_boundary_conditions(self, player_instance):
        world_size = (200, 200)
        player_instance.rect.x = 0
        player_instance.rect.y = 0
        player_instance.move(-1, -1, world_size)
        assert player_instance.rect.x == 0
        assert player_instance.rect.y == 0
        player_instance.rect.x = world_size[0] - player_instance.rect.width
        player_instance.rect.y = world_size[1] - player_instance.rect.height
        player_instance.move(1, 1, world_size)
        assert player_instance.rect.x == world_size[0] - player_instance.rect.width
        assert player_instance.rect.y == world_size[1] - player_instance.rect.height

    def test_draw_ui_calls(self, player_instance, mocker):
        mock_screen = MagicMock(spec=pygame.Surface)
        mock_hp_image = MagicMock(spec=pygame.Surface)
        mock_garlic_image = MagicMock(spec=pygame.Surface)
        mock_hp_image.get_width = MagicMock(return_value=30)
        mock_garlic_image.get_width = MagicMock(return_value=30)
        mock_carrot_juice_icon = MagicMock(spec=pygame.Surface)
        player_instance.asset_manager.images['carrot_juice'] = mock_carrot_juice_icon
        mock_scaled_icon = MagicMock(spec=pygame.Surface)
        mock_scaled_icon.get_width = MagicMock(return_value=16)
        mocker.patch('pygame.transform.scale', return_value=mock_scaled_icon)
        player_instance.health = 2
        player_instance.garlic_count = 1
        player_instance.carrot_juice_count = 5
        player_instance.draw_ui(mock_screen, mock_hp_image, mock_garlic_image, MAX_GARLIC)
        assert mock_screen.blit.call_count >= 5
