import pytest
from unittest.mock import patch, MagicMock
import pygame # Needed for pygame.Surface, pygame.error, pygame.font, pygame.mixer types
from asset_manager import AssetManager, DummySound # The class we're testing and DummySound
from config import DEFAULT_PLACEHOLDER_SIZE as REAL_DEFAULT_PLACEHOLDER_SIZE # Import for type hint or comparison
from config import IMAGE_ASSET_CONFIG as REAL_IMAGE_ASSET_CONFIG # To see its structure

# Import fixtures from common utility file if needed, though AssetManager tests might be self-contained
# from .test_utils import initialized_pygame # Might be needed for real surface creation if not mocking everything

# Ensure Pygame is initialized for these tests, especially for font and surface operations.
# This could be a fixture or called directly at the start of the test module.
# Pygame is initialized by test_utils.mock_pygame_init_and_display which is autouse=True
# However, that fixture also mocks many pygame functions. For AssetManager tests,
# we might want more direct control or to use real pygame functions where appropriate,
# while still mocking file I/O.

@pytest.fixture
def am():
    """Provides a fresh AssetManager instance for each test."""
    # We need to ensure that pygame.init() and potentially pygame.font.init()
    # have been called before AssetManager() is instantiated, as its __init__
    # tries to create a font.
    # The autouse mock_pygame_init_and_display fixture in test_utils.py should handle pygame.init().
    # It also mocks pygame.font.Font. Let's see if this causes issues or needs adjustment
    # for testing AssetManager's font handling.
    return AssetManager()

class TestAssetManagerImageLoading:
    @patch('pygame.image.load')
    @patch('asset_manager.AssetManager._get_path') # Mock _get_path to control returned path
    def test_load_image_success(self, mock_get_path, mock_pygame_load, am):
        """Test successful image loading."""
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_surface.convert_alpha.return_value = mock_surface
        mock_pygame_load.return_value = mock_surface

        # Let's test a specific asset like 'rabbit'
        asset_key_to_test = 'rabbit'
        original_asset_path = 'images/rabbit.png' # Path defined in AssetManager.assets
        expected_resolved_path = "resolved/dummy/path/to/rabbit.png"

        # Make mock_get_path return a specific path when called with original_asset_path
        def get_path_side_effect(path_arg):
            if path_arg == original_asset_path:
                return expected_resolved_path
            return f"default_resolved_{path_arg}" # Default for other assets
        mock_get_path.side_effect = get_path_side_effect

        am.load_assets()

        mock_get_path.assert_any_call(original_asset_path)
        # Pygame.image.load should have been called with the path returned by _get_path for this specific asset
        mock_pygame_load.assert_any_call(expected_resolved_path)

        assert asset_key_to_test in am.images
        assert am.images[asset_key_to_test] is mock_surface
        # Ensure convert_alpha was called on the surface that was loaded for 'rabbit'
        # If multiple images are loaded, mock_surface.convert_alpha might be called multiple times
        # if mock_pygame_load returns the same mock_surface instance for all.
        # To be precise, we'd need to ensure mock_pygame_load returns unique mocks or check call count.
        # For simplicity now, we assume it's called at least once for our target.
        assert mock_surface.convert_alpha.called

    @patch('builtins.print')
    @patch('pygame.image.load', side_effect=pygame.error("Failed to load image for test"))
    @patch('asset_manager.AssetManager._get_path', return_value="dummy/failing/path")
    @patch('pygame.Surface')
    def test_load_image_failure_creates_placeholder_with_correct_size(
            self, mock_pygame_surface_constructor, mock_get_path, mock_pygame_load, mock_print, am, mocker):
        """Test image loading failure creates placeholders with correct sizes (hinted or default)."""

        hinted_asset_key = 'test_sized_asset'
        hinted_size = (200, 150)

        no_hint_asset_key = 'test_unsized_asset'

        test_default_placeholder_size = (70, 30) # Specific default for this test

        # Mock IMAGE_ASSET_CONFIG and DEFAULT_PLACEHOLDER_SIZE as they are used in AssetManager
        mock_image_config_dict = {
            hinted_asset_key: {'path': 'path/to/sized.png', 'size': hinted_size},
            no_hint_asset_key: {'path': 'path/to/unsized.png'}
        }
        # Patch where these are imported and used by AssetManager instance 'am'
        mocker.patch.object(am, 'IMAGE_ASSET_CONFIG', mock_image_config_dict, create=True)
        # If IMAGE_ASSET_CONFIG is a module-level import in asset_manager.py, patch 'asset_manager.IMAGE_ASSET_CONFIG'
        # The current AssetManager imports them from config, so we patch them in asset_manager's scope.
        mocker.patch('asset_manager.IMAGE_ASSET_CONFIG', mock_image_config_dict)
        mocker.patch('asset_manager.DEFAULT_PLACEHOLDER_SIZE', test_default_placeholder_size)

        # Setup side effect for pygame.Surface constructor to track called sizes
        created_surface_sizes = []
        def surface_side_effect(size_arg):
            created_surface_sizes.append(size_arg)
            mock_surf = MagicMock() # Removed spec=pygame.Surface
            mock_surf.convert_alpha.return_value = mock_surf
            mock_surf.fill = MagicMock()
            mock_surf.blit = MagicMock()
            mock_surf.get_rect = MagicMock(return_value=pygame.Rect(0, 0, size_arg[0], size_arg[1]))
            mock_surf.get_width = MagicMock(return_value=size_arg[0])
            mock_surf.get_height = MagicMock(return_value=size_arg[1])
            return mock_surf
        mock_pygame_surface_constructor.side_effect = surface_side_effect

        am.load_assets()

        assert hinted_asset_key in am.images
        assert no_hint_asset_key in am.images

        # Check that pygame.Surface was called with the correct sizes
        assert hinted_size in created_surface_sizes, f"pygame.Surface not called with hinted size {hinted_size}"
        assert test_default_placeholder_size in created_surface_sizes, \
            f"pygame.Surface not called with default placeholder size {test_default_placeholder_size}"

        # Check warnings were printed
        warning_for_hinted_found = any(
            f"WARNING: Could not load image asset '{hinted_asset_key}'" in str(c[0][0])
            for c in mock_print.call_args_list
        )
        warning_for_no_hint_found = any(
            f"WARNING: Could not load image asset '{no_hint_asset_key}'" in str(c[0][0])
            for c in mock_print.call_args_list
        )
        assert warning_for_hinted_found, f"Warning for '{hinted_asset_key}' not found."
        assert warning_for_no_hint_found, f"Warning for '{no_hint_asset_key}' not found."

class TestAssetManagerSoundLoading:
    @patch('pygame.mixer.Sound')
    @patch('asset_manager.AssetManager._get_path')
    @patch('pygame.Surface') # Add patch for pygame.Surface here
    def test_load_sound_success(self, mock_pygame_surface, mock_get_path, mock_pygame_sound, am):
        """Test successful sound loading."""
        # Mock the behavior of any pygame.Surface created (e.g. placeholders for images)
        mock_created_surface = MagicMock()
        mock_created_surface.convert_alpha.return_value = mock_created_surface
        mock_pygame_surface.return_value = mock_created_surface

        mock_sound_object = MagicMock() # Removed spec=pygame.mixer.Sound
        mock_pygame_sound.return_value = mock_sound_object

        asset_key_to_test = 'explosion' # A key defined in AssetManager.sound_assets
        original_asset_path = 'sounds/explosion.mp3'
        expected_resolved_path = "resolved/dummy/path/to/explosion.mp3"

        def get_path_side_effect(path_arg):
            if path_arg == original_asset_path:
                return expected_resolved_path
            return f"default_resolved_{path_arg}"
        mock_get_path.side_effect = get_path_side_effect

        am.load_assets()

        mock_get_path.assert_any_call(original_asset_path)
        mock_pygame_sound.assert_any_call(expected_resolved_path)
        assert asset_key_to_test in am.sounds
        assert am.sounds[asset_key_to_test] is mock_sound_object

    @patch('builtins.print')
    @patch('pygame.mixer.Sound', side_effect=pygame.error("Failed to load sound"))
    @patch('asset_manager.AssetManager._get_path')
    def test_load_sound_failure_logs_warning(self, mock_get_path, mock_pygame_sound, mock_print, am):
        """Test sound loading failure logs a warning and key is not in sounds."""
        asset_key_to_test = 'hurt' # A key defined in AssetManager.sound_assets
        original_asset_path = 'sounds/hurt.mp3'
        expected_resolved_path = "resolved/dummy/path/to/hurt.mp3"

        def get_path_side_effect(path_arg):
            if path_arg == original_asset_path:
                return expected_resolved_path
            # For other image/sound assets that might be loaded by am.load_assets()
            # we should ensure they don't also raise errors, or mock them to succeed.
            # For simplicity, assume this test focuses on 'hurt' failing.
            # We can mock pygame.image.load to prevent it from failing for images.
            return f"default_resolved_{path_arg}"

        mock_get_path.side_effect = get_path_side_effect

        with patch('pygame.image.load', MagicMock(return_value=MagicMock(spec=pygame.Surface))): # Prevent image load errors
            am.load_assets()

        mock_get_path.assert_any_call(original_asset_path)
        mock_pygame_sound.assert_any_call(expected_resolved_path)

        # Check that a warning was printed for 'hurt' sound
        hurt_warning_found = False
        for call_args in mock_print.call_args_list:
            arg_str = str(call_args[0][0])
            if f"WARNING: Could not load sound asset '{asset_key_to_test}'" in arg_str:
                hurt_warning_found = True
                break
        assert hurt_warning_found, f"Warning for missing '{asset_key_to_test}' sound not printed."

        assert asset_key_to_test in am.sounds # Key should now be present
        assert isinstance(am.sounds[asset_key_to_test], DummySound) # Value should be a DummySound instance

class TestAssetManagerFontInitialization:
    @patch('pygame.font.SysFont')
    @patch('pygame.font.init')
    def test_font_initialization_success(self, mock_font_init, mock_sysfont, mocker):
        """Test successful font initialization."""
        # This test needs to run AssetManager.__init__ again with specific mocks for font.
        # The `am` fixture might already have an initialized font.
        # We can patch pygame.font.get_init to control the flow inside AssetManager.__init__
        mocker.patch('pygame.font.get_init', return_value=False) # Force init path

        mock_font_object = MagicMock(spec=pygame.font.Font)
        mock_sysfont.return_value = mock_font_object

        asset_manager_instance = AssetManager()

        mock_font_init.assert_called_once()
        mock_sysfont.assert_called_once_with(None, 20)
        assert asset_manager_instance.placeholder_font is mock_font_object

    @patch('builtins.print')
    @patch('pygame.font.SysFont', side_effect=pygame.error("Failed to create font"))
    @patch('pygame.font.init')
    def test_font_initialization_failure(self, mock_font_init, mock_sysfont, mock_print, mocker):
        """Test font initialization failure."""
        mocker.patch('pygame.font.get_init', return_value=False) # Force init path

        asset_manager_instance = AssetManager()

        mock_font_init.assert_called_once() # pygame.font.init() itself should not fail
        mock_sysfont.assert_called_once_with(None, 20)
        assert asset_manager_instance.placeholder_font is None

        warning_found = False
        for call_args in mock_print.call_args_list:
            if "WARNING: Could not initialize font for asset placeholders" in str(call_args[0][0]):
                warning_found = True
                break
        assert warning_found, "Warning for font initialization failure not printed."

    @patch('pygame.font.init')
    def test_font_already_initialized(self, mock_font_init, mocker):
        """Test that pygame.font.init is not called if font module already initialized."""
        mocker.patch('pygame.font.get_init', return_value=True) # Simulate font already initialized
        mocker.patch('pygame.font.SysFont', return_value=MagicMock(spec=pygame.font.Font)) # Ensure SysFont doesn't fail

        asset_manager_instance = AssetManager()

        mock_font_init.assert_not_called() # Should not be called if get_init() is True
        assert asset_manager_instance.placeholder_font is not None

    @patch('builtins.print')
    @patch('pygame.font', None) # Patch pygame.font to be None for the scope of this test
    def test_font_initialization_fails_if_pygame_font_is_none(self, mock_print, mocker): # Renamed test
        """Test AssetManager font init when pygame.font is None, leading to AttributeError."""

        # AssetManager's __init__ does:
        # if hasattr(pygame, 'font'):  <-- This will be True because pygame.font attribute exists (its value is None)
        #     try:
        #         if not pygame.font.get_init():
        #             pygame.font.init()  <-- This will become None.init(), raising AttributeError
        #         self.placeholder_font = pygame.font.SysFont(None, 20) <-- or this becomes None.SysFont()
        #     except (pygame.error, AttributeError) as e:
        #         print(f"WARNING: Could not initialize font for asset placeholders: {e}")

        asset_manager_instance = AssetManager()

        assert asset_manager_instance.placeholder_font is None
        warning_found = False
        # The AttributeError from trying to use `None.init()` or `None.SysFont()`
        # should be caught by the `except (pygame.error, AttributeError)` block.
        expected_warning_fragment = "WARNING: Could not initialize font for asset placeholders"

        for call_args in mock_print.call_args_list:
            if expected_warning_fragment in str(call_args[0][0]):
                warning_found = True
                break
        assert warning_found, f"Expected warning fragment '{expected_warning_fragment}' not found in print calls."

    @patch('builtins.print')
    def test_font_module_truly_missing(self, mock_print, mocker): # Removed mock_hasattr
        """Test behavior when hasattr(pygame, 'font') is False."""

        original_pygame_font_attr = None
        has_font_attr_originally = hasattr(pygame, 'font')

        if has_font_attr_originally:
            original_pygame_font_attr = pygame.font
            del pygame.font

        try:
            # Ensure re-import or re-evaluation if AssetManager is imported at module level
            # For this test, AssetManager() is instantiated, so it will use current pygame state.
            asset_manager_instance = AssetManager()

            assert asset_manager_instance.placeholder_font is None
            warning_found = False
            expected_warning = "WARNING: Pygame font module not available. Placeholders will not have text."
            for call_args in mock_print.call_args_list:
                if expected_warning in str(call_args[0][0]):
                    warning_found = True
                    break
            assert warning_found, f"Expected warning '{expected_warning}' not found."
        finally:
            if has_font_attr_originally: # Restore pygame.font if it was deleted
                pygame.font = original_pygame_font_attr # Corrected variable name
            # If it didn't exist originally, we don't want to add it.
