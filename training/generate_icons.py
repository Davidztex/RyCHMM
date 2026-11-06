"""
generate_icons.py
=================
Genera iconos/miniaturas gráficas de alta definición para las 27 letras del alfabeto español.
Los iconos se utilizan en el panel de clasificación y probabilidades de la GUI.
"""

import os
import sys

# Permitir ejecutar de forma independiente o como módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QImage, QPainter, QColor, QFont, QPen, QPainterPath
from PyQt6.QtWidgets import QApplication

from engine.hmm_engine import SPANISH_ALPHABET


def generate_letter_icon(char, output_path, size=96):
    """
    Renderiza un icono elegante con tema grafito oscuro y acento cian brillante.
    """
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    rect = QRectF(2, 2, size - 4, size - 4)

    # Fondo redondeado grafito oscuro
    bg_color = QColor(24, 27, 34)
    border_color = QColor(48, 54, 61)
    painter.setBrush(bg_color)
    painter.setPen(QPen(border_color, 1.5))
    painter.drawRoundedRect(rect, 14, 14)

    # Brillo sutil de acento cian en el borde superior
    pen_glow = QPen(QColor(0, 210, 255, 60), 1.0)
    painter.setPen(pen_glow)
    painter.drawLine(10, 3, size - 10, 3)

    # Letra centrada con tipografía limpia
    font = QFont("Segoe UI", int(size * 0.44), QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor(230, 240, 255))

    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char)
    painter.end()

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    image.save(output_path, "PNG")


def generate_all_icons(icons_dir):
    """Genera los 27 iconos de referencia."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    os.makedirs(icons_dir, exist_ok=True)
    count = 0
    for ch in SPANISH_ALPHABET:
        safe_name = f"char_{ord(ch)}.png" if ord(ch) > 127 else f"{ch}.png"
        out_file = os.path.join(icons_dir, safe_name)
        generate_letter_icon(ch, out_file)
        if ch == 'ñ':
            # Guardar también como nn.png para máxima compatibilidad
            generate_letter_icon(ch, os.path.join(icons_dir, "nn.png"))
        count += 1

    print(f"Generados {count} iconos de referencia en: {icons_dir}")


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    icons_target = os.path.join(base_dir, "data", "icons")
    generate_all_icons(icons_target)
