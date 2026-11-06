"""
recognizer_3d_view.py
=====================
Ventana C: Reconocedor y Visualizador 3D (Lienzo Esférico OpenGL).
Integra:
- Lado Izquierdo: Lienzo esférico OpenGL con soporte para dibujo sobre la superficie,
  conversión a coordenadas angulares esféricas (theta, phi), rotación orbital y zoom,
  y proyección dinámica 3D de la trayectoria estimada.
- Lado Derecho: Mismo Panel de clasificación y probabilidades en tiempo real.
- Barra Superior: Botones de navegación, limpiar trazo y centrar vista de cámara.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QFrame
)

from engine.feature_extractor import FeatureExtractor
from gui.widgets.canvas_3d_sphere import Canvas3DSphere
from gui.widgets.ranking_panel import RankingPanel


class Recognizer3DView(QWidget):
    """
    Vista completa del modo 3D para reconocimiento de caracteres sobre cascarón esférico.
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

        # 2. Barra informativa de controles 3D
        hint_bar = QLabel(
            "💡 Guía de Interacción 3D:  "
            "• Clic Izquierdo sobre la esfera: Dibujar trazo  |  "
            "• Clic Derecho / Arrastre fuera: Rotar esfera 360°  |  "
            "• Rueda del ratón: Zoom"
        )
        hint_bar.setStyleSheet("""
            background-color: #161b22;
            color: #8b949e;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 500;
        """)
        main_layout.addWidget(hint_bar)

        # 3. Splitter Horizontal (Lienzo 3D Izquierda / Panel de Clasificación Derecha)
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

        # Sección Izquierda: Lienzo 3D Esférico
        left_container = QFrame()
        left_container.setObjectName("cardFrame")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)

        self.canvas_3d = Canvas3DSphere(self)
        left_layout.addWidget(self.canvas_3d)

        self.stats_label = QLabel("Puntos sobre la esfera: 0  |  Variaciones tangenciales (Δθ, Δϕ): 0")
        self.stats_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 500;")
        left_layout.addWidget(self.stats_label)

        splitter.addWidget(left_container)

        # Sección Derecha: Panel de Clasificación 3D
        self.ranking_panel = RankingPanel(icons_dir=self.icons_dir, parent=self)
        splitter.addWidget(self.ranking_panel)

        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # Conectar actualización del trazo 3D
        self.canvas_3d.stroke_3d_updated.connect(self._on_stroke_3d_updated)

    def _create_top_bar(self):
        """Crea la barra superior de controles 3D."""
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

        title = QLabel("MODO 3D: LIENZO ESFÉRICO (OPENGL)")
        title.setStyleSheet("color: #f0f6fc; font-weight: 800; font-size: 14px; letter-spacing: 0.5px;")
        layout.addWidget(title)

        badge = QLabel("GEOMETRÍA ESFÉRICA")
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

        btn_reset_cam = QPushButton("Centrar Cámara")
        btn_reset_cam.setProperty("class", "navButton")
        btn_reset_cam.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset_cam.clicked.connect(self.reset_camera)
        layout.addWidget(btn_reset_cam)

        btn_clear = QPushButton("Limpiar Esfera")
        btn_clear.setProperty("class", "dangerButton")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_canvas)
        layout.addWidget(btn_clear)

        return bar

    def reset_camera(self):
        """Centra la vista de cámara sobre la esfera."""
        if hasattr(self, 'canvas_3d'):
            self.canvas_3d.reset_view()

    def clear_canvas(self):
        """Limpia el trazo sobre la esfera y restablece el panel de clasificación."""
        self.canvas_3d.clear_canvas()
        self.ranking_panel.reset_display()
        self.stats_label.setText("Puntos sobre la esfera: 0  |  Variaciones tangenciales (Δθ, Δϕ): 0")

    def _on_stroke_3d_updated(self, points_3d):
        """
        Slot invocado en tiempo real cuando el trazo sobre la esfera evoluciona.
        Convierte coordenadas esféricas (theta, phi), mide variaciones tangenciales,
        cuantiza a K=16 sectores y actualiza la clasificación y autocompletado 3D.
        """
        if not points_3d:
            self.ranking_panel.reset_display()
            self.canvas_3d.set_projection_3d([])
            self.stats_label.setText("Puntos sobre la esfera: 0  |  Variaciones tangenciales (Δθ, Δϕ): 0")
            return

        # 1. Transformar a coordenadas esféricas y extraer símbolos angulares tangenciales
        symbols, res_pts_3d = FeatureExtractor.extract_symbols_from_sphere_points(
            points_3d, radius=self.canvas_3d.radius, step=0.06
        )

        self.stats_label.setText(
            f"Puntos 3D: {len(points_3d)}  |  "
            f"Geodésicas remuestreadas: {len(res_pts_3d)}  |  "
            f"Símbolos tangenciales (K=16): {len(symbols)}"
        )

        if len(symbols) == 0:
            self.ranking_panel.reset_display()
            self.canvas_3d.set_projection_3d([])
            return

        # 2. Evaluación Forward y cálculo de probabilidades posteriores
        results = self.classifier.classify(symbols)
        self.ranking_panel.update_ranking(results)

        # 3. Proyección dinámica 3D sobre la superficie esférica
        top1 = results[0]
        top_char = top1["char"]
        top_perc = top1["percentage"]

        future_symbols = self.classifier.predict_trajectory_symbols(symbols, top_char=top_char, horizon=18)

        if future_symbols and len(points_3d) > 0:
            last_pt_3d = points_3d[-1]
            proj_3d = FeatureExtractor.reconstruct_trajectory_3d_sphere(
                start_pt_3d=last_pt_3d,
                symbols=future_symbols,
                radius=self.canvas_3d.radius,
                step=0.06
            )
            self.canvas_3d.set_projection_3d(proj_3d, projected_char=top_char, prob_perc=top_perc)
        else:
            self.canvas_3d.set_projection_3d([], projected_char=top_char, prob_perc=top_perc)
