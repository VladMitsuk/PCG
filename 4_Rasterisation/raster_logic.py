import math


class RasterAlgorithms:
    @staticmethod
    def step_by_step(x1, y1, x2, y2):
        """
        Пошаговый алгоритм (основан на уравнении прямой y = kx + b).
        """
        points = []
        logs = []

        if x1 == x2 and y1 == y2:
            return [(x1, y1)], [{"step": 0, "x": x1, "y": y1, "calc": "Start"}]

        dx = x2 - x1
        dy = y2 - y1

        # Если линия вертикальная
        if dx == 0:
            step_y = 1 if y2 > y1 else -1
            for y in range(y1, y2 + step_y, step_y):
                points.append((x1, y))
                logs.append({"step": y - y1, "x": x1, "y": y, "calc": "x = const"})
            return points, logs

        # Обычный случай
        k = dy / dx
        b = y1 - k * x1

        step = 1 if x2 > x1 else -1
        # Проходим по X, вычисляем Y
        # Примечание: Для крутых линий (>45 град) этот метод плох (будут разрывы),
        # но для лабораторной реализуем его в классическом виде "по иксу".

        steps_count = abs(x2 - x1)
        for i in range(steps_count + 1):
            x = x1 + i * step
            y_float = k * x + b
            y = round(y_float)
            points.append((x, y))
            logs.append({
                "step": i,
                "x": x,
                "y": y,
                "calc": f"y = {k:.2f}*{x} + {b:.2f} = {y_float:.2f}"
            })

        return points, logs

    @staticmethod
    def dda(x1, y1, x2, y2):
        """Алгоритм ЦДА (DDA)"""
        points = []
        logs = []

        dx = x2 - x1
        dy = y2 - y1

        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return [(x1, y1)], []

        x_inc = dx / steps
        y_inc = dy / steps

        x = x1
        y = y1

        for i in range(steps + 1):
            points.append((round(x), round(y)))
            logs.append({
                "step": i,
                "x": round(x),
                "y": round(y),
                "calc": f"rx={x:.2f}, ry={y:.2f}"
            })
            x += x_inc
            y += y_inc

        return points, logs

    @staticmethod
    def bresenham_line(x1, y1, x2, y2):
        """Алгоритм Брезенхема для отрезка (только целые числа)"""
        points = []
        logs = []

        x, y = x1, y1
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        err = dx - dy

        while True:
            points.append((x, y))
            logs.append({
                "step": len(points),
                "x": x, "y": y,
                "calc": f"Err={err}"
            })

            if x == x2 and y == y2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return points, logs

    @staticmethod
    def bresenham_circle(xc, yc, r):
        """Алгоритм Брезенхема для окружности"""
        points = []
        logs = []

        x = 0
        y = r
        d = 3 - 2 * r

        def add_octants(cx, cy, x, y):
            pts = [
                (cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y), (cx - x, cy - y),
                (cx + y, cy + x), (cx - y, cy + x), (cx + y, cy - x), (cx - y, cy - x)
            ]
            return pts

        while y >= x:
            octant_points = add_octants(xc, yc, x, y)
            for p in octant_points:
                points.append(p)

            logs.append({
                "step": x,
                "x": x, "y": y,
                "calc": f"d={d}"
            })

            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6

        return points, logs