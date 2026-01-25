import time  # For time.time mocking
from unittest.mock import MagicMock, patch

import pygame
import pytest

from config import (
    VAMPIRE_DEATH_DURATION,
    VAMPIRE_RESPAWN_TIME,
    VAMPIRE_SPEED,
    WORLD_SIZE,
)
from game_entities import Player, Vampire  # Player needed for Vampire.update

from .test_utils import (
    initialized_pygame,
    mock_asset_manager,
    mock_pygame_init_and_display,
    real_surface_factory,
)


@pytest.fixture
def vampire_image(real_surface_factory):
    # Vampire image from mock_asset_manager in test_utils is 40x40
    return real_surface_factory(40, 40)


@pytest.fixture
def vampire_instance(vampire_image):
    return Vampire(200, 250, vampire_image)


@pytest.fixture
def mock_player_for_vampire_tests(mock_asset_manager, real_surface_factory):
    player_image = real_surface_factory(32, 32)  # Standard player image size
    player = Player(100, 100, player_image, mock_asset_manager)
    return player


class TestVampireInitialization:
    def test_initial_values(self, vampire_instance, vampire_image):
        assert vampire_instance.rect.topleft == (200, 250)
        assert vampire_instance.original_image is vampire_image
        assert vampire_instance.image is vampire_image
        assert vampire_instance.speed == VAMPIRE_SPEED
        assert vampire_instance.active is False  # Vampire starts inactive by default
        assert vampire_instance.respawn_timer == 0
        assert vampire_instance.death_effect_active is False
        assert vampire_instance.death_effect_start_time == 0
        assert vampire_instance.death_effect_duration == VAMPIRE_DEATH_DURATION


class TestVampireRespawn:
    @patch(
        "random.randint"
    )  # If respawn location becomes random within Vampire.respawn
    def test_respawn_resets_state_and_position(self, mock_randint, vampire_instance):
        # Modify state
        vampire_instance.active = False
        vampire_instance.rect.topleft = (500, 500)
        vampire_instance.death_effect_active = True  # Should be cleared by respawn

        # Vampire.respawn(self, x, y)
        new_x, new_y = 70, 80
        # If Vampire.respawn itself called random.randint, we'd mock it here.
        # Currently, it takes x, y as params.

        vampire_instance.respawn(new_x, new_y)

        assert vampire_instance.active is True
        assert vampire_instance.rect.topleft == (new_x, new_y)
        assert vampire_instance.death_effect_active is False
        # death_flash_count is mentioned in Vampire.respawn but not initialized in __init__
        # assert vampire_instance.death_flash_count == 0
        # This attribute isn't in the current Vampire class, so commenting out.


class TestVampireUpdate:
    def test_update_movement_when_active(
        self, vampire_instance, mock_player_for_vampire_tests
    ):
        vampire = vampire_instance
        player = mock_player_for_vampire_tests

        vampire.active = True
        vampire.rect.topleft = (150, 150)  # Vampire's position
        player.rect.topleft = (
            100,
            100,
        )  # Player's position (Vampire should move towards this)

        initial_vamp_x, initial_vamp_y = vampire.rect.x, vampire.rect.y

        # utilities.calculate_movement_towards is complex. We test its effect.
        # Vampire should move towards player. Since player is top-left of vampire, vampire moves up-left.
        vampire.update(player, WORLD_SIZE, time.time())

        assert vampire.rect.x < initial_vamp_x
        assert vampire.rect.y < initial_vamp_y

    def test_update_stays_within_bounds_when_active(
        self, vampire_instance, mock_player_for_vampire_tests
    ):
        vampire = vampire_instance
        player = mock_player_for_vampire_tests
        vampire.active = True

        # Player at center, vampire at edge, trying to move out
        player.rect.center = (WORLD_SIZE[0] // 2, WORLD_SIZE[1] // 2)

        # Top-left corner
        vampire.rect.topleft = (0, 0)
        # Make player appear top-left of vampire to encourage movement further top-left
        player.rect.center = (vampire.rect.centerx - 100,
                              vampire.rect.centery - 100)
        vampire.update(player, WORLD_SIZE, time.time())
        assert vampire.rect.topleft == (0, 0)

        # Bottom-right corner
        vampire.rect.bottomright = (WORLD_SIZE[0], WORLD_SIZE[1])
        player.rect.center = (vampire.rect.centerx + 100,
                              vampire.rect.centery + 100)
        vampire.update(player, WORLD_SIZE, time.time())
        assert vampire.rect.bottomright == (WORLD_SIZE[0], WORLD_SIZE[1])

    @patch("time.time")
    def test_update_respawns_when_inactive_and_timer_up(
        self, mock_current_time, vampire_instance, mock_player_for_vampire_tests
    ):
        vampire = vampire_instance
        # update needs player, though not used for respawn logic here
        player = mock_player_for_vampire_tests

        vampire.active = False
        vampire.respawn_timer = 100.0  # Time when it "died"

        # Time not yet up for respawn
        mock_current_time.return_value = (
            vampire.respawn_timer + VAMPIRE_RESPAWN_TIME - 0.1
        )
        vampire.update(player, WORLD_SIZE, mock_current_time.return_value)
        assert vampire.active is False  # Should not have respawned

        # Time is up for respawn
        mock_current_time.return_value = (
            vampire.respawn_timer + VAMPIRE_RESPAWN_TIME + 0.1
        )
        with patch.object(vampire, "respawn") as mock_vamp_respawn:
            # Patching random.randint as it's called by Vampire.update->respawn if not given x,y
            # The actual Vampire.update calls self.respawn(random.randint(...), random.randint(...))
            with patch(
                "random.randint", side_effect=[50, 60]
            ) as mock_rand_int_for_respawn:
                vampire.update(player, WORLD_SIZE,
                               mock_current_time.return_value)
                mock_vamp_respawn.assert_called_once_with(50, 60)
        # Note: mock_vamp_respawn means original respawn is not called, so active state not set by it.
        # The test above checks that respawn *would be* called.

    def test_update_death_effect_duration_when_active_is_false(
        self, vampire_instance, mock_player_for_vampire_tests
    ):
        # This test is to confirm that the death effect logic inside Vampire.update's `if self.active:`
        # block is NOT triggered when self.active is False, as expected.
        vampire = vampire_instance
        player = mock_player_for_vampire_tests

        vampire.active = False  # IMPORTANT
        vampire.death_effect_active = True

        current_eval_time = time.time()
        vampire.death_effect_start_time = (
            current_eval_time - VAMPIRE_DEATH_DURATION - 1
        )  # Effect should have ended

        # Prevent respawn, so we only test if the `if self.active:` block's death effect logic runs
        vampire.respawn_timer = current_eval_time

        vampire.update(player, WORLD_SIZE, current_eval_time)

        # Because vampire.active is False, the internal check for death_effect_duration in Vampire.update
        # (which is inside the `if self.active:` block) should not run.
        # And because we prevented respawn, vampire.respawn() which also clears death_effect_active, should not run.
        # Thus, death_effect_active should remain True.
        assert vampire.death_effect_active is True


# Drawing tests are harder without visual inspection or complex mocking.
# For now, focusing on state and logic.
# test_draw_tinted_when_death_effect, test_draw_normal_when_active could be added if needed.
