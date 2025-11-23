# ---------------------- Validation ----------------------

def validate_numeric(new_value):
    if new_value == "":
        return True
    if new_value == "-":
        return True
    try:
        int(new_value)
        return True
    except ValueError:
        return False


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def safe_int(value):
    if value in ("-"):
        return 0
    return int(value)