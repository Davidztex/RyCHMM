"""
ranking_panel.py
================
Panel derecho interactivo de clasificación probabilística en tiempo real.
Muestra el listado ordenado descendentemente según P(Carácter | O_{1:t}),
con tarjeta destacada Top-1, barras de progreso y miniaturas de referencia de las 27 letras.
"""

import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QScrollArea, QFrame, QSizePolicy
)

from engine.hmm_engine import SPANISH_ALPHABET


class LetterRowWidget(QFrame):
    """Fila visual individual para una letra en la lista de clasificación."""

    def __init__(self, char, icons_dir, parent=None):
        super().__init__(parent)
        self.char = char
        self.icons_dir = icons_dir

        self.setFixedHeight(48)
        self.setStyleSheet("""
            LetterRowWidget {
                background-color: #161b22;
                border: 1px solid #21262d;
                border-radius: 8px;
                padding: 2px 8px;
            }
            LetterRowWidget:hover {
                background-color: #21262d;
                border-color: #388bfd;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # 1. Badge con el número de ranking
        self.rank_label = QLabel("#--")
        self.rank_label.setFixedWidth(28)
        self.rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rank_label.setStyleSheet("color: #8b949e; font-weight: 700; font-size: 11px;")
        layout.addWidget(self.rank_label)

        # 2. Icono/miniatura estática de referencia
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setScaledContents(True)
        self._load_icon()
        layout.addWidget(self.icon_label)

        # 3. Glifo / Nombre del carácter
        self.char_label = QLabel(self.char)
        self.char_label.setFixedWidth(24)
        self.char_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Segoe UI", 15, QFont.Weight.Bold)
        self.char_label.setFont(font)
        self.char_label.setStyleSheet("color: #f0f6fc;")
        layout.addWidget(self.char_label)

        # 4. Barra de progreso visual estilizada
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.progress_bar)

        # 5. Valor numérico de probabilidad y porcentaje
        self.value_label = QLabel("0.0%")
        self.value_label.setFixedWidth(56)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value_label.setStyleSheet("color: #58a6ff; font-weight: 600; font-size: 12px;")
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
            self.icon_label.setStyleSheet("background-color: #21262d; border-radius: 6px; color: #58a6ff; font-weight: bold;")

    def update_data(self, rank, prob, percentage, log_lik):
        """Actualiza los valores visuales de la fila."""
        self.rank_label.setText(f"#{rank}")
        val = int(prob * 1000)
        self.progress_bar.setValue(max(0, min(1000, val)))
        self.value_label.setText(percentage)

        # Resaltado especial si está en el top 3
        if rank == 1:
            self.rank_label.setStyleSheet("color: #00d2ff; font-weight: 800; font-size: 12px;")
            self.value_label.setStyleSheet("color: #00d2ff; font-weight: 700; font-size: 13px;")
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0077b6, stop:1 #00d2ff);
                    border-radius: 4px;
                }
            """)
        elif rank <= 3:
            self.rank_label.setStyleSheet("color: #58a6ff; font-weight: 700; font-size: 11px;")
            self.value_label.setStyleSheet("color: #58a6ff; font-weight: 600; font-size: 12px;")
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1f6feb, stop:1 #58a6ff);
                    border-radius: 4px;
                }
            """)
        else:
            self.rank_label.setStyleSheet("color: #8b949e; font-weight: 600; font-size: 11px;")
            self.value_label.setStyleSheet("color: #8b949e; font-weight: 500; font-size: 12px;")
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #30363d;
                    border-radius: 4px;
                }
            """)

        self.setToolTip(f"Carácter: '{self.char}'\nProbabilidad P: {prob:.4f} ({percentage})\nLog-Verosimilitud ln P: {log_lik:.2f}")


class RankingPanel(QWidget):
    """
    Panel vertical de clasificación en tiempo real según P(Carácter | O_{1:t}).
    Incluye Hero Card para el candidato Top-1 y lista scrollable de las 27 letras.
    """

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
        main_layout.setSpacing(12)

        # 1. Cabecera del Panel
        header_widget = QWidget()
        h_layout = QVBoxLayout(header_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(2)

        title = QLabel("CLASIFICACIÓN Y PROBABILIDADES")
        title.setStyleSheet("color: #58a6ff; font-size: 12px; font-weight: 800; letter-spacing: 0.8px;")
        h_layout.addWidget(title)

        subtitle = QLabel("Evaluación Forward en Tiempo Real: P(C | O1:t)")
        subtitle.setStyleSheet("color: #8b949e; font-size: 11px;")
        h_layout.addWidget(subtitle)

        main_layout.addWidget(header_widget)

        # 2. Tarjeta Destacada Top-1 (Hero Card)
        self.hero_card = QFrame()
        self.hero_card.setObjectName("heroCard")
        self.hero_card.setFixedHeight(105)
        self.hero_card.setStyleSheet("""
            QFrame#heroCard {
                background-color: #161b22;
                border: 2px solid #00d2ff;
                border-radius: 12px;
            }
        """)
        hero_layout = QHBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(14, 10, 14, 10)
        hero_layout.setSpacing(12)

        # Icono Top-1
        self.hero_icon = QLabel()
        self.hero_icon.setFixedSize(64, 64)
        self.hero_icon.setScaledContents(True)
        self.hero_icon.setStyleSheet("border-radius: 10px; background-color: #21262d;")
        hero_layout.addWidget(self.hero_icon)

        # Información central Top-1
        hero_info = QVBoxLayout()
        hero_info.setSpacing(2)
        hero_info.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        badge_top1 = QLabel("TOP-1 CANDIDATO ESTIMADO")
        badge_top1.setStyleSheet("color: #00d2ff; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;")
        hero_info.addWidget(badge_top1)

        self.hero_char_label = QLabel("Esperando trazo...")
        self.hero_char_label.setStyleSheet("color: #f0f6fc; font-size: 20px; font-weight: 800;")
        hero_info.addWidget(self.hero_char_label)

        self.hero_details_label = QLabel("Dibuje en el lienzo para clasificar")
        self.hero_details_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        hero_info.addWidget(self.hero_details_label)

        hero_layout.addLayout(hero_info)
        hero_layout.addStretch()

        # Porcentaje grande
        self.hero_prob_label = QLabel("0.0%")
        self.hero_prob_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.hero_prob_label.setStyleSheet("color: #00d2ff; font-size: 24px; font-weight: 900;")
        hero_layout.addWidget(self.hero_prob_label)

        main_layout.addWidget(self.hero_card)

        # 3. ScrollArea con el listado ordenado descendente
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_widget = QWidget()
        self.rows_layout = QVBoxLayout(self.scroll_widget)
        self.rows_layout.setContentsMargins(2, 2, 6, 2)
        self.rows_layout.setSpacing(6)

        # Crear filas para las 27 letras del alfabeto español
        self.row_widgets = {}
        for char in SPANISH_ALPHABET:
            row = LetterRowWidget(char, self.icons_dir, self)
            self.row_widgets[char] = row
            self.rows_layout.addWidget(row)

        self.rows_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

    def reset_display(self):
        """Reinicia el panel al estado inicial con distribución uniforme."""
        self.hero_char_label.setText("Esperando trazo...")
        self.hero_prob_label.setText("0.0%")
        self.hero_details_label.setText("Dibuje en el lienzo para clasificar")
        self.hero_icon.clear()

        unif = 1.0 / len(self.row_widgets)
        for idx, (ch, row) in enumerate(self.row_widgets.items(), start=1):
            row.update_data(rank=idx, prob=unif, percentage=f"{unif*100:.1f}%", log_lik=0.0)

    def update_ranking(self, classification_results):
        """
        Recibe la lista de 27 resultados ordenados y actualiza la GUI sin parpadeos.
        """
        if not classification_results:
            self.reset_display()
            return

        # 1. Actualizar Hero Card con Top-1
        top1 = classification_results[0]
        top_char = top1["char"]
        top_prob = top1["probability"]
        top_perc = top1["percentage"]
        top_ll = top1["log_likelihood"]

        self.hero_char_label.setText(f"Letra '{top_char}'")
        self.hero_prob_label.setText(top_perc)
        self.hero_details_label.setText(f"Prob: {top_prob:.4f}  |  ln P: {top_ll:.1f}")

        # Cargar icono de la letra Top-1
        safe_name = f"char_{ord(top_char)}.png" if ord(top_char) > 127 else f"{top_char}.png"
        icon_path = os.path.join(self.icons_dir, safe_name)
        if not os.path.exists(icon_path) and top_char == 'ñ':
            icon_path = os.path.join(self.icons_dir, "nn.png")
        if os.path.exists(icon_path):
            self.hero_icon.setPixmap(QPixmap(icon_path))

        # 2. Reorganizar las filas en orden descendente y actualizar datos
        # Desconectar temporalmente para reordenamiento rápido
        for res in classification_results:
            ch = res["char"]
            row = self.row_widgets.get(ch)
            if row:
                row.update_data(
                    rank=res["rank"],
                    prob=res["probability"],
                    percentage=res["percentage"],
                    log_lik=res["log_likelihood"]
                )
                # Mover el widget a su nueva posición en el layout vertical
                self.rows_layout.removeWidget(row)
                self.rows_layout.insertWidget(res["rank"] - 1, row)
