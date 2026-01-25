# game_entities.py
# This file defines all the game entities (objects) that appear and interact in the game.
# This includes the player, enemies (Carrot, Vampire), projectiles (Bullet, GarlicShot),
# effects (Explosion), collectible items (Collectible), and UI elements like Buttons.
# Each class typically handles its own state, behavior (update logic), and drawing.
#
# *Ce fichier définit toutes les entités (objets) du jeu qui apparaissent et interagissent
# *dans le jeu. Cela inclut le joueur, les ennemis (Carotte, Vampire), les projectiles
# *(Balle, Tir d'Ail), les effets (Explosion), les objets à collectionner (Collectible),
# *et les éléments d'interface utilisateur comme les Boutons. Chaque classe gère généralement
# *son propre état, son comportement (logique de mise à jour) et son affichage.*

import math
import random
import time

import pygame

import config
from utilities import calculate_movement_towards, get_direction_vector


class GameObject:
    """
    Base class for all game entities.
    Provides common attributes like position, image, and an active state.

    *Classe de base pour toutes les entités du jeu.*
    *Fournit des attributs communs comme la position, l'image et un état actif.*
    """

    def __init__(self, x, y, image, cli_mode=False):
        """
        Initializes a GameObject.
        Args:
            x (int): The x-coordinate of the object.
                     *La coordonnée x de l'objet.*
            y (int): The y-coordinate of the object.
                     *La coordonnée y de l'objet.*
            image (pygame.Surface or dict): The image/surface for the object, or metadata in CLI mode.
                                           *L'image/surface pour l'objet, ou des métadonnées en mode CLI.*
            cli_mode (bool): True if running in Command Line Interface mode.
                             *True si exécution en mode Interface en Ligne de Commande.*
        """
        self.cli_mode = cli_mode
        # In CLI, this could be metadata dict / *En CLI, cela pourrait être un dict de métadonnées*
        self.original_image = image
        # In CLI, this could be metadata dict / *En CLI, cela pourrait être un dict de métadonnées*
        self.image = image

        if not self.cli_mode and hasattr(image, "get_rect"):
            self.rect = image.get_rect(topleft=(x, y))
        else:
            # For CLI, or if image is not a surface (e.g. placeholder failed even more)
            # *Pour CLI, ou si l'image n'est pas une surface (par ex. le substitut a encore plus échoué)*
            width, height = 0, 0  # Default size / *Taille par défaut*
            if isinstance(
                image, dict
            ):  # Check if it's metadata from AssetManager CLI mode / *Vérifier si ce sont des métadonnées du mode CLI d'AssetManager*
                size_info = (
                    image.get("size_hint") or image.get("size")
                )  # Prefer 'size_hint' if available from config / *Préférer 'size_hint' si disponible depuis config*
                if size_info:
                    width, height = size_info
            self.rect = pygame.Rect(x, y, width, height)
        self.active = True  # Whether the object is currently active in the game / *Si l'objet est actuellement actif dans le jeu*

    def update(self, *args):
        """
        Update logic for the game object. To be overridden by subclasses.
        *Logique de mise à jour pour l'objet de jeu. À surcharger par les sous-classes.*
        """
        pass

    def draw(self, screen, scroll):
        """
        Draws the entity on the screen, adjusted by camera scroll.
        Args:
            screen (pygame.Surface): The main screen surface to draw on.
                                     *La surface principale de l'écran sur laquelle dessiner.*
            scroll (list[int, int]): The camera's scroll offset [scroll_x, scroll_y].
                                     *Le décalage de défilement de la caméra [scroll_x, scroll_y].*
        """
        if (
            not self.cli_mode and self.image and hasattr(
                self.image, "get_rect")
        ):  # Ensure image is drawable
            screen.blit(self.image, (self.rect.x -
                        scroll[0], self.rect.y - scroll[1]))


class Player(GameObject):
    """
    Represents the player character (the rabbit).
    Handles movement, health, items, and other player-specific logic.

    *Représente le personnage du joueur (le lapin).*
    *Gère le mouvement, la santé, les objets et autre logique spécifique au joueur.*
    """

    def __init__(self, x, y, image, asset_manager, cli_mode=False):
        """
        Initializes the Player.
        Args:
            x, y (int): Initial coordinates. / *Coordonnées initiales.*
            image (pygame.Surface or dict): Player's visual representation or CLI metadata.
                                           *Représentation visuelle du joueur ou métadonnées CLI.*
            asset_manager (AssetManager): For accessing sound assets.
                                          *Pour accéder aux ressources sonores.*
            cli_mode (bool): CLI mode flag. / *Indicateur du mode CLI.*
        """
        super().__init__(x, y, image, cli_mode=cli_mode)
        self.initial_x = x
        self.initial_y = y
        self.flipped = False  # True if the player image is flipped horizontally / *True si l'image du joueur est retournée horizontalement*
        # Last horizontal direction moved / *Dernière direction horizontale de déplacement*
        self.last_direction = "right"
        self.health = config.START_HEALTH
        self.max_health = config.MAX_HEALTH
        self.garlic_count = 0  # Number of garlic items held / *Nombre d'aulx possédés*
        # Number of carrot juice items collected / *Nombre de jus de carotte collectés*
        self.carrot_juice_count = 0
        self.invincible = (
            False  # True if currently invincible / *True si actuellement invincible*
        )
        self.last_hit_time = (
            0  # Time of the last hit taken / *Moment du dernier coup reçu*
        )
        self.speed = config.PLAYER_SPEED
        # True if death animation is playing / *True si l'animation de mort est en cours*
        self.death_effect_active = False
        self.death_effect_start_time = 0
        self.asset_manager = asset_manager
        self.health_changed = (
            False  # Flag for UI update / *Indicateur pour mise à jour UI*
        )
        self.garlic_changed = (
            False  # Flag for UI update / *Indicateur pour mise à jour UI*
        )
        self.juice_changed = (
            False  # Flag for UI update / *Indicateur pour mise à jour UI*
        )

    def move(self, dx, dy, world_bounds):
        """
        Moves the player based on direction input and world boundaries.
        Flips the player image based on horizontal movement.
        Args:
            dx (int): Horizontal movement direction (-1, 0, or 1).
                      *Direction de mouvement horizontal (-1, 0, ou 1).*
            dy (int): Vertical movement direction (-1, 0, or 1).
                      *Direction de mouvement vertical (-1, 0, ou 1).*
            world_bounds (tuple[int, int]): Max x and y coordinates of the world.
                                           *Coordonnées x et y maximales du monde.*
        """
        self.rect.x = max(
            0, min(world_bounds[0] - self.rect.width,
                   self.rect.x + dx * self.speed)
        )
        self.rect.y = max(
            0, min(world_bounds[1] - self.rect.height,
                   self.rect.y + dy * self.speed)
        )

        if (
            not self.cli_mode and self.original_image
        ):  # Image operations only in GUI mode
            if dx < 0 and not self.flipped:
                self.image = pygame.transform.flip(
                    self.original_image, True, False)
                self.flipped = True
            elif dx > 0 and self.flipped:
                self.image = self.original_image
                self.flipped = False

    def take_damage(self, amount=1):
        """
        Reduces player's health if not invincible or already in death effect.
        Plays hurt sound and triggers invincibility.
        Args:
            amount (int): The amount of damage to take.
                          *La quantité de dégâts à subir.*
        """
        if not self.invincible and not self.death_effect_active:
            self.health = max(0, self.health - amount)
            self.health_changed = True
            if self.health > 0:
                if not self.cli_mode:
                    self.asset_manager.sounds["hurt"].play()
                self.invincible = True
                self.last_hit_time = time.time()

    def update_invincibility(self):
        """Checks and updates the player's invincibility status based on duration."""
        # *Vérifie et met à jour l'état d'invincibilité du joueur en fonction de la durée.*
        if self.invincible and (
            time.time() - self.last_hit_time >= config.PLAYER_INVINCIBILITY_DURATION
        ):
            self.invincible = False

    def reset(self):
        """Resets the player to initial state (health, position, items, etc.)."""
        # *Réinitialise le joueur à son état initial (santé, position, objets, etc.).*
        self.health = config.START_HEALTH
        self.garlic_count = 0
        self.carrot_juice_count = 0
        self.rect.x = self.initial_x
        self.rect.y = self.initial_y
        self.invincible = False
        self.death_effect_active = False
        if not self.cli_mode and self.original_image:
            self.image = (
                self.original_image
            )  # Reset image if flipped / *Réinitialiser l'image si retournée*
        self.flipped = False
        # Ensure UI updates on reset / *Assurer la mise à jour de l'UI à la réinitialisation*
        self.health_changed = True
        self.garlic_changed = True
        self.juice_changed = True

    def draw(self, screen, scroll):
        """
        Draws the player on the screen.
        *Dessine le joueur à l'écran.*
        """
        # Overrides GameObject.draw if specific player drawing logic is needed (e.g., invincibility flash handled in main loop)
        # *Surcharge GameObject.draw si une logique de dessin spécifique au joueur est nécessaire (par ex. flash d'invincibilité géré dans la boucle principale)*
        super().draw(screen, scroll)  # Standard drawing / *Dessin standard*

    def draw_ui(self, screen, hp_image, garlic_image, max_garlic):
        """
        Draws player-related UI elements like health and garlic count.
        Args:
            screen (pygame.Surface): The screen to draw on. / *L'écran sur lequel dessiner.*
            hp_image (pygame.Surface): Image for health points. / *Image pour les points de vie.*
            garlic_image (pygame.Surface): Image for garlic count. / *Image pour le compteur d'ail.*
            max_garlic (int): Max garlic player can hold (for UI layout, if needed).
                              *Ail max que le joueur peut tenir (pour la disposition de l'UI, si besoin).*
        """
        if self.cli_mode:
            return  # No UI drawing in CLI mode / *Pas de dessin d'UI en mode CLI*

        # Health display / *Affichage de la santé*
        if hp_image and hasattr(hp_image, "get_width"):
            for i in range(self.health):
                screen.blit(
                    hp_image,
                    (
                        config.UI_HEALTH_X_OFFSET
                        + i * (hp_image.get_width() +
                               config.UI_HEALTH_SPACING),
                        config.UI_HEALTH_Y_OFFSET,
                    ),
                )

        # Garlic display / *Affichage de l'ail*
        if (
            self.garlic_count > 0
            and garlic_image
            and hasattr(garlic_image, "get_width")
        ):
            screen_width = screen.get_width()
            garlic_width = garlic_image.get_width()
            spacing = config.UI_GARLIC_SPACING
            for i in range(self.garlic_count):
                x_pos = (
                    screen_width
                    - config.UI_GARLIC_X_OFFSET
                    - (i + 1) * (garlic_width + spacing)
                )
                screen.blit(garlic_image, (x_pos, config.UI_GARLIC_Y_OFFSET))

        # Carrot juice counter at bottom right (always visible when count > 0)
        # *Compteur de jus de carotte en bas à droite (toujours visible si compte > 0)*
        if self.carrot_juice_count > 0:
            juice_image = self.asset_manager.images.get("carrot_juice")
            digit_0_img = self.asset_manager.images.get("digit_0")

            if (
                juice_image
                and hasattr(juice_image, "get_width")
                and digit_0_img
                and hasattr(digit_0_img, "get_width")
            ):
                digits_str = str(self.carrot_juice_count)
                spacing = (
                    config.UI_JUICE_COUNTER_DIGIT_SPACING
                )  # Reduced spacing for digits / *Espacement réduit pour les chiffres*

                # Use the actual loaded digit images for scaling, assuming they are all same size
                # *Utiliser les images de chiffres réellement chargées pour la mise à l'échelle, en supposant qu'elles ont toutes la même taille*
                # Scale factor can be adjusted here if needed / *Le facteur d'échelle peut être ajusté ici si nécessaire*
                # For simplicity, let's assume digit images are already appropriately sized or use a fixed scale.
                # *Par simplicité, supposons que les images des chiffres sont déjà de taille appropriée ou utilisons une échelle fixe.*
                # Example: scale digits to be half the height of the juice icon
                # *Exemple : mettre à l'échelle les chiffres pour qu'ils fassent la moitié de la hauteur de l'icône de jus*
                digit_scale_factor = config.UI_JUICE_COUNTER_DIGIT_SCALE
                scaled_digit_height = int(
                    digit_0_img.get_height() * digit_scale_factor)
                scaled_digit_width = int(
                    digit_0_img.get_width() * digit_scale_factor)

                total_digits_width = (
                    len(digits_str) * scaled_digit_width
                    + (len(digits_str) - 1) * spacing
                )

                # Position juice image first
                juice_x = screen.get_width() - 10 - juice_image.get_width()
                juice_y = screen.get_height() - 10 - juice_image.get_height()
                screen.blit(juice_image, (juice_x, juice_y))

                # Position digits to the left of the juice image
                digit_start_x = juice_x - spacing - total_digits_width
                digit_y_align = (
                    juice_y + (juice_image.get_height() -
                               scaled_digit_height) // 2
                )  # Vertically center digits with juice image

                current_x = digit_start_x
                for digit_char in digits_str:
                    digit_img_asset = self.asset_manager.images.get(
                        f"digit_{digit_char}"
                    )
                    if digit_img_asset and hasattr(digit_img_asset, "get_width"):
                        scaled_digit_surface = pygame.transform.scale(
                            digit_img_asset, (scaled_digit_width,
                                              scaled_digit_height)
                        )
                        screen.blit(scaled_digit_surface,
                                    (current_x, digit_y_align))
                        current_x += scaled_digit_width + spacing


class Bullet(GameObject):
    """
    Represents a bullet projectile fired by the player.
    Moves in a straight line towards a target.

    *Représente un projectile (balle) tiré par le joueur.*
    *Se déplace en ligne droite vers une cible.*
    """

    def __init__(self, x, y, target_x, target_y, image, cli_mode=False):
        """
        Initializes a Bullet.
        Args:
            x, y (int): Starting coordinates of the bullet.
                        *Coordonnées de départ de la balle.*
            target_x, target_y (int): Coordinates of the target the bullet moves towards.
                                     *Coordonnées de la cible vers laquelle la balle se dirige.*
            image (pygame.Surface or dict): Bullet's visual or CLI metadata.
                                           *Visuel de la balle ou métadonnées CLI.*
            cli_mode (bool): CLI mode flag. / *Indicateur du mode CLI.*
        """
        super().__init__(x, y, image, cli_mode=cli_mode)
        # Calculate direction from the initial (x,y) passed, which is typically player's center or weapon muzzle.
        # *Calculer la direction à partir des (x,y) initiaux passés, qui sont typiquement le centre du joueur ou la bouche de l'arme.*
        dir_x, dir_y = get_direction_vector(x, y, target_x, target_y)
        self.velocity = (dir_x * config.BULLET_SPEED,
                         dir_y * config.BULLET_SPEED)
        self.angle = math.degrees(
            math.atan2(-dir_y, dir_x)
        )  # Angle for rotation / *Angle pour la rotation*

    def update(self):
        """Updates the bullet's position based on its velocity."""
        # *Met à jour la position de la balle en fonction de sa vélocité.*
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

    @property
    def rotated_image(self):
        """
        Returns the bullet image rotated to match its direction of movement.
        Only relevant in GUI mode.

        *Retourne l'image de la balle tournée pour correspondre à sa direction de mouvement.*
        *Pertinent uniquement en mode GUI.*
        """
        if (
            self.cli_mode
            or not self.original_image
            or not hasattr(self.original_image, "get_rect")
        ):
            return None  # Or some default CLI representation if needed / *Ou une représentation CLI par défaut si besoin*
        return pygame.transform.rotate(self.original_image, self.angle)


class Carrot(GameObject):
    """
    Represents a carrot enemy.
    Moves towards the player and respawns after being defeated.

    *Représente une carotte ennemie.*
    *Se déplace vers le joueur et réapparaît après avoir été vaincue.*
    """

    def __init__(self, x, y, image, cli_mode=False):
        """
        Initializes a Carrot enemy.
        Args:
            x, y (int): Initial coordinates. / *Coordonnées initiales.*
            image (pygame.Surface or dict): Carrot's visual or CLI metadata.
                                           *Visuel de la carotte ou métadonnées CLI.*
            cli_mode (bool): CLI mode flag. / *Indicateur du mode CLI.*
        """
        super().__init__(x, y, image, cli_mode=cli_mode)
        self.speed = config.CARROT_SPEED
        self.active = True
        self.respawn_timer = 0  # Timer for respawning / *Minuteur pour la réapparition*
        self.direction = pygame.math.Vector2(
            random.uniform(-1, 1), random.uniform(-1, 1)
        )
        if (
            self.direction.length_squared() > 0
        ):  # Avoid normalizing zero vector / *Éviter de normaliser un vecteur nul*
            self.direction.normalize_ip()
        # Default direction if random resulted in (0,0) / *Direction par défaut si l'aléatoire a donné (0,0)*
        else:
            self.direction = pygame.math.Vector2(1, 0)

        self.spawn_position = (
            x,
            y,
        )  # Store initial spawn position / *Stocker la position d'apparition initiale*

    def respawn(self, world_size, player_rect):
        """
        Resets the carrot to its initial spawn position and reactivates it.
        Args:
            world_size (tuple): Not directly used here but often part of respawn logic for placement.
                                *Non utilisé directement ici mais souvent partie de la logique de réapparition pour le placement.*
            player_rect (pygame.Rect): Player's rectangle, for potential safe spawning logic (not used here).
                                     *Rectangle du joueur, pour une logique potentielle d'apparition sûre (non utilisée ici).*
        """
        # *Réinitialise la carotte à sa position d'apparition initiale et la réactive.*
        self.rect.topleft = self.spawn_position
        self.active = True
        # Ensure new direction is valid (non-zero vector) before normalizing
        # *S'assurer que la nouvelle direction est valide (vecteur non nul) avant de normaliser*
        new_dir_x = random.uniform(-1, 1)
        new_dir_y = random.uniform(-1, 1)
        # If both are zero (unlikely but possible), default to a direction
        # *Si les deux sont nuls (peu probable mais possible), utiliser une direction par défaut*
        if new_dir_x == 0 and new_dir_y == 0:
            new_dir_x = (
                1.0  # Or any non-zero component / *Ou toute composante non nulle*
            )
        self.direction = pygame.math.Vector2(new_dir_x, new_dir_y).normalize()

    def update(self, player_rect, world_bounds):
        """
        Updates the carrot's position and behavior.
        Moves towards the player if within detection radius, otherwise wanders.
        Args:
            player_rect (pygame.Rect): The player's current rectangle for targeting.
                                      *Rectangle actuel du joueur pour le ciblage.*
            world_bounds (tuple[int,int]): Boundaries of the game world.
                                          *Limites du monde du jeu.*
        """
        if self.active:
            player_center = pygame.math.Vector2(player_rect.center)
            carrot_center = pygame.math.Vector2(self.rect.center)

            # Vector pointing from carrot to player / *Vecteur pointant de la carotte vers le joueur*
            # Corrected: vector from player to carrot is carrot_center - player_center.
            # We want to move towards player, so target_direction = player_center - carrot_center.
            player_center = pygame.math.Vector2(player_rect.center)
            carrot_center = pygame.math.Vector2(self.rect.center)

            vector_to_player = player_center - carrot_center
            dist_sq = vector_to_player.length_squared()

            current_speed = self.speed

            # Apply speed multiplier and determine direction if player is in detection radius
            # *Appliquer le multiplicateur de vitesse et déterminer la direction si le joueur est dans le rayon de détection*
            if (
                dist_sq < config.CARROT_DETECTION_RADIUS**2
            ):  # Player is in detection radius (dist_sq can be 0 here)
                # *Le joueur est dans le rayon de détection (dist_sq peut être 0 ici)*
                dist = math.sqrt(dist_sq)

                # Speed multiplier logic (closer = faster, up to MAX_SPEED_MULTIPLIER)
                # *Logique du multiplicateur de vitesse (plus proche = plus rapide, jusqu'à MAX_SPEED_MULTIPLIER)*
                # The original formula was: 1 + (max_distance - dist)/max_distance * (MAX_SPEED_MULTIPLIER - 1)
                # This means when dist is 0, multiplier is MAX_SPEED_MULTIPLIER.
                # When dist is max_distance (CARROT_DETECTION_RADIUS), multiplier is 1.
                speed_factor = (
                    config.CARROT_DETECTION_RADIUS - dist
                ) / config.CARROT_DETECTION_RADIUS
                current_speed = self.speed * (
                    1 + speed_factor * (config.MAX_SPEED_MULTIPLIER - 1)
                )
                current_speed = min(
                    max(self.speed, current_speed),
                    self.speed * config.MAX_SPEED_MULTIPLIER,
                )  # Clamp speed

                if dist < config.CARROT_CHASE_RADIUS:
                    # Player is very close, carrot should move AWAY from the player
                    # *Le joueur est très proche, la carotte doit s'éloigner du joueur*
                    if (
                        dist_sq > 0
                    ):  # Avoid normalizing zero vector if somehow player and carrot are at exact same spot
                        self.direction = (
                            -vector_to_player.normalize()
                        )  # Move directly away
                else:
                    # Player is in detection range but not too close, carrot moves TOWARDS player
                    # *Le joueur est à portée de détection mais pas trop près, la carotte se déplace VERS le joueur*
                    if dist_sq > 0:
                        self.direction = (
                            vector_to_player.normalize()
                        )  # Move directly towards
            else:
                # Player is far, carrot wanders randomly
                # *Le joueur est loin, la carotte erre aléatoirement*
                # Add small random vector to current direction and re-normalize
                # *Ajouter un petit vecteur aléatoire à la direction actuelle et renormaliser*
                self.direction += pygame.math.Vector2(
                    random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2)
                )
                if (
                    self.direction.length_squared() == 0
                ):  # Handle potential zero vector after random addition
                    self.direction = pygame.math.Vector2(
                        random.uniform(-1, 1), random.uniform(-1, 1)
                    )  # New random direction

                if (
                    self.direction.length_squared() > 0
                ):  # Ensure it's not zero before normalizing
                    self.direction.normalize_ip()
                else:  # Fallback if still zero (highly unlikely)
                    self.direction = pygame.math.Vector2(1, 0)

            movement = self.direction * current_speed
            self.rect.x += movement.x
            self.rect.y += movement.y

            # Keep within world bounds / *Rester dans les limites du monde*
            self.rect.x = max(
                0, min(world_bounds[0] - self.rect.width, self.rect.x))
            self.rect.y = max(
                0, min(world_bounds[1] - self.rect.height, self.rect.y))


class GarlicShot(
    GameObject
):  # This class seems unused in favor of the dictionary in GameState.
    # *Cette classe semble inutilisée au profit du dictionnaire dans GameState.*
    # If it were to be used, it would need proper integration.
    # *Si elle devait être utilisée, elle nécessiterait une intégration correcte.*
    """
    Represents a garlic shot projectile, a special attack.
    (Currently, game logic in GameState handles garlic shot as a dictionary, not this class)

    *Représente un projectile de tir d'ail, une attaque spéciale.*
    *(Actuellement, la logique du jeu dans GameState gère le tir d'ail comme un dictionnaire, pas cette classe)*
    """

    def __init__(self, start_x, start_y, target_x, target_y, image, cli_mode=False):
        super().__init__(start_x, start_y, image, cli_mode=cli_mode)
        dir_x, dir_y = get_direction_vector(
            start_x, start_y, target_x, target_y)
        self.direction = pygame.math.Vector2(dir_x, dir_y)
        self.rotation_angle = 0  # For visual rotation / *Pour la rotation visuelle*
        self.speed = config.GARLIC_SHOT_SPEED
        self.max_travel = (
            config.GARLIC_SHOT_MAX_TRAVEL
        )  # Max distance it can travel / *Distance max qu'il peut parcourir*
        self.traveled = (
            0  # Distance traveled so far / *Distance parcourue jusqu'à présent*
        )
        self.active = True

    def update(self):
        """Updates garlic shot's position, rotation, and checks travel limit."""
        # *Met à jour la position, la rotation du tir d'ail et vérifie la limite de déplacement.*
        if self.active:
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
            self.traveled += self.speed
            self.rotation_angle = (
                self.rotation_angle + config.GARLIC_ROTATION_SPEED
            ) % 360  # Use constant from config
            # *Utiliser la constante de config*
            if self.traveled >= self.max_travel:
                self.active = False


class Explosion(
    GameObject
):  # Explosion is not a GameObject in current code, but has similar attributes
    # *Explosion n'est pas un GameObject dans le code actuel, mais a des attributs similaires*
    """
    Represents an explosion effect.
    Lasts for a short duration with a flashing animation.

    *Représente un effet d'explosion.*
    *Dure peu de temps avec une animation clignotante.*
    """

    def __init__(self, x, y, image):  # Does not take cli_mode, assumes GUI if created
        # *Ne prend pas cli_mode, suppose GUI si créé*
        """
        Initializes an Explosion effect.
        Args:
            x, y (int): Center coordinates of the explosion.
                        *Coordonnées centrales de l'explosion.*
            image (pygame.Surface): Image for the explosion.
                                    *Image pour l'explosion.*
        """
        # GameObject.__init__(self, x, y, image) # If it were a GameObject
        # self.rect.center = (x,y)
        self.image = image
        if image and hasattr(image, "get_rect"):  # Check if image is a valid surface
            self.rect = image.get_rect(center=(x, y))
        # Fallback if image is None or not a surface (e.g. asset loading failed)
        else:
            self.rect = pygame.Rect(x, y, 0, 0)  # Placeholder rect

        self.start_time = time.time()  # Time of creation / *Moment de création*
        self.flash_count = (
            0  # Number of flashes so far / *Nombre de flashs jusqu'à présent*
        )
        self.max_flashes = config.EXPLOSION_MAX_FLASHES
        self.flash_interval = config.EXPLOSION_FLASH_INTERVAL
        self.active = True

    def update(self, current_time):
        """
        Updates the explosion's flashing animation.
        Returns True if the explosion effect has finished, False otherwise.
        Args:
            current_time (float): The current game time.
                                  *Le temps de jeu actuel.*
        Returns:
            bool: True if finished, False otherwise.
                  *True si terminé, False sinon.*
        """
        if self.active:
            elapsed = current_time - self.start_time
            if elapsed > self.flash_interval:
                self.flash_count += 1
                # Reset timer for next flash / *Réinitialiser le minuteur pour le prochain flash*
                self.start_time = current_time
            if self.flash_count >= self.max_flashes:
                self.active = False
                return True  # Signal that explosion is done / *Signaler que l'explosion est terminée*
        return False

    def draw(self, screen, scroll):
        """
        Draws the explosion if it's active and in a "flash on" state.
        *Dessine l'explosion si elle est active et dans un état "flash activé".*
        """
        if self.active and (
            self.flash_count % 2 == 0
        ):  # Flash on even counts / *Flash sur les comptes pairs*
            if self.image and hasattr(
                self.image, "get_rect"
            ):  # Ensure image is drawable
                screen.blit(
                    self.image, (self.rect.x -
                                 scroll[0], self.rect.y - scroll[1])
                )


class Collectible(GameObject):
    """
    Represents a collectible item (e.g., HP, Garlic, Carrot Juice).
    Can be picked up by the player.

    *Représente un objet à collectionner (par ex. PV, Ail, Jus de Carotte).*
    *Peut être ramassé par le joueur.*
    """

    def __init__(self, x, y, image, item_type, scale=0.5, cli_mode=False):
        """
        Initializes a Collectible item.
        Args:
            x, y (int): Center coordinates for the item.
                        *Coordonnées centrales de l'objet.*
            image (pygame.Surface or dict): Item's visual or CLI metadata.
                                           *Visuel de l'objet ou métadonnées CLI.*
            item_type (str): Type of the item (e.g., 'hp', 'garlic').
                             *Type de l'objet (par ex. 'hp', 'garlic').*
            scale (float): Scale factor for the item's image.
                           *Facteur d'échelle pour l'image de l'objet.*
            cli_mode (bool): CLI mode flag. / *Indicateur du mode CLI.*
        """
        # In CLI mode, 'image' is metadata, so scaling is not applicable.
        # This logic applies scaling only in GUI mode when a valid surface is provided.
        # *En mode CLI, 'image' correspond à des métadonnées, donc la mise à l'échelle n'est pas applicable.*
        # *Cette logique applique la mise à l'échelle uniquement en mode GUI lorsqu'une surface valide est fournie.*
        final_image = image
        if (
            not cli_mode and image and hasattr(image, "get_width")
        ):  # Check if it's a surface before scaling
            # *Vérifier si c'est une surface avant de mettre à l'échelle*
            final_image = pygame.transform.scale(
                image, (int(image.get_width() * scale),
                        int(image.get_height() * scale))
            )

        # Initialize GameObject. x, y are treated as topleft for GameObject's constructor.
        # The GameObject.__init__ handles using size_hint from metadata if final_image is a dict (CLI mode).
        # *Initialiser GameObject. x, y sont traités comme topleft pour le constructeur de GameObject.*
        # *GameObject.__init__ gère l'utilisation de size_hint des métadonnées si final_image est un dict (mode CLI).*
        super().__init__(x, y, final_image, cli_mode=cli_mode)

        # For Collectibles, the initial x and y are intended as the center.
        # GameObject.__init__ sets self.rect using x,y as topleft.
        # So, now we re-center self.rect based on the original x,y.
        # *Pour les Collectibles, les x et y initiaux sont prévus comme le centre.*
        # *GameObject.__init__ définit self.rect en utilisant x,y comme topleft.*
        # *Donc, nous recentrons maintenant self.rect en fonction des x,y d'origine.*
        if hasattr(
            self.rect, "center"
        ):  # Ensure self.rect exists and has a center attribute
            # *S'assurer que self.rect existe et a un attribut center*
            self.rect.center = (x, y)

        self.active = True
        # Type of collectible (e.g., 'hp', 'garlic') / *Type d'objet à collectionner (par ex. 'hp', 'ail')*
        self.item_type = item_type


class Vampire(GameObject):
    """
    Represents the Vampire enemy.
    Chases the player and has a special death/respawn mechanic.

    *Représente l'ennemi Vampire.*
    *Poursuit le joueur et possède un mécanisme spécial de mort/réapparition.*
    """

    def __init__(self, x, y, image, cli_mode=False):
        """
        Initializes the Vampire enemy.
        Args:
            x, y (int): Initial coordinates. / *Coordonnées initiales.*
            image (pygame.Surface or dict): Vampire's visual or CLI metadata.
                                           *Visuel du vampire ou métadonnées CLI.*
            cli_mode (bool): CLI mode flag. / *Indicateur du mode CLI.*
        """
        super().__init__(x, y, image, cli_mode=cli_mode)
        self.active = False  # Starts inactive, activated by GameState or its own logic
        # *Commence inactif, activé par GameState ou sa propre logique*
        self.respawn_timer = 0  # Timer for respawning / *Minuteur pour la réapparition*
        # True if death animation is playing / *True si l'animation de mort est en cours*
        self.death_effect_active = False
        self.death_effect_start_time = 0
        self.death_effect_duration = config.VAMPIRE_DEATH_DURATION
        self.speed = config.VAMPIRE_SPEED

    def update(self, player, world_bounds, current_time):
        """
        Updates the Vampire's state, including movement, death effect, and respawning.
        Args:
            player (Player): The player object, for targeting.
                             *L'objet joueur, pour le ciblage.*
            world_bounds (tuple[int,int]): Boundaries of the game world.
                                          *Limites du monde du jeu.*
            current_time (float): The current game time.
                                  *Le temps de jeu actuel.*
        """
        if self.active:
            # Movement logic / *Logique de mouvement*
            move_x, move_y = calculate_movement_towards(
                self.rect, player.rect, self.speed, world_bounds
            )
            self.rect.x += move_x
            self.rect.y += move_y

            # Boundary check / *Vérification des limites*
            self.rect.x = max(
                0, min(world_bounds[0] - self.rect.width, self.rect.x))
            self.rect.y = max(
                0, min(world_bounds[1] - self.rect.height, self.rect.y))

            # Death effect check (This seems to be handled by GameState after garlic hit)
            # *Vérification de l'effet de mort (Cela semble être géré par GameState après un coup d'ail)*
            # If vampire has its own health and can die from other means, that logic would be here.
            # *Si le vampire a sa propre santé et peut mourir par d'autres moyens, cette logique serait ici.*
            if self.death_effect_active and (
                current_time - self.death_effect_start_time
                >= self.death_effect_duration
            ):
                self.death_effect_active = False  # Effect finished / *Effet terminé*
                # self.active = False # It's already set to False when death_effect_active is True by GameState
                # *Il est déjà défini sur False lorsque death_effect_active est True par GameState*
        else:  # Not active / *Pas actif*
            # Respawn check when NOT active / *Vérification de réapparition lorsque NON actif*
            if (
                current_time - self.respawn_timer > config.VAMPIRE_RESPAWN_TIME
            ) and not self.death_effect_active:
                # Respawn only if not in the middle of a death effect
                # *Réapparaître uniquement si pas au milieu d'un effet de mort*
                self.respawn(
                    random.randint(0, world_bounds[0] - self.rect.width),
                    random.randint(0, world_bounds[1] - self.rect.height),
                )

    def respawn(self, x, y):
        """
        Respawns the vampire at a new position and activates it.
        Args:
            x, y (int): New coordinates for the vampire.
                        *Nouvelles coordonnées pour le vampire.*
        """
        self.rect.topleft = (x, y)
        self.active = True
        self.death_effect_active = False
        # self.death_flash_count = 0 # This attribute is not defined, maybe from an old version?
        # *Cet attribut n'est pas défini, peut-être d'une ancienne version ?*

    def draw(self, screen, scroll, current_time):
        """
        Draws the vampire, including its death effect animation if active.
        Args:
            screen (pygame.Surface): The screen to draw on. / *L'écran sur lequel dessiner.*
            scroll (list[int,int]): Camera scroll offset. / *Décalage de défilement de la caméra.*
            current_time (float): Current game time for animations.
                                  *Temps de jeu actuel pour les animations.*
        """
        if self.cli_mode:
            return

        if self.death_effect_active:
            time_since_death_effect_start = current_time - self.death_effect_start_time
            if time_since_death_effect_start <= self.death_effect_duration:
                # Flashing effect / *Effet de clignotement*
                if (
                    int(
                        time_since_death_effect_start
                        / config.VAMPIRE_DEATH_FLASH_INTERVAL
                    )
                    % 2
                    == 0
                ):  # Flash every VAMPIRE_DEATH_FLASH_INTERVAL seconds
                    # Tinted image for death effect (e.g., green)
                    # *Image teintée pour l'effet de mort (par ex. vert)*
                    if self.original_image and hasattr(self.original_image, "copy"):
                        tinted_image = self.original_image.copy()
                        tinted_image.fill(
                            config.VAMPIRE_DEATH_TINT_COLOR,
                            special_flags=pygame.BLEND_RGBA_MULT,
                        )  # Green tint
                        screen.blit(
                            tinted_image,
                            (self.rect.x - scroll[0], self.rect.y - scroll[1]),
                        )
            # else: death effect duration passed, it will be set to inactive by update or GameState
            # *sinon : la durée de l'effet de mort est passée, il sera défini comme inactif par update ou GameState*
        elif self.active:  # Draw normally if active and not in death effect
            # *Dessiner normalement si actif et pas en effet de mort*
            super().draw(screen, scroll)


class Button(GameObject):  # Button is also a GameObject
    """
    UI Button class. Can be clicked to trigger a callback function.
    *Classe pour les boutons d'interface utilisateur. Peut être cliqué pour déclencher une fonction de rappel.*
    """

    def __init__(self, x, y, image, callback, cli_mode=False):
        """
        Initializes a Button.
        Args:
            x, y (int): Top-left coordinates. / *Coordonnées en haut à gauche.*
            image (pygame.Surface or dict): Button's visual or CLI metadata.
                                           *Visuel du bouton ou métadonnées CLI.*
            callback (function): Function to call when the button is clicked.
                                 *Fonction à appeler lorsque le bouton est cliqué.*
            cli_mode (bool): CLI mode flag. / *Indicateur du mode CLI.*
        """
        super().__init__(x, y, image, cli_mode=cli_mode)  # Call GameObject constructor
        # *Appeler le constructeur de GameObject*
        self.callback = callback

    def draw(self, screen):
        """
        Draws the button on the screen.
        (Assumes `scroll` is not needed for UI buttons, as they are usually screen-fixed)
        *Dessine le bouton à l'écran.*
        *(Suppose que `scroll` n'est pas nécessaire pour les boutons d'UI, car ils sont généralement fixes à l'écran)*
        """
        if not self.cli_mode and self.image and hasattr(self.image, "get_rect"):
            screen.blit(
                self.image, self.rect
            )  # Use self.rect which is already top-left based
            # *Utiliser self.rect qui est déjà basé sur le coin supérieur gauche*

    def handle_event(self, event):
        """
        Handles a single Pygame event. If the event is a left mouse click
        on the button, its callback function is executed.
        Args:
            event (pygame.event.Event): The Pygame event to handle.
                                        *L'événement Pygame à gérer.*
        """
        if self.cli_mode:
            return  # No mouse events in CLI mode / *Pas d'événements de souris en mode CLI*

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button / *Bouton gauche de la souris*
                if self.rect.collidepoint(event.pos):
                    if self.callback:
                        self.callback()
