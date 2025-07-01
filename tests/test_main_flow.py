import pytest
import pygame
from unittest.mock import patch, MagicMock
import asset_manager # Import the module to be patched

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
    mock_start_screen_surface.get_rect.return_value = pygame.Rect(0,0,1920,1080)


    mock_asset_manager_instance.images = {
            'icon': mock_image_surface, # pygame.display.set_icon(asset_manager.images['icon'])
            'start_screen': mock_start_screen_surface, # screen.blit(start_screen_image, start_screen_pos)
            'start': mock_image_surface, # Passed to Button, then blitted
            'exit': mock_image_surface, # Passed to Button, then blitted
            'restart': mock_image_surface, # Passed to Button, then blitted
            'carrot': mock_image_surface, # game_entities.Carrot(asset_manager.images['carrot']), then blitted
            'vampire': mock_image_surface,
            'hp': mock_image_surface, # player.draw_ui uses this
            'game_over': mock_image_surface, # screen.blit(game_over_image, ...)
            'grass': mock_image_surface, # grass_background.blit(grass_image, ...)
            'garlic': mock_image_surface, # player.draw_ui uses this / garlic_shot blit
            'crosshair': mock_image_surface, # screen.blit(crosshair_img, ...)
            'bullet': mock_image_surface,
            'explosion': mock_image_surface,
            'rabbit': mock_image_surface,
            'carrot_juice': mock_image_surface,
            'digit_0': mock_image_surface, 'digit_1': mock_image_surface, 'digit_2': mock_image_surface,
            'digit_3': mock_image_surface, 'digit_4': mock_image_surface, 'digit_5': mock_image_surface,
            'digit_6': mock_image_surface, 'digit_7': mock_image_surface, 'digit_8': mock_image_surface,
            'digit_9': mock_image_surface,
    }
    # Ensure get_rect is available for rect-based positioning if not covered by mock_image_surface
    mock_asset_manager_instance.images['start'].get_rect = lambda: mock_start_rect
    mock_asset_manager_instance.images['exit'].get_rect = lambda: mock_exit_rect
    mock_asset_manager_instance.images['restart'].get_rect = lambda: mock_restart_rect
    # For other images that might use get_rect directly from asset_manager.images in main
    mock_asset_manager_instance.images['carrot'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))
    mock_asset_manager_instance.images['vampire'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))
    mock_asset_manager_instance.images['hp'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))
    mock_asset_manager_instance.images['game_over'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))
    mock_asset_manager_instance.images['crosshair'].get_rect = MagicMock(return_value=pygame.Rect(0,0,10,10))


    mock_asset_manager_instance.sounds = {
        'press_start': MagicMock(),
        'death': MagicMock(),
    }
    # Configure the _get_path method on the mock_asset_manager_instance itself
    # Using a lambda to ensure it's called and returns the dummy path directly.
    mock_asset_manager_instance._get_path = lambda asset_name_or_path: "dummy_lambda_path"

    # Patch la classe AssetManager dans le module 'asset_manager' pour qu'elle retourne notre instance mockée.
    # Cela affectera l'instanciation dans main.py lors de son import.
    monkeypatch.setattr(asset_manager, 'AssetManager', MagicMock(return_value=mock_asset_manager_instance))
    # game_state.py receives the asset_manager instance from main.py, so no need to patch 'game_state.AssetManager'
    # game_entities.py also receives the instance or uses the one from game_state, so direct patching there might also be unneeded
    # if all instances originate from the one created in main.py.


def test_game_initialization_no_errors():
    """
    Teste si l'importation de main.py et l'initialisation des variables globales
    (y compris les boutons qui utilisent start_game etc.) se passent sans erreur.
    """
    try:
        with patch('pygame.quit'), patch('sys.exit'): # Empêche la fermeture de Pygame/sys
             # L'import de main exécute le code au niveau global
            import main
            # Vérifier que les listes de boutons ont été créées (signe d'initialisation)
            assert hasattr(main, 'start_screen_buttons')
            assert len(main.start_screen_buttons) > 0
            assert hasattr(main, 'game_over_buttons')
            assert len(main.game_over_buttons) > 0
            # On pourrait ajouter plus d'assertions ici si nécessaire
    except Exception as e:
        pytest.fail(f"L'initialisation du jeu a levé une exception: {e}")

def test_start_game_functionality(mock_pygame_modules):
    """Teste si la fonction start_game modifie correctement l'état du jeu."""
    import main # Importer après que les mocks soient actifs

    # S'assurer que le jeu n'est pas démarré initialement
    main.game_state.started = False

    # Appeler la fonction start_game
    main.start_game()

    # Vérifier que l'état du jeu a changé
    assert main.game_state.started == True
    # Vérifier que la musique du jeu a été jouée (via le mock)
    main.asset_manager.sounds['press_start'].play.assert_not_called() # Ce son est pour le clic, pas start_game directement

    # Pour déboguer, vérifions quel est l'objet asset_manager dans main
    # et si sa méthode _get_path est bien notre lambda
    # Ceci est une assertion de débogage, peut être retirée plus tard
    assert main.asset_manager._get_path("test") == "dummy_lambda_path", \
        f"main.asset_manager._get_path n'est pas le mock attendu. Type: {type(main.asset_manager._get_path)}"

    pygame.mixer.music.load.assert_called_with("dummy_lambda_path") # MUSIC_GAME
    pygame.mixer.music.play.assert_called_with(-1)

def test_reset_game_functionality(mock_pygame_modules):
    """Teste si la fonction reset_game réinitialise correctement l'état du jeu."""
    import main

    # Simuler un état de jeu modifié
    main.game_state.started = True
    main.game_state.game_over = True
    main.game_state.player.health = 0

    main.reset_game()

    assert main.game_state.started == False
    assert main.game_state.game_over == False
    assert main.game_state.player.health == main.START_HEALTH # Vérifier une valeur spécifique réinitialisée

    # Assertion de débogage
    assert main.asset_manager._get_path("test") == "dummy_lambda_path", \
        f"main.asset_manager._get_path n'est pas le mock attendu. Type: {type(main.asset_manager._get_path)}"

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
