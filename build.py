#!/usr/bin/env python3
"""
Build script for creating standalone executable with PyInstaller
"""

import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    """Build the standalone executable using PyInstaller"""

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # PyInstaller command with all necessary hidden imports
    cmd = [
        sys.executable, "-m", "pyinstaller",
        "--onefile",
        "--collect-all=flask",
        "--collect-all=playwright",
        "--collect-all=beautifulsoup4",
        "--hidden-import=webdriver_manager",
        "--hidden-import=webview",
        "--hidden-import=webview.platforms.winforms",
        "--hidden-import=clr",
        "--hidden-import=pythonnet",
        "--hidden-import=lxml",
        "--hidden-import=requests",
        "--hidden-import=urllib3",
        "--name=pahe-downloader",
        "--clean",
        "--noconsole",
        "--icon=static/icon.ico",
        "main.py"
    ]

    print("Building executable with PyInstaller...")
    print("Command:", " ".join(cmd))

    try:
        _ = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print("Executable created at: dist/pahe-downloader.exe")

        # Generate checksum
        exe_path = project_root / "dist" / "pahe-downloader.exe"
        if exe_path.exists():
            import hashlib
            with open(exe_path, "rb") as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

            checksum_file = exe_path.with_suffix(".exe.sha256")
            with open(checksum_file, "w") as f:
                f.write(f"{checksum}  pahe-downloader.exe\n")

            print(f"SHA256 checksum: {checksum}")
            print(f"Checksum saved to: {checksum_file}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)