import tkinter as tk

class gui_app:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Color Converter")
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{int(width*0.5)}x{int(height*0.5)}+"
                           f"{int((width-width*0.5)//2)}+{int((height-height*0.5)//2)}")
    def run(self):
        self.root.mainloop()