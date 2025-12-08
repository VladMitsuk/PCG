import cv2
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QSizePolicy,
                             QComboBox, QSpinBox, QGroupBox, QMenu, QMessageBox, QLineEdit)
from PyQt6.QtGui import QImage, QPixmap, QAction
from PyQt6.QtCore import Qt

from image_processor import apply_morphological_operation


class ImageProcessorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processing Workbench (PyQt6)")
        self.setGeometry(100, 100, 1200, 600)

        self.original_image_data = None
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # --- Левая панель: Оригинал ---
        left_panel = QVBoxLayout()
        self.lbl_original = QLabel("Оригинал")
        self.setup_label(self.lbl_original)
        left_panel.addWidget(self.lbl_original)

        btn_load = QPushButton("Загрузить изображение")
        btn_load.clicked.connect(self.load_image)
        left_panel.addWidget(btn_load)

        main_layout.addLayout(left_panel, 1)

        # --- Центральная панель: Элементы управления (постоянно видимые) ---
        control_panel = QVBoxLayout()

        # 1. Общий выбор метода (для будущих расширений)
        control_panel.addWidget(QLabel("Выбор метода:"))
        self.combo_method_selector = QComboBox()
        self.combo_method_selector.addItem("Морфологическая обработка")
        # self.combo_method_selector.addItem("Фильтрация") # Задел на будущее
        control_panel.addWidget(self.combo_method_selector)

        # 2. Группа настроек морфологии (видима по умолчанию)
        morph_group = QGroupBox("Параметры морфологии")
        morph_layout = QVBoxLayout()

        morph_layout.addWidget(QLabel("Операция:"))
        self.combo_operation = QComboBox()
        self.combo_operation.addItems(['Эрозия', 'Дилатация', 'Открытие', 'Закрытие'])
        morph_layout.addWidget(self.combo_operation)

        morph_layout.addWidget(QLabel("Форма ядра:"))
        self.combo_shape = QComboBox()
        self.combo_shape.addItems(['Прямоугольник', 'Окружность', 'Крест'])
        morph_layout.addWidget(self.combo_shape)

        morph_layout.addWidget(QLabel("Размер ядра:"))
        self.spinbox_size = QSpinBox()
        self.spinbox_size.setRange(1, 21)
        self.spinbox_size.setSingleStep(2)
        self.spinbox_size.setValue(3)
        self.spinbox_size.findChild(QLineEdit)

        morph_layout.addWidget(self.spinbox_size)

        morph_group.setLayout(morph_layout)
        control_panel.addWidget(morph_group)

        btn_apply = QPushButton("Применить обработку")
        btn_apply.clicked.connect(self.apply_current_method)
        control_panel.addWidget(btn_apply)

        control_panel.addStretch(1)  # Заполнитель пустого пространства
        main_layout.addLayout(control_panel, 0)

        # --- Правая панель: Результат ---
        right_panel = QVBoxLayout()
        self.lbl_result = QLabel("Результат")
        self.setup_label(self.lbl_result)
        right_panel.addWidget(self.lbl_result)
        main_layout.addLayout(right_panel, 1)

    def setup_label(self, label):
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        label.setStyleSheet("border: 1px solid black;")

    def load_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Открыть изображение', './', "Image files (*.jpg *.png *.bmp)")
        if fname:
            self.original_image_data = cv2.imread(fname)
            self.display_image(self.original_image_data, self.lbl_original)
            self.lbl_result.clear()

    def display_image(self, img_data, label):
        if img_data is None: return

        if len(img_data.shape) == 3:  # Цветное BGR
            img_rgb = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)
            h, w, ch = img_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        else:  # Монохромное/Gray
            h, w = img_data.shape
            bytes_per_line = w
            q_img = QImage(img_data.data, w, h, bytes_per_line, QImage.Format.Format_Grayscale8)

        pixmap = QPixmap.fromImage(q_img)
        label_width = label.width()
        label_height = label.height()
        pixmap = pixmap.scaled(label_width, label_height, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pixmap)

    def apply_current_method(self):
        """Определяет, какой метод выбран в общем комбобоксе, и вызывает его обработчик."""
        if self.original_image_data is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите изображение.")
            return

        selected_method = self.combo_method_selector.currentText()

        if selected_method == "Морфологическая обработка":
            self.apply_morphology_processing()
        # Добавьте сюда другие методы через elif
        # elif selected_method == "Фильтрация":
        #     self.apply_filtering_processing()

    def apply_morphology_processing(self):
        """Вызывает логику обработки и отображает результат, считывая данные с UI."""

        # Считываем параметры прямо из виджетов GUI
        operation = self.combo_operation.currentText()
        shape = self.combo_shape.currentText()
        size = self.spinbox_size.value()

        try:
            result_image_data = apply_morphological_operation(
                self.original_image_data,
                operation,
                shape,
                size
            )

            if result_image_data is not None:
                self.display_image(result_image_data, self.lbl_result)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка обработки", f"Произошла ошибка: {e}")

