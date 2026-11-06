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
                background-color: #21262d;
                border-radius: 4px;
            }
            QSplitter::handle:hover {
                background-color: #58a6ff;
            }
        """)

        # Sección Izquierda: Contenedor del Lienzo 2D a pantalla completa
        left_container = QFrame()
        left_container.setObjectName("cardFrame")
        left_container.setStyleSheet("""
            QFrame#cardFrame {
                background-color: #0b0e14;
                border: 1px solid #30363d;
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

        # Barra de estado inferior compacta
        self.stats_bar = QFrame()
        self.stats_bar.setFixedHeight(28)
        self.stats_bar.setStyleSheet("background-color: #0e1219; border-top: 1px solid #21262d; border-radius: 0 0 12px 12px;")
        sb_layout = QHBoxLayout(self.stats_bar)
        sb_layout.setContentsMargins(14, 0, 14, 0)

        self.stats_label = QLabel("Trazos: 0  |  Puntos: 0  |  Símbolos discretos: 0")
        self.stats_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 500;")
        sb_layout.addWidget(self.stats_label)

        hint_quick = QLabel("Atajo: [C] o [Espacio] para limpiar")
        hint_quick.setStyleSheet("color: #484f58; font-size: 11px;")
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
        self.canvas.stroke_updated.connect(self._on_stroke_updated)

    def _create_top_bar(self):
        """Crea la barra superior con botones de casita, flecha circular y borrador."""
        bar = QFrame()
        bar.setFixedHeight(54)
        bar.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
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
        title.setStyleSheet("color: #f0f6fc; font-weight: 800; font-size: 14px; letter-spacing: 0.5px;")
        layout.addWidget(title)

        badge = QLabel("K=16 DIRECCIONES")
        badge.setStyleSheet("""
            color: #00d2ff;
            background-color: #0d1e2e;
            border: 1px solid #005f73;
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 700;
        """)
        layout.addWidget(badge)

        layout.addStretch()

        # 2. Botón Reiniciar Captura con SVG de retorno (sin texto)
        btn_reset = QPushButton()
        btn_reset.setProperty("class", "iconButton")
        btn_reset.setFixedSize(40, 40)
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setToolTip("Reiniciar Captura (Return)")

        return_icon_path = os.path.join(self.ui_dir, "return.png")
        if not os.path.exists(return_icon_path):
            return_icon_path = os.path.join(self.ui_dir, "return.svg")
        if os.path.exists(return_icon_path):
            btn_reset.setIcon(QIcon(return_icon_path))
            btn_reset.setIconSize(QSize(22, 22))

        btn_reset.clicked.connect(self.reset_capture)
        layout.addWidget(btn_reset)

        # 3. Botón Limpiar Lienzo con SVG de borrador/clear-format (sin texto)
        btn_clear = QPushButton()
        btn_clear.setProperty("class", "iconButtonDanger")
        btn_clear.setFixedSize(40, 40)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setToolTip("Limpiar Lienzo (Clear Format)")

        clear_icon_path = os.path.join(self.ui_dir, "clear.png")
        if not os.path.exists(clear_icon_path):
            clear_icon_path = os.path.join(self.ui_dir, "clear.svg")
        if os.path.exists(clear_icon_path):
            btn_clear.setIcon(QIcon(clear_icon_path))
            btn_clear.setIconSize(QSize(22, 22))

        btn_clear.clicked.connect(self.clear_canvas)
        layout.addWidget(btn_clear)

        return bar

    def clear_canvas(self):
        """Limpia trazos y restablece el panel de ranking."""
        self.canvas.clear_canvas()
        self.ranking_panel.reset_display()
        self.stats_label.setText("Trazos: 0  |  Puntos: 0  |  Símbolos discretos: 0")

    def reset_capture(self):
        """Reinicia la captura actual."""
        self.canvas.reset_capture()
        self.ranking_panel.reset_display()
        self.stats_label.setText("Trazos: 0  |  Puntos: 0  |  Símbolos discretos: 0")

    def _on_stroke_updated(self, strokes):
        """
        Slot invocado en tiempo real cada vez que el usuario dibuja o añade puntos.
        Ejecuta la discretización, evaluación Forward en los 27 HMMs y autocompletado espacial.
        """
        if not strokes:
            self.ranking_panel.reset_display()
            self.canvas.set_projection([])
            self.stats_label.setText("Trazos: 0  |  Puntos: 0  |  Símbolos discretos: 0")
            return

        # 1. Extraer símbolos discretos K=16 a partir de las coordenadas
        symbols, resampled_strokes = FeatureExtractor.extract_symbols_from_strokes_2d(strokes, step=12.0)
        total_pts = sum(len(st) for st in strokes)
        self.stats_label.setText(
            f"Trazos: {len(strokes)}  |  Puntos: {total_pts}  |  "
            f"Símbolos discretos (K=16): {len(symbols)}"
        )

        if len(symbols) == 0:
            self.ranking_panel.reset_display()
            self.canvas.set_projection([])
            return

        # 2. Evaluación Forward y cálculo de probabilidades posteriores
        results = self.classifier.classify(symbols)
        self.ranking_panel.update_ranking(results)

        # 3. Autocompletado espacial (Proyección de Trayectoria Futura)
        top1 = results[0]
        top_char = top1["char"]
        top_perc = top1["percentage"]

        future_symbols = self.classifier.predict_trajectory_symbols(symbols, top_char=top_char, horizon=18)

        start_pt = self.canvas.cursor_pos
        if start_pt is None and strokes and strokes[-1]:
            start_pt = (strokes[-1][-1][0], strokes[-1][-1][1])

        if future_symbols and start_pt:
            projected_traj = FeatureExtractor.reconstruct_trajectory_2d(
                start_pos=start_pt,
                symbols=future_symbols,
                step=12.0
            )
            self.canvas.set_projection(projected_traj, projected_char=top_char, prob_perc=top_perc)
        else:
            self.canvas.set_projection([], projected_char=top_char, prob_perc=top_perc)
