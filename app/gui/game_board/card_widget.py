from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QDrag, QPixmap

class DraggableCardWidget(QLabel):
    """Widget für eine spielbare Karte mit Drag & Drop Funktionalität"""
    
    def __init__(self, card_data, parent=None):
        super().__init__(parent)
        self.card_data = card_data
        self.setAcceptDrops(True)
        
        # Setze das Kartenbild
        self.setPixmap(QPixmap(card_data['image_path']))
        self.setScaledContents(True)
        self.setFixedSize(63, 88)  # Standard MTG Kartengröße im Scale 1:4
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = self.card_data
            drag.setMimeData(mime_data)
            drag.exec_(Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-card'):
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        # Hier implementieren wir später die Logik für das Ablegen von Karten
        pass