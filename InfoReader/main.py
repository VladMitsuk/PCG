import sys
from PyQt6.QtWidgets import QApplication
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
        # Если поток уже запущен, останавливаем его перед новым запуском (опционально)
        if self.worker_thread is not None and self.worker_thread.isRunning():
            # В реальном приложении нужно добавить логику остановки (self.worker_logic.stop())
            return

            # 1. Создаем новый QThread
        self.worker_thread = QThread()

        # 2. Создаем объект логики Worker и передаем ему путь к папке
        self.worker_logic = Worker(folder_path)

        # 3. Перемещаем объект Worker в созданный поток
        self.worker_logic.moveToThread(self.worker_thread)

        # 4. Соединяем сигналы Worker'а со слотами в MainWindow (GUI)
        # Когда Worker сообщает, что данные готовы, MainWindow добавляет строку в таблицу
        self.worker_logic.data_ready.connect(self.main_window.add_file_row)

        # Когда Worker закончил всю работу, вызываем метод завершения в MainWindow
        self.worker_logic.finished.connect(self.main_window.processing_finished)

        # Соединяем сигнал обновления статуса с статус-баром MainWindow
        self.worker_logic.progress_update.connect(self.main_window.status_update_signal.emit)

        # Соединяем сигнал ошибки с отображением ошибки в MainWindow
        self.worker_logic.error.connect(self.main_window.display_error)

        # 5. Соединяем сигнал запуска потока с методом, который выполняет работу
        # Когда поток стартует, он вызывает run_processing
        self.worker_thread.started.connect(self.worker_logic.run_processing)

        # Также полезно удалить объекты после завершения потока
        self.worker_logic.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_logic.deleteLater()

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
