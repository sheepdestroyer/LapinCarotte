# LapinCarotte
Un lapin combat les carottes vampires / *A rabbit fights vampire carrots*

![image](https://github.com/user-attachments/assets/577473aa-4569-43aa-9c7a-0c6f26821257)


# Download latest Windows & Linux binaries
# Télécharger les derniers exécutables Windows & Linux
Get it here / *Téléchargez le ici* : https://github.com/sheepdestroyer/LapinCarotte/releases

# Run dev env
# Exécuter l'environnement de développement
```
git clone https://github.com/sheepdestroyer/LapinCarotte
cd LapinCarotte
pip install pygame-ce
python main.py
```
*To run the game from source:*
*Pour lancer le jeu depuis les sources :*

## Introduction to Python and Pygame (EN)

This game is written in Python and uses the Pygame library.

*   **Python:** A popular, easy-to-learn programming language. It's often recommended for beginners because its syntax is clear and readable. If you're new to programming, Python is a great place to start!
    *   Learn more about Python: [Official Python Website](https://www.python.org)
    *   A simple Python tutorial for kids: [Python for Kids](https://www.pythonforkids.net/) (Note: external resource, content may vary)
*   **Pygame:** A set of Python modules designed for writing video games. It provides functionalities for graphics, sound, input devices (like keyboard and mouse), and more. LapinCarotte uses Pygame to draw everything you see on the screen, play sounds, and handle your commands.
    *   Learn more about Pygame: [Official Pygame Website](https://www.pygame.org/news)
    *   Simple Pygame tutorials: [Pygame Tutorials for Beginners](https://www.pygame.org/wiki/tutorials)

### How This Game Uses Them

*   **Python** is the main language that defines all the game's logic: how the rabbit moves, how carrots behave, what happens when you collect an item, etc.
*   **Pygame** is used to:
    *   Create the game window.
    *   Draw images (the rabbit, carrots, bullets, background).
    *   Play music and sound effects.
    *   Detect when you press keys or click the mouse.

## Introduction à Python et Pygame (FR)

Ce jeu est écrit en Python et utilise la bibliothèque Pygame.

*   **Python :** Un langage de programmation populaire et facile à apprendre. Il est souvent recommandé pour les débutants car sa syntaxe est claire et lisible. Si tu découvres la programmation, Python est un excellent point de départ !
    *   En savoir plus sur Python : [Site Officiel Python](https://www.python.org) (en anglais)
    *   Un tutoriel Python simple pour enfants (ressource externe, le contenu peut varier) : [Python pour les Kids (OpenClassrooms)](https://openclassrooms.com/fr/courses/235344-apprenez-a-programmer-en-python/232701-introduction)
*   **Pygame :** Un ensemble de modules Python conçus pour écrire des jeux vidéo. Il fournit des fonctionnalités pour les graphismes, le son, les périphériques d'entrée (comme le clavier et la souris), et plus encore. LapinCarotte utilise Pygame pour dessiner tout ce que tu vois à l'écran, jouer des sons et gérer tes commandes.
    *   En savoir plus sur Pygame : [Site Officiel Pygame](https://www.pygame.org/news) (en anglais)
    *   Tutoriels Pygame simples : [Tutoriels Pygame pour Débutants](https://www.pygame.org/wiki/tutorials) (en anglais)

### Comment ce jeu les utilise

*   **Python** est le langage principal qui définit toute la logique du jeu : comment le lapin se déplace, comment les carottes se comportent, ce qui se passe quand tu ramasses un objet, etc.
*   **Pygame** est utilisé pour :
    *   Créer la fenêtre du jeu.
    *   Dessiner les images (le lapin, les carottes, les projectiles, l'arrière-plan).
    *   Jouer la musique et les effets sonores.
    *   Détecter lorsque tu appuies sur des touches ou cliques avec la souris.

## Project Structure (EN)
```mermaid
graph TD
    %% ----- Node Definitions -----
    subgraph "Main Loop (main.py)"
        A[Start main_loop]
        B{Choose Mode}
        C[Create PygameRenderer]
        D[Create TerminalRenderer]
        E[Create InputHandler]
        F{Run Game}
        G[Get Actions]
        H[Update GameState]
        I[Pass to Renderer]
        J[Render Frame]
    end

    subgraph "Model (game_state.py)"
        K[GameState]
        L[Game Entities]
    end

    subgraph "View (Renderer Abstraction)"
        M(Abstract Renderer)
        N[PygameRenderer]
        O(GUI Window)
        P[TerminalRenderer]
        Q(Terminal)
    end

    subgraph "Controller (Input Abstraction)"
        R(Abstract InputHandler)
        S[PygameInputHandler]
        T(Keyboard/Mouse Events)
        U[TerminalInputHandler]
        V(Non-blocking Key Presses)
    end

    %% ----- Link Definitions (Simplified) -----

    %% Main Loop Flow
    A --> B
    B -->|GUI| C
    B -->|CLI| D
    B --> E
    C --> F
    D --> F
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> F

    %% Internal Links
    K --> L
    N --> O
    P --> Q
    S --> T
    U --> V
    
    %% "Inheritance" Links (using standard arrows)
    N --> M
    P --> M
    S --> R
    U --> R

    %% Cross-Subgraph Connections
    H --> K
    I --> M
    G --> R
```

Here's a brief overview of the main files in this project:

*   `main.py`: This is the main entry point of the game. It contains the main game loop, handles events (like key presses), and manages different game states (start screen, game active, game over).
*   `game_entities.py`: Defines the classes for all game objects, such as the `Player` (the rabbit), `Carrot` (enemies), `Bullet`, `Vampire`, and `Collectible` items. Each class defines the behavior and properties of these objects.
*   `game_state.py`: Manages the overall state of the game. This includes tracking the player's health, score (like carrot juice collected), active enemies, items on screen, and game conditions like "game over" or "paused".
*   `config.py`: Contains all the configuration values and constants for the game, like player speed, enemy health, world size, colors, and paths to assets. This makes it easy to tweak game parameters without searching through all the code.
*   `asset_manager.py`: Responsible for loading and managing all game assets (images, sounds). It also handles cases where assets might be missing by providing placeholders.
*   `utilities.py`: Contains helper functions that can be used in different parts of the game.
*   `AGENTS.md`: Provides instructions for AI agents (like me!) working on this codebase. It includes coding conventions and testing procedures.
*   `TODO.md`: Tracks tasks that need to be done or are in progress for the project.
*   `README.md`: This file! It gives an overview of the project, how to run it, and other important information.

## Structure du Projet (FR)

Voici un bref aperçu des fichiers principaux de ce projet :

*   `main.py` : C'est le point d'entrée principal du jeu. Il contient la boucle de jeu principale, gère les événements (comme les pressions de touches) et les différents états du jeu (écran de démarrage, jeu actif, game over).
*   `game_entities.py` : Définit les classes pour tous les objets du jeu, tels que le `Player` (le lapin), `Carrot` (les ennemis), `Bullet` (projectiles), `Vampire`, et les objets `Collectible`. Chaque classe définit le comportement et les propriétés de ces objets.
*   `game_state.py` : Gère l'état global du jeu. Cela inclut le suivi de la santé du joueur, du score (comme le jus de carotte collecté), des ennemis actifs, des objets à l'écran et des conditions de jeu comme "game over" ou "en pause".
*   `config.py` : Contient toutes les valeurs de configuration et les constantes du jeu, comme la vitesse du joueur, la santé des ennemis, la taille du monde, les couleurs et les chemins vers les ressources (assets). Cela facilite la modification des paramètres du jeu sans avoir à chercher dans tout le code.
*   `asset_manager.py` : Responsable du chargement et de la gestion de toutes les ressources du jeu (images, sons). Il gère également les cas où des ressources pourraient manquer en fournissant des substituts (placeholders).
*   `utilities.py` : Contient des fonctions utilitaires qui peuvent être utilisées dans différentes parties du jeu.
*   `AGENTS.md` : Fournit des instructions pour les agents IA (comme moi !) travaillant sur ce code. Il inclut des conventions de codage et des procédures de test.
*   `TODO.md` : Suit les tâches à faire ou en cours pour le projet.
*   `README.md` : Ce fichier ! Il donne un aperçu du projet, comment l'exécuter et d'autres informations importantes.

## Contributing / Contribuer (EN/FR)

If you wish to contribute to this project, please follow these guidelines:
*   **Read `AGENTS.md`**: This file contains important rules and protocols for making changes to the codebase, including testing procedures.
*   **Bilingual Documentation**: As per `AGENTS.md`, all new code comments and logging messages must be bilingual (English first, then French). Please maintain this standard for any modifications.

Si vous souhaitez contribuer à ce projet, veuillez suivre ces directives :
*   **Lisez `AGENTS.md`** : Ce fichier contient des règles et protocoles importants pour apporter des modifications au code, y compris les procédures de test.
*   **Documentation Bilingue** : Conformément à `AGENTS.md`, tous les nouveaux commentaires de code et messages de log doivent être bilingues (anglais d'abord, puis français). Veuillez maintenir cette norme pour toute modification.

## Command Line Interface (CLI) Mode
## Mode Interface en Ligne de Commande (CLI)

This project includes a Command Line Interface (CLI) mode, which runs the game logic without rendering graphics. This is primarily intended for automated testing and can be useful in headless environments.
*Ce projet inclut un mode Interface en Ligne de Commande (CLI), qui exécute la logique du jeu sans rendu graphique. Ceci est principalement destiné aux tests automatisés et peut être utile dans des environnements sans affichage (headless).*

To run in CLI mode:
*Pour exécuter en mode CLI :*
```bash
python main.py --cli
```

Basic interactions in CLI mode include:
*Les interactions de base en mode CLI incluent :*
- Starting the game / *Démarrer le jeu*
- Pausing and continuing the game / *Mettre en pause et reprendre le jeu*
- Simulating player death (by inputting 'd' when the game is active) / *Simuler la mort du joueur (en entrant 'd' lorsque le jeu est actif)*
- Quitting the game / *Quitter le jeu*

### Debug Logging
### Journalisation de Débogage

To get more detailed output for debugging purposes, you can run the game with the `--debug` (or `-d`) flag. This will print more verbose logs to the console, including detailed information about game states, events, and potential issues.
*Pour obtenir une sortie plus détaillée à des fins de débogage, vous pouvez lancer le jeu avec l'option \`--debug\` (ou \`-d\`). Cela affichera des journaux plus verbeux dans la console, y compris des informations détaillées sur les états du jeu, les événements et les problèmes potentiels.*

Example:
*Exemple :*
```bash
python main.py --cli --debug
# or for GUI mode
# ou pour le mode GUI
python main.py --debug
```

## Asset Loading
## Chargement des Ressources (Assets)

The game is designed to be robust against missing assets. If an image or sound file cannot be found at startup:
- A placeholder visual (for images) or a silent dummy sound (for sounds) will be used.
- A warning will be logged to the console.
This allows the game to continue running for development and testing purposes even if some assets are not currently available.

*Le jeu est conçu pour être robuste face aux ressources manquantes. Si un fichier image ou son est introuvable au démarrage :*
*- Un substitut visuel (pour les images) ou un son factice silencieux (pour les sons) sera utilisé.*
*- Un avertissement sera consigné dans la console.*
*Cela permet au jeu de continuer à fonctionner à des fins de développement et de test même si certaines ressources ne sont pas disponibles actuellement.*

# Build executable in dist\
# Compiler l'exécutable dans dist\
```
pip install pyinstaller
python build_exe.py
```
*To create a standalone Windows executable (will be located in the `dist` folder):*
*Pour créer un fichier exécutable Windows autonome (sera situé dans le dossier `dist`) :*

## CI/CD & Automation
## Intégration Continue/Déploiement Continu (CI/CD) & Automatisation

This project uses GitHub Actions for Continuous Integration and automation of tests, builds, and releases. Dependabot is also configured for managing dependency updates.
*Ce projet utilise GitHub Actions pour l'Intégration Continue et l'automatisation des tests, des constructions (builds) et des livraisons (releases). Dependabot est également configuré pour gérer les mises à jour des dépendances.*

For detailed information on the workflows and automation setup, please see [CI.md](CI.md).
*Pour des informations détaillées sur les workflows et la configuration de l'automatisation, veuillez consulter [CI.md](CI.md).*

# Credits
# Crédits
```
Game Design / Conception du Jeu : PixelWarrior9000
Arts / Graphismes : PixelWarrior9000 & AIs
Code & Arts / Code & Graphismes : Random mix of AIs
QA / Assurance Qualité (AQ) : PixelWarrior9000 & sheepdestroyer
Bugfixes & Management / Corrections de Bugs & Gestion : sheepdestroyer
```
