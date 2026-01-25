# asset_manager.py
# This file defines the AssetManager class, responsible for loading and managing game assets
# such as images and sounds. It includes fallback mechanisms for missing assets, ensuring
# the game can run even if some files are unavailable by using placeholders or dummy objects.
# It also handles path resolution for assets, whether the game is run from source or as a
# frozen executable.
#
# *Ce fichier définit la classe AssetManager, responsable du chargement et de la gestion
# *des ressources du jeu telles que les images et les sons. Il inclut des mécanismes de
# *remplacement pour les ressources manquantes, assurant que le jeu puisse fonctionner
# *même si certains fichiers ne sont pas disponibles, en utilisant des images de substitution
# *ou des objets factices. Il gère également la résolution des chemins pour les ressources,
# *que le jeu soit exécuté depuis les sources ou comme un exécutable figé.*

import logging
import os
import sys

import pygame

from config import (  # Import new configs
    DEFAULT_PLACEHOLDER_SIZE,
    IMAGE_ASSET_CONFIG,
    PLACEHOLDER_BG_COLOR,
    PLACEHOLDER_FONT_SIZE,
    PLACEHOLDER_TEXT_COLOR,
    SOUND_ASSET_CONFIG,
)
from utilities import get_asset_path  # Import the centralized function

# It's good practice to initialize pygame.font if you're going to use it.
# This should ideally be done once at the start of the game (e.g., in main.py after pygame.init()).
# However, for AssetManager to be self-contained in creating fallback surfaces,
# we might ensure font is initialized here or rely on main.py having done it.
# For now, let's assume main.py handles pygame.init() and pygame.font.init().
# If not, AssetManager might need its own pygame.font.init() call,
# or font creation might fail.
#
# *C'est une bonne pratique d'initialiser pygame.font si vous comptez l'utiliser.*
# *Idéalement, cela devrait être fait une fois au début du jeu (par exemple, dans main.py après pygame.init()).*
# *Cependant, pour que AssetManager soit autonome dans la création de surfaces de remplacement,*
# *nous pourrions nous assurer que la police est initialisée ici ou compter sur main.py pour l'avoir fait.*
# *Pour l'instant, supposons que main.py gère pygame.init() et pygame.font.init().*
# *Sinon, AssetManager pourrait avoir besoin de son propre appel pygame.font.init(),*
# *ou la création de la police pourrait échouer.*


class DummySound:
    """
    A dummy sound object with no-op methods.
    Used as a fallback when a sound file cannot be loaded or in CLI mode.
    Ensures that game code attempting to use a sound object doesn't crash.

    *Un objet son factice avec des méthodes qui ne font rien.*
    *Utilisé comme solution de secours lorsqu'un fichier son ne peut pas être chargé ou en mode CLI.*
    *Assure que le code du jeu tentant d'utiliser un objet son ne plante pas.*
    """

    def play(self, *args, **kwargs):
        """No-op play method. / *Méthode play qui ne fait rien.*"""
        pass

    def stop(self, *args, **kwargs):
        """No-op stop method. / *Méthode stop qui ne fait rien.*"""
        pass

    def fadeout(self, *args, **kwargs):
        """No-op fadeout method. / *Méthode fadeout qui ne fait rien.*"""
        pass

    def set_volume(self, *args, **kwargs):
        """No-op set_volume method. / *Méthode set_volume qui ne fait rien.*"""
        pass

    def get_volume(self, *args, **kwargs):
        """Returns a default volume. / *Retourne un volume par défaut.*"""
        return 0.0

    def get_length(self, *args, **kwargs):
        """Returns a default length. / *Retourne une longueur par défaut.*"""
        return 0.0

    # Add any other methods that might be called on a Sound object to prevent AttributeErrors
    # For now, play() is the most critical.
    # *Ajoutez toute autre méthode qui pourrait être appelée sur un objet Sound pour éviter les AttributeError.*
    # *Pour l'instant, play() est la plus critique.*


class AssetManager:
    """
    Manages loading and storage of game assets like images and sounds.
    Provides fallbacks for missing assets.

    *Gère le chargement et le stockage des ressources du jeu comme les images et les sons.*
    *Fournit des solutions de remplacement pour les ressources manquantes.*
    """

    def __init__(self, cli_mode=False, _test_font_failure=False):
        """
        Initializes the AssetManager.
        Args:
            cli_mode (bool): If True, operates in CLI mode (no graphics/sound loading).
                             *Si True, fonctionne en mode CLI (pas de chargement graphique/son).*
            _test_font_failure (bool): Internal flag for testing font initialization failure.
                                       *Drapeau interne pour tester l'échec d'initialisation de la police.*
        """
        logging.debug(
            f"AssetManager initializing. CLI mode: {cli_mode}, TestFontFailure: {_test_font_failure} / Initialisation de AssetManager. Mode CLI : {cli_mode}, TestFontFailure : {_test_font_failure}"
        )
        self.cli_mode = cli_mode
        self.images = {}
        self.sounds = {}
        self.placeholder_font = None

        if not self.cli_mode:  # Only attempt font initialization if not in CLI mode / *Tenter l'initialisation de la police uniquement si pas en mode CLI*
            if hasattr(pygame, "font"):
                try:
                    if _test_font_failure:  # Test hook / *Hook de test*
                        raise pygame.error("Test-induced font failure")
                    # Assuming pygame.font.init() is called in main.py after pygame.init()
                    # *En supposant que pygame.font.init() est appelé dans main.py après pygame.init()*
                    if pygame.font.get_init():  # Check if font module is truly initialized / *Vérifier si le module font est réellement initialisé*
                        self.placeholder_font = pygame.font.SysFont(
                            None, PLACEHOLDER_FONT_SIZE
                        )  # Use constant
                        logging.debug(
                            "Placeholder font initialized successfully. / Police de substitution initialisée avec succès."
                        )
                    else:
                        logging.warning(
                            "Pygame font module not initialized. Cannot create placeholder font. / Module de police Pygame non initialisé. Impossible de créer la police de substitution."
                        )
                except (pygame.error, AttributeError) as e:
                    logging.warning(
                        f"Could not initialize font for asset placeholders: {e} / Impossible d'initialiser la police pour les images de substitution : {e}"
                    )
            else:
                logging.warning(
                    "Pygame font module not available. Placeholders will not have text. / Module de police Pygame non disponible. Les images de substitution n'auront pas de texte."
                )
        logging.debug(
            f"AssetManager initialized. Placeholder font: {self.placeholder_font} / AssetManager initialisé. Police de substitution : {self.placeholder_font}"
        )

    def load_assets(self):
        """
        Loads all game assets defined in config.py (IMAGE_ASSET_CONFIG, SOUND_ASSET_CONFIG).
        For images, creates placeholders if loading fails (GUI mode).
        For sounds, uses DummySound if loading fails or in CLI mode/mixer not available.

        *Charge toutes les ressources du jeu définies dans config.py (IMAGE_ASSET_CONFIG, SOUND_ASSET_CONFIG).*
        *Pour les images, crée des substituts si le chargement échoue (mode GUI).*
        *Pour les sons, utilise DummySound si le chargement échoue ou en mode CLI/mixeur non disponible.*
        """
        logging.debug(
            "AssetManager.load_assets called. / AssetManager.load_assets appelé."
        )

        # Image loading using IMAGE_ASSET_CONFIG / *Chargement des images en utilisant IMAGE_ASSET_CONFIG*
        for key, config_entry in IMAGE_ASSET_CONFIG.items():
            logging.debug(
                f"Attempting to load image asset '{key}' with config: {config_entry} / Tentative de chargement de la ressource image '{key}' avec la configuration : {config_entry}"
            )
            path = config_entry["path"]
            size_hint = config_entry.get("size")

            if self.cli_mode:
                # In CLI mode, store metadata or None. For now, just path and size hint.
                # *En mode CLI, stocker les métadonnées ou None. Pour l'instant, juste le chemin et l'indice de taille.*
                self.images[key] = {
                    "path": path,
                    "size_hint": size_hint,
                    "type": "cli_placeholder",
                }
                logging.debug(
                    f"CLI mode: Stored metadata for image '{key}'. / Mode CLI : Métadonnées stockées pour l'image '{key}'."
                )
                # No actual image loading or Pygame surface creation / *Pas de chargement d'image réel ni de création de surface Pygame*
            else:  # GUI mode / *Mode GUI*
                try:
                    # Use centralized function
                    image_path = get_asset_path(path)
                    logging.debug(
                        f"GUI mode: Loading image '{key}' from resolved path '{image_path}'. / Mode GUI : Chargement de l'image '{key}' depuis le chemin résolu '{image_path}'."
                    )
                    self.images[key] = pygame.image.load(
                        image_path).convert_alpha()
                    logging.debug(
                        f"Successfully loaded image asset '{key}'. / Ressource image '{key}' chargée avec succès."
                    )
                except (pygame.error, FileNotFoundError) as e:
                    logging.warning(
                        f"Could not load image asset '{key}' from '{path}': {e}. Creating placeholder. / Impossible de charger la ressource image '{key}' depuis '{path}' : {e}. Création d'un substitut."
                    )
                    logging.debug(
                        f"Entering placeholder creation logic for image '{key}'. / Entrée dans la logique de création de substitut pour l'image '{key}'."
                    )
                    placeholder_size = (
                        size_hint if size_hint else DEFAULT_PLACEHOLDER_SIZE
                    )
                    placeholder_surface = pygame.Surface(placeholder_size)
                    placeholder_surface.fill(PLACEHOLDER_BG_COLOR)

                    if self.placeholder_font:
                        try:
                            text_surface = self.placeholder_font.render(
                                key, True, PLACEHOLDER_TEXT_COLOR
                            )
                            text_rect = text_surface.get_rect(
                                center=(
                                    placeholder_surface.get_width() // 2,
                                    placeholder_surface.get_height() // 2,
                                )
                            )
                            placeholder_surface.blit(text_surface, text_rect)
                        except pygame.error as font_e:
                            logging.warning(
                                f"Could not render text on placeholder for '{key}': {font_e} / Impossible de rendre le texte sur le substitut pour '{key}' : {font_e}"
                            )
                    else:
                        logging.warning(
                            f"Placeholder font not available for asset '{key}'. Placeholder will be a plain blue rectangle. / Police de substitution non disponible pour la ressource '{key}'. Le substitut sera un simple rectangle bleu."
                        )

                    self.images[key] = placeholder_surface.convert_alpha()

        # Sound loading using SOUND_ASSET_CONFIG / *Chargement des sons en utilisant SOUND_ASSET_CONFIG*
        for key, path in SOUND_ASSET_CONFIG.items():
            logging.debug(
                f"Attempting to load sound asset '{key}' from path '{path}'. / Tentative de chargement de la ressource sonore '{key}' depuis le chemin '{path}'."
            )
            if self.cli_mode or not (
                hasattr(pygame, "mixer") and pygame.mixer.get_init()
            ):
                # If in CLI mode, or if mixer is not initialized (e.g. no sound card or init failed)
                # *Si en mode CLI, ou si le mixeur n'est pas initialisé (par ex. pas de carte son ou initialisation échouée)*
                # Only log this specific warning if not in CLI (CLI implies no sound hardware focus)
                if not self.cli_mode:
                    # *Journaliser cet avertissement spécifique uniquement si pas en CLI (CLI implique pas de focus sur le matériel sonore)*
                    logging.warning(
                        f"Pygame mixer not initialized. Using dummy sound for '{key}'. / Mixeur Pygame non initialisé. Utilisation d'un son factice pour '{key}'."
                    )
                else:
                    logging.debug(
                        f"CLI mode or mixer not init: Using DummySound for '{key}'. / Mode CLI ou mixeur non initialisé : Utilisation de DummySound pour '{key}'."
                    )
                self.sounds[key] = DummySound()
            else:  # GUI mode with mixer initialized / *Mode GUI avec mixeur initialisé*
                try:
                    sound_file_path = get_asset_path(
                        path)  # Use centralized function
                    logging.debug(
                        f"GUI mode: Loading sound '{key}' from resolved path '{sound_file_path}'. / Mode GUI : Chargement du son '{key}' depuis le chemin résolu '{sound_file_path}'."
                    )
                    self.sounds[key] = pygame.mixer.Sound(sound_file_path)
                    logging.debug(
                        f"Successfully loaded sound asset '{key}'. / Ressource sonore '{key}' chargée avec succès."
                    )
                except pygame.error as e:
                    logging.warning(
                        f"Could not load sound asset '{key}' from '{path}': {e}. Using dummy sound. / Impossible de charger la ressource sonore '{key}' depuis '{path}' : {e}. Utilisation d'un son factice."
                    )
                    self.sounds[key] = (
                        DummySound()
                    )  # Moved inside the except block / *Déplacé dans le bloc except*
        logging.debug(
            "AssetManager.load_assets finished. / AssetManager.load_assets terminé."
        )


# The _get_path method is now removed as it's replaced by the centralized utilities.get_asset_path
# La méthode _get_path est maintenant supprimée car elle est remplacée par utilities.get_asset_path centralisée
