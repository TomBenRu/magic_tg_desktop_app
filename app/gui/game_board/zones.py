from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt

class GameZone(QWidget):
    """Basisklasse für alle Spielzonen (Hand, Battlefield, Library, etc.).

    Eine GameZone repräsentiert einen Bereich auf dem Spielbrett, in dem Karten
    platziert werden können, wie z.B. die Hand eines Spielers oder das Spielfeld.
    """
    
    def __init__(self, name, parent=None):
        """Initialisiert eine neue Spielzone.

        Args:
            name (str): Der Name der Spielzone.
            parent (QWidget, optional): Das übergeordnete Widget. Defaults to None.
        """
        super().__init__(parent)
        self.name = name
        self.cards = []
        
        # Layout
        self.layout = QVBoxLayout(self)
        
        # Titel
        self.title = QLabel(name)
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)
        
        # Scrollbereich für Karten
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.cards_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)
    
    def add_card(self, card_widget):
        """Fügt eine Karte zur Zone hinzu.

        Args:
            card_widget (QWidget): Das Widget der hinzuzufügenden Karte.
        """
        self.cards.append(card_widget)
        self.cards_layout.addWidget(card_widget)
    
    def remove_card(self, card_widget):
        """Entfernt eine Karte aus der Zone.

        Args:
            card_widget (QWidget): Das Widget der zu entfernenden Karte.
        """
        if card_widget in self.cards:
            self.cards.remove(card_widget)
            self.cards_layout.removeWidget(card_widget)
            card_widget.setParent(None)
    
    def clear(self):
        """Entfernt alle Karten aus der Zone."""
        for card in self.cards[:]:
            self.remove_card(card)