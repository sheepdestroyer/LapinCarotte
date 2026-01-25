import time  # Import time for patching
from unittest.mock import MagicMock, patch

import pygame
import pytest

from config import (
    MAX_GARLIC,
    MAX_HEALTH,
    PLAYER_INVINCIBILITY_DURATION,
    PLAYER_SPEED,
    START_HEALTH,
)
from game_entities import Player

# Import fixtures from the common utility file
from .test_utils import (
    initialized_pygame,
    mock_asset_manager,
    mock_pygame_init_and_display,
    real_surface_factory,
)

# The mock_pygame_init_and_display fixture is already autouse=True in test_utils.py
# So, we don't need mock_pygame_display_and_font here anymore.


@pytest.fixture
def player_instance(
    mock_asset_manager, real_surface_factory
):  # Use real_surface_factory
    # Use the factory to create a real surface for the player
    # This surface will be used as player.original_image and player.image
    player_image = real_surface_factory(32, 32)  # Standard player image size

    # The mock_asset_manager from test_utils already provides a mock 'rabbit' image.
    # If a real surface is strictly needed for player.original_image for some specific tests (e.g. flip),
    # we can either:
    # 1. Pass player_image directly to Player constructor, and it will be copied.
    # 2. Or, ensure the mock_asset_manager's 'rabbit' image is this real_surface if Player always gets its image from there.

    # For simplicity and consistency with how Player gets its image, let's assume
    # Player is initialized with an image directly, not by fetching from asset_manager by key.
    # The game_entities.Player constructor takes 'image' as an argument.
    player = Player(100, 100, player_image, mock_asset_manager)
    return player


class TestPlayer:
    def test_player_initialization(
        self, player_instance, mock_asset_manager
    ):  # mock_asset_manager is still needed
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
        player_instance.invincible = (
            False  # Ensure player is not invincible at start of test
        )
        initial_health = player_instance.health
        with patch("time.time", return_value=123.456):
            player_instance.take_damage()
        assert player_instance.health == initial_health - 1
        assert player_instance.invincible
        assert player_instance.last_hit_time == 123.456
        mock_asset_manager.sounds["hurt"].play.assert_called_once()
        assert player_instance.health_changed

    def test_take_damage_when_invincible(self, player_instance, mock_asset_manager):
        player_instance.invincible = True
        initial_health = player_instance.health
        player_instance.take_damage()
        assert player_instance.health == initial_health
        mock_asset_manager.sounds["hurt"].play.assert_not_called()

    def test_take_damage_when_death_effect_active(
        self, player_instance, mock_asset_manager
    ):
        player_instance.death_effect_active = True
        initial_health = player_instance.health
        player_instance.take_damage()
        assert player_instance.health == initial_health
        mock_asset_manager.sounds["hurt"].play.assert_not_called()

    def test_take_damage_until_death_effect_not_triggered_by_take_damage(
        self, player_instance
    ):
        player_instance.invincible = False  # Ensure player is not invincible at start
        current_mock_time = 100.0
        for i in range(START_HEALTH):
            with patch("time.time", return_value=current_mock_time):
                player_instance.take_damage()
                # If health became 0, break, no need to check invincibility update then.
                if (
                    player_instance.health == 0 and i == START_HEALTH - 1
                ):  # only break if it's the last expected hit
                    break
            # Simulate time passing for invincibility to wear off before next hit
            current_mock_time += PLAYER_INVINCIBILITY_DURATION + 0.1
            with patch("time.time", return_value=current_mock_time):
                player_instance.update_invincibility()

        assert player_instance.health == 0
        assert not player_instance.death_effect_active

    def test_update_invincibility(self, player_instance):
        # Ensure player is not invincible before taking damage
        player_instance.invincible = False
        player_instance.last_hit_time = 0

        with patch("time.time", return_value=100.0) as mock_time_damage:
            player_instance.take_damage()
        assert player_instance.invincible
        assert player_instance.last_hit_time == 100.0

        # Check still invincible just before duration ends
        with patch(
            "time.time", return_value=100.0 + PLAYER_INVINCIBILITY_DURATION - 0.01
        ) as mock_time_update_1:
            player_instance.update_invincibility()
        assert player_instance.invincible

        # Check becomes vincible exactly when duration ends
        with patch(
            "time.time", return_value=100.0 + PLAYER_INVINCIBILITY_DURATION
        ) as mock_time_update_2:
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
        assert (
            player_instance.image == player_instance.original_image
        )  # Check if image is reset
        assert not player_instance.flipped  # Check if flipped status is reset

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
        assert player_instance.rect.x == world_size[0] - \
            player_instance.rect.width
        assert player_instance.rect.y == world_size[1] - \
            player_instance.rect.height

    def test_draw_ui_calls(self, player_instance, mocker):
        mock_screen = MagicMock(spec=pygame.Surface)
        mock_hp_image = MagicMock(spec=pygame.Surface)
        mock_garlic_image = MagicMock(spec=pygame.Surface)
        mock_hp_image.get_width = MagicMock(return_value=30)
        mock_garlic_image.get_width = MagicMock(return_value=30)
        mock_carrot_juice_icon = MagicMock(spec=pygame.Surface)
        player_instance.asset_manager.images["carrot_juice"] = mock_carrot_juice_icon
        mock_scaled_icon = MagicMock(spec=pygame.Surface)
        mock_scaled_icon.get_width = MagicMock(return_value=16)
        mocker.patch("pygame.transform.scale", return_value=mock_scaled_icon)
        player_instance.health = 2
        player_instance.garlic_count = 1
        player_instance.carrot_juice_count = 5
        player_instance.draw_ui(
            mock_screen, mock_hp_image, mock_garlic_image, MAX_GARLIC
        )
        assert mock_screen.blit.call_count >= 5
