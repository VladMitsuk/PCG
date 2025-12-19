
# Сазерленд-Коэн
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


def get_code(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code


def cohen_sutherland(p1, p2, rect):
    xmin, ymin, xmax, ymax = rect
    x1, y1 = p1;
    x2, y2 = p2
    code1 = get_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = get_code(x2, y2, xmin, ymin, xmax, ymax)
    while True:
        if code1 == 0 and code2 == 0: return (x1, y1), (x2, y2)
        if (code1 & code2) != 0: return None
        code_out = code1 if code1 != 0 else code2
        if code_out & TOP:
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1);
            y = ymax
        elif code_out & BOTTOM:
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1);
            y = ymin
        elif code_out & RIGHT:
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1);
            x = xmax
        else:
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1);
            x = xmin
        if code_out == code1:
            x1, y1 = x, y;
            code1 = get_code(x1, y1, xmin, ymin, xmax, ymax)
        else:
            x2, y2 = x, y;
            code2 = get_code(x2, y2, xmin, ymin, xmax, ymax)


# Сайрус-Бек (Устойчивая версия)
def cyrus_beck(p1, p2, polygon):
    n = len(polygon)
    if n < 3: return None

    d = (p2[0] - p1[0], p2[1] - p1[1])
    if d == (0, 0): return None  # Отрезок-точка

    # Находим центр многоугольника для определения внутренней стороны
    cx = sum(p[0] for p in polygon) / n
    cy = sum(p[1] for p in polygon) / n

    t_enter, t_leave = 0.0, 1.0

    for i in range(n):
        v1 = polygon[i]
        v2 = polygon[(i + 1) % n]

        # Вектор ребра
        edge = (v2[0] - v1[0], v2[1] - v1[1])
        # Потенциальная нормаль (перпендикуляр)
        normal = (-edge[1], edge[0])

        # Проверяем, чтобы нормаль смотрела ВНУТРЬ
        # Вектор от точки на ребре к центру
        to_center = (cx - v1[0], cy - v1[1])
        if (normal[0] * to_center[0] + normal[1] * to_center[1]) < 0:
            normal = (-normal[0], -normal[1])

        w = (p1[0] - v1[0], p1[1] - v1[1])
        dot_d = normal[0] * d[0] + normal[1] * d[1]
        dot_w = normal[0] * w[0] + normal[1] * w[1]

        if dot_d == 0:  # Отрезок параллелен ребру
            if dot_w < 0: return None  # Снаружи
        else:
            t = -dot_w / dot_d
            if dot_d > 0:  # Входящий (t_enter)
                t_enter = max(t_enter, t)
            else:  # Выходящий (t_leave)
                t_leave = min(t_leave, t)

    if t_enter <= t_leave:
        return (p1[0] + t_enter * d[0], p1[1] + t_enter * d[1]), \
            (p1[0] + t_leave * d[0], p1[1] + t_leave * d[1])
    return None