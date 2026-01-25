# build_exe.py
import glob
import os
import sys

import PyInstaller.__main__


def collect_assets():
    """Collect all PNG and MP3 files from the Assets directory"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "Assets")

    # Create the assets directory if it doesn't exist
    os.makedirs(assets_dir, exist_ok=True)

    # Collect all PNG and MP3 files
    png_files = glob.glob(os.path.join(
        assets_dir, "**", "*.png"), recursive=True)
    mp3_files = glob.glob(os.path.join(
        assets_dir, "**", "*.mp3"), recursive=True)

    # Create data_files list for PyInstaller
    # Use os.pathsep as PyInstaller uses ':' on POSIX (Linux/macOS) and ';' on Windows for --add-data
    data_files = []
    for file in png_files + mp3_files:
        # Get relative path from assets directory
        rel_dir = os.path.dirname(os.path.relpath(file, script_dir))
        # Format for PyInstaller: (source_path, destination_directory)
        data_files.append(f"--add-data={file}{os.pathsep}{rel_dir}")

    return data_files


def build_executable():
    # Directory containing your script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the release tag from environment variable, default to "dev"
    release_tag = os.environ.get("RELEASE_TAG", "dev")
    executable_name = f"LapinCarotte-{release_tag}"
    print(
        f"Using RELEASE_TAG: {release_tag}, executable name will be: {executable_name}"
    )

    # Collect asset files
    asset_args = collect_assets()

    # Create PyInstaller command
    pyinstaller_args = [
        "main.py",
        "--onefile",  # Create a single executable
        "--clean",  # Clean PyInstaller cache
        "--noconfirm",  # Replace output directory without asking
        f"--name={executable_name}",  # Name of your executable
        "--noconsole",
        "-i=Assets/HP.ico",
        "--optimize=2",
        "--noupx",
    ]

    # Add all asset files to the command
    pyinstaller_args.extend(asset_args)

    print("Building executable with the following assets:")
    for arg in asset_args:
        print(f"  {arg}")

    # Run PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)


if __name__ == "__main__":
    build_executable()
