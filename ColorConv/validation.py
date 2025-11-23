def validate_numeric_input(P): # Функция проверки на числовое значение
    if P.isdigit() or P == "":
        return True
    else:
        return False


def limit_range_RGB(int_var, *args): # Проверка на область 0-255
    try:
        current_value = int_var.get()
        MIN_VAL = 0
        MAX_VAL = 255

        if current_value > MAX_VAL:
            int_var.set(MAX_VAL)  # Устанавливаем максимум, если превышен
            status_var.set(f"Значение ограничено {MAX_VAL}")
        elif current_value < MIN_VAL:
            int_var.set(MIN_VAL)  # Устанавливаем минимум, если ниже
            status_var.set(f"Значение ограничено {MIN_VAL}")
        else:
            status_var.set(f"Текущее значение: {current_value}")

    except tk.TclError:
        # Эта ошибка возникнет, если пользователь попытается ввести
        # нецифровой символ, но наша валидация ниже не даст этому случиться
        # или если поле полностью пустое.
        status_var.set("Ожидание ввода числа...")

def limit_range_CMYK(*args):
    pass
def limit_range_Lab(*args):
    pass