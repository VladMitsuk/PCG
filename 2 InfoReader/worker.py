import os
import glob
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from image_utils import get_image_metadata


class Worker(QObject):
    """
    Класс-исполнитель (Worker), который выполняет тяжелую работу в фоновом потоке.
    Наследуется от QObject, чтобы иметь возможность использовать сигналы/слоты.
    """
    # Сигнал, который отправляет словарь с данными одного обработанного файла
    data_ready = pyqtSignal(dict)
    # Сигнал о завершении работы, отправляет общее количество обработанных файлов
    finished = pyqtSignal(int)
    # Сигнал для обновления статус-бара в реальном времени
    progress_update = pyqtSignal(str)
    # Сигнал для сообщения об ошибках в основной поток
    error = pyqtSignal(str)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self._is_running = True

    def run_processing(self):
        """
        Основной метод, который запускается в новом потоке.
        Сканирует папку и обрабатывает файлы.
        """
        if not self.folder_path or not os.path.isdir(self.folder_path):
            self.error.emit(f"Некорректный путь к папке: {self.folder_path}")
            self.finished.emit(0)
            return

        supported_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.tif', '*.tiff', '*.bmp', '*.pcx']
        count = 0

        self.progress_update.emit(f"Начато сканирование папки: {self.folder_path}")

        # Ищем файлы, поддерживаемые нашими форматами
        for ext in supported_extensions:
            # glob.glob находит все файлы, соответствующие маске
            # Используем os.path.join для создания абсолютного пути
            for filepath in glob.glob(os.path.join(self.folder_path, ext), recursive=False):
                if not self._is_running:
                    self.progress_update.emit(f"Обработка прервана пользователем после {count} файлов.")
                    self.finished.emit(count)
                    return

                # Получаем метаданные, используя нашу функцию из image_utils.py
                metadata = get_image_metadata(filepath)

                # Отправляем данные обратно в основной поток через сигнал
                self.data_ready.emit(metadata)

                count += 1
                if count % 100 == 0:
                    # Периодически обновляем статус (например, каждые 100 файлов)
                    self.progress_update.emit(f"Обработано файлов: {count}...")

        self.progress_update.emit(f"Обработка завершена. Всего файлов: {count}")
        # Отправляем сигнал о полном завершении работы
        self.finished.emit(count)

    def stop(self):
        """Метод для безопасной остановки потока, если это потребуется."""
        self._is_running = False
