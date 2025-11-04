def rgb_to_xyz(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    r = ((r + 0.055) / 1.055) ** 2.4 if r > 0.04045 else (r / 12.92)
    g = ((g + 0.055) / 1.055) ** 2.4 if g > 0.04045 else (g / 12.92)
    b = ((b + 0.055) / 1.055) ** 2.4 if b > 0.04045 else (b / 12.92)
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505
    return x, y, z

def xyz_to_rgb(x, y, z):
    r = x * 3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y * -0.2040 + z * 1.0570
    r = 1.055 * r ** (1 / 2.4) - 0.055 if r > 0.0031308 else 12.92 * r
    g = 1.055 * g ** (1 / 2.4) - 0.055 if g > 0.0031308 else 12.92 * g
    b = 1.055 * b ** (1 / 2.4) - 0.055 if b > 0.0031308 else 12.92 * b
    r, g, b = max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b))
    return int(r * 255), int(g * 255), int(b * 255)

Xn, Yn, Zn = 0.95047, 1.0, 1.08883

def xyz_to_lab_helper(t):
    return t ** (1 / 3) if t > 0.008856 else (7.787 * t) + (16 / 116)

def lab_to_xyz_helper(t):
    return t ** 3 if t > 0.206893 else (t - 16 / 116) / 7.787

def rgb_to_lab(r, g, b):
    x, y, z = rgb_to_xyz(r, g, b)
    xr, yr, zr = x / Xn, y / Yn, z / Zn
    fx = xyz_to_lab_helper(xr)
    fy = xyz_to_lab_helper(yr)
    fz = xyz_to_lab_helper(zr)
    L = (116 * fy) - 16
    a = 500 * (fx - fy)
    b_val = 200 * (fy - fz)
    return L, a, b_val

def lab_to_rgb(L, a, b_val):
    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b_val / 200
    xr = lab_to_xyz_helper(fx)
    yr = lab_to_xyz_helper(fy)
    zr = lab_to_xyz_helper(fz)
    x, y, z = xr * Xn, yr * Yn, zr * Zn
    r, g, b = xyz_to_rgb(x, y, z)
    return r, g, b

def rgb_to_cmyk(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    if (r == 0) and (g == 0) and (b == 0):
        return 0, 0, 0, 100

    k = 1 - max(r, g, b)

    if k == 1:
        return 0, 0, 0, 100

    c = (1 - r - k) / (1 - k)
    m = (1 - g - k) / (1 - k)
    y = (1 - b - k) / (1 - k)

    return c * 100, m * 100, y * 100, k * 100


def cmyk_to_rgb(c, m, y, k):
    c, m, y, k = c / 100.0, m / 100.0, y / 100.0, k / 100.0

    r = 1.0 - min(1.0, c * (1.0 - k) + k)
    g = 1.0 - min(1.0, m * (1.0 - k) + k)
    b = 1.0 - min(1.0, y * (1.0 - k) + k)

    return int(r * 255), int(g * 255), int(b * 255)


def lab_to_cmyk(L, a, b_val):
    r, g, b = lab_to_rgb(L, a, b_val)
    c, m, y, k = rgb_to_cmyk(r, g, b)
    return c, m, y, k


def cmyk_to_lab(c, m, y, k):
    r, g, b = cmyk_to_rgb(c, m, y, k)
    L, a, b_val = rgb_to_lab(r, g, b)
    return L, a, b_val
