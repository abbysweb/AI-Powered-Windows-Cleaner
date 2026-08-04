import os
import shutil

import PyInstaller.__main__


def build_app():
    """Builds the AI-Powered Windows Cleaner into a standalone executable."""

    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    print("Starting build process...")

    # We will build main.py or app.py (assuming app.py for GUI)
    # The actual executable is Windows, non-console
    entry_point = "src/ai_health_copilot/main.py"
    if not os.path.exists(entry_point):
        print(f"Error: {entry_point} not found!")
        return

    PyInstaller.__main__.run(
        [
            entry_point,
            "--name=AI_Windows_Health_Copilot",
            "--windowed",
            "--noconfirm",
            "--clean",
            "--add-data=database/schema.sql;database/",
            "--icon=NONE",  # Add an icon later
        ]
    )

    print("Build complete! Executable is in the dist/ directory.")


if __name__ == "__main__":
    build_app()
