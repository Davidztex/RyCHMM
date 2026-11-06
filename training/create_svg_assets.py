"""
create_svg_assets.py
====================
Guarda los SVGs oficiales solicitados por el usuario y los renderiza con QSvgRenderer
a QIcon / PNG para garantizar máxima nitidez y compatibilidad.
"""

import os
import sys
from PyQt6.QtCore import Qt, QByteArray, QRectF
from PyQt6.QtGui import QImage, QPainter, QColor, QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "data", "icons", "ui")
os.makedirs(UI_DIR, exist_ok=True)

# 1. SVG Reiniciar Captura (Return)
# Usamos stroke cian/blanco #00d2ff para que destaque nítido sobre el tema oscuro
SVG_RETURN = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
  <title>return</title>
  <g fill="none" stroke="#00d2ff" stroke-linecap="round" stroke-linejoin="round" stroke-width="4">
    <path d="M12.9998 8L6 14L12.9998 21"/>
    <path d="M6 14H28.9938C35.8768 14 41.7221 19.6204 41.9904 26.5C42.2739 33.7696 36.2671 40 28.9938 40H11.9984"/>
  </g>
</svg>"""

# 2. SVG Limpiar Lienzo (Clear-Format)
# Usamos stroke rojo suave coral #f85149 para representar acción de borrado
SVG_CLEAR = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
  <title>clear-format</title>
  <g fill="none" stroke="#f85149">
    <path stroke-linejoin="round" stroke-width="4.302" d="M44.782 24.17L31.918 7.1L14.135 20.5L27.5 37l3.356-2.336z"/>
    <path stroke-linejoin="round" stroke-width="4.302" d="m27.5 37l-3.839 3.075l-10.563-.001l-2.6-3.45l-6.433-8.536L14.5 20.225"/>
    <path stroke-linecap="round" stroke-width="4.5" d="M13.206 40.072h31.36"/>
  </g>
</svg>"""

# 3. SVG Centrar Cámara (Center-Focus-Weak-Outline)
# Usamos fill cian #00d2ff / azul #58a6ff
SVG_CENTER = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24">
  <title>center-focus-weak-outline</title>
  <path fill="#58a6ff" d="M9.175 14.825Q8 13.65 8 12t1.175-2.825T12 8t2.825 1.175T16 12t-1.175 2.825T12 16t-2.825-1.175m4.238-1.412Q14 12.825 14 12t-.587-1.412T12 10t-1.412.588T10 12t.588 1.413T12 14t1.413-.587M5 21q-.825 0-1.412-.587T3 19v-4h2v4h4v2zm10 0v-2h4v-4h2v4q0 .825-.587 1.413T19 21zM3 9V5q0-.825.588-1.412T5 3h4v2H5v4zm16 0V5h-4V3h4q.825 0 1.413.588T21 5v4z"/>
</svg>"""

# 4. SVG Casita (Home)
SVG_HOME = """<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24">
  <title>home</title>
  <path fill="#f0f6fc" d="M10 20v-6h4v6h5v-8h3L12 3L2 12h3v8z"/>
</svg>"""


def render_svg_to_png(svg_str, out_path, size=64):
    renderer = QSvgRenderer(QByteArray(svg_str.encode("utf-8")))
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(4, 4, size - 8, size - 8))
    painter.end()
    img.save(out_path, "PNG")


def main():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    svgs = {
        "return.svg": (SVG_RETURN, "return.png"),
        "clear.svg": (SVG_CLEAR, "clear.png"),
        "center_focus.svg": (SVG_CENTER, "center_focus.png"),
        "home.svg": (SVG_HOME, "home.png")
    }

    for svg_filename, (svg_content, png_filename) in svgs.items():
        svg_path = os.path.join(UI_DIR, svg_filename)
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        png_path = os.path.join(UI_DIR, png_filename)
        render_svg_to_png(svg_content, png_path, size=64)
        print(f"[OK] Guardado {svg_filename} y renderizado {png_filename}")


if __name__ == "__main__":
    main()
