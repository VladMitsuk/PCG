import tkinter as tk
from tkinter import ttk, messagebox
import time  # <--- 1. Добавляем импорт времени
from raster_logic import RasterAlgorithms


class RasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная: Алгоритмы растеризации")
        self.root.geometry("1000x700")

        # --- Переменные ---
        self.cell_size = 20  # Размер клетки в пикселях (масштаб)
        self.offset_x = 0  # Смещение начала координат
        self.offset_y = 0
        self.last_result_logs = []  # Для хранения данных таблицы
        self.current_algo_name = ""

        # --- Layout ---
        # Левая часть (Canvas)
        self.left_frame = tk.Frame(root, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.left_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Правая часть (Панель управления)
        self.right_frame = tk.Frame(root, width=300, bg="#f0f0f0")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self._init_controls()

        # Биндинги событий
        self.canvas.bind("<Configure>", self.draw_grid)  # Перерисовка при ресайзе
        self.canvas.bind("<Button-1>", self.on_canvas_click)  # Клик мышью для координат
        # Масштабирование колесиком
        self.canvas.bind("<MouseWheel>", self.on_zoom)  # Windows
        self.canvas.bind("<Button-4>", self.on_zoom)  # Linux up
        self.canvas.bind("<Button-5>", self.on_zoom)  # Linux down

        # Рисуем сетку первый раз
        self.draw_grid()

    def _init_controls(self):
        """Создание элементов управления справа"""
        pad_opts = {'padx': 10, 'pady': 5}

        tk.Label(self.right_frame, text="Настройки", font=("Arial", 14, "bold")).pack(**pad_opts)

        # Выбор алгоритма
        tk.Label(self.right_frame, text="Алгоритм:").pack(**pad_opts)
        self.algo_combo = ttk.Combobox(self.right_frame, values=[
            "Пошаговый",
            "ЦДА (DDA)",
            "Брезенхем (Отрезок)",
            "Брезенхем (Окружность)"
        ], state="readonly")
        self.algo_combo.current(0)
        self.algo_combo.pack(**pad_opts)
        self.algo_combo.bind("<<ComboboxSelected>>", self.on_algo_change)

        # Координаты
        self.coord_frame = tk.Frame(self.right_frame)
        self.coord_frame.pack(**pad_opts)

        # X1, Y1
        tk.Label(self.coord_frame, text="X1 / Xc:").grid(row=0, column=0)
        self.ent_x1 = tk.Entry(self.coord_frame, width=8)
        self.ent_x1.grid(row=0, column=1)
        self.ent_x1.insert(0, "0")

        tk.Label(self.coord_frame, text="Y1 / Yc:").grid(row=0, column=2)
        self.ent_y1 = tk.Entry(self.coord_frame, width=8)
        self.ent_y1.grid(row=0, column=3)
        self.ent_y1.insert(0, "0")

        # X2, Y2 (или Радиус)
        self.lbl_x2 = tk.Label(self.coord_frame, text="X2:")
        self.lbl_x2.grid(row=1, column=0)
        self.ent_x2 = tk.Entry(self.coord_frame, width=8)
        self.ent_x2.grid(row=1, column=1)
        self.ent_x2.insert(0, "10")

        self.lbl_y2 = tk.Label(self.coord_frame, text="Y2 / R:")
        self.lbl_y2.grid(row=1, column=2)
        self.ent_y2 = tk.Entry(self.coord_frame, width=8)
        self.ent_y2.grid(row=1, column=3)
        self.ent_y2.insert(0, "5")

        # Кнопки
        tk.Button(self.right_frame, text="Растеризовать", command=self.run_rasterization,
                  bg="#dddddd", font=("Arial", 11)).pack(pady=20, fill=tk.X, padx=10)

        self.btn_table = tk.Button(self.right_frame, text="Таблица расчетов", command=self.show_table_window,
                                   state=tk.DISABLED)
        self.btn_table.pack(pady=5, fill=tk.X, padx=10)

        tk.Label(self.right_frame,
                 text="Инструкция:\n1. Выберите алгоритм.\n2. Введите координаты или\nкликните по сетке (ЛКМ).\n3. Колесо мыши - масштаб.",
                 justify=tk.LEFT, fg="gray").pack(pady=20, padx=10)

        # <--- 2. Метка для времени в самом низу правой панели --->
        self.lbl_time = tk.Label(self.right_frame, text="Время: -", font=("Arial", 10, "bold"), fg="blue")
        # pack с side=BOTTOM прижмет элемент к низу фрейма
        self.lbl_time.pack(side=tk.BOTTOM, anchor="e", padx=10, pady=10)

    def on_algo_change(self, event):
        """Скрывает/показывает поля в зависимости от алгоритма"""
        algo = self.algo_combo.get()
        if "Окружность" in algo:
            self.lbl_x2.grid_remove()
            self.ent_x2.grid_remove()
            self.lbl_y2.config(text="R:")
        else:
            self.lbl_x2.grid()
            self.ent_x2.grid()
            self.lbl_x2.config(text="X2:")
            self.lbl_y2.config(text="Y2:")

    def get_canvas_center(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        return w // 2, h // 2

    def to_screen_coords(self, logic_x, logic_y):
        cx, cy = self.get_canvas_center()
        screen_x = cx + logic_x * self.cell_size
        screen_y = cy - logic_y * self.cell_size  # Y перевернут
        return screen_x, screen_y

    def to_logic_coords(self, screen_x, screen_y):
        cx, cy = self.get_canvas_center()
        logic_x = round((screen_x - cx) / self.cell_size)
        logic_y = round((cy - screen_y) / self.cell_size)
        return logic_x, logic_y

    def draw_grid(self, event=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx, cy = w // 2, h // 2

        # Рисуем сетку
        for i in range(0, w, self.cell_size):
            # Вертикальные линии (с привязкой к центру)
            offset = cx % self.cell_size
            x = i + offset - self.cell_size  # поправка
            self.canvas.create_line(x, 0, x, h, fill="#e0e0e0")

        for i in range(0, h, self.cell_size):
            # Горизонтальные линии
            offset = cy % self.cell_size
            y = i + offset - self.cell_size
            self.canvas.create_line(0, y, w, y, fill="#e0e0e0")

        # Рисуем Оси
        self.canvas.create_line(0, cy, w, cy, width=2, fill="black", arrow=tk.LAST)  # X
        self.canvas.create_text(w - 20, cy + 15, text="X")

        self.canvas.create_line(cx, h, cx, 0, width=2, fill="black", arrow=tk.LAST)  # Y
        self.canvas.create_text(cx + 15, 20, text="Y")

        # Рисуем центр
        self.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill="black")

    def draw_pixel(self, x, y, color="blue"):
        """Закрашивает логический пиксель (клетку)"""
        sx, sy = self.to_screen_coords(x, y)
        half = self.cell_size / 2
        # Квадратик вокруг точки
        self.canvas.create_rectangle(
            sx - half, sy - half,
            sx + half, sy + half,
            fill=color, outline="gray"
        )
        # Опционально: текст координат
        if self.cell_size > 30:
            self.canvas.create_text(sx, sy, text=f"{x},{y}", font=("Arial", 8), fill="white")

    def run_rasterization(self):
        # Очистка предыдущего рисунка (но сетку оставляем)
        self.draw_grid()
        self.lbl_time.config(text="Время: ...") # Сброс времени

        # Чтение данных
        try:
            x1 = int(self.ent_x1.get())
            y1 = int(self.ent_y1.get())

            algo = self.algo_combo.get()
            self.current_algo_name = algo
            points = []
            logs = []

            # <--- 3. Засекаем время перед вычислениями --->
            start_time = time.perf_counter()

            if "Окружность" in algo:
                r = int(self.ent_y2.get())
                if r <= 0:
                    raise ValueError("Радиус должен быть > 0")
                points, logs = RasterAlgorithms.bresenham_circle(x1, y1, r)
            else:
                x2 = int(self.ent_x2.get())
                y2 = int(self.ent_y2.get())

                if "Пошаговый" in algo:
                    points, logs = RasterAlgorithms.step_by_step(x1, y1, x2, y2)
                elif "ЦДА" in algo:
                    points, logs = RasterAlgorithms.dda(x1, y1, x2, y2)
                elif "Брезенхем" in algo:
                    points, logs = RasterAlgorithms.bresenham_line(x1, y1, x2, y2)

            # <--- 4. Останавливаем таймер и вычисляем разницу --->
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            # Обновляем метку времени (форматируем до 6 знаков после запятой)
            self.lbl_time.config(text=f"Время: {elapsed_time:.6f} сек")

            # Сохраняем логи и включаем кнопку
            self.last_result_logs = logs
            self.btn_table.config(state=tk.NORMAL)

            # Рисование (время рисования обычно не включается в время алгоритма,
            # но если нужно, переместите end_time после этого цикла)
            for p in points:
                self.draw_pixel(p[0], p[1])

        except ValueError as e:
            self.lbl_time.config(text="Время: Ошибка")
            messagebox.showerror("Ошибка ввода", f"Некорректные данные:\n{e}")
        except Exception as e:
            self.lbl_time.config(text="Время: Ошибка")
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")

    def show_table_window(self):
        """Окно с таблицей расчетов"""
        if not self.last_result_logs:
            return

        top = tk.Toplevel(self.root)
        top.title(f"Расчеты: {self.current_algo_name}")
        top.geometry("600x400")

        cols = ("Step", "X", "Y", "Calc")
        tree = ttk.Treeview(top, columns=cols, show='headings')

        tree.heading("Step", text="Шаг")
        tree.heading("X", text="X")
        tree.heading("Y", text="Y")
        tree.heading("Calc", text="Вычисления / Ошибка")

        tree.column("Step", width=50)
        tree.column("X", width=50)
        tree.column("Y", width=50)
        tree.column("Calc", width=400)

        for item in self.last_result_logs:
            tree.insert("", "end", values=(
                item.get("step", ""),
                item.get("x", ""),
                item.get("y", ""),
                item.get("calc", "")
            ))

        scrollbar = ttk.Scrollbar(top, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

    def on_zoom(self, event):
        """Масштабирование колесиком"""
        if event.num == 4 or event.delta > 0:
            self.cell_size += 2
        elif (event.num == 5 or event.delta < 0) and self.cell_size > 4:
            self.cell_size -= 2
        self.draw_grid()

    def on_canvas_click(self, event):
        """Удобство: установка координат кликом"""
        lx, ly = self.to_logic_coords(event.x, event.y)

        algo = self.algo_combo.get()

        if not self.ent_x1.get() or (self.ent_x1.get() and self.ent_x2.get() and "Окружность" not in algo):
            self.ent_x1.delete(0, tk.END)
            self.ent_x1.insert(0, str(lx))
            self.ent_y1.delete(0, tk.END)
            self.ent_y1.insert(0, str(ly))

            if "Окружность" not in algo:
                self.ent_x2.delete(0, tk.END)
        else:
            if "Окружность" not in algo:
                self.ent_x2.delete(0, tk.END)
                self.ent_x2.insert(0, str(lx))
                self.ent_y2.delete(0, tk.END)
                self.ent_y2.insert(0, str(ly))
                self.run_rasterization()