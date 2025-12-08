import cv2
import numpy as np


def apply_morphological_operation(image_data, operation_type, kernel_shape, kernel_size):
    # ... код из предыдущего ответа остается прежним ...
    if image_data is None:
        return None

    gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
    _, binary_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    shape_map = {
        'Прямоугольник': cv2.MORPH_RECT,
        'Окружность': cv2.MORPH_ELLIPSE,
        'Крест': cv2.MORPH_CROSS
    }
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
        raise ValueError("Неверный тип операции")

    return result
