import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

# Импортируем нашу логику
from logic_3d import Logic3D


class GLWidget(QGLWidget):
    def __init__(self, logic, parent=None):
        super(GLWidget, self).__init__(parent)
        self.logic = logic
        self.last_pos = None
        self.show_projections = False

        # Настройки мыши
        self.setMouseTracking(True)

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)  # Темно-серый фон
        glEnable(GL_DEPTH_TEST)
        glLineWidth(2.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Перспективная проекция
        gluPerspective(45, w / h if h > 0 else 1, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Отодвигаем камеру назад, чтобы видеть объект
        glTranslatef(0, 0, -5)

        # 1. Рисуем оси координат (Глобальные)
        self.draw_axes()

        # Получаем матрицу преобразования из логики
        model_matrix = self.logic.get_model_matrix()

        # OpenGL использует матрицы по столбцам (column-major), numpy - row-major.
        # Поэтому транспонируем перед загрузкой, если используем glMultMatrix
        # Но здесь мы будем рисовать трансформированные вершины вручную или через матрицу.
        # Для простоты реализации проекций, давайте получим уже трансформированные вершины от CPU
        # (так проще рисовать проекции).

        verts_transformed = self.logic.transform_vertices(self.logic.vertices)

        # Рисуем сам 3D объект (Белый)
        glColor3f(1.0, 1.0, 1.0)
        self.draw_wireframe(verts_transformed)

        # Лаб 6c: Рисуем проекции, если включено
        if self.show_projections:
            oxy, oxz, oyz = self.logic.get_projections()

            # Oxy (Синий оттенок) - Проекция на "пол" или заднюю стенку
            glColor3f(0.0, 0.0, 1.0)
            self.draw_wireframe(oxy)

            # Oxz (Зеленый оттенок)
            glColor3f(0.0, 1.0, 0.0)
            self.draw_wireframe(oxz)

            # Oyz (Красный оттенок)
            glColor3f(1.0, 0.0, 0.0)
            self.draw_wireframe(oyz)

    def draw_axes(self):
        glBegin(GL_LINES)
        # X - Red
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0);
        glVertex3f(10, 0, 0)
        # Y - Green
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0);
        glVertex3f(0, 10, 0)
        # Z - Blue
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0);
        glVertex3f(0, 0, 10)
        glEnd()

    def draw_wireframe(self, vertices):
        glBegin(GL_LINES)
        edges = self.logic.edges
        # edges - это плоский список [start, end, start, end...]
        for i in range(0, len(edges), 2):
            idx1 = edges[i]
            idx2 = edges[i + 1]

            v1 = vertices[idx1]
            v2 = vertices[idx2]

            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        glEnd()

    # --- Обработка событий мыши ---
    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            return

        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()

        if event.buttons() & Qt.LeftButton:
            # Вращение
            self.logic.rotate(dx, dy)
            self.update()
        elif event.buttons() & Qt.RightButton:
            # Перемещение (Паннинг)
            self.logic.pan(dx, dy)
            self.update()

        self.last_pos = event.pos()

    def wheelEvent(self, event):
        # Масштабирование
        angle = event.angleDelta().y()
        self.logic.zoom(angle)
        self.update()

    def toggle_projections(self):
        self.show_projections = not self.show_projections
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная Работа 6: 3D Буква М")
        self.resize(1000, 700)

        self.logic = Logic3D()

        # Центральный виджет и лейаут
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 3D Область (Слева)
        self.gl_widget = GLWidget(self.logic)
        main_layout.addWidget(self.gl_widget, stretch=3)

        # Панель управления (Справа)
        control_panel = QWidget()
        panel_layout = QVBoxLayout(control_panel)
        main_layout.addWidget(control_panel, stretch=1)

        # Инструкция
        lbl_info = QLabel(
            "Управление:\n"
            "LMB Drag: Вращение\n"
            "RMB Drag: Перемещение\n"
            "Wheel: Масштаб"
        )
        panel_layout.addWidget(lbl_info)

        # Кнопка матриц
        btn_matrix = QPushButton("Вывести матрицу\nпреобразования")
        btn_matrix.clicked.connect(self.print_matrix)
        panel_layout.addWidget(btn_matrix)

        # Поле вывода матрицы
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setMaximumHeight(200)
        panel_layout.addWidget(self.text_output)

        # Кнопка проекций
        btn_proj = QPushButton("Показать/Скрыть\nПроекции (Oxy, Oxz, Oyz)")
        btn_proj.clicked.connect(self.gl_widget.toggle_projections)
        panel_layout.addWidget(btn_proj)

        # Растяжка, чтобы кнопки были сверху
        panel_layout.addStretch()

    def print_matrix(self):
        m = self.logic.get_model_matrix()
        # Форматируем вывод
        s = "Model Matrix:\n"
        s += np.array2string(m, formatter={'float_kind': lambda x: "%.2f" % x}, separator='\t')
        self.text_output.setText(s)
        print(s)  # Дублируем в консоль


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())