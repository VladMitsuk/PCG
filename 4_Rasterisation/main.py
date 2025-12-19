import tkinter as tk
from gui import RasterApp

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = RasterApp(root)
    root.mainloop()