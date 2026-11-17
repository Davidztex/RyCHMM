"""
styles.py
=========
Hoja de estilos QSS — Tema claro.
Fondo #FFFFFE (blanco puro), texto negro, botones azul #1565C0 con texto blanco.
"""

MAIN_STYLE_SHEET = """
/* Ventana y contenedores generales */
QMainWindow, QWidget#centralWidget {
    background-color: #FFFFFE;
    color: #111111;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: #FFFFFE;
    color: #111111;
}

/* Encabezados y etiquetas */
QLabel {
    color: #111111;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #1565C0;
    letter-spacing: 0.5px;
    background-color: transparent;
}

QLabel#subTitleLabel {
    font-size: 13px;
    color: #555555;
    background-color: transparent;
}

QLabel#institutionHeader {
    font-size: 18px;
    font-weight: 800;
    color: #111111;
    letter-spacing: 1px;
    background-color: transparent;
}

QLabel#institutionSubHeader {
    font-size: 12px;
    color: #1565C0;
    font-weight: 600;
    background-color: transparent;
}

/* Tarjetas y Paneles */
QFrame.cardFrame {
    background-color: #F5F7FF;
    border: 1px solid #BBCDE5;
    border-radius: 12px;
}

QFrame.cardFrame:hover {
    border: 1px solid #1565C0;
}

QFrame.heroCard {
    background-color: #EAF0FB;
    border: 2px solid #1565C0;
    border-radius: 14px;
}

/* ── Botones principales (todos con fondo azul y texto blanco) ── */
QPushButton {
    background-color: #1565C0;
    color: #FFFFFE;
    border: 1px solid #0D47A1;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1976D2;
    border-color: #1565C0;
    color: #FFFFFE;
}

QPushButton:pressed {
    background-color: #0D47A1;
    color: #FFFFFE;
}

QPushButton:disabled {
    background-color: #B0BEC5;
    color: #FFFFFE;
    border-color: #90A4AE;
}

QPushButton.primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0D47A1, stop:1 #1565C0);
    color: #FFFFFE;
    border: 1px solid #1565C0;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 700;
}

QPushButton.primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1565C0, stop:1 #1976D2);
    border-color: #42A5F5;
}

QPushButton.navButton {
    background-color: #1565C0;
    color: #FFFFFE;
    border: 1px solid #0D47A1;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton.navButton:hover {
    background-color: #1976D2;
    color: #FFFFFE;
    border-color: #42A5F5;
}

QPushButton.dangerButton {
    background-color: #C62828;
    color: #FFFFFE;
    border: 1px solid #B71C1C;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton.dangerButton:hover {
    background-color: #D32F2F;
    color: #FFFFFE;
}

/* Botones de Iconos (sin texto visible — solo icono) */
QPushButton.iconButton {
    background-color: #1565C0;
    border: 1px solid #0D47A1;
    border-radius: 9px;
    padding: 0px;
}

QPushButton.iconButton:hover {
    background-color: #1976D2;
    border-color: #42A5F5;
}

QPushButton.iconButton:pressed {
    background-color: #0D47A1;
}

QPushButton.iconButtonDanger {
    background-color: #C62828;
    border: 1px solid #B71C1C;
    border-radius: 9px;
    padding: 0px;
}

QPushButton.iconButtonDanger:hover {
    background-color: #D32F2F;
    border-color: #EF9A9A;
}

QPushButton.iconButtonDanger:pressed {
    background-color: #B71C1C;
}

/* Barras de progreso */
QProgressBar {
    background-color: #E3EAF8;
    border: 1px solid #BBCDE5;
    border-radius: 5px;
    height: 8px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1565C0, stop:1 #42A5F5);
    border-radius: 4px;
}

/* ScrollArea */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    background-color: #EEF0F4;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #BBCDE5;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #1565C0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tooltips */
QToolTip {
    background-color: #1565C0;
    color: #FFFFFE;
    border: 1px solid #0D47A1;
    border-radius: 6px;
    padding: 6px;
    font-size: 12px;
}
"""
