"""
menu_view.py
============
Ventana A: Menú Principal de Inicio.
Pantalla de bienvenida institucional (Universidad de los Llanos)
que permite seleccionar el modo de trabajo (Modo 2D o Modo 3D).
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy
)


class MenuView(QWidget):
    """
    Vista de bienvenida institucional con selector de modos 2D y 3D.
    """

    # Señales para navegar entre vistas
    navigate_to_2d = pyqtSignal()
    navigate_to_3d = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---------------------------------------------------------
        # 1. Encabezado Institucional
        # ---------------------------------------------------------
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 16px;
                padding: 24px;
            }
        """)
        h_layout = QVBoxLayout(header_frame)
        h_layout.setSpacing(8)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_univ = QLabel("UNIVERSIDAD DE LOS LLANOS")
        lbl_univ.setObjectName("institutionHeader")
        lbl_univ.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(lbl_univ)

        lbl_fac = QLabel("FACULTAD DE CIENCIAS BÁSICAS E INGENIERÍA — PROGRAMA DE INGENIERÍA DE SISTEMAS")
        lbl_fac.setObjectName("institutionSubHeader")
        lbl_fac.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(lbl_fac)


        main_layout.addWidget(header_frame)

        # ---------------------------------------------------------
        # 2. Tarjetas de Selección de Modo (2D vs 3D)
        # ---------------------------------------------------------
        modes_layout = QHBoxLayout()
        modes_layout.setSpacing(24)

        # Tarjeta Modo 2D
        card_2d = self._create_mode_card(
            mode_number="1",
            title="Modo 2D: Plano Cartesiano",
            badge="BIDIMENSIONAL",
            description=(
                "Reconocimiento y proyección dinámica de trazos en plano cartesiano.\n\n"
                "• Remuestreo espacial equidistante (longitud de arco).\n"
                "• Cuantización angular en K = 16 sectores (código de cadena).\n"
                "• Clasificación continua con Algoritmo Forward escalado.\n"
                "• Autocompletado espacial punteado de la trayectoria estimada."
            ),
            button_text="Entrar al Modo 2D",
            on_click=self.navigate_to_2d.emit
        )
        modes_layout.addWidget(card_2d)

        # Tarjeta Modo 3D
        card_3d = self._create_mode_card(
            mode_number="2",
            title="Modo 3D: Superficie Esférica",
            badge="TRIDIMENSIONAL (OPENGL)",
            description=(
                "Reconocimiento y proyección sobre la superficie de una esfera 3D.\n\n"
                "• Renderizado 3D con PyOpenGL y malla de meridianos/paralelos.\n"
                "• Trazado directo sobre el cascarón esférico con raycasting.\n"
                "• Medición de variaciones angulares tangenciales (Δθ, Δϕ).\n"
                "• Proyección geodésica dinámica 3D y controles orbitales de rotación/zoom."
            ),
            button_text="Entrar al Modo 3D",
            on_click=self.navigate_to_3d.emit
        )
        modes_layout.addWidget(card_3d)

        main_layout.addLayout(modes_layout)

        # ---------------------------------------------------------
        # 3. Pie de Estado y Cumplimiento
        # ---------------------------------------------------------
        footer = QLabel(
            "✓ 27 Modelos HMM Listos (a-z + ñ)  |  "
            "✓ Algoritmos Nativos: Forward, Backward, Viterbi, Baum-Welch  |  "
            "✓ Sin Librerías Estocásticas Externas"
        )
        footer.setStyleSheet("color: #8b949e; font-size: 12px; font-weight: 500;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer)

    def _create_mode_card(self, mode_number, title, badge, description, button_text, on_click):
        """Crea una tarjeta interactiva para selección de modo."""
        card = QFrame()
        card.setObjectName("cardFrame")
        card.setStyleSheet("""
            QFrame#cardFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 14px;
                padding: 16px;
            }
            QFrame#cardFrame:hover {
                border: 1px solid #00d2ff;
                background-color: #1a202c;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        badge_lbl = QLabel(badge)
        badge_lbl.setStyleSheet("""
            color: #00d2ff;
            background-color: #0d1e2e;
            border: 1px solid #005f73;
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 10px;
            font-weight: 800;
        """)
        top_row.addWidget(badge_lbl)
        top_row.addStretch()

        num_lbl = QLabel(f"[{mode_number}]")
        num_lbl.setStyleSheet("color: #8b949e; font-size: 14px; font-weight: 700;")
        top_row.addWidget(num_lbl)
        layout.addLayout(top_row)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #f0f6fc; font-size: 17px; font-weight: 700;")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("color: #8b949e; font-size: 12px; line-height: 1.4;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        layout.addStretch()

        btn = QPushButton(button_text)
        btn.setProperty("class", "primaryButton")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(on_click)
        layout.addWidget(btn)

        return card
