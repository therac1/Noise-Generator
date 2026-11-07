import sys, os
import tkinter as tk
from ui import NoiseApp

root = tk.Tk()

# try window app icon
if getattr(sys, 'frozen', False):
    # Running as .exe — use the icon embedded in the exe itself
    root.iconbitmap(sys.executable)
else:
    # Running as a script in VS Code
    root.iconbitmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico'))

NoiseApp(root)
root.mainloop()