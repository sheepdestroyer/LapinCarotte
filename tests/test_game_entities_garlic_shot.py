import pytest
from unittest.mock import MagicMock, patch
import pygame
import math

from game_entities import GarlicShot
from config import GARLIC_SHOT_SPEED, GARLIC_SHOT_MAX_TRAVEL
from utilities import get_direction_vector # Used by GarlicShot
from .test_utils import mock_asset_manager, mock_pygame_init_and_display, real_surface_factory, initialized_pygame

@pytest.fixture
def garlic_shot_image(real_surface_factory):
    # Garlic image from mock_asset_manager in test_utils is 15x15
    return real_surface_factory(15, 15)

@pytest.fixture
def garlic_shot_instance(garlic_shot_image):
    # Standard shot going from (50,50) towards (150,50) (horizontally right)
    return GarlicShot(50, 50, 150, 50, garlic_shot_image)

class TestGarlicShotInitialization:
    def test_initial_values_horizontal(self, garlic_shot_instance, garlic_shot_image):
        # GarlicShot(x,y, target_x, target_y, image) uses x,y as topleft
        assert garlic_shot_instance.rect.topleft == (50,50)
        assert garlic_shot_instance.original_image is garlic_shot_image

        # For (50,50) to (150,50), direction vector should be (1,0)
        assert garlic_shot_instance.direction.x == pytest.approx(1.0)
        assert garlic_shot_instance.direction.y == pytest.approx(0.0)

        assert garlic_shot_instance.rotation_angle == 0
        assert garlic_shot_instance.speed == GARLIC_SHOT_SPEED
        assert garlic_shot_instance.max_travel == GARLIC_SHOT_MAX_TRAVEL
        assert garlic_shot_instance.traveled == 0
        assert garlic_shot_instance.active is True

    def test_initial_values_diagonal(self, garlic_shot_image):
        shot = GarlicShot(0,0, 10, 10, garlic_shot_image)
        expected_dx = 10 / math.sqrt(10**2 + 10**2)
        expected_dy = 10 / math.sqrt(10**2 + 10**2)
        assert shot.direction.x == pytest.approx(expected_dx)
        assert shot.direction.y == pytest.approx(expected_dy)

class TestGarlicShotUpdate:
    def test_update_moves_rect_and_accumulates_travel(self, garlic_shot_instance):
        initial_x, initial_y = garlic_shot_instance.rect.x, garlic_shot_instance.rect.y
        dx, dy = garlic_shot_instance.direction.x, garlic_shot_instance.direction.y
        speed = garlic_shot_instance.speed

        garlic_shot_instance.update()

        assert garlic_shot_instance.rect.x == initial_x + dx * speed
        assert garlic_shot_instance.rect.y == initial_y + dy * speed
        assert garlic_shot_instance.traveled == speed
        assert garlic_shot_instance.rotation_angle == 5 # Rotates by 5 each update

        garlic_shot_instance.update()
        assert garlic_shot_instance.rect.x == initial_x + 2 * dx * speed
        assert garlic_shot_instance.rect.y == initial_y + 2 * dy * speed
        assert garlic_shot_instance.traveled == 2 * speed
        assert garlic_shot_instance.rotation_angle == 10


    def test_update_becomes_inactive_after_max_travel(self, garlic_shot_instance):
        # Move it just under max_travel
        garlic_shot_instance.traveled = GARLIC_SHOT_MAX_TRAVEL - garlic_shot_instance.speed / 2
        assert garlic_shot_instance.active is True

        garlic_shot_instance.update() # This call should push traveled >= max_travel
        assert garlic_shot_instance.traveled >= GARLIC_SHOT_MAX_TRAVEL
        assert garlic_shot_instance.active is False

    def test_update_does_not_move_if_inactive(self, garlic_shot_instance):
        garlic_shot_instance.active = False
        initial_pos = garlic_shot_instance.rect.copy()
        initial_traveled = garlic_shot_instance.traveled
        initial_angle = garlic_shot_instance.rotation_angle

        garlic_shot_instance.update()

        assert garlic_shot_instance.rect.topleft == initial_pos.topleft
        assert garlic_shot_instance.traveled == initial_traveled
        assert garlic_shot_instance.rotation_angle == initial_angle
