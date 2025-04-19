"""
Karten-Widget für die Magic the Gathering Desktop App.

Dieses Modul definiert ein Widget zur Darstellung von Magic-Karten in der GUI.
"""

import os
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QPixmap, QImage, QPainter, QFont, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QSize, QRect, QPoint, Signal


class CardWidget(QWidget):
    """Widget zur Darstellung einer Magic-Karte."""
    
    # Signale für Nutzerinteraktionen
    clicked = Signal(object)  # Emittiert die Karteninstanz
    double_clicked = Signal(object)  # Emittiert die Karteninstanz
    
    def __init__(self, card_data=None, parent=None, size_factor=1.0):
        """
        Initialisiert das Karten-Widget.
        
        Args:
            card_data (dict, optional): Die Kartendaten.
            parent (QWidget, optional): Das Eltern-Widget.
            size_factor (float, optional): Größenfaktor für die Karte (1.0 = Standardgröße).
        """
        super().__init__(parent)
        
        self.card_data = card_data or {}
        self.size_factor = size_factor
        self.tapped = False
        self.highlighted = False
        self.selected = False
        
        # Standardkartengrößen
        self.card_width = int(63 * size_factor)   # Standardbreite: 63mm
        self.card_height = int(88 * size_factor)  # Standardhöhe: 88mm
        
        # Widget-Größe basierend auf der Kartengröße setzen
        self.setMinimumSize(self.card_width, self.card_height)
        self.setMaximumSize(self.card_width, self.card_height)
        
        # Layout für die Karte
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Label für das Kartenbild
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.image_label)
        
        # Lade das Kartenbild, wenn Daten vorhanden sind
        if card_data:
            self.update_card_data(card_data)
    
    def update_card_data(self, card_data):
        """
        Aktualisiert die Kartendaten und die Anzeige.
        
        Args:
            card_data (dict): Die neuen Kartendaten.
        """
        self.card_data = card_data
        self.update_card_display()
    
    def update_card_display(self):
        """Aktualisiert die Anzeige der Karte basierend auf den aktuellen Daten."""
        if not self.card_data:
            return
        
        # Lade das Kartenbild, wenn ein Pfad vorhanden ist
        if 'image_path' in self.card_data and self.card_data['image_path']:
            self.load_card_image(self.card_data['image_path'])
        else:
            # Erstelle ein einfaches Platzhalterbild für die Karte
            self.create_placeholder_image()
    
    def load_card_image(self, image_path):
        """
        Lädt das Kartenbild aus einer Datei.
        
        Args:
            image_path (str): Der Pfad zum Kartenbild.
        """
        # Prüfe, ob die Bilddatei existiert
        if not os.path.isfile(image_path):
            print(f"Kartenbild nicht gefunden: {image_path}")
            self.create_placeholder_image()
            return
        
        # Lade das Bild und skaliere es
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Fehler beim Laden des Kartenbilds: {image_path}")
            self.create_placeholder_image()
            return
        
        scaled_pixmap = pixmap.scaled(
            self.card_width, 
            self.card_height, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
    
    def create_placeholder_image(self):
        """Erstellt ein einfaches Platzhalterbild für die Karte."""
        # Erstelle ein leeres Bild
        image = QImage(self.card_width, self.card_height, QImage.Format_ARGB32)
        image.fill(Qt.white)
        
        # Erstelle einen Maler für das Bild
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Zeichne einen Rahmen
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.card_width - 2, self.card_height - 2)
        
        # Fülle die Karte je nach Kartentyp mit einer Farbe
        if self.card_data.get('type', '').lower().find('creature') != -1:
            painter.fillRect(2, 2, self.card_width - 4, self.card_height - 4, QColor(200, 200, 200))
        elif self.card_data.get('type', '').lower().find('instant') != -1:
            painter.fillRect(2, 2, self.card_width - 4, self.card_height - 4, QColor(200, 200, 255))
        elif self.card_data.get('type', '').lower().find('sorcery') != -1:
            painter.fillRect(2, 2, self.card_width - 4, self.card_height - 4, QColor(255, 200, 200))
        elif self.card_data.get('type', '').lower().find('land') != -1:
            painter.fillRect(2, 2, self.card_width - 4, self.card_height - 4, QColor(200, 255, 200))
        else:
            painter.fillRect(2, 2, self.card_width - 4, self.card_height - 4, QColor(255, 255, 200))
        
        # Zeichne den Kartennamen
        name = self.card_data.get('name', 'Unbekannte Karte')
        font = QFont('Arial', 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRect(5, 5, self.card_width - 10, 20), Qt.AlignCenter, name)
        
        # Zeichne den Kartentyp
        card_type = self.card_data.get('type', '')
        font = QFont('Arial', 8)
        painter.setFont(font)
        painter.drawText(QRect(5, 30, self.card_width - 10, 20), Qt.AlignCenter, card_type)
        
        # Zeichne den Regeltext
        rules_text = self.card_data.get('rules_text', '')
        font = QFont('Arial', 7)
        painter.setFont(font)
        painter.drawText(QRect(5, 55, self.card_width - 10, self.card_height - 80), Qt.AlignLeft | Qt.TextWordWrap, rules_text)
        
        # Zeichne Power/Toughness für Kreaturen
        if self.card_data.get('type', '').lower().find('creature') != -1:
            power = self.card_data.get('power', '0')
            toughness = self.card_data.get('toughness', '0')
            pt_text = f"{power}/{toughness}"
            font = QFont('Arial', 10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QRect(self.card_width - 30, self.card_height - 25, 25, 20), Qt.AlignRight, pt_text)
        
        # Beende den Maler
        painter.end()
        
        # Erstelle ein Pixmap aus dem Bild und setze es für das Label
        pixmap = QPixmap.fromImage(image)
        self.image_label.setPixmap(pixmap)
    
    def set_tapped(self, tapped):
        """
        Setzt den Tapped-Status der Karte.
        
        Args:
            tapped (bool): Ob die Karte getappt ist.
        """
        if self.tapped != tapped:
            self.tapped = tapped
            self.update()
    
    def set_highlighted(self, highlighted):
        """
        Setzt den Hervorhebungsstatus der Karte.
        
        Args:
            highlighted (bool): Ob die Karte hervorgehoben ist.
        """
        if self.highlighted != highlighted:
            self.highlighted = highlighted
            self.update()
    
    def set_selected(self, selected):
        """
        Setzt den Auswahlstatus der Karte.
        
        Args:
            selected (bool): Ob die Karte ausgewählt ist.
        """
        if self.selected != selected:
            self.selected = selected
            self.update()
    
    def paintEvent(self, event):
        """
        Ereignisbehandlung für das Zeichnen des Widgets.
        
        Args:
            event (QPaintEvent): Das Zeichenereignis.
        """
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Zeichne einen Rahmen, wenn die Karte hervorgehoben oder ausgewählt ist
        if self.highlighted or self.selected:
            pen = QPen(QColor(255, 215, 0) if self.selected else QColor(0, 120, 215))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
        
        # Zeichne ein Symbol, wenn die Karte getappt ist
        if self.tapped:
            pen = QPen(QColor(255, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(5, 5, 15, 15)
            painter.drawLine(15, 5, 5, 15)
    
    def mousePressEvent(self, event):
        """
        Ereignisbehandlung für Mausklicks.
        
        Args:
            event (QMouseEvent): Das Mausereignis.
        """
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.card_data)
    
    def mouseDoubleClickEvent(self, event):
        """
        Ereignisbehandlung für Doppelklicks.
        
        Args:
            event (QMouseEvent): Das Mausereignis.
        """
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.card_data)
    
    def sizeHint(self):
        """
        Gibt die bevorzugte Größe des Widgets zurück.
        
        Returns:
            QSize: Die bevorzugte Größe.
        """
        return QSize(self.card_width, self.card_height)
