"""
generate_ui_assets.py
=====================
Genera los iconos vectoriales y las imágenes descriptivas requeridas para la GUI:
- preview_2d.png: Imagen descriptiva del trazo en plano cartesiano.
- preview_3d.png: Imagen descriptiva de la esfera 3D con trazo y geodésica.
- home.png: Icono de casita para volver al inicio.
- reload.png: Icono de flecha circular de reinicio / refresco.
- eraser.png: Icono de borrador para limpiar lienzo.
"""

import os
import sys
import math

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QImage, QPainter, QColor, QPen, QBrush, QPainterPath,
    QFont, QRadialGradient, QLinearGradient
)
from PyQt6.QtWidgets import QApplication

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_ICONS_DIR = os.path.join(BASE_DIR, "data", "icons", "ui")
os.makedirs(UI_ICONS_DIR, exist_ok=True)


def create_home_icon(path, size=64):
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Dibujar casita estilizada
    pen = QPen(QColor(230, 240, 255), size * 0.08)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(QColor(30, 41, 59, 200))

    # Techo triangular
    p_roof = QPainterPath()
    p_roof.moveTo(size * 0.5, size * 0.18)
    p_roof.lineTo(size * 0.15, size * 0.48)
    p_roof.lineTo(size * 0.25, size * 0.48)
    p_roof.lineTo(size * 0.25, size * 0.82)
    p_roof.lineTo(size * 0.75, size * 0.82)
    p_roof.lineTo(size * 0.75, size * 0.48)
    p_roof.lineTo(size * 0.85, size * 0.48)
    p_roof.closeSubpath()
    painter.drawPath(p_roof)

    # Puerta
    p_door = QPainterPath()
    p_door.moveTo(size * 0.40, size * 0.82)
    p_door.lineTo(size * 0.40, size * 0.58)
    p_door.lineTo(size * 0.60, size * 0.58)
    p_door.lineTo(size * 0.60, size * 0.82)
    painter.setBrush(QColor(0, 210, 255, 220))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPath(p_door)

    # Chimenea
    chimney = QPainterPath()
    chimney.moveTo(size * 0.68, size * 0.32)
    chimney.lineTo(size * 0.68, size * 0.22)
    chimney.lineTo(size * 0.78, size * 0.22)
    chimney.lineTo(size * 0.78, size * 0.42)
    painter.setPen(QPen(QColor(230, 240, 255), size * 0.06, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(chimney)

    painter.end()
    img.save(path, "PNG")


def create_reload_icon(path, size=64):
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(0, 210, 255), size * 0.10)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    # Arco circular de 300 grados
    rect = QRectF(size * 0.18, size * 0.18, size * 0.64, size * 0.64)
    painter.drawArc(rect, 40 * 16, 280 * 16)

    # Cabeza de flecha en el extremo del arco (apuntando en sentido circular)
    arrow = QPainterPath()
    arrow.moveTo(size * 0.78, size * 0.35)
    arrow.lineTo(size * 0.88, size * 0.20)
    arrow.lineTo(size * 0.68, size * 0.18)
    arrow.closeSubpath()

    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(0, 229, 255))
    painter.drawPath(arrow)

    painter.end()
    img.save(path, "PNG")


def create_eraser_icon(path, size=64):
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.translate(size * 0.5, size * 0.5)
    painter.rotate(-35)

    w = size * 0.55
    h = size * 0.30

    # Cuerpo del borrador
    # Parte superior (goma rosa/azul)
    r_top = QRectF(-w / 2, -h / 2, w * 0.55, h)
    painter.setBrush(QColor(244, 63, 94))  # Rosa intenso
    painter.setPen(QPen(QColor(225, 29, 72), 2))
    painter.drawRoundedRect(r_top, 4, 4)

    # Parte inferior (goma blanca/azul)
    r_bot = QRectF(-w / 2 + w * 0.50, -h / 2, w * 0.50, h)
    painter.setBrush(QColor(241, 245, 249))  # Blanco
    painter.setPen(QPen(QColor(203, 213, 225), 2))
    painter.drawRoundedRect(r_bot, 4, 4)

    # Banda metálica/central divisoria
    r_band = QRectF(-w / 2 + w * 0.45, -h / 2, w * 0.15, h)
    painter.setBrush(QColor(71, 85, 105))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(r_band)

    painter.end()
    img.save(path, "PNG")


def create_2d_preview_image(path, width=440, height=220):
    img = QImage(width, height, QImage.Format.Format_ARGB32)
    img.fill(QColor(13, 17, 23))
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Grilla cartesiana con paso simétrico
    pen_grid = QPen(QColor(30, 36, 46, 180), 1.0)
    painter.setPen(pen_grid)
    for x in range(20, width, 25):
        painter.drawLine(x, 0, x, height)
    for y in range(20, height, 25):
        painter.drawLine(0, y, width, y)

    # Ejes principales X e Y exactamente centrados
    cx, cy = width // 2, height // 2
    pen_axis = QPen(QColor(56, 139, 253, 220), 1.5)
    painter.setPen(pen_axis)
    painter.drawLine(cx, 15, cx, height - 15)  # Eje Y
    painter.drawLine(15, cy, width - 15, cy)  # Eje X

    # Flechas de ejes
    painter.setBrush(QColor(56, 139, 253))
    p_arrow_y = QPainterPath()
    p_arrow_y.moveTo(cx, 10)
    p_arrow_y.lineTo(cx - 5, 20)
    p_arrow_y.lineTo(cx + 5, 20)
    painter.drawPath(p_arrow_y)

    p_arrow_x = QPainterPath()
    p_arrow_x.moveTo(width - 10, cy)
    p_arrow_x.lineTo(width - 20, cy - 5)
    p_arrow_x.lineTo(width - 20, cy + 5)
    painter.drawPath(p_arrow_x)

    # Etiquetas de ejes
    painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    painter.setPen(QColor(88, 166, 255))
    painter.drawText(cx + 8, 25, "+Y")
    painter.drawText(width - 32, cy - 8, "+X")
    painter.drawText(cx - 30, cy + 18, "(0,0)")

    # Trazo activo en plano centrado
    t = [
        (cx - 50, cy - 20), (cx - 70, cy), (cx - 75, cy + 30),
        (cx - 55, cy + 55), (cx - 25, cy + 60), (cx + 5, cy + 45),
        (cx + 15, cy + 15), (cx + 10, cy - 10), (cx - 10, cy - 25),
        (cx - 35, cy - 25)
    ]
    path_stroke = QPainterPath()
    path_stroke.moveTo(*t[0])
    for pt in t[1:]:
        path_stroke.lineTo(*pt)

    # Resplandor cian
    pen_glow = QPen(QColor(0, 210, 255, 60), 8.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_glow)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(path_stroke)

    # Núcleo cian
    pen_core = QPen(QColor(0, 229, 255), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_core)
    painter.drawPath(path_stroke)

    # Proyección futura punteada en oro/ámbar
    p_proj = [
        (cx - 35, cy - 25), (cx - 50, cy - 20), (cx + 15, cy - 10),
        (cx + 20, cy + 20), (cx + 22, cy + 55), (cx + 35, cy + 60)
    ]
    path_proj = QPainterPath()
    path_proj.moveTo(*p_proj[0])
    for pt in p_proj[1:]:
        path_proj.lineTo(*pt)

    pen_proj = QPen(QColor(255, 183, 3, 230), 2.8, Qt.PenStyle.DashLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    pen_proj.setDashPattern([3, 4])
    painter.setPen(pen_proj)
    painter.drawPath(path_proj)

    # Marcadores de hitos en la proyección
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(255, 183, 3))
    for pt in p_proj[1:]:
        painter.drawEllipse(QPointF(pt[0], pt[1]), 2.5, 2.5)

    # Insignia flotante [Plano Cartesiano 2D]
    badge_rect = QRectF(width - 150, 16, 134, 24)
    painter.setBrush(QColor(13, 30, 46, 220))
    painter.setPen(QPen(QColor(0, 210, 255, 180), 1.0))
    painter.drawRoundedRect(badge_rect, 6, 6)
    painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    painter.setPen(QColor(0, 210, 255))
    painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "Plano Cartesiano 2D")

    painter.end()
    img.save(path, "PNG")


def create_3d_preview_image(path, width=440, height=220):
    img = QImage(width, height, QImage.Format.Format_ARGB32)
    img.fill(QColor(13, 17, 23))
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    cx, cy = width // 2, height // 2
    R = 82.0

    # Fondo radial de iluminación de la esfera
    grad = QRadialGradient(cx - 20, cy - 25, R * 1.3)
    grad.setColorAt(0.0, QColor(25, 45, 75, 240))
    grad.setColorAt(0.7, QColor(15, 25, 42, 220))
    grad.setColorAt(1.0, QColor(10, 15, 24, 250))

    painter.setBrush(grad)
    painter.setPen(QPen(QColor(56, 139, 253, 120), 1.5))
    painter.drawEllipse(QPointF(cx, cy), R, R)

    # Meridianos y Paralelos
    # Paralelos
    for lat_deg in (-60, -30, 0, 30, 60):
        lat_rad = math.radians(lat_deg)
        r_slice = R * math.cos(lat_rad)
        y_slice = cy - R * math.sin(lat_rad) * 0.4
        b_axis = r_slice * 0.28
        if lat_deg == 0:
            painter.setPen(QPen(QColor(0, 210, 255, 150), 1.4))  # Ecuador
        else:
            painter.setPen(QPen(QColor(56, 139, 253, 70), 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, y_slice), r_slice, b_axis)

    # Meridianos
    for lon_deg in (0, 30, 60, 90, 120, 150):
        lon_rad = math.radians(lon_deg)
        a_axis = R * math.cos(lon_rad)
        if lon_deg == 90:
            painter.setPen(QPen(QColor(0, 210, 255, 150), 1.4))
        else:
            painter.setPen(QPen(QColor(56, 139, 253, 70), 1.0))
        painter.drawEllipse(QPointF(cx, cy), abs(a_axis), R)

    # Trazo 3D en la superficie esférica (cian brillante)
    stroke_3d = []
    for ang in range(-40, 50, 10):
        rad = math.radians(ang)
        px = cx + R * 0.85 * math.cos(rad)
        py = cy + R * 0.50 * math.sin(rad * 1.5)
        stroke_3d.append((px, py))

    p_stroke = QPainterPath()
    p_stroke.moveTo(*stroke_3d[0])
    for pt in stroke_3d[1:]:
        p_stroke.lineTo(*pt)

    # Glow y trazo
    painter.setPen(QPen(QColor(0, 210, 255, 60), 8.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.drawPath(p_stroke)
    painter.setPen(QPen(QColor(0, 229, 255), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.drawPath(p_stroke)

    # Proyección geodésica punteada en oro/ámbar
    proj_3d = []
    last_pt = stroke_3d[-1]
    for ang in range(50, 130, 12):
        rad = math.radians(ang)
        px = cx + R * 0.82 * math.cos(rad)
        py = cy + R * 0.50 * math.sin(rad * 1.5)
        proj_3d.append((px, py))

    p_proj_3d = QPainterPath()
    p_proj_3d.moveTo(*last_pt)
    for pt in proj_3d:
        p_proj_3d.lineTo(*pt)

    pen_proj = QPen(QColor(255, 183, 3, 230), 2.8, Qt.PenStyle.DashLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    pen_proj.setDashPattern([3, 4])
    painter.setPen(pen_proj)
    painter.drawPath(p_proj_3d)

    # Marcadores de hitos
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(255, 183, 3))
    for pt in proj_3d:
        painter.drawEllipse(QPointF(pt[0], pt[1]), 2.5, 2.5)

    # Insignia flotante [Superficie Esférica 3D]
    badge_rect = QRectF(width - 150, 16, 134, 24)
    painter.setBrush(QColor(13, 30, 46, 220))
    painter.setPen(QPen(QColor(0, 210, 255, 180), 1.0))
    painter.drawRoundedRect(badge_rect, 6, 6)
    painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    painter.setPen(QColor(0, 210, 255))
    painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "Superficie Esférica 3D")

    painter.end()
    img.save(path, "PNG")

    p_proj_3d = QPainterPath()
    p_proj_3d.moveTo(*last_pt)
    for pt in proj_3d:
        p_proj_3d.lineTo(*pt)

    pen_proj = QPen(QColor(255, 183, 3, 230), 2.8, Qt.PenStyle.DashLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    pen_proj.setDashPattern([3, 4])
    painter.setPen(pen_proj)
    painter.drawPath(p_proj_3d)

    # Marcadores de hitos
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(255, 183, 3))
    for pt in proj_3d:
        painter.drawEllipse(QPointF(pt[0], pt[1]), 2.5, 2.5)

    # Insignia flotante [Esfera OpenGL]
    badge_rect = QRectF(width - 150, 16, 134, 24)
    painter.setBrush(QColor(13, 30, 46, 220))
    painter.setPen(QPen(QColor(0, 210, 255, 180), 1.0))
    painter.drawRoundedRect(badge_rect, 6, 6)
    painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
    painter.setPen(QColor(0, 210, 255))
    painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, "Superficie Esférica 3D")

    painter.end()
    img.save(path, "PNG")


def generate_all_ui_assets():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    create_home_icon(os.path.join(UI_ICONS_DIR, "home.png"))
    create_reload_icon(os.path.join(UI_ICONS_DIR, "reload.png"))
    create_eraser_icon(os.path.join(UI_ICONS_DIR, "eraser.png"))
    create_2d_preview_image(os.path.join(UI_ICONS_DIR, "preview_2d.png"))
    create_3d_preview_image(os.path.join(UI_ICONS_DIR, "preview_3d.png"))

    print(f"[OK] Assets de UI generados en: {UI_ICONS_DIR}")


if __name__ == "__main__":
    generate_all_ui_assets()
