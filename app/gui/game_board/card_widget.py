"""
Widget-Klassen für Karten im Spielbrett.

Dieses Modul enthält die Widget-Klassen für Karten im Spielbrett.
"""

from PySide6.QtWidgets import QLabel, QMenu, QVBoxLayout, QWidget, QFrame
from PySide6.QtCore import Qt, QMimeData, Signal, Property, QPoint
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QPen, QBrush, QFont, QFontMetrics
import json


class CardWidget(QWidget):
    """Widget für eine Karte im Spielbrett."""
    
    # Signale
    clicked = Signal(object)  # Emittiert, wenn die Karte angeklickt wird
    double_clicked = Signal(object)  # Emittiert, wenn die Karte doppelt angeklickt wird
    right_clicked = Signal(object, QPoint)  # Emittiert, wenn die Karte mit rechts angeklickt wird
    
    def __init__(self, card_data, parent=None):
        """Initialisiert das Widget.
        
        Args:
            card_data (dict): Die Daten der Karte.
            parent (QWidget, optional): Das Eltern-Widget.
        """
        super().__init__(parent)
        
        self._card_data = card_data
        self._tapped = card_data.get('tapped', False)
        self._attacking = card_data.get('attacking', False)
        self._blocking = card_data.get('blocking', False)
        self._face_down = False
        
        # Layout und Widgets
        self.init_ui()
        
        # Größe und Seitenverhältnis (Standard-MTG-Karte: 63 x 88 mm = 1:1.4)
        self.setMinimumSize(100, 140)
        self.setMaximumSize(100, 140)
        
        # Interaktionen
        self.setMouseTracking(True)
        
    def init_ui(self):
        """Initialisiert die UI-Komponenten."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Label für den Namen
        self.name_label = QLabel(self._card_data.get('name', 'Unbekannte Karte'))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        self.layout.addWidget(self.name_label)
        
        # Label für den Typ
        self.type_label = QLabel(self._card_data.get('type', ''))
        self.type_label.setAlignment(Qt.AlignCenter)
        self.type_label.setWordWrap(True)
        self.type_label.setStyleSheet("font-size: 8px;")
        self.layout.addWidget(self.type_label)
        
        # Rahmen
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(2)
        
        # Setze die Hintergrundfarbe basierend auf dem Kartentyp
        self.update_background_color()
        
        # Update-Methode aufrufen
        self.update_display()
    
    def update_background_color(self):
        """Aktualisiert die Hintergrundfarbe basierend auf dem Kartentyp."""
        card_type = self._card_data.get('type', '')
        
        if self._face_down:
            # Kartenrückseite: Dunkelblau
            self.setStyleSheet("background-color: #000066;")
            return
        
        # Kartenfarbe basierend auf dem MTG-Farben-System
        card_colors = self._card_data.get('colors', [])
        
        if not card_colors:
            # Farblos
            self.setStyleSheet("background-color: #bbbbbb;")
        elif len(card_colors) > 1:
            # Mehrfarbig
            self.setStyleSheet("background-color: #ddcc77;")
        elif 'White' in card_colors:
            self.setStyleSheet("background-color: #ffffee;")
        elif 'Blue' in card_colors:
            self.setStyleSheet("background-color: #aaddff;")
        elif 'Black' in card_colors:
            self.setStyleSheet("background-color: #aaaaaa;")
        elif 'Red' in card_colors:
            self.setStyleSheet("background-color: #ffaaaa;")
        elif 'Green' in card_colors:
            self.setStyleSheet("background-color: #aaffaa;")
        else:
            # Standard: Hellgrau
            self.setStyleSheet("background-color: #eeeeee;")
        
        # Spezifische Rahmenfarbe für bestimmte Kartentypen
        if 'Land' in card_type:
            self.setStyleSheet(self.styleSheet() + "border: 2px solid #663300;")
        elif 'Artifact' in card_type:
            self.setStyleSheet(self.styleSheet() + "border: 2px solid #777777;")
        elif 'Enchantment' in card_type:
            self.setStyleSheet(self.styleSheet() + "border: 2px solid #ffcc00;")
        elif 'Creature' in card_type:
            self.setStyleSheet(self.styleSheet() + "border: 2px solid #009900;")
        elif 'Planeswalker' in card_type:
            self.setStyleSheet(self.styleSheet() + "border: 2px solid #ff6600;")
    
    def update_display(self):
        """Aktualisiert die Anzeige des Widgets."""
        # Name und Typ aktualisieren
        if not self._face_down:
            self.name_label.setText(self._card_data.get('name', 'Unbekannte Karte'))
            self.type_label.setText(self._card_data.get('type', ''))
        else:
            self.name_label.setText("Karte")
            self.type_label.setText("")
        
        # Status anzeigen
        status = []
        if self._tapped:
            status.append("GETAPPT")
        if self._attacking:
            status.append("ANGREIFEND")
        if self._blocking:
            status.append("BLOCKIEREND")
        
        if status:
            status_text = " | ".join(status)
            self.name_label.setText(f"[{status_text}]\n{self.name_label.text()}")
        
        # Wenn getappt, drehen wir das Widget
        self.setFixedSize(140 if self._tapped else 100, 100 if self._tapped else 140)
        
        # Hintergrundfarbe aktualisieren
        self.update_background_color()
        
        # Widget neu zeichnen
        self.update()
    
    def paintEvent(self, event):
        """Überschreibt die Paint-Methode, um die Karte zu zeichnen.
        
        Args:
            event (QPaintEvent): Das Paint-Event.
        """
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Für Kreaturen zeichnen wir Stärke und Widerstandskraft
        if 'Creature' in self._card_data.get('type', '') and not self._face_down:
            power = self._card_data.get('power', 0)
            toughness = self._card_data.get('toughness', 0)
            
            text = f"{power}/{toughness}"
            font = QFont()
            font.setBold(True)
            painter.setFont(font)
            
            # Positionierung unten rechts
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(text)
            
            if self._tapped:
                x = self.width() - text_width - 5
                y = self.height() - 5
            else:
                x = self.width() - text_width - 5
                y = self.height() - 5
            
            painter.drawText(x, y, text)
        
        # Für tapped Karten drehen wir den Text
        if self._tapped:
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(90)
            painter.translate(-self.width() / 2, -self.height() / 2)
    
    def mousePressEvent(self, event):
        """Behandelt Mausklick-Events.
        
        Args:
            event (QMouseEvent): Das Mausklick-Event.
        """
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)
        elif event.button() == Qt.RightButton:
            self.right_clicked.emit(self, event.pos())
    
    def mouseDoubleClickEvent(self, event):
        """Behandelt Doppelklick-Events.
        
        Args:
            event (QMouseEvent): Das Doppelklick-Event.
        """
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self)
    
    # Getter für Kartendaten
    def get_card_data(self):
        """Gibt die Kartendaten zurück.
        
        Returns:
            dict: Die Kartendaten.
        """
        return self._card_data
    
    # Getter/Setter für Status
    def is_tapped(self):
        """Prüft, ob die Karte getappt ist.
        
        Returns:
            bool: True, wenn die Karte getappt ist, sonst False.
        """
        return self._tapped
    
    def set_tapped(self, tapped):
        """Setzt den Tapp-Status der Karte.
        
        Args:
            tapped (bool): Der neue Tapp-Status.
        """
        if self._tapped != tapped:
            self._tapped = tapped
            self._card_data['tapped'] = tapped
            self.update_display()
    
    def is_attacking(self):
        """Prüft, ob die Karte angreift.
        
        Returns:
            bool: True, wenn die Karte angreift, sonst False.
        """
        return self._attacking
    
    def set_attacking(self, attacking):
        """Setzt den Angriffs-Status der Karte.
        
        Args:
            attacking (bool): Der neue Angriffs-Status.
        """
        if self._attacking != attacking:
            self._attacking = attacking
            self._card_data['attacking'] = attacking
            self.update_display()
    
    def is_blocking(self):
        """Prüft, ob die Karte blockt.
        
        Returns:
            bool: True, wenn die Karte blockt, sonst False.
        """
        return self._blocking
    
    def set_blocking(self, blocking):
        """Setzt den Block-Status der Karte.
        
        Args:
            blocking (bool): Der neue Block-Status.
        """
        if self._blocking != blocking:
            self._blocking = blocking
            self._card_data['blocking'] = blocking
            self.update_display()
    
    def is_face_down(self):
        """Prüft, ob die Karte verdeckt ist.
        
        Returns:
            bool: True, wenn die Karte verdeckt ist, sonst False.
        """
        return self._face_down
    
    def set_face_down(self, face_down):
        """Setzt den Verdeckt-Status der Karte.
        
        Args:
            face_down (bool): Der neue Verdeckt-Status.
        """
        if self._face_down != face_down:
            self._face_down = face_down
            self.update_display()


class DraggableCardWidget(CardWidget):
    """Erweiterung des CardWidget für Drag & Drop-Funktionalität."""
    
    # Signale
    drag_started = Signal(object)  # Emittiert, wenn Drag & Drop gestartet wird
    
    def __init__(self, card_data, zone=None, parent=None):
        """Initialisiert das Widget.
        
        Args:
            card_data (dict): Die Daten der Karte.
            zone (str, optional): Die Zone, in der sich die Karte befindet.
            parent (QWidget, optional): Das Eltern-Widget.
        """
        super().__init__(card_data, parent)
        self.zone = zone
        self.setAcceptDrops(True)
    
    def mouseMoveEvent(self, event):
        """Behandelt Mausbewegungsevents für Drag & Drop.
        
        Args:
            event (QMouseEvent): Das Mausbewegungsevent.
        """
        if event.buttons() & Qt.LeftButton:
            # Mindestabstand für Drag & Drop
            if (event.pos() - self._drag_start_position).manhattanLength() < 10:
                return
            
            # Drag & Drop starten
            self._start_drag()
    
    def mousePressEvent(self, event):
        """Behandelt Mausklick-Events.
        
        Args:
            event (QMouseEvent): Das Mausklick-Event.
        """
        super().mousePressEvent(event)
        
        if event.button() == Qt.LeftButton:
            self._drag_start_position = event.pos()
    
    def _start_drag(self):
        """Startet einen Drag & Drop-Vorgang."""
        # Erstelle ein Drag-Objekt
        drag = QDrag(self)
        
        # Erstelle MIME-Daten mit Karteninformationen
        mime_data = QMimeData()
        
        # Erstelle ein Kartenobjekt mit minimalen Informationen
        card_data = {
            'id': self._card_data.get('id', ''),
            'name': self._card_data.get('name', ''),
            'zone': self.zone,
            'tapped': self._tapped,
            'attacking': self._attacking,
            'blocking': self._blocking
        }
        
        # Konvertiere in JSON und setze es als MIME-Daten
        mime_data.setText(json.dumps(card_data))
        mime_data.setData('application/x-card', json.dumps(card_data).encode())
        drag.setMimeData(mime_data)
        
        # Erstelle ein Pixmap für die Drag-Darstellung
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        # Emittiere Signal
        self.drag_started.emit(self)
        
        # Führe Drag & Drop aus
        result = drag.exec_(Qt.MoveAction | Qt.CopyAction)
    
    def dragEnterEvent(self, event):
        """Behandelt DragEnter-Events.
        
        Args:
            event (QDragEnterEvent): Das DragEnter-Event.
        """
        if event.mimeData().hasFormat('application/x-card'):
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Behandelt Drop-Events.
        
        Args:
            event (QDropEvent): Das Drop-Event.
        """
        if event.mimeData().hasFormat('application/x-card'):
            # Hier kann die Logik für das Ablegen von Karten implementiert werden
            # z.B. Karteninteraktionen, Stapeln von Karten, etc.
            event.accept()
        else:
            event.ignore()