"""
ranking_panel.py
================
Panel derecho de clasificación probabilística en tiempo real.
Muestra el candidato más probable (#1) en una tarjeta destacada grande ("Hero Card"),
y a continuación el listado ordenado descendentemente iniciando desde el #2, #3... #27,
eliminando toda redundancia y como filas informativas no cliqueables.
"""

import os
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QScrollArea, QFrame, QSizePolicy
)

from engine.hmm_engine import SPANISH_ALPHABET


class Top1HeroCard(QFrame):
    """
    Tarjeta destacada grande para la letra más probable (#1).
    Proporciona máxima visibilidad con glifo grande, icono, porcentaje y barra de progreso.
    """

    def __init__(self, icons_dir, parent=None):
        super().__init__(parent)
        self.icons_dir = icons_dir
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self.setObjectName("heroCard")
        self.setFixedHeight(100)
        self.setStyleSheet("""
            QFrame#heroCard {
                background-color: #EEF2FF;
                border: 2px solid #1565C0;
                border-radius: 12px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        # 1. Icono / miniatura grande
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(60, 60)
        self.icon_label.setScaledContents(True)
        self.icon_label.setStyleSheet("border-radius: 10px; background-color: #E0E8FF;")
        layout.addWidget(self.icon_label)

        # 2. Información central (#1, Letra, Detalles)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.badge_label = QLabel("#1 MÁS PROBABLE")
        self.badge_label.setStyleSheet("color: #1565C0; font-size: 11px; font-weight: 800; letter-spacing: 0.6px;")
        info_layout.addWidget(self.badge_label)

        self.char_label = QLabel("Esperando trazo...")
        self.char_label.setStyleSheet("color: #0D47A1; font-size: 21px; font-weight: 900;")
        info_layout.addWidget(self.char_label)

        self.details_label = QLabel("Dibuje en el lienzo para clasificar")
        self.details_label.setStyleSheet("color: #555555; font-size: 11px;")
        info_layout.addWidget(self.details_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # 3. Columna derecha: Porcentaje grande y barra de progreso
        right_layout = QVBoxLayout()
        right_layout.setSpacing(4)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.prob_label = QLabel("0.0%")
        self.prob_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.prob_label.setStyleSheet("color: #1565C0; font-size: 24px; font-weight: 900;")
        right_layout.addWidget(self.prob_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedSize(90, 8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #D6E4FF;
                border: 1px solid #BBCDE5;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D47A1, stop:1 #1565C0);
                border-radius: 3px;
            }
        """)
        right_layout.addWidget(self.progress_bar)

        layout.addLayout(right_layout)

    def set_data(self, char, prob, percentage, log_lik):
        """Actualiza los datos visuales de la letra ganadora."""
        self.badge_label.setText("#1 MÁS PROBABLE")
        self.char_label.setText(f"Letra '{char}'")
        self.prob_label.setText(percentage)
        self.details_label.setText(f"Prob: {prob:.4f}  |  ln P: {log_lik:.1f}")
        self.progress_bar.setValue(int(prob * 1000))

        # Cargar icono
        safe_name = f"char_{ord(char)}.png" if ord(char) > 127 else f"{char}.png"
        icon_path = os.path.join(self.icons_dir, safe_name)
        if not os.path.exists(icon_path) and char == 'ñ':
            icon_path = os.path.join(self.icons_dir, "nn.png")
        if os.path.exists(icon_path):
            self.icon_label.setPixmap(QPixmap(icon_path))
        else:
            self.icon_label.setText(char)
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.icon_label.setStyleSheet("background-color: #E0E8FF; border-radius: 10px; color: #1565C0; font-size: 24px; font-weight: bold;")

    def reset_display(self):
        """Restablece al estado inicial."""
        self.badge_label.setText("#1 MÁS PROBABLE")
        self.char_label.setText("Esperando trazo...")
        self.prob_label.setText("0.0%")
        self.details_label.setText("Dibuje en el lienzo para clasificar")
        self.icon_label.clear()
        self.progress_bar.setValue(0)

    def mousePressEvent(self, event):
        event.accept()


class LetterRowWidget(QFrame):
    """
    Fila visual informativa para una letra (puestos #2 al #27).
    No es un botón interactivo para evitar clics accidentales.
    """

    def __init__(self, char, icons_dir, parent=None):
        super().__init__(parent)
        self.char = char
        self.icons_dir = icons_dir
        self.setCursor(Qt.CursorShape.ArrowCursor)

        self.setFixedHeight(46)
        self.setStyleSheet("""
            LetterRowWidget {
                background-color: #F8FAFD;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 2px 8px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 3, 10, 3)
        layout.setSpacing(10)

        # 1. Badge con el número de ranking (#2, #3, ...)
        self.rank_label = QLabel("#--")
        self.rank_label.setFixedWidth(32)
        self.rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rank_label.setStyleSheet("color: #64748B; font-weight: 700; font-size: 11px;")
        layout.addWidget(self.rank_label)

        # 2. Icono/miniatura estática
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(30, 30)
        self.icon_label.setScaledContents(True)
        self._load_icon()
        layout.addWidget(self.icon_label)

        # 3. Glifo / Nombre del carácter
        self.char_label = QLabel(self.char)
        self.char_label.setFixedWidth(24)
        self.char_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Segoe UI", 15, QFont.Weight.Bold)
        self.char_label.setFont(font)
        self.char_label.setStyleSheet("color: #111111;")
        layout.addWidget(self.char_label)

        # 4. Barra de progreso visual
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.progress_bar)

        # 5. Porcentaje
        self.value_label = QLabel("0.0%")
        self.value_label.setFixedWidth(60)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value_label.setStyleSheet("color: #555555; font-weight: 600; font-size: 12px;")
        layout.addWidget(self.value_label)

    def _load_icon(self):
        """Carga la imagen PNG de referencia desde el directorio de iconos."""
        safe_name = f"char_{ord(self.char)}.png" if ord(self.char) > 127 else f"{self.char}.png"
        icon_path = os.path.join(self.icons_dir, safe_name)
        if not os.path.exists(icon_path) and self.char == 'ñ':
            icon_path = os.path.join(self.icons_dir, "nn.png")

        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText(self.char)
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.icon_label.setStyleSheet("background-color: #E0E8FF; border-radius: 6px; color: #1565C0; font-weight: bold;")

    def update_data(self, rank, prob, percentage, log_lik):
        """Actualiza los valores visuales de la fila."""
        self.rank_label.setText(f"#{rank}")
        val = int(prob * 1000)
        self.progress_bar.setValue(max(0, min(1000, val)))
        self.value_label.setText(percentage)

        if rank <= 3:
            self.setStyleSheet("""
                LetterRowWidget {
                    background-color: #F0F4FC;
                    border: 1px solid #90B4E2;
                    border-radius: 8px;
                    padding: 2px 8px;
                }
            """)
            self.rank_label.setStyleSheet("color: #1565C0; font-weight: 700; font-size: 11px;")
            self.char_label.setStyleSheet("color: #111111; font-weight: 700; font-size: 15px;")
            self.value_label.setStyleSheet("color: #1565C0; font-weight: 700; font-size: 12px;")
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1976D2, stop:1 #42A5F5);
                    border-radius: 4px;
                }
            """)
        else:
            self.setStyleSheet("""
                LetterRowWidget {
                    background-color: #F8FAFD;
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                    padding: 2px 8px;
                }
            """)
            self.rank_label.setStyleSheet("color: #64748B; font-weight: 600; font-size: 11px;")
            self.char_label.setStyleSheet("color: #334155; font-weight: 600; font-size: 14px;")
            self.value_label.setStyleSheet("color: #64748B; font-weight: 500; font-size: 11px;")
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #CBD5E1;
                    border-radius: 4px;
                }
            """)

        self.setToolTip(f"Carácter: '{self.char}'\nProbabilidad P: {prob:.4f} ({percentage})\nLog-Verosimilitud ln P: {log_lik:.2f}")

    def mousePressEvent(self, event):
        event.accept()


class RankingPanel(QWidget):
    """
    Panel vertical de clasificación en tiempo real según P(Carácter | O_{1:t}).
    - Recuadro superior grande (Hero Card) para la letra más probable (#1).
    - Lista scrollable directamente debajo, iniciando desde la segunda (#2) hasta la #27.
    """

    letter_selected = pyqtSignal(str)

    def __init__(self, icons_dir=None, parent=None):
        super().__init__(parent)
        if icons_dir is None:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            icons_dir = os.path.join(base, "data", "icons")
        self.icons_dir = icons_dir

        self.setMinimumWidth(320)
        self.setMaximumWidth(400)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. Cabecera del Panel
        header_widget = QWidget()
        h_layout = QVBoxLayout(header_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(3)

        title = QLabel("CLASIFICACIÓN Y PROBABILIDADES")
        title.setStyleSheet("color: #1565C0; font-size: 13px; font-weight: 800; letter-spacing: 0.8px;")
        h_layout.addWidget(title)

        subtitle = QLabel("Evaluación Forward en Tiempo Real: P(C | O1:t)")
        subtitle.setStyleSheet("color: #555555; font-size: 11px;")
        h_layout.addWidget(subtitle)

        main_layout.addWidget(header_widget)

        # 2. Recuadro destacado grande para la letra más probable (#1)
        self.hero_card = Top1HeroCard(self.icons_dir, self)
        main_layout.addWidget(self.hero_card)

        # 3. ScrollArea con el listado de las demás letras (inicia en #2)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)

        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: #FFFFFE;")
        self.rows_layout = QVBoxLayout(self.scroll_widget)
        self.rows_layout.setContentsMargins(6, 6, 6, 6)
        self.rows_layout.setSpacing(6)

        # Crear filas para las 27 letras del alfabeto español
        self.row_widgets = {}
        for char in SPANISH_ALPHABET:
            row = LetterRowWidget(char, self.icons_dir, self)
            self.row_widgets[char] = row
            self.rows_layout.addWidget(row)

        self.rows_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area, stretch=1)

    def reset_display(self):
        """Reinicia el panel al estado inicial con distribución uniforme."""
        self.hero_card.reset_display()
        unif = 1.0 / len(self.row_widgets)
        # Mostrar filas desde #2 en adelante (la primera se queda en el hero)
        for idx, (ch, row) in enumerate(self.row_widgets.items(), start=1):
            if idx == 1:
                row.setVisible(False)
            else:
                row.setVisible(True)
                row.update_data(rank=idx, prob=unif, percentage=f"{unif*100:.1f}%", log_lik=0.0)

    def update_ranking(self, classification_results):
        """
        Recibe la lista de 27 resultados ordenados:
        - El puesto #1 (la más probable) se coloca en la tarjeta destacada grande.
        - Los puestos del #2 al #27 se listan en el scrollarea en orden descendente.
        Sin duplicar el puesto #1 en la lista inferior.
        """
        if not classification_results:
            self.reset_display()
            return

        # 1. Candidato #1: actualiza la tarjeta destacada grande
        top1 = classification_results[0]
        self.hero_card.set_data(
            char=top1["char"],
            prob=top1["probability"],
            percentage=top1["percentage"],
            log_lik=top1["log_likelihood"]
        )

        # Ocultar la fila correspondiente al #1 dentro de la lista scrollable para no duplicarla
        top1_row = self.row_widgets.get(top1["char"])
        if top1_row:
            top1_row.setVisible(False)

        # 2. Candidatos restantes (#2 al #27): mostrar y reordenar en la lista
        remaining = classification_results[1:]
        for idx, res in enumerate(remaining):
            ch = res["char"]
            row = self.row_widgets.get(ch)
            if row:
                row.setVisible(True)
                row.update_data(
                    rank=res["rank"],
                    prob=res["probability"],
                    percentage=res["percentage"],
                    log_lik=res["log_likelihood"]
                )
                self.rows_layout.removeWidget(row)
                self.rows_layout.insertWidget(idx, row)
