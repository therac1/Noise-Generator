import tkinter as tk
from tkinter import font

root = tk.Tk()
root.withdraw()  # hide the window

for family in sorted(font.families()):
    print(family)

root.destroy()   