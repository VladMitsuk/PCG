import tkinter as tk
from tkinter import ttk
from color_logic import *
from validation import *


class ColorConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Model Converter")

        self.updating = False  # Prevent recursive updates

        self.create_ui()

    # ---------------------- UI Layout ----------------------

    def create_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid()

        # Validation for numeric only
        vcmd = (self.root.register(validate_numeric), "%P")

        # RGB
        ttk.Label(frame, text="RGB").grid(row=0, column=0, pady=5)
        self.r = self.create_entry(frame, 0, 1, vcmd)
        self.g = self.create_entry(frame, 0, 2, vcmd)
        self.b = self.create_entry(frame, 0, 3, vcmd)

        # CMYK
        ttk.Label(frame, text="CMYK").grid(row=1, column=0, pady=5)
        self.c = self.create_entry(frame, 1, 1, vcmd)
        self.m = self.create_entry(frame, 1, 2, vcmd)
        self.y = self.create_entry(frame, 1, 3, vcmd)
        self.k = self.create_entry(frame, 1, 4, vcmd)

        # Lab
        ttk.Label(frame, text="Lab").grid(row=2, column=0, pady=5)
        self.L = self.create_entry(frame, 2, 1, vcmd)
        self.a = self.create_entry(frame, 2, 2, vcmd)
        self.b_lab = self.create_entry(frame, 2, 3, vcmd)

    def create_entry(self, parent, row, col, vcmd):
        entry = ttk.Entry(parent, width=7, validate="key", validatecommand=vcmd)
        entry.insert(0, "0")
        entry.grid(row=row, column=col, padx=3)
        entry.bind("<KeyRelease>", self.on_change)
        return entry

    # ---------------------- Event Handling ----------------------

    def on_change(self, event):
        if self.updating:
            return

        widget = event.widget
        if not widget.get():
            return

        self.updating = True
        try:
            if widget in (self.r, self.g, self.b):
                self.update_from_rgb()

            elif widget in (self.c, self.m, self.y, self.k):
                self.update_from_cmyk()

            elif widget in (self.L, self.a, self.b_lab):
                self.update_from_lab()
        finally:
            self.updating = False

    # ---------------------- Update Logic ----------------------

    def update_from_rgb(self):
        r = clamp(safe_int(self.r.get()), 0, 255)
        g = clamp(safe_int(self.g.get()), 0, 255)
        b = clamp(safe_int(self.b.get()), 0, 255)
        self.set_vals(self.r, r, self.g, g, self.b, b)

        # -> CMYK
        c, m, y, k = rgb_to_cmyk(r, g, b)
        self.set_vals(self.c, c, self.m, m, self.y, y, self.k, k)

        # -> Lab
        L, a, b_lab = rgb_to_lab(r, g, b)
        self.set_vals(self.L, L, self.a, a, self.b_lab, b_lab)

    def update_from_cmyk(self):
        c = clamp(safe_int(self.c.get()), 0, 100)
        m = clamp(safe_int(self.m.get()), 0, 100)
        y = clamp(safe_int(self.y.get()), 0, 100)
        k = clamp(safe_int(self.k.get()), 0, 100)
        self.set_vals(self.c, c, self.m, m, self.y, y, self.k, k)

        # -> RGB
        r, g, b = cmyk_to_rgb(c, m, y, k)
        self.set_vals(self.r, r, self.g, g, self.b, b)

        # -> Lab
        L, a, b_lab = rgb_to_lab(r, g, b)
        self.set_vals(self.L, L, self.a, a, self.b_lab, b_lab)

    def update_from_lab(self):
        if self.a.get() in "-" or \
                self.b_lab.get() in "-":
            return
        L = clamp(safe_int(self.L.get()), 0, 100)
        a = clamp(safe_int(self.a.get()), -128, 127)
        b = clamp(safe_int(self.b_lab.get()), -128, 127)
        self.set_vals(self.L, L, self.a, a, self.b_lab, b)

        # -> RGB
        r, g, b = lab_to_rgb(L, a, b)
        self.set_vals(self.r, r, self.g, g, self.b, b)

        # -> CMYK
        c, m, y_c, k = rgb_to_cmyk(r, g, b)
        self.set_vals(self.c, c, self.m, m, self.y, y_c, self.k, k)

    # ---------------------- Helper ----------------------

    def set_vals(self, *pairs):
        for entry, value in zip(pairs[::2], pairs[1::2]):
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
