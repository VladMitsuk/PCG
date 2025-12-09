import cv2
import numpy as np


def apply_morphological_operation(image_data, operation_type, kernel_shape, kernel_size):
    # ... код морфологии остается прежним, только обновляем mapping'и под русские названия ...
    if image_data is None:
        return None

    gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
    # Для морфологии обычно используют бинарные изображения, оставляем пороговую обработку
    _, binary_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    shape_map = {
        'Прямоугольник': cv2.MORPH_RECT,
        'Окружность': cv2.MORPH_ELLIPSE,
        'Крест': cv2.MORPH_CROSS
    }
    # Используем .get() с запасным вариантом на случай, если ключ не найден
    shape = shape_map.get(kernel_shape, cv2.MORPH_RECT)

    k_size = (kernel_size, kernel_size)
    kernel = cv2.getStructuringElement(shape, k_size)

    if operation_type == 'Эрозия':
        result = cv2.erode(binary_img, kernel, iterations=1)
    elif operation_type == 'Дилатация':
        result = cv2.dilate(binary_img, kernel, iterations=1)
    elif operation_type == 'Открытие':
        result = cv2.morphologyEx(binary_img, cv2.MORPH_OPEN, kernel)
    elif operation_type == 'Закрытие':
        result = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)
    else:
        raise ValueError("Неверный тип операции морфологии")

    return result


def apply_filter(image_data, filter_type, kernel_size):
    """
    Применяет выбранный фильтр (Гаусса или Усредняющий) к изображению.
    Фильтры применяются к цветному изображению напрямую.
    """
    if image_data is None:
        return None

    # Kernel size must be positive and odd
    if kernel_size % 2 == 0 or kernel_size <= 0:
        kernel_size += 1  # Ensure it is odd and positive

    if filter_type == 'Фильтр Гаусса':
        # Сигма (стандартное отклонение) можно оставить 0, OpenCV рассчитает его сам по размеру ядра
        result = cv2.GaussianBlur(image_data, (kernel_size, kernel_size), 0)
    elif filter_type == 'Усредняющий фильтр':
        # Однородный (Blur) фильтр
        result = cv2.blur(image_data, (kernel_size, kernel_size))
    else:
        raise ValueError("Неверный тип фильтра")

    return result
