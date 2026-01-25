import random
from unittest.mock import MagicMock, call, patch

import pygame
import pytest

import config
from game_entities import (
    Bullet,
    Carrot,
    Collectible,
    Explosion,
    GarlicShot,
    Player,
    Vampire,
)
from game_state import GameState

from .test_utils import (
    initialized_pygame,
    mock_asset_manager,
    mock_pygame_init_and_display,
    real_surface_factory,
)


@pytest.fixture
def game_state_instance(mock_asset_manager):
    gs = GameState(mock_asset_manager)
    return gs


def _create_test_garlic_shot(x, y, image, dx=1, dy=0):
    """Helper function to create a garlic_shot dictionary for testing."""
    shot = {
        "active": True,
        "x": x,
        "y": y,
        "dx": dx,
        "dy": dy,
        "rotation_angle": 0,
        "image": image,
        "rect": pygame.Rect(0, 0, config.GARLIC_WIDTH, config.GARLIC_HEIGHT),
    }
    shot["rect"].center = (x, y)
    return shot


class TestGameStateInitialization:
    def test_initial_values(self, game_state_instance):
        gs = game_state_instance
        assert gs.scroll == [0, 0]
        assert gs.scroll_trigger == config.SCROLL_TRIGGER
        assert gs.world_size == config.WORLD_SIZE
        assert not gs.game_over
        assert not gs.started
        assert gs.asset_manager is not None
        assert isinstance(gs.player, Player)
        assert gs.garlic_shot is None
        assert gs.garlic_shot_start_time == 0
        assert gs.garlic_shot_travel == 0
        assert isinstance(gs.vampire, Vampire)
        assert gs.vampire.active
        assert gs.bullets == []
        assert len(gs.carrots) == config.CARROT_COUNT
        assert all(isinstance(c, Carrot) for c in gs.carrots)
        assert gs.explosions == []
        assert gs.garlic_shots == []
        assert gs.items == []
        assert gs.vampire_killed_count == 0
        assert gs.last_vampire_death_pos == (0, 0)

    def test_player_initial_position(self, game_state_instance):
        assert game_state_instance.player.rect.topleft == (200, 200)
        assert game_state_instance.player.initial_x == 200
        assert game_state_instance.player.initial_y == 200

    def test_vampire_initial_position_random(self, mock_asset_manager):
        with patch("random.randint") as mock_randint:
            vampire_x_expected, vampire_y_expected = 100, 150

            expected_init_carrot_coords = []
            player_image_for_init = mock_asset_manager.images["rabbit"]
            player_center_x_init = 200 + player_image_for_init.get_width() // 2
            player_center_y_init = 200 + player_image_for_init.get_height() // 2
            for i in range(config.CARROT_COUNT):
                expected_init_carrot_coords.extend(
                    [player_center_x_init + 1500 + i * 50, player_center_y_init]
                )

            mock_values_for_init = [
                vampire_x_expected,
                vampire_y_expected,
            ] + expected_init_carrot_coords
            mock_values_iter_init = list(mock_values_for_init)

            def side_effect_pop_func_init(*args):
                if not mock_values_iter_init:
                    raise AssertionError(
                        f"Mock randint called too many times for init. Expected {len(mock_values_for_init)}"
                    )
                return mock_values_iter_init.pop(0)

            mock_randint.side_effect = side_effect_pop_func_init
            gs = GameState(mock_asset_manager)

            assert gs.vampire.rect.topleft == (
                vampire_x_expected, vampire_y_expected)
            assert mock_randint.call_count == len(mock_values_for_init)
            for i in range(config.CARROT_COUNT):
                assert gs.carrots[i].rect.topleft == (
                    expected_init_carrot_coords[i * 2],
                    expected_init_carrot_coords[i * 2 + 1],
                )
            assert not mock_values_iter_init


class TestGameStateReset:
    @patch("random.randint")
    def test_reset_values(self, mock_randint, game_state_instance, mock_asset_manager):
        gs = game_state_instance
        gs.scroll = [100, 100]
        gs.game_over = True
        gs.started = True
        gs.player.health = 1
        gs.player.garlic_count = 2
        gs.player.carrot_juice_count = 3
        gs.player.rect.topleft = (500, 500)
        gs.vampire.active = False
        gs.carrots = [MagicMock()]

        vamp_x_effective, vamp_y_effective = 300, 400  # For the single vampire respawn

        expected_carrot_coords = []
        player_image_for_reset = mock_asset_manager.images["rabbit"]
        # Get player initial position and image dimensions for safe carrot spawning calculation
        player_initial_x = gs.player.initial_x
        player_initial_y = gs.player.initial_y

        player_width = 0
        player_height = 0
        if hasattr(player_image_for_reset, "get_width"):  # GUI mode with valid surface
            player_width = player_image_for_reset.get_width()
            player_height = player_image_for_reset.get_height()
        elif isinstance(player_image_for_reset, dict):  # CLI mode with metadata
            size_hint = player_image_for_reset.get(
                "size_hint"
            ) or player_image_for_reset.get("size")
            if size_hint:
                player_width, player_height = size_hint

        PLAYER_PLACEHOLDER_WIDTH = 72
        PLAYER_PLACEHOLDER_HEIGHT = 72
        if player_width == 0:
            player_width = PLAYER_PLACEHOLDER_WIDTH
        if player_height == 0:
            player_height = PLAYER_PLACEHOLDER_HEIGHT

        player_center_x_reset = player_initial_x + player_width // 2
        player_center_y_reset = player_initial_y + player_height // 2

        for i in range(config.CARROT_COUNT):
            # Provide coordinates far from the player for carrot creation to avoid excessive randint calls
            expected_carrot_coords.extend(
                [player_center_x_reset + 1600 + i *
                    50, player_center_y_reset + i * 10]
            )

        # GameState.reset() now calls vampire.respawn once (2 randint calls)
        # Then CARROT_COUNT * 2 randint calls for carrots.
        # Total expected = 2 + CARROT_COUNT * 2
        mock_values_for_reset = [
            vamp_x_effective,
            vamp_y_effective,
        ] + expected_carrot_coords

        assert len(mock_values_for_reset) == 2 + (config.CARROT_COUNT * 2), (
            f"Expected {2 + config.CARROT_COUNT * 2} mock values, got {len(mock_values_for_reset)}"
        )

        mock_values_iter = list(mock_values_for_reset)

        def side_effect_pop_func(*args):
            if not mock_values_iter:
                raise AssertionError(
                    f"Mock randint called more than {len(mock_values_for_reset)} times. Actual calls: {mock_randint.call_count + 1}"
                )
            return mock_values_iter.pop(0)

        mock_randint.side_effect = side_effect_pop_func
        gs.reset()

        assert gs.scroll == [0, 0]
        assert not gs.game_over
        assert not gs.started
        assert gs.player.health == config.START_HEALTH
        assert gs.player.garlic_count == 0
        assert gs.player.carrot_juice_count == 0
        assert gs.player.rect.topleft == (
            gs.player.initial_x, gs.player.initial_y)
        assert gs.bullets == []
        assert gs.explosions == []
        assert gs.items == []

        assert gs.vampire.rect.topleft == (vamp_x_effective, vamp_y_effective)
        assert gs.vampire.active
        assert not gs.vampire.death_effect_active

        assert len(gs.carrots) == config.CARROT_COUNT
        assert mock_randint.call_count == len(mock_values_for_reset)
        for i in range(config.CARROT_COUNT):
            assert gs.carrots[i].rect.topleft == (
                expected_carrot_coords[i * 2],
                expected_carrot_coords[i * 2 + 1],
            )
        assert not mock_values_iter, (
            "Not all mock_randint values for reset were consumed"
        )

    def test_reset_clears_garlic_shot_state(self, game_state_instance):
        gs = game_state_instance
        gs.garlic_shot = {
            "active": True,
            "x": 100,
            "y": 100,
            "dx": 1,
            "dy": 0,
            "rotation_angle": 0,
        }
        gs.reset()
        assert gs.garlic_shot is None


class TestGameStateEntityManagement:
    def test_add_bullet(self, game_state_instance, mock_asset_manager):
        gs = game_state_instance
        bullet_image = mock_asset_manager.images["bullet"]
        gs.add_bullet(10, 20, 100, 100, bullet_image)
        new_bullet = gs.bullets[-1]
        assert new_bullet.rect.topleft == (10, 20)
        assert new_bullet.rect.centerx == 10 + bullet_image.get_width() // 2
        assert new_bullet.rect.centery == 20 + bullet_image.get_height() // 2

    def test_add_garlic_shot(self, game_state_instance, mock_asset_manager):
        gs = game_state_instance
        garlic_image = mock_asset_manager.images["garlic"]
        gs.add_garlic_shot(50, 60, 200, 200, garlic_image)
        new_shot = gs.garlic_shots[-1]
        assert new_shot.rect.topleft == (50, 60)
        assert new_shot.rect.centerx == 50 + garlic_image.get_width() // 2
        assert new_shot.rect.centery == 60 + garlic_image.get_height() // 2

    @patch("random.randint")
    def test_create_carrot(self, mock_randint, game_state_instance, mock_asset_manager):
        gs = game_state_instance
        gs.carrots = []
        gs.player.rect.centerx = 216
        gs.player.rect.centery = 216
        mock_randint.side_effect = [2000, 2000]
        gs.create_carrot(mock_asset_manager)
        assert gs.carrots[0].rect.topleft == (2000, 2000)
        assert mock_randint.call_count == 2

        gs.carrots = []
        gs.player.rect.centerx = 150
        gs.player.rect.centery = 150
        mock_randint.reset_mock()
        mock_randint.side_effect = [160, 160, 3000, 3000]
        gs.create_carrot(mock_asset_manager)
        assert gs.carrots[0].rect.topleft == (3000, 3000)
        assert mock_randint.call_count == 4


class TestGameStateUpdate:
    @patch("time.time")
    def test_update_carrot_movement_and_respawn(
        self, mock_time, game_state_instance, mock_asset_manager
    ):
        gs = game_state_instance
        gs.carrots = []
        carrot_image = mock_asset_manager.images["carrot"]
        with patch("random.uniform", MagicMock(return_value=0.5)):
            gs.player.rect.center = (2000, 2000)
            carrot_far = Carrot(10, 10, carrot_image)
            gs.carrots.append(carrot_far)
            initial_carrot_pos_far = carrot_far.rect.topleft
            carrot_close = Carrot(2050, 2000, carrot_image)
            gs.carrots.append(carrot_close)
            initial_carrot_pos_close_x = carrot_close.rect.x

            mock_time.return_value = 10.0
            gs.update(mock_time.return_value)

            assert carrot_far.rect.topleft != initial_carrot_pos_far
            assert carrot_close.rect.x > initial_carrot_pos_close_x

            gs.carrots[0].active = False
            gs.carrots[0].respawn_timer = mock_time.return_value
            with patch.object(gs.carrots[0], "respawn") as mock_carrot_respawn:
                mock_time.return_value += config.CARROT_RESPAWN_DELAY + 0.1
                gs.update(mock_time.return_value)
                mock_carrot_respawn.assert_called_once()

    @patch("time.time")
    def test_update_bullet_carrot_collision(
        self, mock_time, game_state_instance, mock_asset_manager
    ):
        gs = game_state_instance
        current_time = 50.0
        mock_time.return_value = current_time
        gs.carrots = []
        carrot = Carrot(100, 100, mock_asset_manager.images["carrot"])
        gs.carrots.append(carrot)
        gs.add_bullet(100, 100, 200, 200, mock_asset_manager.images["bullet"])
        bullet = gs.bullets[0]

        bullet.rect = MagicMock(spec=pygame.Rect)
        bullet.rect.colliderect.return_value = True
        bullet.rect.centerx = carrot.rect.centerx
        bullet.rect.centery = carrot.rect.centery
        bullet.rect.right = bullet.rect.centerx + 5
        bullet.rect.left = bullet.rect.centerx - 5
        bullet.rect.bottom = bullet.rect.centery + 5
        bullet.rect.top = bullet.rect.centery - 5

        gs.update(current_time)
        bullet.rect.colliderect.assert_called_once_with(carrot.rect)
        assert not carrot.active

    def test_update_removes_off_screen_bullets(
        self, game_state_instance, mock_asset_manager
    ):
        gs = game_state_instance
        bullet_image = mock_asset_manager.images["bullet"]
        gs.add_bullet(
            config.WORLD_SIZE[0] / 2,
            config.WORLD_SIZE[1] / 2,
            config.WORLD_SIZE[0] / 2 + 100,
            config.WORLD_SIZE[1] / 2,
            bullet_image,
        )
        gs.add_bullet(
            -200, config.WORLD_SIZE[1] / 2, -
            300, config.WORLD_SIZE[1] / 2, bullet_image
        )

        initial_center_x_on_screen = gs.bullets[0].rect.centerx
        gs.bullets[1].rect.right = -1

        gs.update(1.0)
        assert len(gs.bullets) == 1
        assert (
            gs.bullets[0].rect.centerx
            == initial_center_x_on_screen + config.BULLET_SPEED
        )

    @patch("time.time")
    def test_update_garlic_shot_vampire_collision(
        self, mock_time, game_state_instance, mock_asset_manager
    ):
        gs = game_state_instance
        vampire = gs.vampire
        current_time = 100.0
        mock_time.return_value = current_time
        vampire.rect = pygame.Rect(200, 200, 40, 40)
        vampire.active = True
        gs.garlic_shot = _create_test_garlic_shot(
            x=200, y=200, image=MagicMock())
        gs.garlic_shot_start_time = current_time - 0.1
        gs.garlic_shot_travel = 0

        gs.update(current_time)

        assert vampire.death_effect_active
        assert gs.garlic_shot is None

    @patch("time.time")
    def test_update_player_vampire_collision(self, mock_time, game_state_instance):
        gs = game_state_instance
        player = gs.player
        vampire = gs.vampire
        current_time = 300.0
        mock_time.return_value = current_time

        player.rect = MagicMock(spec=pygame.Rect)
        player.rect.x = 100
        player.rect.y = 100
        player.rect.width = 32
        player.rect.height = 32
        player.rect.centerx = player.rect.x + player.rect.width // 2
        player.rect.centery = player.rect.y + player.rect.height // 2
        player.rect.colliderect.return_value = True
        player.invincible = False

        vampire.rect = pygame.Rect(110, 110, 40, 40)
        vampire.active = True
        with patch.object(player, "take_damage") as mock_take_damage:
            gs.update(current_time)
            mock_take_damage.assert_called_once()
        player.rect.colliderect.assert_called_once_with(vampire.rect)

    @patch("time.time")
    def test_update_vampire_death_item_drop(
        self, mock_time, game_state_instance, mock_asset_manager, real_surface_factory
    ):
        gs = game_state_instance
        vampire = gs.vampire
        current_time_initial = 400.0
        mock_time.return_value = current_time_initial

        vampire.active = False
        vampire.death_effect_active = True
        vampire.death_effect_start_time = current_time_initial
        vampire.respawn_timer = current_time_initial
        gs.last_vampire_death_pos = (250, 250)
        initial_item_count = len(gs.items)

        real_juice_image = real_surface_factory(20, 20)
        original_juice_image_mock = mock_asset_manager.images["carrot_juice"]
        try:
            mock_asset_manager.images["carrot_juice"] = real_juice_image

            assert vampire.death_effect_active is True, (
                "Pre-update: death effect should be active"
            )
            gs.update(current_time_initial)
            assert vampire.death_effect_active is True, (
                "Post-update (elapsed 0): death effect should still be active"
            )
            assert len(gs.items) == initial_item_count, (
                "No item should drop if elapsed 0"
            )

            time_for_effect_to_complete = vampire.death_effect_start_time + float(
                config.VAMPIRE_DEATH_DURATION
            )
            mock_time.return_value = time_for_effect_to_complete

            gs.update(time_for_effect_to_complete)
            assert not vampire.death_effect_active, (
                "Death effect should be false after duration met"
            )
            assert len(gs.items) == initial_item_count + \
                1, "Item should have dropped"
        finally:
            mock_asset_manager.images["carrot_juice"] = original_juice_image_mock

    @patch("time.time")
    @patch("random.random")
    def test_update_explosion_item_drop(
        self,
        mock_random_random,
        mock_time,
        game_state_instance,
        mock_asset_manager,
        real_surface_factory,
    ):
        gs = game_state_instance
        current_time = 500.0
        mock_time.return_value = current_time
        real_hp_image = real_surface_factory(16, 16)
        original_hp_image_mock = mock_asset_manager.images["hp"]
        mock_asset_manager.images["hp"] = real_hp_image

        mock_explosion = MagicMock(spec=Explosion)
        mock_explosion.rect = pygame.Rect(300, 300, 5, 5)
        mock_explosion.update = MagicMock(return_value=True)
        gs.explosions.append(mock_explosion)
        initial_item_count = len(gs.items)
        mock_random_random.return_value = config.ITEM_DROP_GARLIC_CHANCE + 0.1  # HP
        gs.update(current_time)

        assert len(gs.items) == initial_item_count + 1
        dropped_item = gs.items[-1]
        expected_scaled_width = int(
            real_hp_image.get_width() * config.ITEM_SCALE)
        expected_scaled_height = int(
            real_hp_image.get_height() * config.ITEM_SCALE)
        assert dropped_item.original_image.get_width() == expected_scaled_width
        assert dropped_item.original_image.get_height() == expected_scaled_height

        mock_asset_manager.images["hp"] = original_hp_image_mock

    def test_update_player_collects_item(
        self, game_state_instance, mock_asset_manager, real_surface_factory
    ):
        gs = game_state_instance
        player = gs.player
        player.rect = MagicMock(spec=pygame.Rect)
        player.rect.centerx = 150
        player.rect.centery = 150
        player.rect.colliderect.return_value = True
        real_item_surface = real_surface_factory(20, 20)

        gs.vampire.active = False
        gs.vampire.respawn_timer = (
            600.0  # Prevent vampire respawn during this test's update
        )

        hp_item = Collectible(
            player.rect.centerx,
            player.rect.centery,
            real_item_surface,
            "hp",
            config.ITEM_SCALE,
        )
        gs.items.append(hp_item)
        player.health = config.START_HEALTH - 1
        assert player.health < config.MAX_HEALTH
        initial_health = player.health

        with patch.object(
            player, "take_damage", wraps=player.take_damage
        ) as mock_take_damage:  # wraps to still execute original
            gs.update(600.0)
            # Should not be called if vampire is inactive and respawn timer is set
            mock_take_damage.assert_not_called()

        assert player.health == initial_health + 1
        assert hp_item not in gs.items
        player.rect.colliderect.assert_any_call(hp_item.rect)
        mock_asset_manager.sounds["get_hp"].play.assert_called_once()

        player.rect.colliderect.reset_mock()
        mock_asset_manager.sounds["get_garlic"].play.reset_mock()
        garlic_item = Collectible(
            player.rect.centerx,
            player.rect.centery,
            real_item_surface,
            "garlic",
            config.ITEM_SCALE,
        )
        gs.items.append(garlic_item)
        player.garlic_count = 0
        initial_garlic = player.garlic_count
        # Assuming take_damage is not called in this update either
        gs.update(601.0)
        assert player.garlic_count == initial_garlic + 1
        assert garlic_item not in gs.items
        mock_asset_manager.sounds["get_garlic"].play.assert_called_once()

        player.rect.colliderect.reset_mock()
        mock_asset_manager.sounds["get_hp"].play.reset_mock()
        carrot_juice_item = Collectible(
            player.rect.centerx,
            player.rect.centery,
            real_item_surface,
            "carrot_juice",
            config.ITEM_SCALE,
        )
        gs.items.append(carrot_juice_item)
        player.carrot_juice_count = 0
        initial_juice = player.carrot_juice_count
        gs.update(602.0)  # Assuming take_damage is not called
        assert player.carrot_juice_count == initial_juice + 1
        assert carrot_juice_item not in gs.items
        mock_asset_manager.sounds["get_hp"].play.assert_called_once()

    @patch("time.time")
    def test_update_garlic_shot_expiration_by_travel(
        self, mock_time, game_state_instance, mock_asset_manager
    ):
        """Tests that the garlic shot expires when it exceeds its maximum travel distance."""
        gs = game_state_instance
        current_time = 200.0
        mock_time.return_value = current_time
        gs.garlic_shot = _create_test_garlic_shot(
            x=10, y=10, image=mock_asset_manager.images["garlic"]
        )
        # Set travel distance to be just under the limit
        gs.garlic_shot_travel = config.GARLIC_SHOT_MAX_TRAVEL - (
            config.GARLIC_SHOT_SPEED / 2
        )
        gs.garlic_shot_start_time = current_time

        # First update: shot is still active, travel distance is updated inside this call.
        gs.update(current_time)
        assert gs.garlic_shot["active"]

        # Second update: shot should expire due to the travel distance check at the start of the update.
        gs.update(current_time)  # Time doesn't need to advance for this check
        assert gs.garlic_shot is None

    @patch("time.time")
    def test_update_garlic_shot_expiration_by_duration(
        self, mock_time, game_state_instance, mock_asset_manager
    ):
        """Tests that the garlic shot expires when its duration runs out."""
        gs = game_state_instance
        current_time = 200.0
        mock_time.return_value = current_time
        gs.garlic_shot = _create_test_garlic_shot(
            x=10, y=10, image=mock_asset_manager.images["garlic"]
        )
        gs.garlic_shot_travel = 0
        gs.garlic_shot_start_time = current_time

        # Update at a time just at the expiration moment
        time_at_expiry = current_time + config.GARLIC_SHOT_DURATION
        mock_time.return_value = time_at_expiry
        gs.update(time_at_expiry)
        assert gs.garlic_shot["active"]

        # Update at a time just after expiration
        time_after_expiry = current_time + config.GARLIC_SHOT_DURATION + 0.1
        mock_time.return_value = time_after_expiry
        gs.update(time_after_expiry)
        assert gs.garlic_shot is None
