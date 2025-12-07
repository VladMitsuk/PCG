import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThread
from gui import MainWindow
from worker import Worker


class Application:
    """
    Класс приложения, управляющий основным циклом и связями между модулями.
    """

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()

        # Переменные для управления потоком и обработчиком
        self.worker_thread = None
        self.worker_logic = None

        # Подключение сигнала выбора папки из GUI к нашему методу запуска обработки
        self.main_window.folder_selected_signal.connect(self.start_processing)

        self.main_window.show()

    def start_processing(self, folder_path: str):
        """
        Метод запускает процесс обработки файлов в новом потоке.
        """
        # Проверяем, существует ли объект и запущен ли он
        if self.worker_thread is not None and self.worker_thread.isRunning():
            QMessageBox.warning(self.main_window, "Внимание",
                                "Предыдущая обработка еще не завершена. Пожалуйста, подождите.")
            return

            # 1. Создаем новый QThread
        self.worker_thread = QThread()

        # 2. Создаем объект логики Worker и передаем ему путь к папке
        self.worker_logic = Worker(folder_path)

        # 3. Перемещаем объект Worker в созданный поток
        self.worker_logic.moveToThread(self.worker_thread)

        # 4. Соединяем сигналы Worker'а со слотами в MainWindow (GUI)
        self.worker_logic.data_ready.connect(self.main_window.add_file_row)
        self.worker_logic.finished.connect(self.main_window.processing_finished)
        self.worker_logic.progress_update.connect(self.main_window.status_update_signal.emit)
        self.worker_logic.error.connect(self.main_window.display_error)

        # 5. Соединяем сигнал запуска потока с методом, который выполняет работу
        self.worker_thread.started.connect(self.worker_logic.run_processing)

        # Когда логика worker завершится (сигнал finished), мы останавливаем QThread (слот quit)
        self.worker_logic.finished.connect(self.worker_thread.quit)

        # 6. Запускаем поток
        self.worker_thread.start()

    def run(self):
        """
        Запуск основного цикла приложения.
        """
        sys.exit(self.app.exec())


if __name__ == "__main__":
    # Запуск приложения
    app_instance = Application()
    app_instance.run()
