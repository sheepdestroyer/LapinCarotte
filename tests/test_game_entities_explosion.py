import time  # For time.time mocking
from unittest.mock import MagicMock, patch

import pygame
import pytest

from config import EXPLOSION_FLASH_INTERVAL, EXPLOSION_MAX_FLASHES
from game_entities import Explosion

from .test_utils import (
    initialized_pygame,
    mock_asset_manager,
    mock_pygame_init_and_display,
    real_surface_factory,
)


@pytest.fixture
def explosion_image(real_surface_factory):
    # Explosion image from mock_asset_manager in test_utils is 50x50
    return real_surface_factory(50, 50)


@pytest.fixture
@patch(
    "time.time", MagicMock(return_value=100.0)
)  # Mock time.time for consistent start_time
def explosion_instance(explosion_image):
    return Explosion(200, 250, explosion_image)


class TestExplosionInitialization:
    def test_initial_values(self, explosion_instance, explosion_image):
        assert explosion_instance.image is explosion_image
        assert explosion_instance.rect.center == (200, 250)
        assert explosion_instance.start_time == 100.0  # From mocked time.time()
        assert explosion_instance.flash_count == 0
        assert explosion_instance.max_flashes == EXPLOSION_MAX_FLASHES
        assert explosion_instance.flash_interval == EXPLOSION_FLASH_INTERVAL
        assert explosion_instance.active is True


class TestExplosionUpdate:
    def test_update_flash_logic_and_completion(self, explosion_instance):
        # Initial state: start_time = 100.0, flash_count = 0, active = True

        # Simulate time passing, but not enough for a flash
        current_test_time = 100.0 + EXPLOSION_FLASH_INTERVAL - 0.01
        assert explosion_instance.update(
            current_test_time) is False  # Not finished
        assert explosion_instance.flash_count == 0
        assert (
            explosion_instance.start_time == 100.0
        )  # start_time should not change yet
        assert explosion_instance.active is True

        # Simulate time passing enough for one flash
        current_test_time = 100.0 + EXPLOSION_FLASH_INTERVAL + 0.01
        assert explosion_instance.update(current_test_time) is False
        assert explosion_instance.flash_count == 1
        assert (
            explosion_instance.start_time == current_test_time
        )  # start_time updates to current_test_time
        assert explosion_instance.active is True

        # Simulate more flashes until max_flashes is reached
        # EXPLOSION_MAX_FLASHES is 3 by default in config
        # flash_count is already 1. Need 2 more flashes.

        # Flash 2
        last_flash_time = current_test_time
        current_test_time = last_flash_time + EXPLOSION_FLASH_INTERVAL + 0.01
        assert explosion_instance.update(current_test_time) is False
        assert explosion_instance.flash_count == 2
        assert explosion_instance.start_time == current_test_time
        assert explosion_instance.active is True

        # Flash 3 (should be the last one before inactive)
        # If MAX_FLASHES is 3, then when flash_count becomes 3, it should become inactive.
        last_flash_time = current_test_time
        current_test_time = last_flash_time + EXPLOSION_FLASH_INTERVAL + 0.01

        # At this point, flash_count will become 3.
        # The condition is `if self.flash_count >= self.max_flashes: self.active = False; return True`
        # So, when flash_count becomes 3, and if max_flashes is 3, it should return True.
        assert (
            explosion_instance.update(current_test_time) is True
        )  # Should be finished
        assert explosion_instance.flash_count == 3
        assert (
            explosion_instance.start_time == current_test_time
        )  # start_time updates one last time
        assert explosion_instance.active is False

    def test_update_when_not_active(self, explosion_instance):
        explosion_instance.active = False
        initial_flash_count = explosion_instance.flash_count
        initial_start_time = explosion_instance.start_time

        # Current time doesn't matter much if not active
        assert (
            explosion_instance.update(200.0) is False
        )  # Should return False as it's not newly finished

        assert explosion_instance.flash_count == initial_flash_count
        assert explosion_instance.start_time == initial_start_time
        assert explosion_instance.active is False  # Remains inactive
