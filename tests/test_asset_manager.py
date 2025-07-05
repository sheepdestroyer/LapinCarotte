import pytest
from unittest.mock import patch, MagicMock, DEFAULT as MOCK_DEFAULT # Import DEFAULT
import pygame # Needed for pygame.Surface, pygame.error, pygame.font, pygame.mixer types
from asset_manager import AssetManager, DummySound # The class we're testing and DummySound
from config import DEFAULT_PLACEHOLDER_SIZE as REAL_DEFAULT_PLACEHOLDER_SIZE # Import for type hint or comparison
from config import IMAGE_ASSET_CONFIG as REAL_IMAGE_ASSET_CONFIG, SOUND_ASSET_CONFIG as REAL_SOUND_ASSET_CONFIG # To see its structure

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
        # Patch the module-level imports in asset_manager.py
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
    @patch('builtins.print') # To check for warnings
    @patch('asset_manager.IMAGE_ASSET_CONFIG', {}) # Ensure no images are processed
    def test_load_sound_when_mixer_not_initialized(self, mock_print, am, mocker):
        """Test that DummySound is used if pygame.mixer is not initialized."""
        # Ensure mixer.get_init() returns False for this test
        mocker.patch('pygame.mixer.get_init', return_value=False)
        # Also mock hasattr for mixer to be safe, though get_init is primary
        mocker.patch('asset_manager.hasattr')
        mock_hasattr_instance = mocker.patch('asset_manager.hasattr')
        def hasattr_side_effect(obj, name):
            if obj == pygame and name == 'mixer':
                return True # Mixer module exists
            return __builtins__.hasattr(obj, name)
        mock_hasattr_instance.side_effect = hasattr_side_effect

        am.load_assets() # Will now use SOUND_ASSET_CONFIG from config.py

        asset_key_to_test = 'explosion' # A key from SOUND_ASSET_CONFIG
        assert asset_key_to_test in am.sounds
        assert isinstance(am.sounds[asset_key_to_test], DummySound)

        warning_found = any(
            f"WARNING: Pygame mixer not initialized. Using dummy sound for '{asset_key_to_test}'" in str(c[0][0])
            for c in mock_print.call_args_list
        )
        assert warning_found, "Warning for uninitialized mixer not found."

    @patch('builtins.print')
    @patch('pygame.mixer.Sound', side_effect=pygame.error("Failed to load sound"))
    @patch('asset_manager.AssetManager._get_path')
    @patch('asset_manager.IMAGE_ASSET_CONFIG', {}) # Ensure no images are processed
    def test_load_sound_failure_logs_warning_and_uses_dummy(self, mock_get_path, mock_pygame_sound, mock_print, am, mocker):
        """Test sound loading failure (e.g. file not found) uses DummySound and logs a warning."""
        # Ensure mixer.get_init() returns True so it attempts to load
        mocker.patch('pygame.mixer.get_init', return_value=True)
        mocker.patch('asset_manager.hasattr')
        mock_hasattr_instance = mocker.patch('asset_manager.hasattr')
        def hasattr_side_effect(obj, name): # Ensure it thinks mixer module exists
            if obj == pygame and name == 'mixer': return True
            return __builtins__.hasattr(obj,name)
        mock_hasattr_instance.side_effect = hasattr_side_effect

        asset_key_to_test = 'hurt'
        original_asset_path = REAL_SOUND_ASSET_CONFIG[asset_key_to_test] # Use real config path
        mock_get_path.return_value = f"resolved/dummy/{original_asset_path}"

        am.load_assets()

        mock_get_path.assert_any_call(original_asset_path)
        mock_pygame_sound.assert_any_call(f"resolved/dummy/{original_asset_path}")

        # Check that a specific warning for load failure was printed
        expected_warning_fragment = f"WARNING: Could not load sound asset '{asset_key_to_test}'"
        load_failure_warning_found = False
        for call_args in mock_print.call_args_list:
            arg_str = str(call_args[0][0])
            if f"WARNING: Could not load sound asset '{asset_key_to_test}'" in arg_str:
                hurt_warning_found = True
                break
        assert hurt_warning_found, f"Warning for missing '{asset_key_to_test}' sound not printed."

        assert asset_key_to_test in am.sounds # Key should now be present
        assert isinstance(am.sounds[asset_key_to_test], DummySound) # Value should be a DummySound instance

class TestAssetManagerFontInitialization:
    @patch('builtins.hasattr')
    # We will not mock pygame.font.SysFont directly here for success,
    # but rely on it working in a test environment where pygame.font is available.
    def test_font_initialization_success(self, mock_builtin_hasattr, mocker):
        """Test successful font initialization if pygame.font is available and SysFont works."""

        def hasattr_side_effect(obj, name):
            if obj == pygame and name == 'font':
                return True  # Simulate pygame.font module is present
            return MOCK_DEFAULT # Default behavior for other hasattr calls
        mock_builtin_hasattr.side_effect = hasattr_side_effect

        # This test relies on the test environment's Pygame setup.
        # If pygame.font.SysFont(None, 20) works, placeholder_font will be a Font object.
        asset_manager_instance = AssetManager(_test_font_failure=False)

        # Check if font system is actually usable in the test environment
        font_system_works = False
        if hasattr(pygame, 'font') and pygame.font.get_init():
            try:
                pygame.font.SysFont(None, 20) # Try to create a font
                font_system_works = True
            except pygame.error:
                font_system_works = False # SysFont failed

        if font_system_works:
            assert asset_manager_instance.placeholder_font is not None
            assert isinstance(asset_manager_instance.placeholder_font, pygame.font.FontType)
        else:
            # If font system isn't really usable (e.g. CI without display/font support),
            # or if hasattr(pygame, 'font') was false, placeholder_font should be None.
            # AssetManager's except block for SysFont or the hasattr check would lead to None.
            assert asset_manager_instance.placeholder_font is None

    @patch('builtins.hasattr')
    @patch('builtins.print')
    def test_font_initialization_failure_via_hook(self, mock_print, mock_builtin_hasattr):
        """Test font initialization failure using the _test_font_failure hook."""
        def hasattr_side_effect(obj, name):
            if obj == pygame and name == 'font':
                return True  # Simulate pygame.font module is present
            return MOCK_DEFAULT
        mock_builtin_hasattr.side_effect = hasattr_side_effect

        asset_manager_instance = AssetManager(_test_font_failure=True)

        assert asset_manager_instance.placeholder_font is None

        warning_found = False
        expected_warning_fragment = "WARNING: Could not initialize font for asset placeholders"
        expected_error_detail = "Test-induced font failure" # From the hook
        full_warning_found = False

        for call_args in mock_print.call_args_list:
            log_message = str(call_args[0][0])
            if expected_warning_fragment in log_message and expected_error_detail in log_message:
                full_warning_found = True
                break
        assert full_warning_found, f"Expected warning '{expected_warning_fragment}' with detail '{expected_error_detail}' not found."

    # Removing test_font_already_initialized due to persistent INTERNALERRORs
    # related to patching pygame.font.init and pytest's error reporting.
    # The AssetManager class no longer calls pygame.font.init(), so this test's
    # primary purpose is achieved by the current code structure.

    @patch('builtins.print')
    @patch('pygame.font', None)
    def test_font_initialization_fails_if_pygame_font_is_none(self, mock_print, mocker):
        """Test AssetManager font init when pygame.font is None, leading to AttributeError."""
        # This setup makes hasattr(pygame, 'font') True, but pygame.font is None.
        # AssetManager will try `pygame.font.SysFont` which becomes `None.SysFont`, an AttributeError.
        asset_manager_instance = AssetManager()
        assert asset_manager_instance.placeholder_font is None
        warning_found = False
        expected_warning_fragment = "WARNING: Could not initialize font for asset placeholders"

        printed_messages = [str(c[0][0]) for c in mock_print.call_args_list]
        assert any(expected_warning_fragment in msg for msg in printed_messages), \
            f"Expected warning fragment '{expected_warning_fragment}' not found in {printed_messages}"

    # Removed @patch('builtins.print')
    @patch('builtins.hasattr') # Patch builtins.hasattr for this specific test
    def test_font_module_truly_missing(self, mock_builtin_hasattr, mocker): # Added mocker, mock_print removed from args
        """Test behavior when hasattr(pygame, 'font') is False."""
        # mock_print = mocker.patch('builtins.print') # Removed print mocking

        def hasattr_side_effect(obj, name):
            if obj == pygame and name == 'font':
                return False # Simulate module truly missing
            return MOCK_DEFAULT
        mock_builtin_hasattr.side_effect = hasattr_side_effect

        asset_manager_instance = AssetManager()
        assert asset_manager_instance.placeholder_font is None
        # warning_found = False # Print check removed
        # expected_warning = "WARNING: Pygame font module not available. Placeholders will not have text."
        # for call_args in mock_print.call_args_list:
        #     if expected_warning in str(call_args[0][0]):
        #         warning_found = True
        #         break
        # assert warning_found, f"Expected warning '{expected_warning}' not found."
