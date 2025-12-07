from PIL import Image, ImageFile
import os

# Убедимся, что Pillow не обрезает изображения при чтении
ImageFile.LOAD_TRUNCATED_IMAGES = True


def get_image_metadata(filepath: str) -> dict:
    """
    Извлекает метаданные изображения из указанного файла с помощью Pillow.

    Args:
        filepath: Путь к файлу изображения.

    Returns:
        Словарь с извлеченными данными или информацией об ошибке.
    """
    metadata = {
        "filename": os.path.basename(filepath),
        "size_px": "N/A",
        "dpi": "N/A",
        "depth": "N/A",
        "compression": "N/A"
    }

    try:
        with Image.open(filepath) as img:
            # --- 1. Размер изображения в пикселях ---
            metadata["size_px"] = f"{img.width}x{img.height}"

            # --- 2. Глубина цвета ---
            # Режим 'L' (8-бит), 'RGB' (24-бит), 'RGBA' (32-бит), 'P' (палитра)
            mode_to_depth = {
                '1': '1-bit (B&W)',
                'L': '8-bit (Grayscale)',
                'P': '8-bit (Palette)',
                'RGB': '24-bit',
                'RGBA': '32-bit (Alpha)',
                'CMYK': '32-bit (CMYK)',
                'I': '32-bit (Integer)',
                'F': '32-bit (Float)'
            }
            metadata["depth"] = mode_to_depth.get(img.mode, f"{img.mode} mode")

            # --- 3. Разрешение (DPI) ---
            if 'dpi' in img.info:
                # dpi возвращается как кортеж (x_dpi, y_dpi)
                dpi_x, dpi_y = img.info['dpi']
                if dpi_x == dpi_y:
                    metadata["dpi"] = f"{int(dpi_x)} DPI"
                else:
                    metadata["dpi"] = f"{int(dpi_x)}x{int(dpi_y)} DPI"

            # --- 4. Сжатие (Compression) ---
            # Эта информация часто хранится в img.info
            # Форматы TIFF, PNG, JPEG имеют разные способы хранения этой инфы.
            if 'compression' in img.info:
                metadata["compression"] = str(img.info['compression'])
            elif img.format == 'JPEG':
                # JPEG всегда использует сжатие
                metadata["compression"] = "JPEG (Lossy)"
            elif img.format == 'PNG':
                # PNG всегда использует сжатие без потерь
                metadata["compression"] = "PNG (Lossless)"
            elif img.format == 'BMP':
                # BMP обычно без сжатия, но может быть RLE
                if img.info.get('compression', 0) != 0:
                    metadata["compression"] = f"BMP ({img.info['compression']})"
                else:
                    metadata["compression"] = "None"
            elif img.format == 'GIF':
                metadata["compression"] = "LZW (Lossless)"
            elif img.format == 'PCX':
                metadata["compression"] = "RLE (Lossless)"
            else:
                metadata["compression"] = "N/A or None"


    except IOError as e:
        # Если Pillow не может открыть или распознать файл
        metadata["size_px"] = f"Ошибка чтения: {e}"
        metadata["depth"] = "Ошибка"
        metadata["compression"] = "Ошибка"

    return metadata


if __name__ == "__main__":
    # Пример использования для тестирования модуля
    # Замените 'test_image.jpg' на реальный путь к файлу для проверки
    # print(get_image_metadata('test_image.jpg'))
    print(get_image_metadata(r'D:\IDE\BSU\py\PCG\InfoReader\Для проверки Lab2\Fig5.10(a).bmp'))
