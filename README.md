# LapinCarotte
Un lapin combat les carottes vampires

![image](https://github.com/user-attachments/assets/577473aa-4569-43aa-9c7a-0c6f26821257)


# Download latest Windows executable
Get [LapinCarotte.exe](https://github.com/sheepdestroyer/LapinCarotte/releases/download/v0.3-beta/LapinCarotte.exe) here: https://github.com/sheepdestroyer/LapinCarotte/releases

# Run dev env
```
pip install pygame-ce
python main.py
```

# Build executable in dist\
```
pip install pyinstaller
python build_exe.py
```

## Gameplay Features

*   **Dynamic Scrolling World:** Explore a large world that scrolls as you move.
*   **Combat:** Shoot projectiles (left-click or Space) to defend yourself.
*   **Special Attack:** Use a powerful Garlic Shot (right-click, consumes garlic).
*   **Collectibles:** Gather HP, Garlic, and Carrot Juice dropped by enemies.
*   **Enemies:** Face off against vampire carrots and a main vampire boss.
*   **Pause and Settings:** Press `ESCAPE` to pause the game. From the pause menu, you can resume, access game settings, or quit. The settings screen allows live modification of various game parameters like player speed, bullet speed, etc. *(Note: Currently, a SyntaxError in `main.py` prevents the game from running, but this feature is implemented).*

## CI/CD & Automation

This project uses GitHub Actions for Continuous Integration and automation of tests, builds, and releases. Dependabot is also configured for managing dependency updates.

For detailed information on the workflows and automation setup, please see [CI.md](CI.md).

# Credits
```
Game Design : PixelWarrior9000
Arts : PixelWarrior9000 & AIs
Code & Arts : Random mix of AIs
QA : PixelWarrior9000 & sheepdestroyer
Bugfixes & Management : sheepdestroyer
```
