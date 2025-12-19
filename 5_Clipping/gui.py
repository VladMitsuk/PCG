# gui.py
import tkinter as tk
from tkinter import ttk
import algorithms


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clipping Algorithms Lab")
        self.geometry("1200x850")
        self.scale, self.off_x, self.off_y = 1.0, 150, 150
        self.setup_ui()

    def setup_ui(self):
        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=1)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", lambda e: setattr(self, 'lx', e.x) or setattr(self, 'ly', e.y))
        self.canvas.bind("<B1-Motion>", self.pan)
        self.canvas.bind("<MouseWheel>", self.zoom)

        ctrl = tk.Frame(self, width=400)
        ctrl.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Выбор алгоритма
        tk.Label(ctrl, text="Алгоритмы", font=('Arial', 10, 'bold')).pack(anchor="w")
        self.algo_var = tk.StringVar(value="Сазерленд-Коэн")
        algo_cb = ttk.Combobox(ctrl, textvariable=self.algo_var, state="readonly",
                               values=("Сазерленд-Коэн", "Сайрус-Бек (Выпуклый многоугольник)"))
        algo_cb.pack(fill=tk.X, pady=5)
        algo_cb.bind("<<ComboboxSelected>>", lambda e: self.switch_ui())

        # Окна ввода отсекателя
        self.clipping_frame = tk.LabelFrame(ctrl, text="Окна ввода отсекателя", padx=5, pady=5)
        self.clipping_frame.pack(fill=tk.X, pady=5)

        self.rect_frame = tk.Frame(self.clipping_frame)
        tk.Label(self.rect_frame, text="Rect:").pack(side=tk.LEFT)
        self.rect_input = tk.Entry(self.rect_frame);
        self.rect_input.insert(0, "200 100 500 450");
        self.rect_input.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.poly_container = tk.Frame(self.clipping_frame)
        tk.Label(self.poly_container, text="Вершин:").pack(side=tk.LEFT)
        self.poly_count = tk.Entry(self.poly_container, width=5);
        self.poly_count.insert(0, "3");
        self.poly_count.pack(side=tk.LEFT, padx=5)
        tk.Button(self.poly_container, text="OK", command=self.update_poly_fields).pack(side=tk.LEFT)
        self.poly_fields_frame = tk.Frame(self.clipping_frame)

        # Окна ввода отрезков
        tk.Label(ctrl, text="Окна ввода отрезков:", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(10, 0))
        self.lines_count_entry = tk.Entry(ctrl);
        self.lines_count_entry.insert(0, "2");
        self.lines_count_entry.pack(fill=tk.X)
        tk.Button(ctrl, text="Обновить поля", command=self.update_line_fields).pack(fill=tk.X, pady=5)

        sf = tk.Frame(ctrl);
        sf.pack(fill=tk.BOTH, expand=True)
        self.line_canvas = tk.Canvas(sf, height=250)
        sb = ttk.Scrollbar(sf, orient="vertical", command=self.line_canvas.yview)
        self.line_scroll_frame = tk.Frame(self.line_canvas)
        self.line_scroll_frame.bind("<Configure>",
                                    lambda e: self.line_canvas.configure(scrollregion=self.line_canvas.bbox("all")))
        self.line_canvas.create_window((0, 0), window=self.line_scroll_frame, anchor="nw")
        self.line_canvas.configure(yscrollcommand=sb.set)
        self.line_canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        tk.Button(ctrl, text="ВЫПОЛНИТЬ", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), command=self.draw).pack(
            fill=tk.X, pady=10)
        self.switch_ui();
        self.update_line_fields()

    def switch_ui(self):
        if "Сазерленд" in self.algo_var.get():
            self.poly_container.pack_forget();
            self.poly_fields_frame.pack_forget();
            self.rect_frame.pack(fill=tk.X)
        else:
            self.rect_frame.pack_forget();
            self.poly_container.pack(fill=tk.X);
            self.poly_fields_frame.pack(fill=tk.X);
            self.update_poly_fields()

    def update_poly_fields(self):
        for w in self.poly_fields_frame.winfo_children(): w.destroy()
        self.poly_entries = []
        try:
            n = int(self.poly_count.get())
            default = ["200 100", "350 350", "200 350"]
            for i in range(n):
                f = tk.Frame(self.poly_fields_frame);
                f.pack(fill=tk.X)
                tk.Label(f, text=f"V{i + 1}:", width=5).pack(side=tk.LEFT)
                e = tk.Entry(f);
                e.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                e.insert(0, default[i] if i < len(default) else "100 100")
                self.poly_entries.append(e)
        except:
            pass

    def update_line_fields(self):
        for w in self.line_scroll_frame.winfo_children(): w.destroy()
        self.line_entries = []
        try:
            n = int(self.lines_count_entry.get())
            default = ["50 150 600 200", "50 250 600 250"]
            for i in range(n):
                f = tk.Frame(self.line_scroll_frame);
                f.pack(fill=tk.X, pady=2)
                tk.Label(f, text=f"L{i + 1}:", width=5).pack(side=tk.LEFT)
                e = tk.Entry(f);
                e.pack(side=tk.RIGHT, fill=tk.X, expand=True)
                e.insert(0, default[i] if i < len(default) else "0 0 100 100")
                self.line_entries.append(e)
        except:
            pass

    def to_screen(self, x, y):
        return x * self.scale + self.off_x, y * self.scale + self.off_y

    def pan(self, e):
        self.off_x += (e.x - self.lx);
        self.off_y += (e.y - self.ly)
        self.lx, self.ly = e.x, e.y;
        self.draw()

    def zoom(self, e):
        f = 1.1 if (e.delta > 0 or e.num == 4) else 0.9
        self.scale *= f;
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        # Сетка
        for i in range(-50, 50):
            sx, _ = self.to_screen(i * 100, 0);
            _, sy = self.to_screen(0, i * 100)
            self.canvas.create_line(sx, -5000, sx, 5000, fill="#f0f0f0")
            self.canvas.create_line(-5000, sy, 5000, sy, fill="#f0f0f0")

        # ОСИ координат
        ox, oy = self.to_screen(0, 0)
        self.canvas.create_line(-5000, oy, 5000, oy, fill="black", width=1)  # Ось X
        self.canvas.create_line(ox, -5000, ox, 5000, fill="black", width=1)  # Ось Y

        try:
            is_suth = "Сазерленд" in self.algo_var.get()
            if is_suth:
                r = list(map(float, self.rect_input.get().split()))
                p1 = self.to_screen(r[0], r[1]);
                p2 = self.to_screen(r[2], r[3])
                self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1], outline="blue", width=2)
            else:
                poly = [tuple(map(float, e.get().split())) for e in self.poly_entries]
                scr_p = []
                for i, p in enumerate(poly):
                    sx, sy = self.to_screen(*p)
                    scr_p.extend([sx, sy])
                    self.canvas.create_text(sx, sy - 12, text=f"V{i + 1}({p[0]},{p[1]})", fill="blue",
                                            font=("Arial", 9))
                self.canvas.create_polygon(scr_p, fill="", outline="blue", width=2)

            for i, e in enumerate(self.line_entries):
                c = list(map(float, e.get().split()))
                p1, p2 = (c[0], c[1]), (c[2], c[3])
                sp1, sp2 = self.to_screen(*p1), self.to_screen(*p2)
                self.canvas.create_line(sp1, sp2, fill="red", dash=(4, 2))
                self.canvas.create_text(sp1[0], sp1[1] - 10, text=f"L{i + 1}({int(p1[0])},{int(p1[1])})", fill="red",
                                        font=("Arial", 8))

                res = algorithms.cohen_sutherland(p1, p2, r) if is_suth else algorithms.cyrus_beck(p1, p2, poly)
                if res:
                    rp1, rp2 = self.to_screen(*res[0]), self.to_screen(*res[1])
                    self.canvas.create_line(rp1, rp2, fill="green", width=3)
                    self.canvas.create_text(rp1[0], rp1[1] + 12, text=f"({int(res[0][0])},{int(res[0][1])})",
                                            fill="green", font=("Arial", 8, "bold"))
                    self.canvas.create_text(rp2[0], rp2[1] + 12, text=f"({int(res[1][0])},{int(res[1][1])})",
                                            fill="green", font=("Arial", 8, "bold"))
        except:
            pass