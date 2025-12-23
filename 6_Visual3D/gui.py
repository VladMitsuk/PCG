import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

from logic_3d import Logic3D


class GLWidget(QGLWidget):
    # Сигнал, который будет испускаться при любом изменении (вращение, зум, перемещение)
    matrix_changed = pyqtSignal()

    def __init__(self, logic, parent=None):
        super(GLWidget, self).__init__(parent)
        self.logic = logic
        self.last_pos = None
        self.show_projections = False
        self.setMouseTracking(True)

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glLineWidth(2.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h > 0 else 1, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0, 0, -5)

        # Поворот сцены для изометрии (чтобы видеть 3 оси)
        glRotatef(20, 1, 0, 0)
        glRotatef(-30, 0, 1, 0)

        self.draw_axes()

        verts_transformed = self.logic.transform_vertices(self.logic.vertices)

        glColor3f(1.0, 1.0, 1.0)
        self.draw_wireframe(verts_transformed)

        if self.show_projections:
            oxy, oxz, oyz = self.logic.get_projections()
            glColor3f(0.0, 0.0, 1.0);
            self.draw_wireframe(oxy)
            glColor3f(0.0, 1.0, 0.0);
            self.draw_wireframe(oxz)
            glColor3f(1.0, 0.0, 0.0);
            self.draw_wireframe(oyz)

    def draw_axes(self):
        glBegin(GL_LINES)
        glColor3f(1, 0, 0);
        glVertex3f(0, 0, 0);
        glVertex3f(10, 0, 0)
        glColor3f(0, 1, 0);
        glVertex3f(0, 0, 0);
        glVertex3f(0, 10, 0)
        glColor3f(0, 0, 1);
        glVertex3f(0, 0, 0);
        glVertex3f(0, 0, 10)
        glEnd()

    def draw_wireframe(self, vertices):
        glBegin(GL_LINES)
        edges = self.logic.edges
        for i in range(0, len(edges), 2):
            idx1 = edges[i]
            idx2 = edges[i + 1]
            v1 = vertices[idx1]
            v2 = vertices[idx2]
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        glEnd()

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            return
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()

        updated = False
        if event.buttons() & Qt.LeftButton:
            self.logic.rotate(dx, dy)
            updated = True
        elif event.buttons() & Qt.RightButton:
            self.logic.pan(dx, dy)
            updated = True

        if updated:
            self.update()
            # Отправляем сигнал об изменении матрицы
            self.matrix_changed.emit()

        self.last_pos = event.pos()

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        self.logic.zoom(angle)
        self.update()
        # Отправляем сигнал об изменении матрицы
        self.matrix_changed.emit()

    def toggle_projections(self):
        self.show_projections = not self.show_projections
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лабораторная Работа 6: 3D Буква М")
        self.resize(1000, 700)
        self.logic = Logic3D()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.gl_widget = GLWidget(self.logic)
        main_layout.addWidget(self.gl_widget, stretch=3)

        control_panel = QWidget()
        panel_layout = QVBoxLayout(control_panel)
        main_layout.addWidget(control_panel, stretch=1)

        lbl_info = QLabel(
            "Управление:\n"
            "LMB Drag: Вращение\n"
            "RMB Drag: Перемещение\n"
            "Wheel: Масштаб"
        )
        panel_layout.addWidget(lbl_info)

        # Кнопка удалена, вместо нее метка заголовка
        panel_layout.addWidget(QLabel("<b>Model Matrix:</b>"))

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setMaximumHeight(200)
        panel_layout.addWidget(self.text_output)

        btn_proj = QPushButton("Показать/Скрыть\nПроекции (Oxy, Oxz, Oyz)")
        btn_proj.clicked.connect(self.gl_widget.toggle_projections)
        panel_layout.addWidget(btn_proj)

        panel_layout.addStretch()

        # Подключаем сигнал изменения матрицы к функции обновления текста
        self.gl_widget.matrix_changed.connect(self.update_matrix_text)

        # Первичное обновление текста при запуске
        self.update_matrix_text()

    def update_matrix_text(self):
        """Обновляет текст в окне на основе текущей матрицы."""
        m = self.logic.get_model_matrix()
        s = np.array2string(m, formatter={'float_kind': lambda x: "%.2f" % x}, separator='\t')
        self.text_output.setText(s)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())