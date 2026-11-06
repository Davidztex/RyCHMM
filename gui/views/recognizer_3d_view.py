"""
recognizer_3d_view.py
=====================
Ventana C: Reconocedor y Visualizador 3D (Lienzo Esférico OpenGL).
Diseño optimizado:
- La esfera 3D es significativamente más grande y ocupa TODO el recuadro disponible.
- Botón 'Inicio' con logo de casita.
- Botón 'Centrar Cámara' con icono de flecha circular.
- Botón 'Limpiar Esfera' con icono de borrador.
- Eliminación de espacios vacíos para maximizar la superficie de dibujo.
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

        # Sección Izquierda: Contenedor del Lienzo 3D a pantalla completa
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

        # Lienzo 3D OpenGL esférico ocupando el 100% del área
        self.canvas_3d = Canvas3DSphere(self)
        self.canvas_3d.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self.canvas_3d, stretch=1)

        # Barra de estado inferior compacta
        self.stats_bar = QFrame()
        self.stats_bar.setFixedHeight(28)
        self.stats_bar.setStyleSheet("background-color: #0e1219; border-top: 1px solid #21262d; border-radius: 0 0 12px 12px;")
        sb_layout = QHBoxLayout(self.stats_bar)
        sb_layout.setContentsMargins(14, 0, 14, 0)

        self.stats_label = QLabel("Puntos sobre la esfera: 0  |  Variaciones tangenciales (Δθ, Δϕ): 0")
        self.stats_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 500;")
        sb_layout.addWidget(self.stats_label)

        hint_quick = QLabel("Arrastrar: rotar 360° | Rueda: zoom")
        hint_quick.setStyleSheet("color: #484f58; font-size: 11px;")
        hint_quick.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        sb_layout.addWidget(hint_quick)

        left_layout.addWidget(self.stats_bar)

        splitter.addWidget(left_container)

        # Sección Derecha: Panel de Clasificación 3D
        self.ranking_panel = RankingPanel(icons_dir=self.icons_dir, parent=self)
        splitter.addWidget(self.ranking_panel)

        # Proporción: 72% lienzo para esfera grande, 28% ranking
        splitter.setStretchFactor(0, 72)
        splitter.setStretchFactor(1, 28)

        main_layout.addWidget(splitter, stretch=1)

        # Conectar actualización del trazo 3D
        self.canvas_3d.stroke_3d_updated.connect(self._on_stroke_3d_updated)

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

        # 2. Botón Centrar Cámara con SVG center_focus (sin texto)
        btn_reset_cam = QPushButton()
        btn_reset_cam.setProperty("class", "iconButton")
        btn_reset_cam.setFixedSize(40, 40)
        btn_reset_cam.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset_cam.setToolTip("Centrar Cámara (Center Focus)")

        center_icon_path = os.path.join(self.ui_dir, "center_focus.png")
        if not os.path.exists(center_icon_path):
            center_icon_path = os.path.join(self.ui_dir, "center_focus.svg")
        if os.path.exists(center_icon_path):
            btn_reset_cam.setIcon(QIcon(center_icon_path))
            btn_reset_cam.setIconSize(QSize(22, 22))

        btn_reset_cam.clicked.connect(self.reset_camera)
        layout.addWidget(btn_reset_cam)

        # 3. Botón Limpiar Esfera con SVG de borrador/clear-format (sin texto)
        btn_clear = QPushButton()
        btn_clear.setProperty("class", "iconButtonDanger")
        btn_clear.setFixedSize(40, 40)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setToolTip("Limpiar Esfera (Clear Format)")

        clear_icon_path = os.path.join(self.ui_dir, "clear.png")
        if not os.path.exists(clear_icon_path):
            clear_icon_path = os.path.join(self.ui_dir, "clear.svg")
        if os.path.exists(clear_icon_path):
            btn_clear.setIcon(QIcon(clear_icon_path))
            btn_clear.setIconSize(QSize(22, 22))

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
