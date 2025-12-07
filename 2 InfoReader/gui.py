import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QAbstractItemView,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QFileInfo


COLUMN_HEADERS = [
    "Имя файла",
    "Размер (px)",
    "Разрешение (DPI)",
    "Глубина цвета",
    "Сжатие"
]
COL_FILENAME, COL_SIZE_PX, COL_DPI, COL_DEPTH, COL_COMPRESSION = range(len(COLUMN_HEADERS))


class MainWindow(QMainWindow):
    # Сигнал, который будет испускаться при выборе папки пользователем.
    # Мы передадим путь к папке в модуль worker.py через этот сигнал.
    folder_selected_signal = pyqtSignal(str)

    # Сигнал для отображения статуса обработки (например, в будущем статус-баре)
    status_update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("2 InfoReader")
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()
        # Список для хранения данных, пока они обрабатываются и добавляются в таблицу
        self.file_data = []

    def init_ui(self):
        """Инициализация виджетов и компоновки."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # 1. Кнопка выбора папки
        self.select_folder_button = QPushButton("Выбрать папку для сканирования")
        self.select_folder_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.select_folder_button)

        # 2. Таблица для отображения данных
        self.table_widget = QTableWidget()
        self.setup_table()
        layout.addWidget(self.table_widget)

        central_widget.setLayout(layout)

        # Инициализация статус-бара (используем встроенный в QMainWindow)
        self.status_update_signal.connect(self.statusBar().showMessage)
        self.status_update_signal.emit("Приложение готово. Выберите папку.")

    def setup_table(self):
        """Настройка внешнего вида и структуры таблицы."""
        self.table_widget.setColumnCount(len(COLUMN_HEADERS))
        self.table_widget.setHorizontalHeaderLabels(COLUMN_HEADERS)

        # Растягиваем первый столбец, чтобы он занимал доступное пространство
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(COL_FILENAME, QHeaderView.ResizeMode.Stretch)
        for i in range(1, len(COLUMN_HEADERS)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        # Запрещаем редактирование ячеек
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def browse_folder(self):
        """Открывает диалог выбора папки и испускает сигнал."""
        self.status_update_signal.emit("Ожидание выбора папки...")
        # QFileDialog.getExistingDirectory возвращает путь к выбранной папке
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку с изображениями")

        if folder_path:
            self.status_update_signal.emit(f"Папка выбрана: {folder_path}. Запуск сканирования...")
            # Очищаем таблицу перед новым сканированием
            self.table_widget.setRowCount(0)
            self.file_data = []
            # Испускаем сигнал, который будет перехвачен модулем worker
            self.folder_selected_signal.emit(folder_path)
        else:
            self.status_update_signal.emit("Выбор папки отменен.")

    def add_file_row(self, data: dict):
        """
        Метод для добавления одной строки данных в таблицу.
        Вызывается из worker.py через сигналы.
        """
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        # Заполнение ячеек данными из словаря
        self.table_widget.setItem(row_position, COL_FILENAME, QTableWidgetItem(data.get("filename", "N/A")))
        self.table_widget.setItem(row_position, COL_SIZE_PX, QTableWidgetItem(data.get("size_px", "N/A")))
        self.table_widget.setItem(row_position, COL_DPI, QTableWidgetItem(data.get("dpi", "N/A")))
        self.table_widget.setItem(row_position, COL_DEPTH, QTableWidgetItem(data.get("depth", "N/A")))
        self.table_widget.setItem(row_position, COL_COMPRESSION, QTableWidgetItem(data.get("compression", "N/A")))

    def processing_finished(self, count):
        """Обновление статуса, когда обработка завершена."""
        QMessageBox.information(self, "Готово", f"Обработка завершена. Найдено {count} файлов.")
        self.status_update_signal.emit(f"Готово. Обработано {count} файлов.")

    def display_error(self, error_message):
        """Отображение критических ошибок."""
        QMessageBox.critical(self, "Ошибка", str(error_message))
        self.status_update_signal.emit(f"Ошибка: {error_message}")


if __name__ == "__main__":
    # Этот блок позволяет запускать gui.py напрямую для тестирования интерфейса
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
