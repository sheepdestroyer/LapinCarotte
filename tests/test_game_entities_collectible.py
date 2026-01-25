from unittest.mock import MagicMock, patch

import pygame
import pytest

from config import ITEM_SCALE  # Default scale is 0.5
from game_entities import Collectible

from .test_utils import (
    initialized_pygame,
    mock_asset_manager,
    mock_pygame_init_and_display,
    real_surface_factory,
)


@pytest.fixture
def item_image(real_surface_factory):
    # Using a size that's easy to scale, e.g., 30x40. ITEM_SCALE = 0.5 -> 15x20
    return real_surface_factory(30, 40)


@pytest.fixture
def collectible_instance(item_image):
    # Creates a collectible of type 'hp' at (100,120)
    return Collectible(100, 120, item_image, "hp", ITEM_SCALE)


class TestCollectibleInitialization:
    def test_initial_values(self, collectible_instance, item_image):
        assert collectible_instance.item_type == "hp"
        assert collectible_instance.active is True

        # Check rect is centered
        expected_center_x, expected_center_y = 100, 120
        assert collectible_instance.rect.centerx == expected_center_x
        assert collectible_instance.rect.centery == expected_center_y

        # Check image scaling
        # Original image was 30x40. ITEM_SCALE is 0.5.
        # Scaled image should be 15x20.
        # Due to GameObject.__init__, both self.image and self.original_image point to the scaled image.
        expected_width = int(item_image.get_width() * ITEM_SCALE)
        expected_height = int(item_image.get_height() * ITEM_SCALE)

        assert collectible_instance.image.get_width() == expected_width
        assert collectible_instance.image.get_height() == expected_height
        assert collectible_instance.original_image.get_width() == expected_width
        assert collectible_instance.original_image.get_height() == expected_height

        # Check that the rect size matches the scaled image size
        assert collectible_instance.rect.width == expected_width
        assert collectible_instance.rect.height == expected_height

    def test_different_item_type_and_scale(self, item_image):
        custom_scale = 0.25
        collectible = Collectible(50, 50, item_image, "garlic", custom_scale)

        assert collectible.item_type == "garlic"

        expected_width = int(
            item_image.get_width() * custom_scale
        )  # 30 * 0.25 = 7.5 -> 7
        expected_height = int(item_image.get_height() *
                              custom_scale)  # 40 * 0.25 = 10

        assert collectible.image.get_width() == expected_width
        assert collectible.image.get_height() == expected_height
        assert collectible.rect.width == expected_width
        assert collectible.rect.height == expected_height
        assert collectible.rect.center == (50, 50)

    @patch("pygame.transform.scale")
    def test_pygame_transform_scale_called_correctly(
        self, mock_transform_scale, item_image
    ):
        # We need to ensure the mock_transform_scale returns a surface-like object
        # that has get_rect, get_width, get_height
        mock_scaled_surface = MagicMock(spec=pygame.Surface)
        mock_scaled_surface.get_width.return_value = int(
            item_image.get_width() * ITEM_SCALE
        )
        mock_scaled_surface.get_height.return_value = int(
            item_image.get_height() * ITEM_SCALE
        )

        # Configure get_rect for the scaled surface
        # It's called as self.image.get_rect(center=(x,y)) in Collectible
        def mock_get_rect_for_scaled(**kwargs):
            if "center" in kwargs:
                return pygame.Rect(
                    kwargs["center"][0] - mock_scaled_surface.get_width() // 2,
                    kwargs["center"][1] -
                    mock_scaled_surface.get_height() // 2,
                    mock_scaled_surface.get_width(),
                    mock_scaled_surface.get_height(),
                )
            return pygame.Rect(
                0, 0, mock_scaled_surface.get_width(), mock_scaled_surface.get_height()
            )

        mock_scaled_surface.get_rect = MagicMock(
            side_effect=mock_get_rect_for_scaled)
        mock_transform_scale.return_value = mock_scaled_surface

        collectible = Collectible(10, 20, item_image, "test_item", ITEM_SCALE)

        expected_target_width = int(item_image.get_width() * ITEM_SCALE)
        expected_target_height = int(item_image.get_height() * ITEM_SCALE)

        mock_transform_scale.assert_called_once_with(
            item_image, (expected_target_width, expected_target_height)
        )
        assert collectible.image is mock_scaled_surface
        assert (
            collectible.original_image is mock_scaled_surface
        )  # Due to GameObject constructor
        assert collectible.rect.center == (10, 20)
