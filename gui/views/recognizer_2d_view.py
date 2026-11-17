"""
recognizer_2d_view.py
=====================
Ventana B: Reconocedor y Visualizador 2D (Plano Cartesiano).
Diseño optimizado:
- El lienzo de dibujo ocupa TODO el recuadro disponible, eliminando espacios vacíos.
- Botón 'Inicio' con logo de casita.
- Botón 'Reiniciar Captura' con icono de flecha circular.
- Botón 'Limpiar Lienzo' con icono de borrador.
- Panel derecho de clasificación y probabilidades en tiempo real.
"""

import os
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QFrame, QSizePolicy
)

from engine.feature_extractor import FeatureExtractor
from gui.widgets.canvas_2d import Canvas2D
from gui.widgets.ranking_panel import RankingPanel


class Recognizer2DView(QWidget):
    """
    Vista completa del modo 2D para reconocimiento de caracteres en plano cartesiano.
    """

    navigate_to_menu = pyqtSignal()

    def __init__(self, classifier, icons_dir=None, parent=None):
        super().__init__(parent)
        self.classifier = classifier
        self.icons_dir = icons_dir

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.ui_dir = os.path.join(base_dir, "data", "icons", "ui")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 12)
        main_layout.setSpacing(8)

        # 1. Barra Superior de Control y Navegación con Iconos
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)

        # 2. Contenedor Principal Dividido (Splitter Izquierda / Derecha)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E8FF;
                border-radius: 4px;
            }
            QSplitter::handle:hover {
                background-color: #1565C0;
            }
        """)

        # Sección Izquierda: Contenedor del Lienzo 2D a pantalla completa
        left_container = QFrame()
        left_container.setObjectName("cardFrame")
        left_container.setStyleSheet("""
            QFrame#cardFrame {
                background-color: #F5F7FA;
                border: 1px solid #C8D8F0;
                border-radius: 12px;
                padding: 0px;
            }
        """)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Lienzo 2D ocupando el 100% del área
        self.canvas = Canvas2D(self)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self.canvas, stretch=1)

        # Barra flotante de herramientas (reseteo y limpieza) en la esquina superior izquierda del lienzo
        self._create_canvas_overlay()

        # Barra de estado inferior compacta
        self.stats_bar = QFrame()
        self.stats_bar.setFixedHeight(28)
        self.stats_bar.setStyleSheet("background-color: #F5F7FA; border-top: 1px solid #E0E8FF; border-radius: 0 0 12px 12px;")
        sb_layout = QHBoxLayout(self.stats_bar)
        sb_layout.setContentsMargins(14, 0, 14, 0)

        self.stats_label = QLabel("Trazos: 0  |  Puntos: 0  |  Símbolos discretos: 0")
        self.stats_label.setStyleSheet("color: #555555; font-size: 11px; font-weight: 500;")
        sb_layout.addWidget(self.stats_label)

        hint_quick = QLabel("Atajo: [C] o [Espacio] para limpiar")
        hint_quick.setStyleSheet("color: #777777; font-size: 11px;")
        hint_quick.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        sb_layout.addWidget(hint_quick)

        left_layout.addWidget(self.stats_bar)

        splitter.addWidget(left_container)

        # Sección Derecha: Panel de Clasificación y Probabilidades
        self.ranking_panel = RankingPanel(icons_dir=self.icons_dir, parent=self)
        splitter.addWidget(self.ranking_panel)

        # Configurar proporción inicial (72% lienzo para máximo espacio, 28% ranking)
        splitter.setStretchFactor(0, 72)
        splitter.setStretchFactor(1, 28)

        main_layout.addWidget(splitter, stretch=1)

        # Conectar señales del lienzo al procesador de inferencia
        self.selected_target_char = None
        self.canvas.stroke_updated.connect(self._on_stroke_updated)
        self.ranking_panel.letter_selected.connect(self._on_letter_selected)

    def _on_letter_selected(self, char: str):
        """Permite al usuario fijar manualmente la proyección a una letra específica."""
        self.selected_target_char = char
        # Re-proyectar si hay trazos
        strokes = self.canvas.all_strokes + ([self.canvas.current_stroke] if self.canvas.current_stroke else [])
        if strokes:
            self._on_stroke_updated(strokes)

    def _create_top_bar(self):
        """Crea la barra superior con botones de casita, flecha circular y borrador."""
        bar = QFrame()
        bar.setFixedHeight(54)
        bar.setStyleSheet("""
            QFrame {
                background-color: #EEF2FF;
                border: 1px solid #C8D8F0;
                border-radius: 10px;
                padding: 4px 12px;
            }
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(12)

        # 1. Botón Inicio con icono de casita (sin texto)
        btn_home = QPushButton()
        btn_home.setProperty("class", "iconButton")
        btn_home.setFixedSize(40, 40)
        btn_home.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_home.setToolTip("Inicio / Volver al Menú Principal")

        home_icon_path = os.path.join(self.ui_dir, "home.png")
        if not os.path.exists(home_icon_path):
            home_icon_path = os.path.join(self.ui_dir, "home.svg")
        if os.path.exists(home_icon_path):
            btn_home.setIcon(QIcon(home_icon_path))
            btn_home.setIconSize(QSize(22, 22))

        btn_home.clicked.connect(self.navigate_to_menu.emit)
        layout.addWidget(btn_home)

        # Título del modo
        title = QLabel("MODO 2D: RECONOCEDOR CARTESIANO")
        title.setStyleSheet("color: #111111; font-weight: 800; font-size: 14px; letter-spacing: 0.5px;")
        layout.addWidget(title)

        badge = QLabel("K=16 DIRECCIONES")
        badge.setStyleSheet("""
            color: #1565C0;
            background-color: #D6E4FF;
            border: 1px solid #005f73;
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 700;
        """)
        layout.addWidget(badge)

        layout.addStretch()
        return bar

    def _create_canvas_overlay(self):
        """Crea la barra flotante con botones de reseteo en la esquina superior izquierda del lienzo."""
        overlay = QFrame(self.canvas)
        overlay.setObjectName("canvasOverlayBar")
        overlay.setStyleSheet("""
            QFrame#canvasOverlayBar {
                background-color: rgba(255, 255, 254, 0.88);
                border: 1px solid #C8D8F0;
                border-radius: 9px;
            }
        """)

        layout = QHBoxLayout(overlay)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        # 1. Botón Reiniciar Captura con SVG de retorno (diseño idéntico a 3D)
        btn_reset = QPushButton(overlay)
        btn_reset.setProperty("class", "iconButton")
        btn_reset.setFixedSize(36, 36)
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setToolTip("Reiniciar Captura (Return)")
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #1565C0;
                border: 1px solid #0D47A1;
                border-radius: 9px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #1976D2;
                border-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)

        return_icon_path = os.path.join(self.ui_dir, "return.png")
        if not os.path.exists(return_icon_path):
            return_icon_path = os.path.join(self.ui_dir, "return.svg")
        if os.path.exists(return_icon_path):
            btn_reset.setIcon(QIcon(return_icon_path))
            btn_reset.setIconSize(QSize(20, 20))

        btn_reset.clicked.connect(self.reset_capture)
        layout.addWidget(btn_reset)

        # 2. Botón Limpiar Lienzo con SVG de borrador (diseño idéntico a 3D)
        btn_clear = QPushButton(overlay)
        btn_clear.setProperty("class", "iconButtonDanger")
        btn_clear.setFixedSize(36, 36)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setToolTip("Limpiar Lienzo (Clear Format)")
        btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #C62828;
                border: 1px solid #B71C1C;
                border-radius: 9px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
                border-color: #EF9A9A;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """)

        clear_icon_path = os.path.join(self.ui_dir, "clear.png")
        if not os.path.exists(clear_icon_path):
            clear_icon_path = os.path.join(self.ui_dir, "clear.svg")
        if os.path.exists(clear_icon_path):
            btn_clear.setIcon(QIcon(clear_icon_path))
            btn_clear.setIconSize(QSize(20, 20))

        btn_clear.clicked.connect(self.clear_canvas)
        layout.addWidget(btn_clear)

        # Evitar que hacer clic o arrastrar en el marco del overlay dibuje sobre el lienzo
        overlay.mousePressEvent = lambda e: e.accept()
        overlay.mouseMoveEvent = lambda e: e.accept()
        overlay.mouseReleaseEvent = lambda e: e.accept()

        overlay.adjustSize()
        overlay.move(14, 14)
        overlay.show()
        overlay.raise_()

        self.canvas.overlay_toolbar = overlay

    def clear_canvas(self):
        """Limpia trazos y restablece el panel de ranking."""
        self.selected_target_char = None
        self.canvas.clear_canvas()
        self.ranking_panel.reset_display()
        self.stats_label.setText("Trazos: 0  |  Puntos: 0  |  Símbolos discretos: 0")

    def reset_capture(self):
        """Reinicia la captura actual."""
        self.selected_target_char = None
        self.canvas.reset_capture()
        self.ranking_panel.reset_display()
        self.stats_label.setText("Trazos: 0  |  Puntos: 0  |  Símbolos discretos: 0")

    def _on_stroke_updated(self, strokes):
        """
        Slot invocado en tiempo real cada vez que el usuario dibuja o añade puntos.
        Ejecuta la discretización, evaluación Forward en los 27 HMMs y autocompletado espacial
        proyectando todo el trazo faltante con puntos.
        """
        if not strokes:
            self.ranking_panel.reset_display()
            self.canvas.set_projection([])
            self.stats_label.setText("Trazos: 0  |  Puntos: 0  |  Símbolos discretos: 0")
            return

        # 1. Extraer símbolos discretos K=16 a partir de las coordenadas (invariante a escala)
        symbols, resampled_strokes = FeatureExtractor.extract_symbols_from_strokes_2d(strokes)
        total_pts = sum(len(st) for st in strokes)

        # Si aún no hay símbolos remuestreados pero hay al menos 2 puntos en el trazo actual:
        # Extraer el vector directo para tener un símbolo inicial inmediato
        if len(symbols) == 0 and strokes and len(strokes[-1]) >= 2:
            p_start = strokes[-1][0]
            p_last = strokes[-1][-1]
            dx = p_last[0] - p_start[0]
            dy = p_last[1] - p_start[1]
            if dx * dx + dy * dy >= 16.0:  # Mínimo 4 píxeles de desplazamiento
                s0 = FeatureExtractor.quantize_angle_2d(dx, dy)
                symbols = [s0]

        self.stats_label.setText(
            f"Trazos: {len(strokes)}  |  Puntos: {total_pts}  |  "
            f"Símbolos discretos (K=16): {len(symbols)}"
        )

        if len(symbols) == 0:
            self.ranking_panel.reset_display()
            self.canvas.set_projection([])
            return

        # 2. Evaluación Forward y cálculo de probabilidades posteriores en tiempo real
        results = self.classifier.classify(symbols)
        self.ranking_panel.update_ranking(results)

        # 3. Autocompletado espacial dinámico: todo el trazo faltante de la letra más probable con puntos
        top_char = self.selected_target_char if self.selected_target_char else results[0]["char"]
        top_match = next((r for r in results if r["char"] == top_char), results[0])
        top_perc = top_match["percentage"]

        projected_strokes = FeatureExtractor.predict_complete_projection_2d(
            strokes=strokes,
            top_char=top_char,
            classifier=self.classifier
        )

        self.canvas.set_projection(projected_strokes, projected_char=top_char, prob_perc=top_perc)
