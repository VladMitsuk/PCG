import tkinter as tk
from gui import RasterApp

if __name__ == "__main__":
    root = tk.Tk()
    # Пытаемся настроить масштабирование для HighDPI дисплеев (Windows)
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = RasterApp(root)
    root.mainloop()