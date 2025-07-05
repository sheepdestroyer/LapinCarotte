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

## Command Line Interface (CLI) Mode

This project includes a Command Line Interface (CLI) mode, which runs the game logic without rendering graphics. This is primarily intended for automated testing and can be useful in headless environments.

To run in CLI mode:
```bash
python main.py --cli
```

Basic interactions in CLI mode include:
- Starting the game
- Pausing and continuing the game
- Simulating player death (by inputting 'd' when the game is active)
- Quitting the game

## Asset Loading

The game is designed to be robust against missing assets. If an image or sound file cannot be found at startup:
- A placeholder visual (for images) or a silent dummy sound (for sounds) will be used.
- A warning will be logged to the console.
This allows the game to continue running for development and testing purposes even if some assets are not currently available.

# Build executable in dist\
```
pip install pyinstaller
python build_exe.py
```

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
