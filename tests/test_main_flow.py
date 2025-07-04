import pytest
import pygame
from unittest.mock import patch, MagicMock
import asset_manager # Import the module to be patched
import argparse # Import argparse
import config # Import config to access its constants in the fixture

# Mocker les modules Pygame qui posent problème en environnement headless
# Cela doit être fait avant d'importer les modules du jeu qui les utilisent.
mock_pygame_display = MagicMock()
mock_pygame_mixer = MagicMock()
mock_pygame_font = MagicMock()

# Appliquer les mocks au niveau du module sys.modules
# pour que tous les imports de ces modules utilisent nos mocks.
@pytest.fixture(autouse=True)
def mock_pygame_modules(monkeypatch):
    # Mock for screen surface and its methods
    mock_screen_surface = MagicMock()
    mock_screen_surface.get_size.return_value = (1920, 1080) # Default screen size for tests
    mock_screen_surface.get_width.return_value = 1920
    mock_screen_surface.get_height.return_value = 1080

    monkeypatch.setattr(pygame, 'display', mock_pygame_display)
    monkeypatch.setattr(pygame.display, 'set_mode', MagicMock(return_value=mock_screen_surface))
    monkeypatch.setattr(pygame.display, 'set_icon', MagicMock())
    monkeypatch.setattr(pygame.display, 'flip', MagicMock()) # Nécessaire si main_loop est appelé


    # Store real classes before they are potentially mocked globally
    real_pygame_surface = pygame.Surface
    real_pygame_rect = pygame.Rect

    # Mock pygame.image.load to return a mock surface instance
    # This mock_image_surface will be used for most loaded images via AssetManager
    mock_image_surface = MagicMock(spec=real_pygame_surface)
    mock_image_surface.convert_alpha.return_value = mock_image_surface
    mock_image_surface.get_width.return_value = 50  # Default width
    mock_image_surface.get_height.return_value = 50 # Default height
    mock_image_surface.get_rect.return_value = real_pygame_rect(0,0,50,50)
    mock_image_surface.get_size.return_value = (50,50)
    # Add a blit method to this general mock surface, in case it's directly blitted (e.g. Buttons)
    mock_image_surface.blit = MagicMock()


    monkeypatch.setattr(pygame, 'image', MagicMock()) # Mock the image module itself
    monkeypatch.setattr(pygame.image, 'load', MagicMock(return_value=mock_image_surface))

    # Now, mock pygame.Surface globally so that calls to pygame.Surface() in main.py
    # return a mock that has a blit method which can accept other mocks.
    # This is for surfaces created directly in code, like 'grass_background'.
    mock_created_surface_instance = MagicMock(spec=real_pygame_surface)
    mock_created_surface_instance.blit = MagicMock() # This blit can accept MagicMocks
    mock_created_surface_instance.convert_alpha.return_value = mock_created_surface_instance
    mock_created_surface_instance.get_rect.return_value = real_pygame_rect(0,0,100,100) # Example default
    mock_created_surface_instance.get_width.return_value = 100
    mock_created_surface_instance.get_height.return_value = 100

    monkeypatch.setattr(pygame, 'Surface', MagicMock(return_value=mock_created_surface_instance))

    monkeypatch.setattr(pygame, 'mouse', MagicMock())
    monkeypatch.setattr(pygame.mouse, 'set_visible', MagicMock())
    monkeypatch.setattr(pygame.mouse, 'get_pos', MagicMock(return_value=(0,0)))


    monkeypatch.setattr(pygame, 'mixer', mock_pygame_mixer)
    monkeypatch.setattr(pygame.mixer, 'music', MagicMock())
    monkeypatch.setattr(pygame.mixer.music, 'load', MagicMock())
    monkeypatch.setattr(pygame.mixer.music, 'play', MagicMock())
    monkeypatch.setattr(pygame.mixer.music, 'stop', MagicMock())
    monkeypatch.setattr(pygame.mixer.music, 'get_busy', MagicMock(return_value=False))


    # Mocker AssetManager pour éviter le chargement réel des fichiers
    # et les problèmes avec les sons/images dans un environnement de test.
    mock_asset_manager_instance = MagicMock()

    # Create mock rects with width and height attributes for buttons
    mock_start_rect = MagicMock(spec=real_pygame_rect) # Use real_pygame_rect for spec
    mock_start_rect.width = 100
    mock_start_rect.height = 50

    mock_exit_rect = MagicMock(spec=real_pygame_rect) # Use real_pygame_rect for spec
    mock_exit_rect.width = 100
    mock_exit_rect.height = 50

    mock_restart_rect = MagicMock(spec=real_pygame_rect) # Use real_pygame_rect for spec
    mock_restart_rect.width = 100
    mock_restart_rect.height = 50

    # Use the general mock_image_surface for images that need to behave like surfaces
    # This mock_image_surface is already configured with get_width, get_height, convert_alpha etc.
    # For specific images needing different dimension mocks, they can be individual MagicMocks.

    # Specific mock for start_screen due to its large dimensions used in calculations
    mock_start_screen_surface = MagicMock(spec=real_pygame_surface) # Use real_pygame_surface for spec
    mock_start_screen_surface.convert_alpha.return_value = mock_start_screen_surface
    mock_start_screen_surface.get_width.return_value = 1920
    mock_start_screen_surface.get_height.return_value = 1080
    mock_start_screen_surface.get_rect.return_value = real_pygame_rect(0,0,1920,1080)

    # Define a list of common image keys that can use the generic mock_image_surface
    common_image_keys = [
        'icon', 'carrot', 'vampire', 'hp', 'game_over', 'grass', 'garlic',
        'crosshair', 'bullet', 'explosion', 'rabbit', 'carrot_juice',
        'digit_0', 'digit_1', 'digit_2', 'digit_3', 'digit_4',
        'digit_5', 'digit_6', 'digit_7', 'digit_8', 'digit_9'
    ]

    mock_asset_manager_instance.images = {
        key: mock_image_surface for key in common_image_keys
    }

    # Add/override specific mocks
    mock_asset_manager_instance.images['start_screen'] = mock_start_screen_surface

    # For button images, they use mock_image_surface by default through pygame.image.load mock,
    # but their get_rect methods need to return specific rects for positioning logic in main.py
    # So, we ensure these specific rects are available.
    # Create new mocks for these specific images if they need distinct properties beyond get_rect
    # or re-assign if mock_image_surface is sufficient but just need to override get_rect.

    start_button_mock_img = MagicMock(spec=real_pygame_surface)
    start_button_mock_img.get_rect.return_value = mock_start_rect
    start_button_mock_img.get_width.return_value = mock_start_rect.width # Consistent width
    start_button_mock_img.get_height.return_value = mock_start_rect.height # Consistent height
    start_button_mock_img.convert_alpha.return_value = start_button_mock_img

    exit_button_mock_img = MagicMock(spec=real_pygame_surface)
    exit_button_mock_img.get_rect.return_value = mock_exit_rect
    exit_button_mock_img.get_width.return_value = mock_exit_rect.width
    exit_button_mock_img.get_height.return_value = mock_exit_rect.height
    exit_button_mock_img.convert_alpha.return_value = exit_button_mock_img

    restart_button_mock_img = MagicMock(spec=real_pygame_surface)
    restart_button_mock_img.get_rect.return_value = mock_restart_rect
    restart_button_mock_img.get_width.return_value = mock_restart_rect.width
    restart_button_mock_img.get_height.return_value = mock_restart_rect.height
    restart_button_mock_img.convert_alpha.return_value = restart_button_mock_img

    mock_asset_manager_instance.images['start'] = start_button_mock_img
    mock_asset_manager_instance.images['exit'] = exit_button_mock_img
    mock_asset_manager_instance.images['restart'] = restart_button_mock_img
    mock_asset_manager_instance.images['continue_button'] = mock_image_surface # Corrected key
    mock_asset_manager_instance.images['settings_button'] = mock_image_surface # Corrected key


    # The general mock_image_surface already has a get_rect returning a 50x50 rect.
    # This should be sufficient for other images like 'carrot', 'vampire', 'hp', 'game_over', 'crosshair'
    # as their exact rect dimensions are not as critical for the current tests as button rects are for positioning.
    # Thus, the explicit get_rect overrides below are removed.
    # mock_asset_manager_instance.images['carrot'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))
    # mock_asset_manager_instance.images['vampire'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))
    # mock_asset_manager_instance.images['hp'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))
    # mock_asset_manager_instance.images['game_over'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))
    # mock_asset_manager_instance.images['crosshair'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))

    mock_asset_manager_instance.sounds = {
        'press_start': MagicMock(),
        'death': MagicMock(),
    }
    # mock_asset_manager_instance._get_path = lambda asset_name_or_path: "dummy_lambda_path" # Removed: _get_path is no longer on AssetManager

    # Patch la classe AssetManager dans le module 'asset_manager' pour qu'elle retourne notre instance mockée.
    # Cela assure que `main.asset_manager` sera notre `mock_asset_manager_instance`.
    # Ce patch est appliqué pour toute la durée de la fixture (et donc pour chaque test utilisant cette fixture).
    # unittest.mock.patch en tant que décorateur ou context manager serait utilisé au niveau de chaque test
    # si on ne voulait pas que le patch soit actif globalement pendant la fixture.
    # Ici, comme la fixture est autouse=True et configure l'environnement pour tous les tests du module,
    # monkeypatch.setattr est acceptable et cohérent avec les autres patchs de la fixture.
    # La suggestion de la revue de code d'utiliser `with patch(...)` serait plus pertinente si on importait `main`
    # une seule fois en haut du fichier test et qu'on voulait isoler le patch de AssetManager pour des tests spécifiques.
    # Étant donné que `main` est importé dans chaque test, le monkeypatch appliqué par la fixture
    # sera actif au moment de cet import.
    monkeypatch.setattr(asset_manager, 'AssetManager', MagicMock(return_value=mock_asset_manager_instance))

    # Mock the centralized get_asset_path function as it's imported and used in main.py
    # This ensures that when _play_game_music_and_sound calls get_asset_path, it gets our mock.
    def mock_main_get_asset_path(path_arg):
        # Allow specific paths to be mocked for music loading checks
        if path_arg == config.MUSIC_GAME: # Used in start_game and reset_game
            return "dummy_lambda_path"
        elif path_arg == config.MUSIC_INTRO: # Used in main global scope
            return "dummy_intro_path"
        elif path_arg == config.MUSIC_GAMEOVER: # Used in run_gui_mode
            return "dummy_gameover_path"
        # Fallback for any other asset paths if get_asset_path is called for them within main's scope
        return f"resolved_utility_path_for_{path_arg}"

    # We need to ensure 'main' module is loaded or patchable by pytest/mocker when this fixture runs.
    # Since tests import 'main' individually, we use monkeypatch which is already an argument.
    # Patching 'main.get_asset_path' as this is the name used within main.py after `from utilities import get_asset_path`
    monkeypatch.setattr('main.get_asset_path', mock_main_get_asset_path)

    # Create a default 'args' object and set it in the 'main' module's namespace.
    # The tests in this file will import 'main', and the functions within 'main'
    # (like _play_game_music_and_sound, start_game, etc.) will then find `main.args`.
    default_args = argparse.Namespace(cli=False, debug=True) # Default to non-CLI, debug True for tests
    monkeypatch.setattr('main.args', default_args)

    # Set main.asset_manager to the mock_asset_manager_instance created in this fixture.
    # This ensures that functions in main.py use the mocked AssetManager.
    monkeypatch.setattr('main.asset_manager', mock_asset_manager_instance)

    # Create a mock GameState and set it as main.game_state.
    # This allows tests to manipulate main.game_state.started, etc.
    # The GameState is instantiated with the (mocked) asset_manager.
    # We also pass the default_args.cli to its constructor.
    import main # Import main here to allow GameState to be potentially patched if needed, though not currently
    from game_state import GameState # Import GameState for spec if desired

    # We need a GameState that uses the mock_asset_manager_instance.
    # The AssetManager class is already patched to return mock_asset_manager_instance.
    # So, if GameState was instantiated here using `GameState(main.asset_manager, ...)`
    # it would correctly receive the mock.
    # However, main.py's functions will refer to `main.game_state`.
    # We need `main.game_state` to be a valid, controllable object for the tests.

    _mock_gs = MagicMock(spec=GameState) # Use spec for better type checking
    _mock_gs.started = False
    _mock_gs.paused = False
    _mock_gs.game_over = False
    _mock_gs.player = MagicMock()
    _mock_gs.player.health = main.START_HEALTH # Access START_HEALTH from main's imported config
    _mock_gs.asset_manager = mock_asset_manager_instance # Ensure the mock GameState uses the mock AssetManager
    _mock_gs.cli_mode = default_args.cli

    # Configure the mock's reset method to simulate the real reset behavior for 'started', 'game_over', 'paused'
    def mock_reset_side_effect():
        _mock_gs.started = False
        _mock_gs.game_over = False
        _mock_gs.paused = False
        # Simulate other reset actions if necessary for other tests
        _mock_gs.player.health = main.START_HEALTH # Use main.START_HEALTH for consistency
        # Add other resets like bullets = [], items = [], etc. if tests depend on them after reset
        # For example:
        # _mock_gs.bullets = []
        # _mock_gs.items = []
        # _mock_gs.vampire_killed_count = 0
    _mock_gs.reset = MagicMock(side_effect=mock_reset_side_effect)

    # Mock pause_game and resume_game to modify the mock's 'paused' attribute
    def mock_pause_game_side_effect():
        _mock_gs.paused = True
    _mock_gs.pause_game = MagicMock(side_effect=mock_pause_game_side_effect)

    def mock_resume_game_side_effect():
        _mock_gs.paused = False
    _mock_gs.resume_game = MagicMock(side_effect=mock_resume_game_side_effect)

    monkeypatch.setattr('main.game_state', _mock_gs)

    # Also, button image variables in main.py need to be populated from the mock_asset_manager
    # as Button() instances are created at global scope in main.py using these.
    # These are now moved to main_entry_point, so this direct patching might be less critical
    # if tests are structured to call main_entry_point or if Button creation is also mocked/deferred.
    # However, to be safe for any test importing main and expecting these to be somewhat valid:
    monkeypatch.setattr('main.start_button_img', mock_asset_manager_instance.images.get('start'))
    monkeypatch.setattr('main.exit_button_img', mock_asset_manager_instance.images.get('exit'))
    monkeypatch.setattr('main.restart_button_img', mock_asset_manager_instance.images.get('restart'))
    monkeypatch.setattr('main.continue_button_img', mock_asset_manager_instance.images.get('continue_button'))
    monkeypatch.setattr('main.settings_button_img', mock_asset_manager_instance.images.get('settings_button'))

    # Initialize global rects in main, as Button() calls might use their .width/.height
    # These are initialized to Rect(0,0,0,0) in main.py. For tests, if Button() constructor
    # relies on these having dimensions from loaded images, we should provide mocks.
    # The mock_asset_manager_instance.images already provide mock surfaces with get_rect().
    # The current Button constructor in main.py uses these image objects directly.
    # The _*_width variables in main_entry_point handle cases where images are not surfaces (CLI).
    # So this part should be fine as long as the image mocks in asset_manager have get_rect.
    # The global rects (e.g., main.restart_button_rect) are used if not args.cli for some calculations.
    # Let's ensure they are at least valid pygame.Rect objects.
    monkeypatch.setattr('main.restart_button_rect', mock_asset_manager_instance.images['restart'].get_rect())
    monkeypatch.setattr('main.exit_button_rect', mock_asset_manager_instance.images['exit'].get_rect())
    monkeypatch.setattr('main.start_button_rect', mock_asset_manager_instance.images['start'].get_rect())
    monkeypatch.setattr('main.continue_button_rect', mock_asset_manager_instance.images['continue_button'].get_rect())
    monkeypatch.setattr('main.settings_button_rect', mock_asset_manager_instance.images['settings_button'].get_rect())


# NOTE: L'import de `main` est fait dans chaque fonction de test ci-dessous.
# Idéalement, `main.py` serait structuré pour que son initialisation puisse être
# appelée explicitement, permettant un import unique en haut du fichier de test
# et un meilleur contrôle de l'état global pour l'isolation des tests.
# Pour l'instant, cette approche fonctionne car la fixture `mock_pygame_modules`
# (qui est autouse=True) réinitialise les mocks nécessaires avant chaque test,
# y compris le patch de `asset_manager.AssetManager`.

def test_game_initialization_no_errors():
    """
    Teste si l'importation de main.py et l'initialisation des variables globales
    (y compris les boutons qui utilisent start_game etc.) se passent sans erreur.
    """
    try:
        # Le patch de AssetManager est déjà actif grâce à la fixture autouse=True.
        with patch('pygame.quit'), patch('sys.exit'): # Empêche la fermeture de Pygame/sys
             # L'import de main exécute le code au niveau global
            import main
            # Vérifier que les listes de boutons ont été créées (signe d'initialisation)
            assert hasattr(main, 'start_screen_buttons')
            # assert len(main.start_screen_buttons) > 0 # Buttons are initialized in main_entry_point now
            assert hasattr(main, 'game_over_buttons')
            # assert len(main.game_over_buttons) > 0 # Buttons are initialized in main_entry_point now
            # On pourrait ajouter plus d'assertions ici si nécessaire
    except Exception as e:
        pytest.fail(f"L'initialisation du jeu a levé une exception: {e}")

def test_start_game_functionality(mock_pygame_modules):
    """Teste si la fonction start_game modifie correctement l'état du jeu."""
    import main # Importer après que les mocks soient actifs

    # S'assurer que le jeu n'est pas démarré initialement et réinitialiser le mock du son spécifique
    main.game_state.started = False
    main.asset_manager.sounds['press_start'].play.reset_mock()

    # Appeler la fonction start_game
    main.start_game()

    # Vérifier que l'état du jeu a changé
    assert main.game_state.started == True
    # Vérifier que la musique du jeu a été jouée et que le son du bouton a été joué
    main.asset_manager.sounds['press_start'].play.assert_called_once()

    # et si sa méthode _get_path est bien notre lambda
    # NOTE: Debug assertion removed.

    pygame.mixer.music.load.assert_called_with("dummy_lambda_path") # MUSIC_GAME
    pygame.mixer.music.play.assert_called_with(-1)

def test_reset_game_functionality(mock_pygame_modules):
    """Teste si la fonction reset_game réinitialise correctement l'état du jeu."""
    import main

    # Simuler un état de jeu modifié et réinitialiser le mock du son spécifique
    main.game_state.started = True
    main.game_state.game_over = True
    main.game_state.player.health = 0
    main.asset_manager.sounds['press_start'].play.reset_mock()

    main.reset_game()

    assert main.game_state.started == False
    assert main.game_state.game_over == False
    assert main.game_state.player.health == main.START_HEALTH # Vérifier une valeur spécifique réinitialisée
    main.asset_manager.sounds['press_start'].play.assert_called_once()

    # NOTE: Debug assertion removed.

    pygame.mixer.music.load.assert_called_with("dummy_lambda_path") # MUSIC_GAME
    pygame.mixer.music.play.assert_called_with(-1)

def test_quit_game_functionality(mock_pygame_modules):
    """Teste si la fonction quit_game met la variable running à False."""
    import main

    main.running = True # S'assurer que running est True
    main.quit_game()
    assert main.running == False

# On pourrait ajouter un test qui simule un clic sur un bouton
# mais cela devient plus complexe car il faut simuler la boucle d'événements de Pygame.
# Pour l'instant, ces tests couvrent l'initialisation et les callbacks.
