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

### Statut : ⏳ À faire

### Étapes :

-   [ ] **1. Centraliser les positions des boutons**
    -   Dans `config.py`, ajoutez des variables pour les positions des boutons de l'écran de démarrage, qui sont actuellement codées en dur dans `main.py` (ex: 787, 742).
    -   Dans `main.py`, importez ces nouvelles variables et utilisez-les lors de la création de vos instances de `Button`.

-   [ ] **2. Centraliser les paramètres de l'écran "Game Over"**
    -   La position des boutons sur l'écran "Game Over" est calculée dynamiquement, ce qui est bien.
    -   Pour améliorer, déplacez l'espacement de `20` pixels dans `config.py` (ex: `BUTTON_SPACING = 20`).
    -   Mettez à jour le code de `main.py` pour utiliser cette nouvelle constante.

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
