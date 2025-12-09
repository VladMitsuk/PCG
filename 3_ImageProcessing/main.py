import sys
from PyQt6.QtWidgets import QApplication
from gui import ImageProcessorWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageProcessorWindow()
    ex.show()
    sys.exit(app.exec())
