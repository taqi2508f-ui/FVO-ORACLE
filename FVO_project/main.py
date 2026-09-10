import sys
import os
import tkinter as tk
from tkinter import messagebox

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_dependencies():
    missing = []
    try:
        import requests
    except ImportError:
        missing.append("requests")
    try:
        from PIL import Image
    except ImportError:
        pass
    return missing


def main():
    missing = check_dependencies()
    if missing:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "FVO — Missing Dependencies",
            f"Missing packages: {', '.join(missing)}\n\n"
            "Run requirements.bat to install all dependencies.\n\n"
            "Or manually run:\n"
            f"  pip install {' '.join(missing)}"
        )
        root.destroy()
        sys.exit(1)

    from ui.app import FVOApp
    app = FVOApp()
    app.mainloop()


if __name__ == "__main__":
    main()
