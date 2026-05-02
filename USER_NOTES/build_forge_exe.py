import PyInstaller.__main__

PyInstaller.__main__.run([
    "main.py",
    "--name=AkiraForge",
    "--onefile",
    "--windowed",
    "--icon=assets/app_icon.png.png",

    "--collect-all=PySide6",

    "--exclude-module=PyQt6",

    "--add-data=assets;assets",
    "--add-data=resources;resources",
    "--add-data=config.json;."
])
