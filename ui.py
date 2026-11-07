import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from noise_handler import gen_fpn, gen_vn, rescale
from typing import Literal

from tkinter import ttk
THEME_BG = "#302f2f"
THEME_FG = "#e8e8e8"
THEME_ACCENT = "#3D4F2A"
THEME_ACCENT_FG = "#ffffff"
THEME_FIELD_BG = "#3c3c3c"
THEME_FONT = ("Palatino Linotype", 12)
def apply_theme(root):
    """Apply the project theme as defaults; per-widget options override these."""
    root.configure(bg=THEME_BG)
    root.option_add("*background", THEME_BG)
    root.option_add("*foreground", THEME_FG)
    root.option_add("*font", THEME_FONT)
    root.option_add("*Entry.background", THEME_FIELD_BG)
    root.option_add("*Text.background", THEME_FIELD_BG)
    root.option_add("*Listbox.background", THEME_FIELD_BG)
    root.option_add("*Button.background", THEME_ACCENT)
    root.option_add("*Button.foreground", THEME_ACCENT_FG)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", background=THEME_BG, foreground=THEME_FG, fieldbackground=THEME_FIELD_BG, font=THEME_FONT)


class NoiseApp:
    def __init__(self, root):
        apply_theme(root)
        self.root = root
        self.root.title("Bryce's Noise Generator")
        self.current_img = Image.new('RGB', (16, 16), 0)
        self.stored_imgs = []
        self.stored_photos = []
        self.stored_lbls = []
        self._build_ui()
        self._on_select()  # initial show of FPN frame   


    # - Helper for making and placing widgets -
    def makeWidget(self, widget, row=-1, column=-1, padx=5, pady=5, ipadx=0, ipady=0, sticky="nsew", appendRow:Literal["top","bottom","none"]="none", appendCol:Literal["left","right","none"]="none", rowWeight=0, columnWeight=0):
        parent = widget.master
        if appendRow == "top":
            row = 0
            for child in parent.winfo_children():
                info = child.grid_info()
                if info:
                    child.grid_configure(row=int(info["row"]) + 1)
        elif appendRow == "bottom":
            row = parent.grid_size()[1]

        if appendCol == "left":
            column = 0
            for child in parent.winfo_children():
                info = child.grid_info()
                if info:
                    child.grid_configure(column=int(info["column"]) + 1)
        elif appendCol == "right":
            column = parent.grid_size()[0]

        if row == -1:       row =    parent.grid_size()[1] - 1
        if row<0: row=0; #in case first widget
        if column == -1:    column = parent.grid_size()[0] - 1
        if column<0: column=0; #in case first widget

        widget.grid(row=row, column=column, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady, sticky=sticky)
        if rowWeight!=0:    parent.grid_rowconfigure(row, weight=rowWeight);
        if columnWeight!=0: parent.grid_columnconfigure(column, weight=columnWeight);

        return widget    


    # --- UI construction ---
    def _build_ui(self):

        self.gen_frame = self.makeWidget(tk.Frame(self.root, relief="groove", border=5))
        self.genSettings_frame = self.makeWidget(tk.Frame(self.gen_frame, relief="raised", border=2), padx=10,pady=10)
    
        # Generator Mode Menu (no trace yet)
        self.option_var = tk.StringVar(value="Fractal Perlin Noise")
        self.makeWidget(tk.Label(self.genSettings_frame, text="Generation Mode:"))
        self.makeWidget(tk.OptionMenu(self.genSettings_frame, self.option_var, "Fractal Perlin Noise", *["Voronoi Noise"], command=self._on_select), appendRow="bottom")

        # Universal params
        self.univ = {"resolutionX": tk.IntVar(value=32), "resolutionY": tk.IntVar(value=32), "seed": tk.IntVar(value=0)}
        self.frame_univ = self.makeWidget(tk.Frame(self.genSettings_frame), appendRow="bottom")
        self._param_frame(self.univ, self.frame_univ)

        # FPN params
        self.fpn = {"octaves": tk.IntVar(value=1), "persistence": tk.DoubleVar(value=.5), "lacunarity": tk.DoubleVar(value=2), "scale": tk.IntVar(value=1)}
        self.frame_fpn = self.makeWidget(tk.Frame(self.genSettings_frame), appendCol="right")
        self._param_frame(self.fpn, self.frame_fpn)

        # VN params
        self.vn = {"cellsX": tk.IntVar(value=4), "cellsY": tk.IntVar(value=4), "shake": tk.DoubleVar(value=1), "returnMode": tk.StringVar(value="integer")}
        self.frame_vn = self.makeWidget(tk.Frame(self.genSettings_frame))
        self._param_frame(self.vn, self.frame_vn)

        # Run button
        run_button = self.makeWidget(tk.Button(self.genSettings_frame, text="Generate Image", command=self.run, border=4), appendRow="bottom", column=0)
        run_button.grid(columnspan=4)

        # Image display
        self.image_label = self.makeWidget(tk.Label(self.gen_frame, relief="sunken", border=5), row=0, appendCol="right")

        # Storage
        self._build_storage()

        # NOW attach the trace — all attributes exist
        self.option_var.trace_add("write", self._on_select)   

    def _param_frame(self, params, frame=None):
        frame = frame or self.makeWidget(tk.Frame(self.root), appendCol="right", appendRow="bottom")
        for name, var in params.items():
            lbl = self.makeWidget(tk.Label(frame, text=name), sticky="w", appendRow="bottom", column=0)
            entry = self.makeWidget(tk.Entry(frame, textvariable=var, width=20), sticky="w", column=1)
        return frame    

    def _build_storage(self):
        self.stored_var = tk.IntVar(value=1)
        self.storage_frame = self.makeWidget(tk.Frame(self.root, relief='groove', border=5), appendRow="bottom", sticky="nsew", ipady=5, ipadx=5)
        # Button ui
        self.storeButtons_frame = self.makeWidget(tk.Frame(self.storage_frame), sticky="EW", columnWeight=1)

        self.makeWidget(tk.Label(self.storeButtons_frame, text="Storage Slot #"), row=0, column=0)
        self.makeWidget(tk.Label(self.storeButtons_frame, textvariable=self.stored_var), appendCol="right", sticky='EW')

        self.makeWidget(tk.Button(self.storeButtons_frame, text="Store New", command=self.store_new), row=1, column=0)
        self.makeWidget(tk.Button(self.storeButtons_frame, text="Overwrite", command=self.store_img), row=1, column=1)
        self.makeWidget(tk.Button(self.storeButtons_frame, text="Load", command=self.pull_img), row=1, column=2)


        # Stored images ui
        self.storageSlots_frame = self.makeWidget(tk.Frame(self.storage_frame, relief="sunken", border=2), appendRow="bottom", pady=0)

        self.storageSlots_canvas = self.makeWidget(
            tk.Canvas(self.storageSlots_frame),
            row=0, column=0, columnWeight=1, pady=0
        )
        self.storageSlots_scrollbar = self.makeWidget(
            tk.Scrollbar(self.storageSlots_frame, orient="horizontal", command=self.storageSlots_canvas.xview, width=20),
            row=1, column=0, sticky="EW", appendRow="top", ipady=5
        )
        self.storageSlots_scrollframe = self.makeWidget(tk.Frame(self.storageSlots_canvas))

        self.storageSlots_canvas.configure(xscrollcommand=self.storageSlots_scrollbar.set)

        win_id = self.storageSlots_canvas.create_window((0, 0), window=self.storageSlots_scrollframe, anchor="nw")
        self.storageSlots_canvas.bind("<Configure>", lambda e: self.storageSlots_canvas.itemconfig(win_id, height=e.height))
        self.storageSlots_scrollframe.bind("<Configure>", lambda e: self.storageSlots_canvas.configure(scrollregion=self.storageSlots_canvas.bbox("all")))     

    # --- Callbacks ---
    def _on_select(self, *_):
        self.frame_fpn.grid_remove()
        self.frame_vn.grid_remove()
        (self.frame_fpn if self.option_var.get() == "Fractal Perlin Noise" else self.frame_vn).grid()

    def run(self):
        res = (self.univ["resolutionX"].get(), self.univ["resolutionY"].get())
        if self.option_var.get() == "Fractal Perlin Noise":
            self.current_img = gen_fpn(res, self.fpn["octaves"].get(), self.univ["seed"].get(), self.fpn["persistence"].get(), self.fpn["lacunarity"].get(), self.fpn["scale"].get())
        elif self.option_var.get() == "Voronoi Noise":
            self.current_img = gen_vn(res, (self.vn["cellsX"].get(), self.vn["cellsY"].get()), self.univ["seed"].get(), self.vn["shake"].get(), self.vn["returnMode"].get())
        else: return;
        self._show_image(self.current_img)

    def _show_image(self, img):
        if np.linalg.norm(img.size) < 400:
            img = img.resize(rescale(img.size, 512), Image.Resampling.NEAREST)
        photo = ImageTk.PhotoImage(img)
        self.image_label.config(image=photo)
        self.image_label.image = photo  # prevent GC

    # --- Storage ---
    def _new_slot(self, i):
        lbl = self.makeWidget(tk.Label(self.storageSlots_scrollframe, highlightbackground="green"), appendCol="right")
        lbl.grid(sticky="w")
        self.stored_lbls.append(lbl)
        self.stored_photos.append(None)
        self.stored_imgs.append(None)
        lbl.bind("<Button-1>", lambda e, num=i: self._select_slot(num))

    def _select_slot(self, num):
        self.stored_var.set(num)
        for i, lbl in enumerate(self.stored_lbls):
            lbl.configure(relief=("raised" if i == num else "flat"), border=(5 if i==num else 0))
            lbl.configure(highlightthickness=(2 if i == num else 0))

    def store_img(self):
        num = self.stored_var.get()
        if num < 0: return
        elif type(num) != type(int(0)):
            if num == int(num): num = int(num)
            else: return
        if num >= len(self.stored_imgs):
            num = len(self.stored_imgs)
            self._new_slot(num)
            self.stored_var.set(num)
        self._select_slot(num)
        self.stored_imgs[num] = self.current_img
        self.stored_photos[num] = ImageTk.PhotoImage(
            self.current_img.resize(rescale(self.current_img.size, 128), Image.Resampling.NEAREST))
        self.stored_lbls[num].config(image=self.stored_photos[num])

    def store_new(self):
        self.stored_var.set(len(self.stored_imgs) + 1)
        self.store_img()

    def pull_img(self):
        num = self.stored_var.get()
        self.current_img = self.stored_imgs[num]
        self._show_image(self.current_img)