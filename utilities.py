# utilities.py
# This file contains utility functions that provide common calculations or operations
# used across different parts of the LapinCarotte game. For example, functions for
# vector calculations or movement logic.
#
# *Ce fichier contient des fonctions utilitaires qui fournissent des calculs ou des opérations
# *communs utilisés dans différentes parties du jeu LapinCarotte. Par exemple, des fonctions
# *pour les calculs vectoriels ou la logique de mouvement.*

import math
import pygame

def get_direction_vector(start_x, start_y, target_x, target_y):
    """
    Calculates and returns a normalized direction vector between two points.
    Args:
        start_x, start_y (float): Coordinates of the starting point.
                                  *Coordonnées du point de départ.*
        target_x, target_y (float): Coordinates of the target point.
                                    *Coordonnées du point cible.*
    Returns:
        tuple[float, float]: A normalized (dx, dy) vector, or (0,0) if points are identical.
                             *Un vecteur normalisé (dx, dy), ou (0,0) si les points sont identiques.*

    *Calcule et retourne un vecteur de direction normalisé entre deux points.*
    *Args:*
        *start_x, start_y (float): Coordonnées du point de départ.*
        *target_x, target_y (float): Coordonnées du point cible.*
    *Returns:*
        *tuple[float, float]: Un vecteur normalisé (dx, dy), ou (0,0) si les points sont identiques.*
    """
    dx = target_x - start_x
    dy = target_y - start_y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return (0, 0)
    return (dx/dist, dy/dist)

def calculate_movement_towards(source_rect, target_rect, speed, world_bounds):
    """
    Calculates the x and y components of movement for a source rectangle moving towards a target rectangle,
    respecting speed and world boundaries.
    Args:
        source_rect (pygame.Rect): The rectangle of the object that is moving.
                                   *Le rectangle de l'objet qui se déplace.*
        target_rect (pygame.Rect): The rectangle of the target to move towards.
                                   *Le rectangle de la cible vers laquelle se déplacer.*
        speed (float): The speed of movement.
                       *La vitesse de déplacement.*
        world_bounds (tuple[int, int]): The (width, height) of the game world.
                                        *La (largeur, hauteur) du monde du jeu.*
    Returns:
        tuple[float, float]: The (dx, dy) movement to apply to source_rect.x and source_rect.y.
                             *Le mouvement (dx, dy) à appliquer à source_rect.x et source_rect.y.*

    *Calcule les composantes x et y du mouvement pour un rectangle source se déplaçant vers un rectangle cible,*
    *en respectant la vitesse et les limites du monde.*
    *Args:*
        *source_rect (pygame.Rect): Le rectangle de l'objet qui se déplace.*
        *target_rect (pygame.Rect): Le rectangle de la cible vers laquelle se déplacer.*
        *speed (float): La vitesse de déplacement.*
        *world_bounds (tuple[int, int]): La (largeur, hauteur) du monde du jeu.*
    *Returns:*
        *tuple[float, float]: Le mouvement (dx, dy) à appliquer à source_rect.x et source_rect.y.*
    """
    dx_center = target_rect.centerx - source_rect.centerx
    dy_center = target_rect.centery - source_rect.centery
    dist = math.hypot(dx_center, dy_center)
    
    if dist == 0: # Already at the target center / *Déjà au centre de la cible*
        return (0, 0)
        
    # Normalized direction vector / *Vecteur de direction normalisé*
    norm_dx = dx_center / dist
    norm_dy = dy_center / dist

    # Potential movement / *Mouvement potentiel*
    move_x = norm_dx * speed
    move_y = norm_dy * speed
    
    # Calculate new potential top-left position / *Calculer la nouvelle position potentielle en haut à gauche*
    new_x_tl = source_rect.x + move_x
    new_y_tl = source_rect.y + move_y
    
    # Apply world boundaries to the new top-left position
    # *Appliquer les limites du monde à la nouvelle position en haut à gauche*
    final_x_tl = max(0, min(world_bounds[0] - source_rect.width, new_x_tl))
    final_y_tl = max(0, min(world_bounds[1] - source_rect.height, new_y_tl))

    # Return the actual delta to apply / *Retourner le delta réel à appliquer*
    return (final_x_tl - source_rect.x, final_y_tl - source_rect.y)

def get_asset_path(relative_path):
    """
    Constructs the absolute path to an asset, correctly handling running from source vs. frozen executable.
    Args:
        relative_path (str): The path relative to the 'Assets' directory (e.g., 'images/player.png').
                             *Le chemin relatif au répertoire 'Assets' (par ex. 'images/player.png').*
    Returns:
        str: The absolute path to the asset.
             *Le chemin absolu vers la ressource.*

    *Construit le chemin absolu vers une ressource, gérant correctement l'exécution depuis les sources*
    *par rapport à un exécutable figé.*
    *Args:*
        *relative_path (str): Le chemin relatif au répertoire 'Assets' (par ex. 'images/player.png').*
    *Returns:*
        *str: Le chemin absolu vers la ressource.*
    """
    # Ensure 'os' and 'sys' are imported if not already at the top of utilities.py
    # For this operation, they are typically needed.
    import os
    import sys

    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle/frozen executable (e.g., PyInstaller)
        # *Si l'application est exécutée en tant que bundle/exécutable figé (par ex. PyInstaller)*
        base_path = sys._MEIPASS
    else:
        # If run from source code / *Si exécuté depuis le code source*
        base_path = os.path.abspath(".")
    return os.path.join(base_path, 'Assets', relative_path)
