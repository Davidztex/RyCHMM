"""
recognizer_2d_view.py
=====================
Ventana B: Reconocedor y Visualizador 2D (Plano Cartesiano).
Integra:
- Lado Izquierdo: Lienzo 2D interactivo de trazado y proyección de trayectoria dinámica.
- Lado Derecho: Panel de clasificación probabilística en tiempo real con ranking y miniaturas.
- Barra Superior: Controles de navegación, limpiar lienzo, reiniciar captura y estadísticas de trazo.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QFrame
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

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 16)
        main_layout.setSpacing(10)

        # 1. Barra Superior de Control y Navegación
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

        # Sección Izquierda: Contenedor del Lienzo 2D
        left_container = QFrame()
        left_container.setObjectName("cardFrame")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)

        self.canvas = Canvas2D(self)
        left_layout.addWidget(self.canvas)

        # Barra de estado inferior del lienzo
        self.stats_label = QLabel("Trazos: 0  |  Puntos: 0  |  Símbolos discretos: 0")
        self.stats_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 500;")
        left_layout.addWidget(self.stats_label)

        splitter.addWidget(left_container)

        # Sección Derecha: Panel de Clasificación y Probabilidades
        self.ranking_panel = RankingPanel(icons_dir=self.icons_dir, parent=self)
        splitter.addWidget(self.ranking_panel)

        # Configurar proporción inicial (70% lienzo, 30% panel de ranking)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # Conectar señales del lienzo al procesador de inferencia
        self.canvas.stroke_updated.connect(self._on_stroke_updated)

    def _create_top_bar(self):
        """Crea la barra superior con botones de control y navegación."""
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

        btn_back = QPushButton("← Volver al Menú")
        btn_back.setProperty("class", "navButton")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.navigate_to_menu.emit)
        layout.addWidget(btn_back)

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

        btn_reset = QPushButton("Reiniciar Captura")
        btn_reset.setProperty("class", "navButton")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(self.reset_capture)
        layout.addWidget(btn_reset)

        btn_clear = QPushButton("Limpiar Lienzo")
        btn_clear.setProperty("class", "dangerButton")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
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
