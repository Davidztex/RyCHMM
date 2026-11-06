"""
menu_view.py
============
Ventana A: Menú Principal de Inicio.
Pantalla de bienvenida institucional (Universidad de los Llanos).
Diseño moderno y limpio:
- Encabezado institucional sin bordes restrictivos.
- Tarjetas interactivas de modo (2D y 3D) que actúan directamente como botones de acceso.
- Imágenes descriptivas con relación de aspecto estricta (AspectRatioMode.KeepAspectRatio).
"""

import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)


class AspectRatioImage(QLabel):
    """
    Widget que renderiza la imagen manteniendo rigurosamente su relación de aspecto original
    (KeepAspectRatio) con filtrado bilineal suave (SmoothTransformation), evitando cualquier
    deformación o estiramiento.
    """

    def __init__(self, image_path=None, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(185)
        self.setStyleSheet("border-radius: 10px; border: 1px solid #21262d; background-color: #0d1117;")
        self._orig_pixmap = None

        if image_path and os.path.exists(image_path):
            self._orig_pixmap = QPixmap(image_path)
            self._apply_scaled_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_scaled_pixmap()

    def _apply_scaled_pixmap(self):
        if self._orig_pixmap and not self._orig_pixmap.isNull():
            w = max(20, self.width() - 8)
            h = max(20, self.height() - 8)
            scaled = self._orig_pixmap.scaled(
                w, h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            super().setPixmap(scaled)


class ClickableModeCard(QFrame):
    """
    Recuadro interactivo de selección de modo que actúa directamente como botón al hacer clic.
    """
    clicked = pyqtSignal()

    def __init__(self, mode_number, title, badge_text, image_path, description, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.setStyleSheet("""
            ClickableModeCard {
                background-color: #161b22;
                border: 2px solid #30363d;
                border-radius: 16px;
                padding: 16px;
            }
            ClickableModeCard:hover {
                border: 2px solid #00d2ff;
                background-color: #1c2330;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 18)
        layout.setSpacing(12)

        # 1. Cabecera de la tarjeta: Badge + Número
        top_row = QHBoxLayout()
        badge_lbl = QLabel(badge_text)
        badge_lbl.setStyleSheet("""
            color: #00d2ff;
            background-color: #0d1e2e;
            border: 1px solid #005f73;
            border-radius: 6px;
            padding: 3px 10px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.5px;
        """)
        top_row.addWidget(badge_lbl)
        top_row.addStretch()

        num_lbl = QLabel(f"[{mode_number}]")
        num_lbl.setStyleSheet("color: #8b949e; font-size: 15px; font-weight: 700;")
        top_row.addWidget(num_lbl)
        layout.addLayout(top_row)

        # 2. Imagen descriptiva con relación de aspecto preservada
        self.image_widget = AspectRatioImage(image_path, parent=self)
        layout.addWidget(self.image_widget)

        # 3. Título del modo
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #f0f6fc; font-size: 18px; font-weight: 800; margin-top: 4px;")
        layout.addWidget(title_lbl)

        # 4. Descripción breve de capacidades
        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("color: #8b949e; font-size: 12px; line-height: 1.4;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        layout.addStretch()

        # 5. Indicador interactivo de clic
        click_hint = QLabel("▶ Haga clic para ingresar al modo")
        click_hint.setStyleSheet("""
            color: #00d2ff;
            font-size: 12px;
            font-weight: 700;
            padding-top: 6px;
        """)
        click_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(click_hint)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class MenuView(QWidget):
    """
    Vista de bienvenida institucional con selector de modos 2D y 3D en recuadros interactivos.
    """

    navigate_to_2d = pyqtSignal()
    navigate_to_3d = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        ui_dir = os.path.join(base_dir, "data", "icons", "ui")
        img_2d = os.path.join(ui_dir, "preview_2d.png")
        img_3d = os.path.join(ui_dir, "preview_3d.png")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 25, 40, 25)
        main_layout.setSpacing(22)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---------------------------------------------------------
        # 1. Encabezado Institucional LIMPIO Y SIN BORDERLINE
        # ---------------------------------------------------------
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent; border: none;")
        h_layout = QVBoxLayout(header_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(5)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_univ = QLabel("UNIVERSIDAD DE LOS LLANOS")
        lbl_univ.setStyleSheet("color: #f0f6fc; font-size: 21px; font-weight: 900; letter-spacing: 1.5px;")
        lbl_univ.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(lbl_univ)

        lbl_fac = QLabel("FACULTAD DE CIENCIAS BÁSICAS E INGENIERÍA — PROGRAMA DE INGENIERÍA DE SISTEMAS")
        lbl_fac.setStyleSheet("color: #00d2ff; font-size: 12px; font-weight: 700; letter-spacing: 0.8px;")
        lbl_fac.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(lbl_fac)

        lbl_proj_title = QLabel("Reconocedor y Clasificador de Caracteres en Tiempo Real 2D/3D mediante HMM")
        lbl_proj_title.setStyleSheet("color: #58a6ff; font-size: 16px; font-weight: 800; margin-top: 6px;")
        lbl_proj_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(lbl_proj_title)

        main_layout.addWidget(header_widget)

        # ---------------------------------------------------------
        # 2. Recuadros Interactivos como Botones de Acceso (2D y 3D)
        # ---------------------------------------------------------
        modes_layout = QHBoxLayout()
        modes_layout.setSpacing(28)

        # Recuadro Interactivo Modo 2D
        self.card_2d = ClickableModeCard(
            mode_number="1",
            title="Modo 2D: Plano Cartesiano",
            badge_text="BIDIMENSIONAL",
            image_path=img_2d,
            description=(
                "Trazado continuo en plano cartesiano bidimensional.\n"
                "• Remuestreo espacial equidistante (longitud de arco).\n"
                "• Cuantización angular en K = 16 sectores (código de cadena).\n"
                "• Autocompletado espacial dinámico de la trayectoria futura."
            ),
            parent=self
        )
        self.card_2d.clicked.connect(self.navigate_to_2d.emit)
        modes_layout.addWidget(self.card_2d)

        # Recuadro Interactivo Modo 3D
        self.card_3d = ClickableModeCard(
            mode_number="2",
            title="Modo 3D: Superficie Esférica",
            badge_text="TRIDIMENSIONAL (OPENGL)",
            image_path=img_3d,
            description=(
                "Trazado sobre la superficie de una esfera 3D interactiva.\n"
                "• Renderizado acelerado por hardware con PyOpenGL.\n"
                "• Medición de variaciones angulares tangenciales (Δθ, Δϕ).\n"
                "• Proyección geodésica dinámica sobre el cascarón esférico."
            ),
            parent=self
        )
        self.card_3d.clicked.connect(self.navigate_to_3d.emit)
        modes_layout.addWidget(self.card_3d)

        main_layout.addLayout(modes_layout)
