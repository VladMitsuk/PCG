import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser

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
        self.r = self.create_spinbox(frame, 0, 1, 0, 255, vcmd)
        self.g = self.create_spinbox(frame, 0, 2, 0, 255, vcmd)
        self.b = self.create_spinbox(frame, 0, 3, 0, 255, vcmd)

        # CMYK
        ttk.Label(frame, text="CMYK").grid(row=1, column=0, pady=5)
        self.c = self.create_spinbox(frame, 1, 1, 0, 100, vcmd)
        self.m = self.create_spinbox(frame, 1, 2, 0, 100, vcmd)
        self.y = self.create_spinbox(frame, 1, 3, 0, 100, vcmd)
        self.k = self.create_spinbox(frame, 1, 4, 0, 100, vcmd)

        # Lab
        ttk.Label(frame, text="Lab").grid(row=2, column=0, pady=5)
        self.L = self.create_spinbox(frame, 2, 1, 0, 100, vcmd)
        self.a = self.create_spinbox(frame, 2, 2, -128, 127, vcmd)
        self.b_lab = self.create_spinbox(frame, 2, 3, -128, 127, vcmd)

        # Color Picker
        ttk.Label(frame, text="Color").grid(row=3, column=0, pady=5)

        self.color_btn = ttk.Button(frame, text="Pick", command=self.on_color_pick)
        self.color_btn.grid(row=3, column=1, padx=5)

        self.color_preview = tk.Label(frame, width=4, background="#000000", relief="solid", borderwidth=1)
        self.color_preview.grid(row=3, column=2, padx=5)

        # notification
        self.notification = ttk.Label(self.root, foreground="red")
        self.notification.grid(row=10, column=0, columnspan=5, pady=5)

    def create_spinbox(self, parent, row, col, from_, to_, vcmd):
        var = tk.StringVar(value="0")
        spin = tk.Spinbox(
            parent,
            from_=from_,
            to_=to_,
            width=7,
            textvariable=var,
            validate="key",
            validatecommand=vcmd
        )
        spin.var = var
        spin.grid(row=row, column=col, padx=3)
        spin.bind("<KeyRelease>", self.on_change)
        spin.config(command=lambda w=spin: self.on_change_spin(w))
        return spin

    def on_change_spin(self, widget):
        if self.updating:
            return
        self.on_change(type("Event", (), {"widget": widget}))

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
        r = safe_int(self.r.get())
        g = safe_int(self.g.get())
        b = safe_int(self.b.get())

        self.check_range(r, 0, 255, "R")
        self.check_range(g, 0, 255, "G")
        self.check_range(b, 0, 255, "B")

        r = clamp(r, 0, 255)
        g = clamp(g, 0, 255)
        b = clamp(b, 0, 255)
        self.set_vals(self.r, r, self.g, g, self.b, b)

        # -> CMYK
        c, m, y, k = rgb_to_cmyk(r, g, b)
        self.set_vals(self.c, c, self.m, m, self.y, y, self.k, k)

        # -> Lab
        L, a, b_lab = rgb_to_lab(r, g, b)
        self.set_vals(self.L, L, self.a, a, self.b_lab, b_lab)

        # update preview color
        self.color_preview.config(background=f"#{r:02x}{g:02x}{b:02x}")

    def update_from_cmyk(self):
        c = safe_int(self.c.get())
        m = safe_int(self.m.get())
        y = safe_int(self.y.get())
        k = safe_int(self.k.get())

        self.check_range(c, 0, 100, "C")
        self.check_range(m, 0, 100, "M")
        self.check_range(y, 0, 100, "Y")
        self.check_range(k, 0, 100, "K")

        c = clamp(c, 0, 100)
        m = clamp(m, 0, 100)
        y = clamp(y, 0, 100)
        k = clamp(k, 0, 100)
        self.set_vals(self.c, c, self.m, m, self.y, y, self.k, k)

        # -> RGB
        r, g, b = cmyk_to_rgb(c, m, y, k)
        self.set_vals(self.r, r, self.g, g, self.b, b)

        # -> Lab
        L, a, b_lab = rgb_to_lab(r, g, b)
        self.set_vals(self.L, L, self.a, a, self.b_lab, b_lab)

        # update preview
        self.color_preview.config(background=f"#{r:02x}{g:02x}{b:02x}")

    def update_from_lab(self):
        if self.a.get() in "-" or self.b_lab.get() in "-":
            return

        L = safe_int(self.L.get())
        a = int(self.a.get())
        b = int(self.b_lab.get())

        # уведомления
        self.check_range(L, 0, 100, "L")
        self.check_range(a, -128, 127, "a")
        self.check_range(b, -128, 127, "b")

        L = clamp(L, 0, 100)
        a = clamp(a, -128, 127)
        b = clamp(b, -128, 127)
        self.set_vals(self.L, L, self.a, a, self.b_lab, b)

        # -> RGB
        r, g, b_val = lab_to_rgb(L, a, b)
        self.set_vals(self.r, r, self.g, g, self.b, b_val)

        # -> CMYK
        c, m, y, k = rgb_to_cmyk(r, g, b_val)
        self.set_vals(self.c, c, self.m, m, self.y, y, self.k, k)

        # update preview
        self.color_preview.config(background=f"#{r:02x}{g:02x}{b_val:02x}")

    # ---------------------- Color Picker ----------------------

    def on_color_pick(self):
        color = colorchooser.askcolor()
        if not color or not color[0]:
            return

        r, g, b = map(int, color[0])

        self.updating = True
        try:
            # Обновляем RGB
            self.set_vals(self.r, r, self.g, g, self.b, b)
            self.update_from_rgb()

            # Обновляем preview
            self.color_preview.config(background=f"#{r:02x}{g:02x}{b:02x}")
        finally:
            self.updating = False

    # ---------------------- Helper ----------------------

    def notify(self, text, duration=2000):
        """Показывает уведомление и автоматически скрывает его через duration мс"""
        self.notification.config(text=text)
        self.root.after(duration, lambda: self.notification.config(text=""))

    def check_range(self, value, min_v, max_v, field_name):
        if value < min_v or value > max_v:
            self.notify(f"{field_name}: {value} вне диапазона [{min_v}; {max_v}]")
            return False
        return True

    def set_vals(self, *pairs):
        for entry, value in zip(pairs[::2], pairs[1::2]):
            entry.delete(0, tk.END)
            entry.insert(0, str(value))