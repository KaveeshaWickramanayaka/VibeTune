import tkinter as tk
from gui import MoodMusicPlayer

def main():
    root = tk.Tk()
    app = MoodMusicPlayer(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1200 // 2)
    y = (root.winfo_screenheight() // 2) - (900 // 2)
    root.geometry(f"1200x900+{x}+{y}")
    
    # Set window icon (optional)
    try:
        root.iconbitmap("music_icon.ico")  # You can add an icon file
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()