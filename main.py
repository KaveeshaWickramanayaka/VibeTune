import tkinter as tk
from gui import VibeTuneApp

def main():
    """Initializes and runs the VibeTune application."""
    root = tk.Tk()
    VibeTuneApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
