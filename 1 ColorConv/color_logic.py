from validation import *

# -------------------- RGB <-> CMYK --------------------------

def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100

    r_p = r / 255
    g_p = g / 255
    b_p = b / 255

    k = 1 - max(r_p, g_p, b_p)
    c = (1 - r_p - k) / (1 - k)
    m = (1 - g_p - k) / (1 - k)
    y = (1 - b_p - k) / (1 - k)

    return round(c * 100), round(m * 100), round(y * 100), round(k * 100)


def cmyk_to_rgb(c, m, y, k):
    c /= 100
    m /= 100
    y /= 100
    k /= 100

    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)

    return round(r), round(g), round(b)


# -------------------- RGB <-> Lab ---------------------------

# sRGB to XYZ
def rgb_to_xyz(r, g, b):
    # Normalize
    r, g, b = [v / 255 for v in (r, g, b)]

    # Gamma correction
    def inv_gamma(c):
        return pow((c + 0.055) / 1.055, 2.4) if c > 0.04045 else c / 12.92

    r, g, b = inv_gamma(r), inv_gamma(g), inv_gamma(b)

    # Matrix for D65
    x = r * 0.4124 + g * 0.3576 + b * 0.1805
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = r * 0.0193 + g * 0.1192 + b * 0.9505

    return x, y, z


# XYZ to Lab
def xyz_to_lab(x, y, z):
    # Reference white D65
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883

    def f(t):
        return pow(t, 1/3) if t > 0.008856 else (7.787 * t + 16/116)

    fx = f(x / Xn)
    fy = f(y / Yn)
    fz = f(z / Zn)

    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)

    return round(L), round(a), round(b)


# Lab to XYZ
def lab_to_xyz(L, a, b):
    fy = (L + 16) / 116
    fx = fy + a / 500
    fz = fy - b / 200

    def f_inv(t):
        return t**3 if t**3 > 0.008856 else (t - 16/116) / 7.787

    x = f_inv(fx)
    y = f_inv(fy)
    z = f_inv(fz)

    # Reference white D65
    Xn, Yn, Zn = 0.95047, 1.00000, 1.08883

    return x * Xn, y * Yn, z * Zn


# XYZ to RGB
def xyz_to_rgb(x, y, z):
    r = x * 3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y * -0.2040 + z * 1.0570

    def gamma(c):
        return 1.055 * pow(c, 1/2.4) - 0.055 if c > 0.0031308 else 12.92 * c

    r, g, b = gamma(r), gamma(g), gamma(b)
    r = clamp(round(r * 255), 0, 255)
    g = clamp(round(g * 255), 0, 255)
    b = clamp(round(b * 255), 0, 255)
    return r, g, b


def rgb_to_lab(r, g, b):
    return xyz_to_lab(*rgb_to_xyz(r, g, b))


def lab_to_rgb(L, a, b):
    return xyz_to_rgb(*lab_to_xyz(L, a, b))