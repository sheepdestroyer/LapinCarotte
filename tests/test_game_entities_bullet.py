import pytest
from unittest.mock import MagicMock, patch
import pygame
import math

from game_entities import Bullet
from config import BULLET_SPEED
from utilities import get_direction_vector # Bullet uses this
from .test_utils import mock_asset_manager, mock_pygame_init_and_display, real_surface_factory, initialized_pygame

@pytest.fixture
def bullet_image(real_surface_factory):
    # Bullet image from mock_asset_manager in test_utils is 10x10
    return real_surface_factory(10, 10)

@pytest.fixture
def bullet_instance(bullet_image):
    # Standard bullet going from (50,50) towards (150,50) (horizontally right)
    return Bullet(50, 50, 150, 50, bullet_image)

class TestBulletInitialization:
    def test_initial_values_horizontal(self, bullet_instance, bullet_image):
        # Bullet(x,y, target_x, target_y, image) uses x,y as topleft for rect, but as origin for shot vector
        assert bullet_instance.rect.topleft == (50,50) # Rect is still based on x,y topleft
        assert bullet_instance.original_image is bullet_image

        # For shot originating at (50,50) to (150,50), dir_x=1, dir_y=0
        expected_vel_x = 1 * BULLET_SPEED
        expected_vel_y = 0 * BULLET_SPEED
        assert bullet_instance.velocity[0] == pytest.approx(expected_vel_x)
        assert bullet_instance.velocity[1] == pytest.approx(expected_vel_y)

        # Angle for (1,0) vector (math.atan2(-0, 1)) is 0 degrees
        assert bullet_instance.angle == pytest.approx(0.0)

    def test_initial_values_diagonal(self, bullet_image):
        # Bullet going from (0,0) towards (10,10)
        # dir_x, dir_y for (0,0) to (10,10) should be (1/sqrt(2), 1/sqrt(2))
        start_x, start_y = 0, 0
        target_x, target_y = 10, 10
        bullet = Bullet(start_x, start_y, target_x, target_y, bullet_image)

        dx = target_x - start_x # 10
        dy = target_y - start_y # 10
        dist = math.hypot(dx, dy) # sqrt(10^2 + 10^2) = 10 * sqrt(2)

        expected_dir_x = dx / dist # 10 / (10 * sqrt(2)) = 1/sqrt(2)
        expected_dir_y = dy / dist # 1/sqrt(2)

        expected_vel_x = expected_dir_x * BULLET_SPEED
        expected_vel_y = expected_dir_y * BULLET_SPEED

        assert pytest.approx(bullet.velocity[0]) == expected_vel_x
        assert pytest.approx(bullet.velocity[1]) == expected_vel_y

        # Angle for (1,1) vector (math.atan2(-1, 1)) is -45 degrees
        assert pytest.approx(bullet.angle) == -45.0

class TestBulletUpdate:
    def test_update_moves_rect(self, bullet_instance):
        initial_x, initial_y = bullet_instance.rect.x, bullet_instance.rect.y
        vel_x, vel_y = bullet_instance.velocity # This velocity is now correctly calculated from (50,50)

        bullet_instance.update()

        # The rect's topleft should move by the velocity
        assert bullet_instance.rect.x == pytest.approx(initial_x + vel_x)
        assert bullet_instance.rect.y == pytest.approx(initial_y + vel_y)

        bullet_instance.update()
        assert bullet_instance.rect.x == pytest.approx(initial_x + 2 * vel_x)
        assert bullet_instance.rect.y == pytest.approx(initial_y + 2 * vel_y)

class TestBulletRotatedImage:
    @patch('pygame.transform.rotate')
    def test_rotated_image_property_calls_transform_rotate(self, mock_rotate, bullet_instance, bullet_image):
        # Setup: bullet_instance has angle 0 by default from fixture
        # Let's change angle for a more specific test
        bullet_instance.angle = -30.0

        # Access the property
        rotated_img = bullet_instance.rotated_image

        # Check pygame.transform.rotate was called correctly
        mock_rotate.assert_called_once_with(bullet_image, -30.0)
        assert rotated_img is mock_rotate.return_value # Ensure the property returns what rotate returns
