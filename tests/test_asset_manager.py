import pytest
from unittest.mock import patch, MagicMock
import pygame # Needed for pygame.Surface, pygame.error, pygame.font, pygame.mixer types
from asset_manager import AssetManager, DummySound # The class we're testing and DummySound

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

    @patch('builtins.print') # Mock print to check warnings
    @patch('pygame.image.load', side_effect=pygame.error("Failed to load image"))
    @patch('asset_manager.AssetManager._get_path')
    @patch('pygame.Surface') # Patch pygame.Surface
    def test_load_image_failure_creates_placeholder(self, mock_pygame_surface, mock_get_path, mock_pygame_load, mock_print, am):
        """Test image loading failure creates a placeholder and logs a warning."""
        mock_placeholder_surf = MagicMock() # Removed spec=pygame.Surface
        mock_placeholder_surf.convert_alpha.return_value = mock_placeholder_surf
        mock_placeholder_surf.get_width.return_value = 100 # Match placeholder size in AssetManager
        mock_placeholder_surf.get_height.return_value = 50
        mock_pygame_surface.return_value = mock_placeholder_surf # Ensure pygame.Surface() returns our mock

        dummy_path = "dummy/path/to/failing_image.png"
        mock_get_path.return_value = dummy_path

        # Test with 'grass' asset for failure
        am.load_assets()

        assert 'grass' in am.images
        placeholder = am.images['grass']
        # pygame.Surface is mocked in this test, placeholder is the mock_placeholder_surf instance
        assert placeholder is mock_placeholder_surf
        # Check for the specific DEBUG prints related to placeholder creation
        # Example: print(f"DEBUG: Placeholder for '{key}' assigned in self.images. Type: {type(self.images[key])}")
        #          print(f"DEBUG: Keys in self.images after trying to set '{key}': {list(self.images.keys())}")

        # Check that a warning was printed for 'grass'
        # Example: print(f"WARNING: Could not load image asset '{key}' from '{path}': {e}. Creating placeholder.")
        # We need to find the call to print that contains the relevant warning.
        # This is tricky because other assets might load successfully or also fail.
        # Let's check if any print call contains "WARNING: Could not load image asset 'grass'"
        grass_warning_found = False

        for call_args in mock_print.call_args_list:
            arg_str = str(call_args[0][0]) # Get the first positional argument of the print call
            if "WARNING: Could not load image asset 'grass'" in arg_str:
                grass_warning_found = True
                break # Found the warning, no need to check further prints for this

        assert grass_warning_found, "Warning for missing 'grass' asset not printed."

        # Verify placeholder properties (e.g., size, or that it's not the mocked successful surface)
        assert placeholder.get_width() == 100 # As defined in AssetManager for placeholder
        assert placeholder.get_height() == 50


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
    @patch('pygame.font', None) # Attempt to effectively remove pygame.font for this test
    def test_pygame_font_module_missing_by_patching_module(self, mock_print, mocker):
        """Test behavior if pygame.font is None (simulating module not available)."""
        # This approach of patching 'pygame.font' to None might not always work as expected
        # depending on how AssetManager imports or accesses it, and Pytest's isolation.
        # A more robust way would be to mock `hasattr(pygame, 'font')` to return False.
        # However, let's try this simpler patch first.

        # We need to control 'hasattr(pygame, 'font')' for the AssetManager's __init__
        # Patching 'pygame.font' to None should make hasattr(pygame, 'font') behave as if it's not there,
        # if pygame itself doesn't complain about its 'font' attribute being None.
        # A more direct approach for `if hasattr(pygame, 'font')` in AssetManager:
        with patch('asset_manager.hasattr') as mock_hasattr:
            # Configure mock_hasattr to return False only when checking for 'font' on 'pygame'
            def hasattr_side_effect(obj, name):
                if obj == pygame and name == 'font':
                    return False
                # For any other hasattr call, use the real hasattr
                # This requires having access to the original hasattr if we were replacing it globally.
                # Since we are patching 'asset_manager.hasattr', it's simpler:
                return __builtins__.hasattr(obj, name)

            # It's better to patch where it's used if possible:
            # If AssetManager did `from os import path`, we'd patch `asset_manager.path`.
            # Since it's `hasattr(pygame, 'font')`, we patch `hasattr` in the scope of `asset_manager` module.
            # However, `hasattr` is a builtin. Patching `asset_manager.hasattr` won't work unless
            # `asset_manager.py` does `import builtins; builtins.hasattr`.
            # The most reliable is to patch `hasattr` globally for the test or use `mocker.patch.object(pygame, 'font', create=True, new=None)`
            # if that worked, but `font` is a module.

            # Let's try patching `hasattr` globally for this test's scope using mocker.
            # This is generally risky but can work for specific scenarios.
            # A better solution might be to refactor AssetManager to allow injecting dependencies like `hasattr`.

            # Sticking to the plan: the code in AssetManager is `if hasattr(pygame, 'font'):`
            # So, we need `hasattr(pygame, 'font')` to be false.
            # `mocker.patch.object(pygame, 'font', create=True)` can be used to add an attribute if it's missing.
            # To simulate it missing, we can try to `delattr` if it exists, or ensure `hasattr` returns False.

            # Let's assume the `if hasattr(pygame, 'font')` check is what we need to influence.
            # The `AssetManager` uses `pygame.font.init()` and `pygame.font.SysFont()`.
            # If `pygame.font` is None, these will fail.
            # The `hasattr(pygame, 'font')` check in `AssetManager` is the first gate.

            mocker.patch('asset_manager.pygame.font', None) # Make pygame.font None for this test
            # This will cause `hasattr(pygame, 'font')` to be True (as 'font' attr exists, value is None)
            # but subsequent `pygame.font.init()` will fail. AssetManager's `hasattr` check is too simple.
            # AssetManager should ideally check `if getattr(pygame, 'font', None) is not None:`

            # Given current AssetManager code `if hasattr(pygame, 'font'):`
            # and then `pygame.font.init()`, if `pygame.font` is `None`, `pygame.font.init()` will raise AttributeError.
            # The `except Exception as e:` in AssetManager should catch this.

            asset_manager_instance = AssetManager() # This will now run with pygame.font = None

            assert asset_manager_instance.placeholder_font is None
            warning_found = False
            # The warning will be "Could not initialize font" because `pygame.font.init()` will fail.
            # The "Pygame font module not available" warning is if `hasattr(pygame, 'font')` is false.
            expected_warning = "WARNING: Could not initialize font for asset placeholders"
            # If `pygame.font` is truly absent (not just None), then "Pygame font module not available"
            # For this test, patching to None makes `pygame.font.init()` fail.

            for call_args in mock_print.call_args_list:
                if expected_warning in str(call_args[0][0]):
                    warning_found = True
                    break
            assert warning_found, f"Expected warning '{expected_warning}' not found."

    @patch('builtins.print')
    @patch('asset_manager.hasattr') # Patch hasattr in the asset_manager's scope
    def test_font_module_truly_missing(self, mock_hasattr, mock_print):
        """Test behavior when hasattr(pygame, 'font') is False."""

        # Configure mock_hasattr to return False only when checking for 'font' on 'pygame'
        def hasattr_side_effect(obj, name):
            if obj == pygame and name == 'font':
                return False
            return __builtins__.hasattr(obj, name) # Call real hasattr for other checks
        mock_hasattr.side_effect = hasattr_side_effect

        asset_manager_instance = AssetManager()

        assert asset_manager_instance.placeholder_font is None
        warning_found = False
        expected_warning = "WARNING: Pygame font module not available. Placeholders will not have text."
        for call_args in mock_print.call_args_list:
            if expected_warning in str(call_args[0][0]):
                warning_found = True
                break
        assert warning_found, f"Expected warning '{expected_warning}' not found."
