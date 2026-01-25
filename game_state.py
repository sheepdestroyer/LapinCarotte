# game_state.py
# This file defines the GameState class, which is central to managing the overall
# state of the LapinCarotte game. It holds references to all game entities (player,
# enemies, projectiles, items), manages game conditions (e.g., game over, paused),
# handles entity interactions, updates, and resets the game.
#
# *Ce fichier définit la classe GameState, qui est centrale pour la gestion de l'état
# *global du jeu LapinCarotte. Elle contient les références à toutes les entités du jeu
# *(joueur, ennemis, projectiles, objets), gère les conditions de jeu (par ex. game over,
# *en pause), s'occupe des interactions entre entités, des mises à jour et réinitialise le jeu.*

import logging
import math
import random

import pygame

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


class GameState:
    """
    Manages the overall state of the game, including all entities,
    game conditions, and updates.

    *Gère l'état global du jeu, y compris toutes les entités,*
    *les conditions de jeu et les mises à jour.*
    """

    def __init__(self, asset_manager, cli_mode=False):
        """
        Initializes the game state.
        Args:
            asset_manager (AssetManager): The asset manager instance for accessing game assets.
                                          *L'instance de AssetManager pour accéder aux ressources du jeu.*
            cli_mode (bool): True if the game is running in Command Line Interface mode.
                             *True si le jeu fonctionne en mode Interface en Ligne de Commande.*
        """
        self.cli_mode = cli_mode
        self.scroll = [
            0,
            0,
        ]  # Camera scroll position / *Position de défilement de la caméra*
        # Screen edge percentage to trigger scroll / *Pourcentage du bord de l'écran pour déclencher le défilement*
        self.scroll_trigger = config.SCROLL_TRIGGER
        self.world_size = (
            config.WORLD_SIZE
        )  # Total dimensions of the game world / *Dimensions totales du monde du jeu*
        self.carrot_spawn_safe_radius_sq = (
            min(self.world_size) / config.CARROT_SPAWN_SAFE_RATIO
        ) ** 2
        self.game_over = (
            False  # True if the game has ended / *True si le jeu est terminé*
        )
        # True if the game has started (past the initial screen) / *True si le jeu a commencé (après l'écran initial)*
        self.started = False
        # True if the game is currently paused / *True si le jeu est actuellement en pause*
        self.paused = False
        self.asset_manager = asset_manager

        self.player = Player(
            200,
            200,
            asset_manager.images["rabbit"],
            asset_manager,
            cli_mode=self.cli_mode,
        )

        # Stores active garlic shot details / *Stocke les détails du tir d'ail actif*
        self.garlic_shot = None
        self.garlic_shot_start_time = 0
        self.garlic_shot_travel = 0

        self.vampire = Vampire(
            random.randint(0, config.WORLD_SIZE[0]),
            random.randint(0, config.WORLD_SIZE[1]),
            asset_manager.images["vampire"],
            cli_mode=self.cli_mode,
        )
        # This might need to be conditional if Vampire init changes based on cli_mode
        self.vampire.active = True
        # *Ceci pourrait devoir être conditionnel si l'initialisation de Vampire change en fonction du cli_mode*
        self.bullets = []  # List of active player bullets / *Liste des projectiles actifs du joueur*
        self.carrots = []  # List of active carrot enemies / *Liste des carottes ennemies actives*
        self.explosions = []  # List of active explosions / *Liste des explosions actives*
        # List of active garlic shots (though current logic uses a single self.garlic_shot)
        self.garlic_shots = []
        # *Liste des tirs d'ail actifs (bien que la logique actuelle utilise un seul self.garlic_shot)*
        self.items = []  # List of active collectible items / *Liste des objets collectables actifs*

        # Redundant garlic_shot attributes, already defined above. Consider removing if not distinct.
        # *Attributs garlic_shot redondants, déjà définis ci-dessus. Envisager de supprimer s'ils ne sont pas distincts.*
        # self.garlic_shot = None
        # self.garlic_shot_travel = 0
        # self.garlic_shot_start_time = 0
        self.garlic_shot_speed = config.GARLIC_SHOT_SPEED
        self.garlic_shot_duration = config.GARLIC_SHOT_DURATION

        self.vampire_killed_count = (
            0  # Track vampires killed / *Compteur de vampires tués*
        )
        self.last_vampire_death_pos = (
            0,
            0,
        )  # Position tracking for item drops from vampire / *Suivi de la position pour les chutes d'objets du vampire*

        # Initialize carrots / *Initialiser les carottes*
        for _ in range(config.CARROT_COUNT):
            self.create_carrot(asset_manager)

    def reset(self):
        """
        Resets the game state to its initial conditions, typically for starting a new game.
        This includes resetting player, enemies, items, and game flags.

        *Réinitialise l'état du jeu à ses conditions initiales, typiquement pour commencer une nouvelle partie.*
        *Cela inclut la réinitialisation du joueur, des ennemis, des objets et des indicateurs de jeu.*
        """
        logging.info(
            "Resetting game state. / Réinitialisation de l'état du jeu.")
        self.scroll = [0, 0]
        self.game_over = False
        self.started = False
        self.paused = False  # Reset pause state / *Réinitialiser l'état de pause*

        # Completely reset all entity containers / *Réinitialiser complètement tous les conteneurs d'entités*
        self.bullets = []
        self.explosions = []
        # If multiple garlic shots were intended / *Si plusieurs tirs d'ail étaient prévus*
        self.garlic_shots = []
        self.items = []
        self.carrots = []

        # Reset single garlic shot state / *Réinitialiser l'état du tir d'ail unique*
        self.garlic_shot = None
        self.garlic_shot_travel = 0
        self.garlic_shot_start_time = 0

        # Reset entities / *Réinitialiser les entités*
        if self.player:
            self.player.reset()
            # Clear any bullet rotation state (if applicable) / *Effacer tout état de rotation de projectile (si applicable)*
            if hasattr(self.player, "bullet_rotation"):
                del self.player.bullet_rotation

        # Hard reset vampire / *Réinitialisation matérielle du vampire*
        if self.vampire:
            vampire_width = self.vampire.rect.width
            vampire_height = self.vampire.rect.height
            if vampire_width == 0 and isinstance(
                self.asset_manager.images.get("vampire"), dict
            ):  # CLI mode with size hint
                size_hint = self.asset_manager.images["vampire"].get(
                    "size_hint"
                ) or self.asset_manager.images["vampire"].get("size")
                if size_hint:
                    vampire_width, vampire_height = size_hint
                else:  # Fallback if no size info in CLI metadata
                    vampire_width, vampire_height = config.IMAGE_ASSET_CONFIG[
                        "vampire"
                    ]["size"]

            self.vampire.active = False
            self.vampire.death_effect_active = False
            self.vampire.respawn_timer = 0
            # Respawn the vampire at a new random valid position
            # *Faire réapparaître le vampire à une nouvelle position aléatoire valide*
            self.vampire.respawn(
                random.randint(
                    0,
                    (
                        self.world_size[0] - vampire_width
                        if self.world_size[0] > vampire_width
                        else 0
                    ),
                ),
                random.randint(
                    0,
                    (
                        self.world_size[1] - vampire_height
                        if self.world_size[1] > vampire_height
                        else 0
                    ),
                ),
            )
            # self.vampire.active = True # This is redundant as Vampire.respawn() sets self.active = True

        self.vampire_killed_count = (
            0  # Reset kill count / *Réinitialiser le compteur de victimes*
        )

        # Recreate carrots with fresh instances / *Recréer les carottes avec de nouvelles instances*
        self.carrots = []
        for _ in range(config.CARROT_COUNT):
            self.create_carrot(self.asset_manager)

    def add_bullet(self, start_x, start_y, target_x, target_y, image):
        """
        Creates and adds a new bullet to the game.
        *Crée et ajoute un nouveau projectile au jeu.*
        """
        self.bullets.append(
            Bullet(start_x, start_y, target_x, target_y,
                   image, cli_mode=self.cli_mode)
        )

    # add_garlic_shot is not used if self.garlic_shot is a single dictionary.
    # *add_garlic_shot n'est pas utilisé si self.garlic_shot est un dictionnaire unique.*
    def add_garlic_shot(self, start_x, start_y, target_x, target_y, image):
        """
        Creates and adds a new garlic shot to the game's list of garlic shots.
        Note: Current game logic uses a single `self.garlic_shot` dictionary, not this list.
        This method is kept for potential future use or test compatibility.

        *Crée et ajoute un nouveau tir d'ail à la liste des tirs d'ail du jeu.*
        *Note : La logique de jeu actuelle utilise un unique dictionnaire `self.garlic_shot`, et non cette liste.*
        *Cette méthode est conservée pour une utilisation future potentielle ou la compatibilité des tests.*
        """
        self.garlic_shots.append(
            GarlicShot(
                start_x, start_y, target_x, target_y, image, cli_mode=self.cli_mode
            )
        )

    def add_explosion(self, x, y, image):
        """
        Creates and adds a new explosion effect to the game.
        *Crée et ajoute un nouvel effet d'explosion au jeu.*
        """
        self.explosions.append(Explosion(x, y, image))

    # add_collectible seems unused, Collectibles are created directly in update()
    # *add_collectible semble inutilisé, les Collectibles sont créés directement dans update()*
    # def add_collectible(self, x, y, image, item_type='hp'): # item_type added for clarity
    #     """Create and add a new collectible item"""
    #     self.items.append(Collectible(x, y, image, item_type, config.ITEM_SCALE, cli_mode=self.cli_mode))

    def create_carrot(self, asset_manager):
        """
        Creates a new carrot enemy at a random position, ensuring it's not too close to the player.
        *Crée une nouvelle carotte ennemie à une position aléatoire, en s'assurant qu'elle n'est pas trop proche du joueur.*
        """
        while True:
            carrot_image_data = asset_manager.images["carrot"]
            carrot_width, carrot_height = 0, 0
            if isinstance(carrot_image_data, dict):  # CLI mode, use size_hint
                size_hint = carrot_image_data.get("size_hint") or carrot_image_data.get(
                    "size"
                )
                if size_hint:
                    carrot_width, carrot_height = size_hint
                else:  # Fallback if no size info in CLI metadata
                    carrot_width, carrot_height = config.IMAGE_ASSET_CONFIG["carrot"][
                        "size"
                    ]  # Default size from config
            elif hasattr(carrot_image_data, "get_width"):  # GUI mode, actual surface
                carrot_width = carrot_image_data.get_width()
                carrot_height = carrot_image_data.get_height()
            else:  # Should not happen if asset loading is robust
                carrot_width, carrot_height = 48, 48

            x = random.randint(0, self.world_size[0] - carrot_width)
            y = random.randint(0, self.world_size[1] - carrot_height)
            # Ensure player exists and check distance, or spawn if player doesn't exist (e.g. initial setup)
            # *S'assurer que le joueur existe et vérifier la distance, ou apparaître si le joueur n'existe pas (par ex. configuration initiale)*
            # Ensure player rect is valid before accessing centerx/centery
            # *S'assurer que le rect du joueur est valide avant d'accéder à centerx/centery*
            player_center_x = (
                self.player.rect.centerx
                if self.player and hasattr(self.player.rect, "centerx")
                else self.world_size[0] / 2
            )
            player_center_y = (
                self.player.rect.centery
                if self.player and hasattr(self.player.rect, "centery")
                else self.world_size[1] / 2
            )

            if not self.player or (
                (x - player_center_x) ** 2 + (y - player_center_y) ** 2
                > self.carrot_spawn_safe_radius_sq
            ):
                self.carrots.append(
                    Carrot(x, y, carrot_image_data, cli_mode=self.cli_mode)
                )
                break

    def update(self, current_time):
        """
        Updates the state of all game entities and handles interactions for the current frame.
        Args:
            current_time (float): The current game time, used for time-based logic.
                                  *Le temps de jeu actuel, utilisé pour la logique basée sur le temps.*
        """
        # Update player's invincibility state / *Mettre à jour l'état d'invincibilité du joueur*
        self.player.update_invincibility()

        # Update carrot logic / *Mettre à jour la logique des carottes*
        for carrot in self.carrots:
            if carrot.active:
                carrot.update(
                    self.player.rect, self.world_size
                )  # Delegate update to Carrot method
                # *Déléguer la mise à jour à la méthode Carrot*

        # Update bullets and handle collisions / *Mettre à jour les projectiles et gérer les collisions*
        for bullet in self.bullets[:]:
            bullet.update()

            # Remove off-screen bullets / *Supprimer les projectiles hors écran*
            if (
                bullet.rect.right < 0
                or bullet.rect.left > self.world_size[0]
                or bullet.rect.bottom < 0
                or bullet.rect.top > self.world_size[1]
            ):
                self.bullets.remove(bullet)
                continue

            # Check collisions with carrots / *Vérifier les collisions avec les carottes*
            for carrot in self.carrots:
                if carrot.active and bullet.rect.colliderect(carrot.rect):
                    self.explosions.append(
                        Explosion(
                            carrot.rect.centerx,
                            carrot.rect.centery,
                            self.asset_manager.images["explosion"],
                        )
                    )
                    carrot.active = False  # Carrot becomes inactive
                    # *La carotte devient inactive*
                    carrot.respawn_timer = current_time  # Set respawn timer
                    # *Définir le minuteur de réapparition*
                    if not self.cli_mode:
                        self.asset_manager.sounds["explosion"].play()
                    try:
                        self.bullets.remove(bullet)
                    except ValueError:  # Bullet might have been removed by another collision in same frame
                        # *Le projectile a peut-être été supprimé par une autre collision dans la même frame*
                        logging.debug(
                            "Bullet already removed, skipping. / Projectile déjà supprimé, on ignore."
                        )
                    break  # Bullet is consumed, no need to check other carrots
                    # *Le projectile est consommé, pas besoin de vérifier les autres carottes*

        # Respawn carrots after delay / *Faire réapparaître les carottes après un délai*
        for carrot in self.carrots:
            if not carrot.active and (
                current_time - carrot.respawn_timer > config.CARROT_RESPAWN_DELAY
            ):
                carrot.respawn_timer = 0  # Reset timer / *Réinitialiser le minuteur*
                carrot.respawn(
                    self.world_size, self.player.rect
                )  # Call carrot's own respawn logic
                # *Appeler la logique de réapparition propre à la carotte*

        # Garlic shot logic / *Logique du tir d'ail*
        if self.garlic_shot and self.garlic_shot["active"]:
            if self.garlic_shot_travel < config.GARLIC_SHOT_MAX_TRAVEL and (
                current_time - self.garlic_shot_start_time <= self.garlic_shot_duration
            ):  # Check duration as well
                # *Vérifier également la durée*
                # Update rotation angle each frame / *Mettre à jour l'angle de rotation à chaque frame*
                self.garlic_shot["rotation_angle"] = (
                    self.garlic_shot["rotation_angle"] +
                    config.GARLIC_ROTATION_SPEED
                ) % 360
                # Move in the pre-calculated direction / *Se déplacer dans la direction pré-calculée*
                self.garlic_shot["x"] += self.garlic_shot["dx"] * \
                    self.garlic_shot_speed
                self.garlic_shot["y"] += self.garlic_shot["dy"] * \
                    self.garlic_shot_speed
                self.garlic_shot_travel += self.garlic_shot_speed
            else:  # Max travel reached or duration expired / *Voyage maximal atteint ou durée expirée*
                self.garlic_shot["active"] = False
                self.garlic_shot = None  # Clear the shot / *Effacer le tir*
                # Reset travel for next shot / *Réinitialiser le voyage pour le prochain tir*
                self.garlic_shot_travel = 0

            # Check for collision with vampire (only if garlic shot still exists and is active)
            # *Vérifier la collision avec le vampire (seulement si le tir d'ail existe encore et est actif)*
            if self.garlic_shot and self.garlic_shot["active"] and self.vampire.active:
                self.garlic_shot["rect"].center = (
                    self.garlic_shot["x"],
                    self.garlic_shot["y"],
                )
                if self.garlic_shot["rect"].colliderect(self.vampire.rect):
                    self.vampire.death_effect_active = True
                    self.vampire.death_effect_start_time = current_time
                    self.vampire.active = False
                    self.vampire.respawn_timer = (
                        current_time  # Set respawn timer for vampire
                    )
                    # *Définir le minuteur de réapparition pour le vampire*
                    if not self.cli_mode:
                        self.asset_manager.sounds["vampire_death"].play()
                    self.garlic_shot = (
                        None  # Garlic shot is consumed / *Le tir d'ail est consommé*
                    )
                    self.garlic_shot_travel = 0
                    self.vampire_killed_count += 1
                    self.last_vampire_death_pos = (
                        self.vampire.rect.center
                    )  # Store death position / *Stocker la position de la mort*
                    logging.info(
                        f"Vampire killed by garlic! Total kills: {self.vampire_killed_count} / Vampire tué par l'ail ! Total victimes : {self.vampire_killed_count}"
                    )

        # Update vampire / *Mettre à jour le vampire*
        self.vampire.update(
            self.player, self.world_size, current_time
        )  # Delegate to Vampire's update
        # *Déléguer à la mise à jour de Vampire*

        # Handle finished vampire death animations and item drop
        # *Gérer les animations de mort de vampire terminées et la chute d'objets*
        if (
            self.vampire.death_effect_active
            and not self.vampire.active
            and (
                current_time - self.vampire.death_effect_start_time
                >= config.VAMPIRE_DEATH_DURATION
            )
        ):
            self.vampire.death_effect_active = (
                False  # Clear flag / *Effacer l'indicateur*
            )

            # Drop carrot juice at the vampire's last known position
            # *Laisser tomber du jus de carotte à la dernière position connue du vampire*
            self.items.append(
                Collectible(
                    self.last_vampire_death_pos[0],
                    self.last_vampire_death_pos[1],
                    self.asset_manager.images["carrot_juice"],
                    "carrot_juice",  # item_type
                    config.ITEM_SCALE,
                    cli_mode=self.cli_mode,
                )
            )
            logging.debug(
                f"Carrot juice dropped at {self.last_vampire_death_pos} / Jus de carotte déposé à {self.last_vampire_death_pos}"
            )

        # Check collision between player and active vampire / *Vérifier la collision entre le joueur et le vampire actif*
        if self.vampire.active and self.player.rect.colliderect(self.vampire.rect):
            self.player.take_damage()
            # Vampire might become inactive or teleport upon hitting player, handle in Vampire class or here
            # *Le vampire pourrait devenir inactif ou se téléporter en touchant le joueur, à gérer dans la classe Vampire ou ici*
            # For now, simple model: vampire also "dies" or becomes inactive and respawns
            # *Pour l'instant, modèle simple : le vampire "meurt" aussi ou devient inactif et réapparaît*
            self.vampire.active = False
            self.vampire.respawn_timer = current_time
            logging.debug(
                "Player collided with Vampire. / Le joueur est entré en collision avec le Vampire."
            )

        # Update explosions and handle item drops from them / *Mettre à jour les explosions et gérer les chutes d'objets associées*
        for explosion in self.explosions[:]:
            if explosion.update(
                current_time
            ):  # update returns True when explosion is finished
                # *update retourne True quand l'explosion est terminée*
                # Create collectible item (HP or Garlic) / *Créer un objet collectable (PV ou Ail)*
                is_garlic = random.random() < config.ITEM_DROP_GARLIC_CHANCE
                item_image_key = "garlic" if is_garlic else "hp"
                item_type = "garlic" if is_garlic else "hp"

                self.items.append(
                    Collectible(
                        explosion.rect.centerx,
                        explosion.rect.centery,
                        self.asset_manager.images[item_image_key],
                        item_type,
                        config.ITEM_SCALE,
                        cli_mode=self.cli_mode,
                    )
                )
                logging.debug(
                    f"{item_type} dropped from explosion at ({explosion.rect.centerx}, {explosion.rect.centery}) / {item_type} déposé par explosion à ({explosion.rect.centerx}, {explosion.rect.centery})"
                )
                self.explosions.remove(explosion)

        # Check item collisions with player / *Vérifier les collisions d'objets avec le joueur*
        for item in self.items[:]:
            if item.active and self.player.rect.colliderect(item.rect):
                logging.debug(
                    f"Player collecting item: {item.item_type}. Player HP: {self.player.health}, Garlic: {self.player.garlic_count} / Joueur ramassant l'objet : {item.item_type}. PV Joueur : {self.player.health}, Ail : {self.player.garlic_count}"
                )
                collected = False
                if item.item_type == "hp" and self.player.health < config.MAX_HEALTH:
                    self.player.health += 1
                    self.player.health_changed = (
                        True  # For UI update / *Pour mise à jour UI*
                    )
                    if not self.cli_mode:
                        self.asset_manager.sounds["get_hp"].play()
                    collected = True
                    logging.info(
                        f"Player collected HP. Current HP: {self.player.health} / Joueur a ramassé PV. PV actuels : {self.player.health}"
                    )
                elif (
                    item.item_type == "garlic"
                    and self.player.garlic_count < config.MAX_GARLIC
                ):
                    self.player.garlic_count += 1
                    self.player.garlic_changed = (
                        True  # For UI update / *Pour mise à jour UI*
                    )
                    if not self.cli_mode:
                        self.asset_manager.sounds["get_garlic"].play()
                    collected = True
                    logging.info(
                        f"Player collected Garlic. Current Garlic: {self.player.garlic_count} / Joueur a ramassé Ail. Ail actuel : {self.player.garlic_count}"
                    )
                elif item.item_type == "carrot_juice":
                    self.player.carrot_juice_count = min(
                        self.player.carrot_juice_count + 1, config.MAX_CARROT_JUICE
                    )
                    self.player.juice_changed = (
                        True  # For UI update / *Pour mise à jour UI*
                    )
                    if not self.cli_mode:
                        self.asset_manager.sounds[
                            "get_hp"
                        ].play()  # Reuse existing pickup sound / *Réutiliser son de ramassage existant*
                    collected = True
                    logging.info(
                        f"Player collected Carrot Juice. Current Juice: {self.player.carrot_juice_count} / Joueur a ramassé Jus de Carotte. Jus actuel : {self.player.carrot_juice_count}"
                    )

                if collected:
                    self.items.remove(item)

    def pause_game(self):
        """
        Sets the game to a paused state.
        *Met le jeu en état de pause.*
        """
        if not self.paused:
            self.paused = True
            logging.info("Game paused. / Jeu mis en pause.")

    def resume_game(self):
        """
        Resumes the game from a paused state.
        *Reprend le jeu à partir d'un état de pause.*
        """
        if self.paused:
            self.paused = False
            logging.info("Game resumed. / Jeu repris.")
