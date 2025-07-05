# TODO - Refactorisation LapinCarotte

Ce document détaille les étapes nécessaires pour refactoriser la boucle de jeu principale et améliorer la gestion de l'interface utilisateur.

---

## Tâche 1 : Refactoriser la Gestion des Entités

**Objectif :** Centraliser toute la logique de mise à jour des entités du jeu (joueur, ennemis, projectiles, etc.) dans la classe `GameState` pour simplifier la boucle principale de `main.py`.

### Statut : ✅ Terminé

### Étapes :

-   [x] **1. Créer une méthode `update` dans `GameState`**
    -   Dans le fichier `game_state.py`, ajoutez une nouvelle méthode à la classe `GameState` : `def update(self, current_time):`.

-   [x] **2. Déplacer la logique de mise à jour des carottes**
    -   Coupez le bloc de code qui gère la mise à jour de la position des carottes depuis `main.py`.
    -   Collez ce bloc dans la nouvelle méthode `update` de `game_state.py`.

-   [x] **3. Déplacer la logique de mise à jour des projectiles (`Bullet`)**
    -   Coupez la boucle `for bullet in game_state.bullets[:]:` de `main.py` qui gère la mise à jour des projectiles et leurs collisions avec les carottes.
    -   Collez-la dans la méthode `update` de `game_state.py`.

-   [x] **4. Déplacer la logique de réapparition des carottes**
    -   Coupez la boucle `for carrot in game_state.carrots:` de `main.py` qui gère leur réapparition.
    -   Collez-la dans la méthode `update` de `game_state.py`.

-   [x] **5. Déplacer la logique du tir d'ail (`GarlicShot`)**
    -   Coupez tout le bloc `if game_state.garlic_shot and game_state.garlic_shot["active"]:` de `main.py`.
    -   Collez-le dans la méthode `update` de `game_state.py`.

-   [x] **6. Déplacer la logique de mise à jour du vampire**
    -   Coupez l'appel `game_state.vampire.update(...)` et la logique de collision avec le joueur depuis `main.py`.
    -   Collez-les dans la méthode `update` de `game_state.py`.

-   [x] **7. Déplacer la logique de mise à jour des explosions**
    -   Coupez la boucle `for explosion in game_state.explosions[:]:` de `main.py`.
    -   Collez-la dans la méthode `update` de `game_state.py`. Assurez-vous que la création des `Collectible` après l'explosion est bien incluse.

-   [x] **8. Déplacer la logique de collecte des items**
    -   Coupez la boucle `for item in game_state.items[:]:` de `main.py`.
    -   Collez-la dans la méthode `update` de `game_state.py`.

-   [x] **9. Nettoyer `main.py`**
    -   Dans la boucle de jeu principale de `main.py` (sous `elif not game_state.game_over:`), supprimez tous les blocs de code que vous venez de déplacer.
    -   Remplacez-les par un unique appel : `game_state.update(current_time)`.

---

## Tâche 2 : Améliorer l'UI avec une Classe `Button`

**Objectif :** Créer une classe réutilisable pour tous les boutons du jeu afin de rendre le code de l'interface plus propre, plus lisible et plus facile à maintenir.

### Statut : ✅ Terminé

### Étapes :

-   [x] **1. Créer la classe `Button`**
    -   Dans le fichier `game_entities.py`, créez une nouvelle classe `Button`.
    -   Son `__init__` doit accepter `x`, `y`, `image` et une fonction `callback` (l'action à exécuter lors du clic).
    -   La classe doit avoir une méthode `draw(self, screen)` pour s'afficher.
    -   Elle doit aussi avoir une méthode `handle_event(self, event)` qui vérifie si l'événement est un clic de souris à l'intérieur de son rectangle. Si c'est le cas, elle appelle la fonction `callback`.

-   [x] **2. Intégrer les boutons sur l'écran de démarrage**
    -   Dans `main.py`, avant la boucle de jeu, créez des instances de `Button` pour les boutons "Start" et "Exit" de l'écran de démarrage.
    -   Passez les fonctions appropriées en `callback` (ex: `start_game` pour le bouton Start, et une fonction pour quitter le jeu).
    -   Dans la boucle d'événements pour l'écran de démarrage, appelez la méthode `handle_event` pour chaque bouton.
    -   Dans la section de dessin de l'écran de démarrage, appelez la méthode `draw` de chaque bouton.

-   [x] **3. Intégrer les boutons sur l'écran "Game Over"**
    -   Faites de même pour les boutons "Restart" et "Exit" de l'écran "Game Over".
    -   Utilisez la fonction `reset_game` comme `callback` pour le bouton de redémarrage.

---

## Tâche 3 : Externaliser les Constantes de l'UI

**Objectif :** Supprimer les valeurs "magiques" (nombres codés en dur) du code en les déplaçant dans `config.py` pour une configuration centralisée.

### Statut : ✅ Terminé

### Étapes :

-   [x] **1. Centraliser les positions des boutons**
    -   Dans `config.py`, ajoutez des variables pour les positions des boutons de l'écran de démarrage, qui sont actuellement codées en dur dans `main.py` (ex: 787, 742).
    -   Dans `main.py`, importez ces nouvelles variables et utilisez-les lors de la création de vos instances de `Button`.

-   [x] **2. Centraliser les paramètres de l'écran "Game Over"**
    -   La position des boutons sur l'écran "Game Over" est calculée dynamiquement, ce qui est bien.
    -   Pour améliorer, déplacez l'espacement de `20` pixels dans `config.py` (ex: `BUTTON_SPACING = 20`). (Note: Constante `BUTTON_SPACING` déjà existante et utilisée).
    -   Mettez à jour le code de `main.py` pour utiliser cette nouvelle constante. (Note: Déjà en place).

---

## Tâche 4 : Ajouter un Nouvel Item (Fonctionnalité)

**Objectif :** Ajouter un item de "Boost de Vitesse" pour rendre le jeu plus dynamique. *Note : Ceci est une nouvelle fonctionnalité, pas seulement de la refactorisation.*

### Statut : ⏳ À faire

### Étapes :

-   [ ] **1. Mettre à jour la configuration**
    -   Dans `config.py`, ajoutez les constantes pour le nouvel item : `ITEM_DROP_SPEED_CHANCE`, `PLAYER_SPEED_BOOST_DURATION`, `PLAYER_SPEED_BOOST_MULTIPLIER`.

-   [ ] **2. Ajouter l'asset**
    -   Dans `asset_manager.py`, ajoutez une image pour l'item "speed_boost" dans le dictionnaire `assets`.

-   [ ] **3. Mettre à jour la classe `Player`**
    -   Dans `game_entities.py`, modifiez la classe `Player` :
        -   Ajoutez les attributs `self.speed_boost_active = False` et `self.speed_boost_end_time = 0`.
        -   Ajoutez une méthode `update(self, current_time)` qui vérifie si le boost est terminé.
        -   Modifiez la méthode `move` pour que la vitesse soit multipliée si le boost est actif.

-   [ ] **4. Gérer la création et la collecte de l'item**
    -   Dans `game_state.py` (dans la méthode `update` refactorisée), au moment où une explosion crée un `Collectible`, ajoutez une chance de créer un item de type `speed_boost`.
    -   Dans la logique de collecte d'items, si le joueur touche un item de type `speed_boost`, activez le boost sur le joueur.
    -   N'oubliez pas d'appeler `self.player.update(current_time)` dans la méthode `update` de `GameState`.

---

## Tâche 5 : Normaliser la Vitesse du Jeu avec Delta Time (dt)

**Objectif :** Rendre la vitesse du jeu indépendante du framerate (FPS) en intégrant un calcul de delta time (dt) dans la boucle de jeu et en l'utilisant pour les mises à jour de mouvement et de physique. Cela corrigera les problèmes d'accélération du jeu et assurera une expérience cohérente à différentes fréquences de rafraîchissement.

### Statut : ⏳ À faire

### Étapes :

-   [ ] **1. Calculer le Delta Time (dt) dans `main.py`**
    -   Dans la boucle `main_loop`, stocker le `current_time` de la frame précédente.
    -   Calculer `dt = current_time - previous_time`.
    -   Mettre à jour `previous_time = current_time` à la fin de la boucle.
    -   Initialiser `previous_time` correctement avant le début de la boucle (par exemple, à `time.time()`).
    -   Optionnel : Capper `dt` à une valeur maximale pour éviter des sauts importants si le jeu freeze temporairement.

-   [ ] **2. Passer `dt` aux fonctions de mise à jour**
    -   Modifier `game_state.update()` pour accepter `dt` en plus de (ou à la place de) `current_time` si `current_time` n'est plus nécessaire pour certaines logiques.
    -   Propager `dt` aux méthodes `update` et `move` des entités du jeu (`Player`, `Carrot`, `Bullet`, `GarlicShot`, `Vampire`, etc.).

-   [ ] **3. Mettre à jour la logique de mouvement avec `dt`**
    -   Dans chaque entité, modifier la logique de mouvement pour qu'elle soit multipliée par `dt`. Par exemple, `self.rect.x += self.speed * dx * dt`.
    -   Ajuster les valeurs de `SPEED` (par exemple, `PLAYER_SPEED`, `BULLET_SPEED`) pour qu'elles représentent des unités par seconde plutôt que par frame. Elles devront probablement être augmentées significativement. Par exemple, si une vitesse était de 5 pixels/frame et qu'on vise 60 FPS, la nouvelle vitesse sera de `5 * 60 = 300` pixels/seconde.

-   [ ] **4. Mettre à jour les timers et animations basés sur `dt`**
    -   Pour les animations ou les timers qui ne sont pas déjà basés sur `time.time()` (par exemple, des compteurs de frames), les convertir pour utiliser `dt`. Par exemple, `timer -= dt`.
    -   Les logiques basées sur `time.time()` (comme l'invincibilité, la durée des explosions) peuvent rester telles quelles car elles sont déjà indépendantes du framerate.

-   [ ] **5. Supprimer `time.sleep(config.FRAME_DELAY)`**
    -   Une fois que le jeu est basé sur `dt`, le `time.sleep()` pour limiter le FPS n'est plus nécessaire et peut même être contre-productif. La boucle de jeu tournera aussi vite que possible, et `dt` assurera que la vitesse du jeu reste constante.
    -   Alternativement, si un FPS cap est toujours désiré (par exemple pour économiser les ressources CPU), il peut être réimplémenté d'une manière qui n'interfère pas avec le calcul de `dt` (par exemple, en utilisant `pygame.time.Clock().tick(TARGET_FPS)` qui retourne aussi le `dt` en millisecondes).

-   [ ] **6. Tester et ajuster**
    -   Tester le jeu intensivement pour s'assurer que la vitesse est correcte et cohérente.
    -   Ajuster les constantes de vitesse et de timing si nécessaire.

---

## Tâche 6 : Implémenter un Écran de Pause

**Objectif :** Permettre au joueur de mettre le jeu en pause en appuyant sur la touche "Échap". L'écran de pause réutilisera l'écran de "Game Over" mais affichera des boutons "Continue" et "Settings".

### Statut : ✅ Terminé

### Étapes :

-   [x] **1. Ajouter un état "paused" à `GameState`**
    -   Dans `game_state.py`, ajouter un attribut `self.paused = False` à la classe `GameState`.
    -   Créer des méthodes `pause_game(self)` et `resume_game(self)` pour changer cet état.

-   [x] **2. Préparer les assets pour les nouveaux boutons**
    -   Ajouter les images pour les boutons "Continue" et "Settings" dans le dossier `Assets/images/`.
    -   Mettre à jour `asset_manager.py` pour charger ces nouvelles images (par exemple, `continue_button`, `settings_button`).

-   [x] **3. Créer les boutons de l'écran de pause dans `main.py`**
    -   Définir les fonctions callback pour ces boutons :
        -   `resume_game_callback()`: appellera `game_state.resume_game()`.
        -   `open_settings_callback()`: pour l'instant, cette fonction ne fera rien (placeholder).
    -   Instancier les objets `Button` pour "Continue" et "Settings", en utilisant les nouvelles images et callbacks.
    -   Positionner ces boutons de manière similaire à ceux de l'écran "Game Over" (centrés horizontalement, espacés verticalement).

-   [x] **4. Gérer l'événement "Échap" dans `main.py`**
    -   Dans la boucle principale d'événements (quand le jeu est démarré et non "game over"), détecter `pygame.KEYDOWN` avec `event.key == pygame.K_ESCAPE`.
    -   Si "Échap" est pressé :
        -   Si le jeu n'est pas en pause, appeler `game_state.pause_game()`.
        -   Si le jeu est déjà en pause, appeler `game_state.resume_game()`.

-   [x] **5. Logique de la boucle de jeu pour l'état "paused" dans `main.py`**
    -   Modifier la boucle principale de `main.py` pour ajouter une nouvelle section `elif game_state.paused:`.
    -   **Affichage :**
        -   Dessiner l'arrière-plan (par exemple, une version assombrie de l'écran de jeu ou l'image "Game Over" comme demandé).
        -   Dessiner le titre "PAUSE" (ou réutiliser l'image "Game Over").
        -   Dessiner les boutons "Continue" et "Settings".
    -   **Gestion des événements :**
        -   Dans cette section, appeler `handle_event` pour les boutons de l'écran de pause.
    -   **Arrêt de la logique de jeu :**
        -   S'assurer que `game_state.update()` n'est PAS appelé lorsque le jeu est en pause.
        -   S'assurer que les mouvements du joueur et autres actions de jeu sont désactivés.

-   [x] **6. Implémenter les callbacks des boutons**
    -   `resume_game_callback()`: doit simplement appeler `game_state.resume_game()`.
    -   `open_settings_callback()`: pour l'instant, elle peut être vide ou afficher un message "Settings not implemented".

-   [x] **7. Tests (Manuels et/ou Automatisés)**
    -   Vérifier que la pause s'active/se désactive avec "Échap".
    -   Vérifier que les boutons "Continue" et "Settings" s'affichent correctement.
    -   Vérifier que le bouton "Continue" reprend le jeu.
    -   Vérifier que le jeu est bien figé en arrière-plan lorsque la pause est active (pas de mouvement d'ennemis, etc.).
    -   Si possible, ajouter des tests unitaires pour les nouvelles fonctions et la logique d'état.

---

## Tâche 7 : Améliorer la Robustesse du Chargement des Assets

**Objectif :** Empêcher le jeu de crasher si un fichier image ou son n'est pas trouvé. Afficher un placeholder pour les images manquantes et un avertissement pour les sons.

### Statut : ✅ Terminé

### Étapes :

-   [x] **1. Modifier `AssetManager.load_assets` pour les images**
    -   Dans `asset_manager.py`, encadrer `pygame.image.load()` dans un bloc `try-except`.
    -   En cas d'erreur (`FileNotFoundError`, `pygame.error`):
        -   Afficher un message d'avertissement dans la console.
        -   Créer une image placeholder (par exemple, un rectangle bleu avec le nom de l'asset).
        -   Assigner ce placeholder à `self.images[key]`.
    -   S'assurer que `pygame.font.init()` est appelé si nécessaire pour rendre le texte sur le placeholder.

-   [x] **2. Modifier `AssetManager.load_assets` pour les sons**
    -   Encadrer `pygame.mixer.Sound()` dans un bloc `try-except`.
    -   En cas d'erreur (`pygame.error`):
        -   Afficher un message d'avertissement.
        -   Le son sera manquant, mais le jeu ne crashera pas.

-   [x] **3. Tests**
    -   Vérifier que les tests automatisés passent toujours.
    -   Effectuer des tests manuels en supprimant/renommant temporairement des assets pour vérifier que les placeholders s'affichent et que des avertissements sont journalisés.

---

## Tâche 8 : Implémenter un Mode CLI de Base (Fondation)

**Objectif :** Permettre au jeu de fonctionner sans initialisation graphique via une option `--cli`. Afficher les menus et options sous forme de texte, sélectionnables par numéro. Ceci est une première étape pour améliorer la testabilité et la flexibilité.

### Statut : ✅ Terminé

### Étapes Initiales :

-   [x] **1. Analyse d'Arguments en Ligne de Commande**
    -   Dans `main.py`, utiliser `argparse` pour ajouter et gérer une option `--cli`.
    -   Rendre la valeur de ce drapeau (mode CLI actif/inactif) accessible globalement ou la passer aux modules concernés.

-   [x] **2. Initialisation Conditionnelle de Pygame**
    *   Dans `main.py`, rendre l'initialisation des modules Pygame (surtout `pygame.display`, `pygame.font`, `pygame.mixer`) conditionnelle à l'absence du mode CLI.
    *   Gérer les variables globales dépendantes de l'écran (ex: `screen`, `screen_width`, `screen_height`) pour qu'elles ne causent pas d'erreur en mode CLI (peuvent être `None` ou des valeurs par défaut non graphiques).

-   [x] **3. Adaptation de `AssetManager` pour le Mode CLI**
    *   Modifier `AssetManager` pour qu'il accepte un indicateur `cli_mode`.
    *   Si en mode CLI :
        -   Pour les images : Ne pas charger les surfaces `pygame.Surface`. `self.images` pourrait stocker des chemins, des métadonnées (comme les dimensions de `config.ASSET_CONFIG`), ou `None`. La logique de placeholder visuel doit être sautée.
        -   Pour les sons : Sauter les appels à `pygame.mixer.Sound()` ou utiliser `DummySound` si `pygame.mixer` n'est pas initialisé.
        -   La création de `self.placeholder_font` doit être sautée si `pygame.font` n'est pas initialisé.

-   [x] **4. Affichage Textuel de Base pour les États de Jeu**
    *   Dans `main.py` (`main_loop`) :
        -   Si en mode CLI, utiliser `print()` au lieu de `screen.blit()`.
        -   Écran de Démarrage : Afficher "Écran de Démarrage\n1. Commencer\n2. Quitter".
        -   Pause : Afficher "PAUSE\n1. Continuer\n2. Paramètres (Non implémenté)\n3. Quitter".
        -   Game Over : Afficher "GAME OVER\n1. Recommencer\n2. Quitter".
        -   Jeu Actif : Afficher un message simple comme "Jeu en cours... (interactions CLI à venir)".

-   [x] **5. Interaction Basique par Menu Textuel**
    *   En mode CLI, utiliser `input()` pour récupérer le choix de l'utilisateur dans les menus.
    *   Traiter l'entrée pour appeler les fonctions correspondantes (`start_game`, `quit_game`, etc.).
    *   Pour cette étape initiale, la logique de jeu (`game_state.update()`, mouvements) n'est pas exécutée en mode CLI ; se concentrer sur la navigation dans les menus.

-   [x] **6. Tests (Manuels Initiaux & Stratégie CLI)**
    *   Exécuter `python main.py --cli`.
    *   Vérifier l'absence de fenêtre Pygame.
    *   Vérifier l'affichage des menus textuels et la possibilité de naviguer (ex: commencer, quitter).
    *   Définir une stratégie pour les tests automatisés du mode CLI (à développer dans les étapes suivantes).

-   [x] **7. Mettre à Jour la Documentation (.md files) & Workflows (placeholder)**
    *   Ajouter une section à `README.md` sur l'option `--cli`.
    *   Planifier les mises à jour de `CI.md` et `AGENTS.md` pour inclure les tests CLI.
    *   (Les modifications réelles des workflows et des tests CI seront des sous-tâches ultérieures).

---

## Tâche 9 : Implémenter un Système de Logging Configurable

**Objectif :** Remplacer les `print()` de débogage par un système de logging structuré utilisant le module `logging` de Python. Permettre l'activation des logs de débogage via une option en ligne de commande (`--debug`).

### Statut : ✅ Terminé

### Étapes :

-   [x] **1. Intégrer le Module `logging`**
    -   Importer `logging` dans `main.py`.
    -   Ajouter un argument `--debug` (ou `-d`) via `argparse`.
    -   Configurer le logger racine au démarrage pour définir le niveau (`INFO` par défaut, `DEBUG` si flag) et le format des messages. Diriger les logs vers `stdout` pour la compatibilité avec les tests CLI.

-   [x] **2. Remplacer les `print()` Existants**
    -   Parcourir `main.py`, `asset_manager.py`, `game_state.py`, `game_entities.py`.
    -   Convertir les `print("DEBUG: ...")` en `logging.debug(...)`.
    -   Convertir les `print("INFO: ...")` ou les impressions CLI en `logging.info(...)`.
    -   Convertir les `print("WARNING: ...")` en `logging.warning(...)`.
    -   Convertir les `print("ERROR: ...")` en `logging.error(...)` ou `logging.exception(...)`.
    -   Supprimer les appels `sys.stdout.flush()` associés aux anciens `print` de débogage.

-   [x] **3. Ajouter de Nouveaux Logs de Débogage Pertinents**
    -   Identifier les chemins critiques dans le code (changements d'état, gestion d'événements majeurs, traitement des entrées, mises à jour importantes de `GameState`).
    -   Ajouter des instructions `logging.debug()` pour tracer le flux d'exécution et les valeurs des variables importantes dans ces sections.

-   [x] **4. Adapter les Tests CLI**
    -   Modifier la fonction utilitaire `run_cli_test` dans `tests/test_cli_mode.py` pour qu'elle passe le drapeau `--debug` à `main.py`.
    -   Vérifier que les assertions existantes dans les tests CLI fonctionnent toujours avec les messages de log formatés (elles devraient si elles vérifient la présence de sous-chaînes du message original).

-   [x] **5. Mettre à Jour la Documentation**
    -   `README.md` : Expliquer le nouveau drapeau `--debug`.
    -   `AGENTS.md` : Noter l'utilisation du framework de logging pour le débogage et le développement.
    -   `TODO.md` : Ajouter cette tâche (Tâche 9) et la marquer comme terminée.

-   [x] **6. Tester Intensivement**
    -   Exécuter le jeu avec et sans `--debug` (GUI et CLI) pour vérifier la verbosité et la correction des logs.
    -   S'assurer que le mode CLI reste utilisable et que les menus s'affichent correctement via `logging.info()`.
    -   Exécuter tous les tests automatisés pour confirmer l'absence de régressions.
