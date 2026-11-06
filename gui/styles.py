"""
styles.py
=========
Hoja de estilos CSS / QSS moderna, sobria y minimalista con estética de ingeniería.
Tema grafito oscuro (#0e1117, #161b22) con acentos cian (#00d2ff) y azul cobalto (#3b82f6).
"""

MAIN_STYLE_SHEET = """
/* Ventana y contenedores generales */
QMainWindow, QWidget#centralWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
    font-size: 13px;
}

QWidget {
    color: #e6edf3;
}

/* Encabezados y etiquetas */
QLabel {
    color: #e6edf3;
}

QLabel#titleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #58a6ff;
    letter-spacing: 0.5px;
}

QLabel#subTitleLabel {
    font-size: 13px;
    color: #8b949e;
}

QLabel#institutionHeader {
    font-size: 18px;
    font-weight: 800;
    color: #f0f6fc;
    letter-spacing: 1px;
}

QLabel#institutionSubHeader {
    font-size: 12px;
    color: #00d2ff;
    font-weight: 600;
}

/* Tarjetas y Paneles */
QFrame.cardFrame {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
}

QFrame.cardFrame:hover {
    border: 1px solid #58a6ff;
}

QFrame.heroCard {
    background-color: #161b22;
    border: 2px solid #00d2ff;
    border-radius: 14px;
}

/* Botones principales */
QPushButton {
    background-color: #21262d;
    color: #f0f6fc;
    border: 1px solid #363b42;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton.primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0077b6, stop:1 #0096c7);
    color: #ffffff;
    border: 1px solid #00b4d8;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 700;
}

QPushButton.primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0096c7, stop:1 #00b4d8);
    border-color: #90e0ef;
}

QPushButton.navButton {
    background-color: transparent;
    color: #8b949e;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
}

QPushButton.navButton:hover {
    background-color: #21262d;
    color: #58a6ff;
    border-color: #58a6ff;
}

QPushButton.dangerButton {
    background-color: #21262d;
    color: #f85149;
    border: 1px solid #da3633;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
}

QPushButton.dangerButton:hover {
    background-color: #da3633;
    color: #ffffff;
}

/* Botones de Iconos SVG Minimalistas */
QPushButton.iconButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 9px;
    padding: 0px;
}

QPushButton.iconButton:hover {
    background-color: #30363d;
    border-color: #00d2ff;
}

QPushButton.iconButton:pressed {
    background-color: #161b22;
}

QPushButton.iconButtonDanger {
    background-color: #21262d;
    border: 1px solid #482326;
    border-radius: 9px;
    padding: 0px;
}

QPushButton.iconButtonDanger:hover {
    background-color: #3e1b1e;
    border-color: #f85149;
}

QPushButton.iconButtonDanger:pressed {
    background-color: #2a1215;
}

/* Barras de progreso */
QProgressBar {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 5px;
    height: 8px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0077b6, stop:1 #00d2ff);
    border-radius: 4px;
}

/* ScrollArea */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    background-color: #0d1117;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #58a6ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tooltips */
QToolTip {
    background-color: #161b22;
    color: #f0f6fc;
    border: 1px solid #58a6ff;
    border-radius: 6px;
    padding: 6px;
    font-size: 12px;
}
"""
