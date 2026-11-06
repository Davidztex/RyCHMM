"""
canvas_2d.py
============
Lienzo interactivo bidimensional de trazado y autocompletado espacial en tiempo real.
Renderizado optimizado con QPainter, grilla milimétrica cartesiana sutil,
trazo activo continuo y proyección punteada/traslúcida de la trayectoria futura estimada.
"""

from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QRectF
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QBrush, QPainterPath, QFont,
    QRadialGradient, QLinearGradient
)
from PyQt6.QtWidgets import QWidget


class Canvas2D(QWidget):
    """
    Lienzo 2D con captura de eventos de ratón, renderizado de trazo manual
    y proyección dinámica de autocompletado espacial para HMM.
    """

    # Señal emitida cuando el usuario dibuja o modifica el trazo: emite lista de trazos [[[x, y], ...], ...]
    stroke_updated = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Estado de trazos
        self.all_strokes = []       # Trazos finalizados: [[[x, y], ...], ...]
        self.current_stroke = []    # Trazo activo actual: [[x, y], ...]
        self.is_drawing = False

        # Estado de proyección dinámica
        self.projected_trajectory = []  # Puntos proyectados: [[x, y], ...]
        self.projected_char = ""        # Letra predicha Top-1
        self.projected_perc = ""        # Porcentaje de confianza

        # Posición actual del cursor
        self.cursor_pos = None

        self.setStyleSheet("background-color: #0b0e14; border-radius: 12px;")

    def clear_canvas(self):
        """Limpia todos los trazos y proyecciones del lienzo."""
        self.all_strokes.clear()
        self.current_stroke.clear()
        self.projected_trajectory.clear()
        self.projected_char = ""
        self.projected_perc = ""
        self.cursor_pos = None
        self.update()
        self.stroke_updated.emit([])

    def reset_capture(self):
        """Reinicia la captura actual conservando la posición del lienzo."""
        self.clear_canvas()

    def set_projection(self, trajectory_points, projected_char="", prob_perc=""):
        """
        Actualiza los puntos de la trayectoria futura estimada y la letra asociada.
        Se redibuja inmediatamente en tiempo real.
        """
        self.projected_trajectory = trajectory_points or []
        self.projected_char = projected_char
        self.projected_perc = prob_perc
        self.update()

    def get_current_strokes_payload(self):
        """Retorna la lista completa de trazos (completados + activo actual)."""
        payload = [list(st) for st in self.all_strokes if len(st) >= 2]
        if len(self.current_stroke) >= 2:
            payload.append(list(self.current_stroke))
        return payload

    # -------------------------------------------------------------
    # Eventos de Ratón
    # -------------------------------------------------------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_drawing = True
            pos = event.position()
            self.current_stroke = [[pos.x(), pos.y()]]
            self.cursor_pos = (pos.x(), pos.y())
            self.update()
            self.stroke_updated.emit(self.get_current_strokes_payload())

    def mouseMoveEvent(self, event):
        pos = event.position()
        self.cursor_pos = (pos.x(), pos.y())

        if self.is_drawing and (event.buttons() & Qt.MouseButton.LeftButton):
            # Agregar punto si la distancia euclidiana es suficiente para no saturar
            if self.current_stroke:
                last_x, last_y = self.current_stroke[-1]
                dx = pos.x() - last_x
                dy = pos.y() - last_y
                if dx * dx + dy * dy >= 4.0:  # Mínimo 2 píxeles de desplazamiento
                    self.current_stroke.append([pos.x(), pos.y()])
                    self.update()
                    self.stroke_updated.emit(self.get_current_strokes_payload())
            else:
                self.current_stroke.append([pos.x(), pos.y()])
                self.update()
        else:
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.is_drawing = False
            if len(self.current_stroke) >= 2:
                self.all_strokes.append(list(self.current_stroke))
            self.current_stroke = []
            self.update()
            self.stroke_updated.emit(self.get_current_strokes_payload())

    def keyPressEvent(self, event):
        # Atajo: Tecla C o Espacio limpia el lienzo
        if event.key() in (Qt.Key.Key_C, Qt.Key.Key_Space):
            self.clear_canvas()
        else:
            super().keyPressEvent(event)

    # -------------------------------------------------------------
    # Renderizado Gráfico
    # -------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w, h = self.width(), self.height()

        # 1. Fondo milimétrico cartesiano sutil
        self._draw_cartesian_grid(painter, w, h)

        # 2. Trazos completados anteriormente (en azul hielo / gris nítido)
        pen_completed = QPen(QColor(203, 213, 225, 230), 4.0)
        pen_completed.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen_completed.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen_completed)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        for stroke in self.all_strokes:
            if len(stroke) >= 2:
                path = QPainterPath()
                path.moveTo(stroke[0][0], stroke[0][1])
                for pt in stroke[1:]:
                    path.lineTo(pt[0], pt[1])
                painter.drawPath(path)

        # 3. Trazo activo actual (en cian fluorescente con brillo)
        if len(self.current_stroke) >= 2:
            # Resplandor exterior suave
            glow_pen = QPen(QColor(0, 210, 255, 60), 8.0)
            glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            glow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(glow_pen)

            path = QPainterPath()
            path.moveTo(self.current_stroke[0][0], self.current_stroke[0][1])
            for pt in self.current_stroke[1:]:
                path.lineTo(pt[0], pt[1])
            painter.drawPath(path)

            # Núcleo nítido del trazo activo
            active_pen = QPen(QColor(0, 229, 255), 4.0)
            active_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            active_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(active_pen)
            painter.drawPath(path)

        # 4. Proyección Dinámica de Trayectoria (Autocompletado Espacial)
        self._draw_projected_trajectory(painter)

        # 5. Indicador del cursor del lápiz
        if self.cursor_pos:
            cx, cy = self.cursor_pos
            painter.setPen(QPen(QColor(0, 210, 255, 180), 1.5))
            painter.setBrush(QColor(0, 210, 255, 50))
            painter.drawEllipse(QPointF(cx, cy), 6.0, 6.0)
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(QPointF(cx, cy), 2.0, 2.0)

        # 6. Mensaje instructivo si el lienzo está completamente vacío
        if not self.all_strokes and not self.current_stroke:
            painter.setPen(QColor(139, 148, 158, 120))
            font = QFont("Segoe UI", 14, QFont.Weight.DemiBold)
            painter.setFont(font)
            text_rect = QRectF(0, h * 0.45, w, 40)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "Dibuje una letra aquí con el ratón")
            font_sub = QFont("Segoe UI", 11)
            painter.setFont(font_sub)
            text_sub = QRectF(0, h * 0.45 + 30, w, 25)
            painter.drawText(text_sub, Qt.AlignmentFlag.AlignCenter, "El autocompletado y las probabilidades se actualizarán paso a paso")

    def _draw_cartesian_grid(self, painter, w, h):
        """Dibuja una grilla técnica milimétrica suave."""
        grid_step = 30
        pen_minor = QPen(QColor(30, 36, 46, 100), 1.0)
        painter.setPen(pen_minor)

        # Líneas verticales
        for x in range(grid_step, w, grid_step):
            painter.drawLine(x, 0, x, h)

        # Líneas horizontales
        for y in range(grid_step, h, grid_step):
            painter.drawLine(0, y, w, y)

        # Ejes centrales ligeramente más marcados
        pen_major = QPen(QColor(48, 54, 61, 160), 1.2)
        painter.setPen(pen_major)
        mid_x, mid_y = w // 2, h // 2
        painter.drawLine(mid_x, 0, mid_x, h)
        painter.drawLine(0, mid_y, w, mid_y)

    def _draw_projected_trajectory(self, painter):
        """Renderiza la curva de autocompletado con línea punteada y etiqueta flotante."""
        if len(self.projected_trajectory) < 2:
            return

        # Estilo de proyección: línea punteada dorada/ámbar de alta visibilidad
        pen_proj = QPen(QColor(255, 183, 3, 220), 2.8)
        pen_proj.setStyle(Qt.PenStyle.DashLine)
        pen_proj.setDashPattern([3, 4])
        pen_proj.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_proj)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        proj_path = QPainterPath()
        p0 = self.projected_trajectory[0]
        proj_path.moveTo(p0[0], p0[1])

        for pt in self.projected_trajectory[1:]:
            proj_path.lineTo(pt[0], pt[1])
        painter.drawPath(proj_path)

        # Dibujar pequeños puntos marcadores en la trayectoria proyectada
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 183, 3, 180))
        for idx, pt in enumerate(self.projected_trajectory):
            if idx % 3 == 0:
                painter.drawEllipse(QPointF(pt[0], pt[1]), 2.5, 2.5)

        # Etiqueta flotante con el carácter predicho cerca del final de la proyección
        if self.projected_char:
            last_pt = self.projected_trajectory[-1]
            badge_text = f"Proyección: '{self.projected_char}' ({self.projected_perc})"

            font = QFont("Segoe UI", 10, QFont.Weight.Bold)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            text_w = metrics.horizontalAdvance(badge_text) + 16
            text_h = 24

            badge_x = min(float(last_pt[0]) + 10, float(self.width() - text_w - 10))
            badge_y = max(float(last_pt[1]) - 12, 10.0)

            badge_rect = QRectF(badge_x, badge_y, text_w, text_h)

            # Fondo del badge
            painter.setBrush(QColor(22, 27, 34, 230))
            painter.setPen(QPen(QColor(255, 183, 3, 200), 1.2))
            painter.drawRoundedRect(badge_rect, 6, 6)

            # Texto del badge
            painter.setPen(QColor(255, 200, 50))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, badge_text)
