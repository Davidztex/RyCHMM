"""
main_window.py
==============
Ventana principal de la aplicación de escritorio en PyQt6.
Administra la navegación fluida entre las 3 vistas principales
(Menú Principal, Modo 2D y Modo 3D) mediante un QStackedWidget central.
"""

import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QStatusBar, QLabel
)

from gui.styles import MAIN_STYLE_SHEET
from gui.views.menu_view import MenuView
from gui.views.recognizer_2d_view import Recognizer2DView
from gui.views.recognizer_3d_view import Recognizer3DView


class MainWindow(QMainWindow):
    """
    Ventana contenedora principal con gestión de vistas apiladas.
    """

    def __init__(self, classifier, icons_dir=None, parent=None):
        super().__init__(parent)
        self.classifier = classifier
        self.icons_dir = icons_dir

        self.setWindowTitle("Reconocedor y Clasificador de caracteres en tiempo real")
        self.resize(1280, 840)
        self.setMinimumSize(1024, 680)

        # Aplicar hoja de estilos institucional moderna
        self.setStyleSheet(MAIN_STYLE_SHEET)

        # Widget central con QStackedWidget
        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)

        # Instanciar las 3 vistas
        self.menu_view = MenuView(self)
        self.view_2d = Recognizer2DView(self.classifier, icons_dir=self.icons_dir, parent=self)
        self.view_3d = Recognizer3DView(self.classifier, icons_dir=self.icons_dir, parent=self)

        # Añadir al stack
        self.stack.addWidget(self.menu_view)     # Índice 0
        self.stack.addWidget(self.view_2d)       # Índice 1
        self.stack.addWidget(self.view_3d)       # Índice 2

        # Conectar señales de navegación
        self.menu_view.navigate_to_2d.connect(self.go_to_2d)
        self.menu_view.navigate_to_3d.connect(self.go_to_3d)
        self.view_2d.navigate_to_menu.connect(self.go_to_menu)
        self.view_3d.navigate_to_menu.connect(self.go_to_menu)

        # Barra de estado inferior
        self._init_status_bar()

    def _init_status_bar(self):
        status_bar = QStatusBar(self)
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #0d1117;
                color: #8b949e;
                border-top: 1px solid #21262d;
                font-size: 11px;
                padding: 4px 12px;
            }
        """)
        self.setStatusBar(status_bar)

        n_models = len(self.classifier.models)
        self.status_label = QLabel(
            f"✓ Estado: {n_models}/27 Modelos HMM Activos"
        )
        self.status_label.setStyleSheet("color: #00d2ff; font-weight: 600;")
        status_bar.addWidget(self.status_label)

    def go_to_menu(self):
        """Regresa a la vista del Menú Principal."""
        self.stack.setCurrentIndex(0)

    def go_to_2d(self):
        """Cambia a la vista del Reconocedor 2D."""
        self.view_2d.clear_canvas()
        self.stack.setCurrentIndex(1)

    def go_to_3d(self):
        """Cambia a la vista del Reconocedor 3D."""
        self.view_3d.clear_canvas()
        self.stack.setCurrentIndex(2)
