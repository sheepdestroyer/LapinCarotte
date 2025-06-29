import pytest
import pygame
from unittest.mock import MagicMock, patch

from config import START_HEALTH, MAX_HEALTH, PLAYER_INVINCIBILITY_DURATION
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
    mock_image = MagicMock(spec=pygame.Surface)
    mock_image.get_rect = MagicMock(return_value=pygame.Rect(0, 0, 32, 32))
    mock_image.copy = MagicMock(return_value=mock_image)
    manager.images = {
        'rabbit': mock_image,
        'carrot_juice': mock_image
    }
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
    return Player(100, 100, mock_asset_manager.images['rabbit'], mock_asset_manager)

class TestPlayer:
    def test_player_initialization(self, player_instance, mock_asset_manager):
        assert player_instance.rect.x == 100
        assert player_instance.rect.y == 100
        assert player_instance.health == START_HEALTH
        assert player_instance.max_health == MAX_HEALTH
        assert player_instance.garlic_count == 0
        assert not player_instance.invincible
        assert not player_instance.death_effect_active
        assert player_instance.asset_manager == mock_asset_manager
        assert player_instance.carrot_juice_count == 0

    def test_take_damage_reduces_health(self, player_instance, mock_asset_manager):
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
        for _ in range(START_HEALTH):
            player_instance.take_damage()
        assert player_instance.health == 0
        assert not player_instance.death_effect_active

    def test_update_invincibility(self, player_instance):
        with patch('time.time', return_value=100.0):
            player_instance.take_damage()
        assert player_instance.invincible
        with patch('time.time', return_value=100.0 + PLAYER_INVINCIBILITY_DURATION - 0.1):
            player_instance.update_invincibility()
        assert player_instance.invincible
        with patch('time.time', return_value=100.0 + PLAYER_INVINCIBILITY_DURATION):
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
```
