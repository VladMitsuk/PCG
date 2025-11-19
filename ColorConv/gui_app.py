import tkinter as tk
from tkinter import ttk


class gui_app:
    def __init__(self):
        self.models = {'RGB':['R','G','B'],'CMYK':['C','M','Y','K'],'Lab':['L','a','b']}
        self.root = tk.Tk()
        self.config()
        self.widgets()

    def config(self):
        self.root.title("Color Converter")
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{int(width*0.5)}x{int(height*0.5)}+"
                           f"{int((width-width*0.5)//2)}+{int((height-height*0.5)//2)}")

    def widgets(self):  # добавляет виджеты с отслеживанием
        # Entry
        self.vars = {}
        for row, (model_name, values) in enumerate(self.models.items()):
            model_label = tk.Label(self.root, text=model_name, font=('Arial', 10, 'bold'))
            model_label.grid(row=row, column=0, padx=5, pady=5)
            for col, component in enumerate(values):
                frame = tk.Frame(self.root)
                frame.grid(row=row, column=col+1, padx=2, pady=5)
                component_label = tk.Label(frame, text=component, font=('Arial', 8))
                component_label.pack()

                self.vars[row,col] = tk.DoubleVar()
                self.vars[row,col].trace_add("write",self.update_all)
                entry = ttk.Entry(frame, width=10, textvariable=self.vars[row,col])
                entry.pack()
        # Palette
        # Scale

    def update_all(self,*args):
        try:
            pass
        except Exception:
            pass

    def run(self):
        self.root.mainloop()
