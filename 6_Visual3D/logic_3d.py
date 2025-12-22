import numpy as np
import math


class Logic3D:
    def __init__(self):
        self.vertices = self._create_letter_m_vertices()
        self.edges = self._create_edges()

        self.scale = 1.0
        self.translation = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.rotation_matrix = np.identity(4, dtype=np.float32)

    def _create_letter_m_vertices(self):
        """
        Создает вершины для буквы М
        """
        depth = 0.2  # Половина глубины (толщина буквы)

        # Координаты передней грани (Z = +depth)
        # Описываем контур против часовой стрелки или по порядку из задания
        v_front = [
            [-0.6, -0.6, depth],  # 0: Низ лево
            [-0.6, 0.6, depth],  # 1: Верх лево
            [0.0, 0.0, depth],  # 2: Середина верх (впадина буквы М)
            [0.6, 0.6, depth],  # 3: Верх право
            [0.6, -0.6, depth],  # 4: Низ право
            [0.35, -0.6, depth],  # 5: Низ право внутр (толщина ноги)
            [0.25, -0.2, depth],  # 6: Внутр право (подъем к середине)
            [0.0, -0.4, depth],  # 7: Середина низ (пик снизу)
            [-0.25, -0.2, depth],  # 8: Внутрен лево
            [-0.35, -0.6, depth],  # 9: Нижняя лево внутр
        ]

        # Задняя грань (z = -depth) - зеркальная копия по XY, но Z инвертирован
        v_back = [[x, y, -z] for x, y, z in v_front]

        return np.array(v_front + v_back, dtype=np.float32)

    def _create_edges(self):
        """Создает список ребер (индексов вершин) для каркаса."""
        # Поскольку у нас 10 вершин на грань, логика остается той же:
        # 0-1-2-3-4-5-6-7-8-9-0
        front_loop = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 0]

        offset = 10
        back_loop = [i + offset for i in front_loop]

        connectors = []
        for i in range(10):
            connectors.extend([i, i + offset])

        return front_loop + back_loop + connectors

    def get_model_matrix(self):
        S = np.diag([self.scale, self.scale, self.scale, 1.0])
        T = np.identity(4)
        T[0, 3] = self.translation[0]
        T[1, 3] = self.translation[1]
        T[2, 3] = self.translation[2]

        M = np.dot(self.rotation_matrix, S)
        M = np.dot(T, M)
        return M

    def transform_vertices(self, vertices):
        M = self.get_model_matrix()
        ones = np.ones((vertices.shape[0], 1))
        v_homo = np.hstack([vertices, ones])
        v_trans = v_homo.dot(M.T)
        return v_trans[:, :3]

    def zoom(self, delta_y):
        factor = 1.1 if delta_y > 0 else 0.9
        self.scale *= factor

    def pan(self, dx, dy):
        sensitivity = 0.005
        self.translation[0] += dx * sensitivity
        self.translation[1] -= dy * sensitivity

    def rotate(self, dx, dy):
        sensitivity = 0.01
        angle_x = dy * sensitivity
        angle_y = dx * sensitivity

        c, s = math.cos(angle_x), math.sin(angle_x)
        Rx = np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        c, s = math.cos(angle_y), math.sin(angle_y)
        Ry = np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        R_delta = np.dot(Ry, Rx)
        self.rotation_matrix = np.dot(R_delta, self.rotation_matrix)

    def get_projections(self):
        verts = self.transform_vertices(self.vertices)
        oxy = verts.copy();
        oxy[:, 2] = -2.0
        oxz = verts.copy();
        oxz[:, 1] = -2.0
        oyz = verts.copy();
        oyz[:, 0] = -2.0
        return oxy, oxz, oyz