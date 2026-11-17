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

        # Barra de botones flotante en la esquina superior izquierda
        self.overlay_toolbar = None

        # Estilo del lienzo (restringido a Canvas2D para no sobreescribir los botones overlay)
        self.setStyleSheet("Canvas2D { background-color: #F5F7FA; border-radius: 12px; }")

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

    def set_projection(self, trajectory_data, projected_char="", prob_perc=""):
        """
        Actualiza los puntos de la trayectoria futura estimada y la letra asociada.
        trajectory_data puede ser una lista de trazos [[[x, y], ...], ...] o una lista plana.
        """
        if not trajectory_data:
            self.projected_trajectory = []
        elif len(trajectory_data) > 0 and len(trajectory_data[0]) > 0 and isinstance(trajectory_data[0][0], (int, float)):
            self.projected_trajectory = [trajectory_data]
        else:
            self.projected_trajectory = [st for st in trajectory_data if len(st) > 0]

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "overlay_toolbar") and self.overlay_toolbar:
            self.overlay_toolbar.move(14, 14)
            self.overlay_toolbar.raise_()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, "overlay_toolbar") and self.overlay_toolbar:
            self.overlay_toolbar.move(14, 14)
            self.overlay_toolbar.raise_()

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

        # 2. Trazos completados anteriormente (en azul marino oscuro)
        pen_completed = QPen(QColor(21, 101, 192, 220), 4.0)
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

        # 3. Trazo activo actual (en azul eléctrico con brillo)
        if len(self.current_stroke) >= 2:
            # Resplandor exterior suave
            glow_pen = QPen(QColor(25, 118, 210, 60), 8.0)
            glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            glow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(glow_pen)

            path = QPainterPath()
            path.moveTo(self.current_stroke[0][0], self.current_stroke[0][1])
            for pt in self.current_stroke[1:]:
                path.lineTo(pt[0], pt[1])
            painter.drawPath(path)

            # Núcleo nítido del trazo activo
            active_pen = QPen(QColor(13, 71, 161), 4.0)
            active_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            active_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(active_pen)
            painter.drawPath(path)

        # 4. Proyección Dinámica de Trayectoria (Autocompletado Espacial)
        self._draw_projected_trajectory(painter)

        # 5. Indicador del cursor del lápiz
        if self.cursor_pos:
            cx, cy = self.cursor_pos
            painter.setPen(QPen(QColor(21, 101, 192, 180), 1.5))
            painter.setBrush(QColor(21, 101, 192, 50))
            painter.drawEllipse(QPointF(cx, cy), 6.0, 6.0)
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(QPointF(cx, cy), 2.0, 2.0)

        # 6. Mensaje instructivo si el lienzo está completamente vacío
        if not self.all_strokes and not self.current_stroke:
            painter.setPen(QColor(100, 120, 160, 120))
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
        pen_minor = QPen(QColor(180, 195, 215, 100), 1.0)
        painter.setPen(pen_minor)

        # Líneas verticales
        for x in range(grid_step, w, grid_step):
            painter.drawLine(x, 0, x, h)

        # Líneas horizontales
        for y in range(grid_step, h, grid_step):
            painter.drawLine(0, y, w, y)

        # Ejes centrales ligeramente más marcados
        pen_major = QPen(QColor(140, 165, 200, 160), 1.2)
        painter.setPen(pen_major)
        mid_x, mid_y = w // 2, h // 2
        painter.drawLine(mid_x, 0, mid_x, h)
        painter.drawLine(0, mid_y, w, mid_y)

    def _draw_projected_trajectory(self, painter):
        """
        Renderiza la trayectoria de autocompletado proyectando TODO el trazo faltante
        de la letra más probable mediante una constelación de puntos luminosos ('con puntos').
        """
        if not self.projected_trajectory:
            return

        # Línea guía punteada muy fina y sutil para la continuidad visual
        pen_guide = QPen(QColor(255, 183, 3, 75), 1.4)
        pen_guide.setStyle(Qt.PenStyle.DashLine)
        pen_guide.setDashPattern([2, 4])
        pen_guide.setCapStyle(Qt.PenCapStyle.RoundCap)

        last_pt_overall = None

        for stroke in self.projected_trajectory:
            if len(stroke) < 1:
                continue

            last_pt_overall = stroke[-1]

            # 1. Dibujar línea guía punteada sutil
            if len(stroke) >= 2:
                painter.setPen(pen_guide)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                path = QPainterPath()
                path.moveTo(stroke[0][0], stroke[0][1])
                for pt in stroke[1:]:
                    path.lineTo(pt[0], pt[1])
                painter.drawPath(path)

            # 2. Dibujar TODOS LOS PUNTOS faltantes ("con puntos")
            painter.setPen(Qt.PenStyle.NoPen)
            for idx, pt in enumerate(stroke):
                px, py = float(pt[0]), float(pt[1])

                # Resplandor exterior suave del punto
                painter.setBrush(QColor(255, 183, 3, 70))
                painter.drawEllipse(QPointF(px, py), 4.5, 4.5)

                # Núcleo nítido y brillante del punto
                painter.setBrush(QColor(255, 215, 65, 245))
                painter.drawEllipse(QPointF(px, py), 2.5, 2.5)

                # Destello central blanco
                painter.setBrush(QColor(255, 255, 255, 220))
                painter.drawEllipse(QPointF(px, py), 1.0, 1.0)

        # 3. Etiqueta flotante con el carácter predicho y el porcentaje de confianza
        if self.projected_char and last_pt_overall:
            badge_text = f"Proyección: '{self.projected_char}' ({self.projected_perc})"

            font = QFont("Segoe UI", 10, QFont.Weight.Bold)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            text_w = metrics.horizontalAdvance(badge_text) + 16
            text_h = 24

            badge_x = min(float(last_pt_overall[0]) + 12, float(self.width() - text_w - 12))
            badge_y = max(float(last_pt_overall[1]) - 14, 12.0)

            badge_rect = QRectF(badge_x, badge_y, text_w, text_h)

            # Fondo del badge
            painter.setBrush(QColor(22, 27, 34, 235))
            painter.setPen(QPen(QColor(255, 183, 3, 200), 1.2))
            painter.drawRoundedRect(badge_rect, 6, 6)

            # Texto del badge
            painter.setPen(QColor(255, 210, 60))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, badge_text)
