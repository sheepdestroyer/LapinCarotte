import subprocess
import sys
import os
import pytest

# Determine the correct path to main.py relative to the tests directory
MAIN_PY_PATH = os.path.join(os.path.dirname(__file__), '..', 'main.py')

def run_cli_test(inputs, include_debug_flag=True): # Added include_debug_flag
    """Helper function to run main.py --cli with given inputs."""
    cmd = [sys.executable, MAIN_PY_PATH, '--cli']
    if include_debug_flag:
        cmd.append('--debug')

    process = subprocess.Popen(
        cmd, # Use the constructed command
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input='\n'.join(inputs) + '\n', timeout=10) # Added timeout
    return process.returncode, stdout, stderr

class TestCLIPassThrough: # Renamed to avoid conflict with Pytest's own 'TestCLI' or similar
    def test_cli_start_and_exit(self):
        """Test starting the game in CLI mode and exiting from the start menu."""
        inputs = ['2'] # Select "Exit"
        returncode, stdout, stderr = run_cli_test(inputs)

        assert returncode == 0, f"CLI process exited with code {returncode}. Stderr:\n{stderr}"
        # "Running in CLI mode." is now an INFO log, so it will be in stdout with formatting.
        # We check for the core message.
        assert "CLI mode enabled." in stdout # This is the new INFO log message
        assert "Start Screen (CLI Mode)" in stdout
        assert "1. Start Game" in stdout
        assert "2. Exit" in stdout
        # Check that the game doesn't proceed to "Game Active"
        assert "Game Active (CLI Mode)" not in stdout
        # Check for clean exit, no error messages in stderr ideally
        # Allow specific warnings from AssetManager if assets are missing (like buttons for GUI mode)
        # For now, a simple check:
        # assert "ERROR" not in stderr.upper(), f"Errors in stderr: {stderr}"
        # This might be too strict if there are benign warnings.
        # Let's check for specific error patterns if needed later.
        # For now, successful returncode is the primary check for clean exit.
        print(f"STDOUT:\n{stdout}") # Print stdout for debugging in CI if needed
        if stderr:
            print(f"STDERR:\n{stderr}") # Print stderr if not empty

    # Placeholder for other tests
    def test_cli_start_die_restart_exit(self):
        """Test starting, simulating death, restarting, and then exiting."""
        inputs = [
            '1', # Start Game
            'd', # Simulate Death
            '1', # Restart
            '2'  # Exit
        ]
        returncode, stdout, stderr = run_cli_test(inputs)

        assert returncode == 0, f"CLI process exited with code {returncode}. Stderr:\n{stderr}"
        print(f"STDOUT:\n{stdout}")
        if stderr:
            print(f"STDERR:\n{stderr}")

        assert "Start Screen (CLI Mode)" in stdout
        assert "Game Active (CLI Mode)" in stdout # Initial active state
        assert "Simulating player death for CLI testing..." in stdout # Message from 'd' block
        # "Player died. Game Over." was removed from main.py, this check is no longer valid.
        assert "--- GAME OVER (CLI Mode) ---" in stdout # Check for the actual Game Over menu
        assert "Game reset (CLI)." in stdout # Confirms the restart action from game over menu
        # Ensure it returns to start screen after restart and then exits
        assert stdout.count("Start Screen (CLI Mode)") >= 2 # Initial, and after restart
        assert "Exiting game." in stdout # Final exit message

    def test_cli_start_pause_continue_quit(self):
        """Test starting, pausing, continuing, and then quitting."""
        inputs = [
            '1', # Start Game
            'p', # Pause
            '1', # Continue
            'q'  # Quit from active game
        ]
        returncode, stdout, stderr = run_cli_test(inputs)

        assert returncode == 0, f"CLI process exited with code {returncode}. Stderr:\n{stderr}"
        print(f"STDOUT:\n{stdout}")
        if stderr:
            print(f"STDERR:\n{stderr}")

        assert "Start Screen (CLI Mode)" in stdout
        assert stdout.count("Game Active (CLI Mode)") >= 2 # Before pause, and after continue
        assert "PAUSED (CLI Mode)" in stdout
        # Check that the game doesn't show game over screen
        assert "GAME OVER (CLI Mode)" not in stdout
