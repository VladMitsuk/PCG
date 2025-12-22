import numpy as np
import math


class Logic3D:
    def __init__(self):
        self.vertices = self._create_letter_m_vertices()
        self.edges = self._create_edges()

        # Начальные параметры преобразований
        self.scale = 1.0
        self.translation = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        # Матрица вращения (идентичная в начале)
        self.rotation_matrix = np.identity(4, dtype=np.float32)

    def _create_letter_m_vertices(self):
        """
        Создает вершины для объемной буквы М.
        Координаты центрированы относительно (0,0,0).
        """
        w = 0.5  # half width
        h = 0.5  # half height
        d = 0.2  # half depth (thickness)
        t = 0.15  # thickness of the leg

        # Определяем ключевые точки для передней грани (Z = d)
        # Координаты: x, y, z

        # Левая нога (внешняя, внутренняя)
        # Правая нога (внешняя, внутренняя)
        # Середина V

        front_face = [
            [-w, -h, d],  # 0: Левый нижний внешний
            [-w, h, d],  # 1: Левый верхний внешний
            [-w + t, h, d],  # 2: Левый верхний внутренний
            [-w + t, -h, d],  # 3: Левый нижний внутренний (не используется если сплошная, но для каркаса нужно)

            # Вершина V образного выреза
            [0, -h + 0.3, d],  # 4: Низ середины
            [0, -h + 0.5, d],
            # 5: Верх середины (впадина) - это геометрически сложнее, упростим до "палочной" M с толщиной
        ]

        # Упрощенная каркасная модель (брусковая М)
        # Передняя грань (z = +d)
        v_front = [
            [-0.6, -0.6, 0.2],  # 0: Низ Лево
            [-0.6, 0.6, 0.2],  # 1: Верх Лево
            [-0.2, 0.6, 0.2],  # 2: Верх Лево (внутр)
            [0.0, 0.0, 0.2],  # 3: Центр Низ (галочка)
            [0.2, 0.6, 0.2],  # 4: Верх Право (внутр)
            [0.6, 0.6, 0.2],  # 5: Верх Право
            [0.6, -0.6, 0.2],  # 6: Низ Право
            [0.2, -0.6, 0.2],  # 7: Низ Право (внутр нога)
            [0.0, -0.2, 0.2],  # 8: Центр (под галочкой) - для толщины
            [-0.2, -0.6, 0.2],  # 9: Низ Лево (внутр нога)
        ]

        # Задняя грань (z = -d) - копия передней, но Z = -0.2
        v_back = [[x, y, -z] for x, y, z in v_front]

        return np.array(v_front + v_back, dtype=np.float32)

    def _create_edges(self):
        """Создает список ребер (индексов вершин) для каркаса."""
        # Индексы передней грани: 0-1-2-3-4-5-6-7-8-9-0
        front_loop = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 0]
        # Смещение индексов для задней грани
        offset = 10
        back_loop = [i + offset for i in front_loop]

        # Соединяющие ребра (между передней и задней гранью)
        connectors = []
        for i in range(10):
            connectors.extend([i, i + offset])

        return front_loop + back_loop + connectors

    def get_model_matrix(self):
        """
        Собирает итоговую матрицу преобразования (Model Matrix).
        Порядок: Scale -> Rotate -> Translate
        """
        # 1. Матрица масштабирования
        S = np.diag([self.scale, self.scale, self.scale, 1.0])

        # 2. Матрица перемещения
        T = np.identity(4)
        T[0, 3] = self.translation[0]
        T[1, 3] = self.translation[1]
        T[2, 3] = self.translation[2]

        # 3. Итоговая: T * R * S
        # Сначала масштабируем, потом крутим, потом двигаем
        M = np.dot(self.rotation_matrix, S)  # R * S
        M = np.dot(T, M)  # T * (R * S)
        return M

    def transform_vertices(self, vertices):
        """Применяет текущую матрицу к вершинам (для CPU расчетов, если нужно)."""
        M = self.get_model_matrix()
        # Добавляем 4-ю компоненту w=1
        ones = np.ones((vertices.shape[0], 1))
        v_homo = np.hstack([vertices, ones])

        # Умножаем (v * M^T) или (M * v)
        # Обычно v_transformed = M @ v. Здесь массив строк, поэтому v @ M.T
        v_trans = v_homo.dot(M.T)

        return v_trans[:, :3]  # Возвращаем x, y, z

    # --- Управление ---

    def zoom(self, delta_y):
        """Масштабирование колесиком."""
        factor = 1.1 if delta_y > 0 else 0.9
        self.scale *= factor

    def pan(self, dx, dy):
        """Перемещение (Drag правой кнопкой)."""
        # Коэффициент чувствительности зависит от масштаба (чтобы удобно двигать)
        sensitivity = 0.005
        self.translation[0] += dx * sensitivity
        self.translation[1] -= dy * sensitivity  # Y в экранах обычно инвертирован

    def rotate(self, dx, dy):
        """
        Вращение (Drag левой кнопкой).
        Реализуем вращение вокруг осей камеры (X и Y).
        Матрица вращения накапливается.
        """
        sensitivity = 0.01
        angle_x = dy * sensitivity
        angle_y = dx * sensitivity

        # Вращение вокруг оси X (локальной/экранной)
        c, s = math.cos(angle_x), math.sin(angle_x)
        Rx = np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        # Вращение вокруг оси Y (локальной/экранной)
        c, s = math.cos(angle_y), math.sin(angle_y)
        Ry = np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        # Обновляем глобальную матрицу вращения
        # R_new = Ry * Rx * R_old (порядок важен для интуитивного вращения)
        R_delta = np.dot(Ry, Rx)
        self.rotation_matrix = np.dot(R_delta, self.rotation_matrix)

    def get_projections(self):
        """Возвращает проекции текущих (трансформированных) вершин."""
        verts = self.transform_vertices(self.vertices)

        # Oxy (z=0)
        oxy = verts.copy()
        oxy[:, 2] = -2.0  # Сдвигаем плоскость назад для визуализации

        # Oxz (y=0)
        oxz = verts.copy()
        oxz[:, 1] = -2.0

        # Oyz (x=0)
        oyz = verts.copy()
        oyz[:, 0] = -2.0

        return oxy, oxz, oyz