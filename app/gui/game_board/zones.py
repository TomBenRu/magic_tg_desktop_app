from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QScrollArea, QFrame
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


class BattlefieldZone(QWidget):
    """Spielfeldzone für Magic the Gathering.
    
    Diese Zone repräsentiert das Spielfeld, auf dem sich die gespielten Karten befinden.
    Sie unterstützt ein komplexeres Layout als die einfachen GameZone-Klassen.
    """
    
    def __init__(self, name, player_id=None, parent=None):
        """Initialisiert ein neues Spielfeld.
        
        Args:
            name (str): Der Name des Spielfelds.
            player_id (str, optional): Die ID des Spielers, dem das Spielfeld gehört.
            parent (QWidget, optional): Das übergeordnete Widget.
        """
        super().__init__(parent)
        self.name = name
        self.player_id = player_id
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
        
        # Container für Karten
        self.scroll_content = QWidget()
        self.cards_layout = QHBoxLayout(self.scroll_content)  # Horizontales Layout für mehr Platz
        
        # Kategorien für verschiedene Kartentypen
        self.land_area = QWidget()
        self.land_layout = QHBoxLayout(self.land_area)
        self.land_layout.setContentsMargins(2, 2, 2, 2)
        self.land_layout.setSpacing(2)
        
        self.creature_area = QWidget()
        self.creature_layout = QHBoxLayout(self.creature_area)
        self.creature_layout.setContentsMargins(2, 2, 2, 2)
        self.creature_layout.setSpacing(2)
        
        self.other_area = QWidget()
        self.other_layout = QHBoxLayout(self.other_area)
        self.other_layout.setContentsMargins(2, 2, 2, 2)
        self.other_layout.setSpacing(2)
        
        # Rahmen um die Bereiche
        self._add_frame_to_widget(self.land_area, "Länder")
        self._add_frame_to_widget(self.creature_area, "Kreaturen")
        self._add_frame_to_widget(self.other_area, "Andere Permanents")
        
        # Bereiche zum Layout hinzufügen
        battlefield_layout = QVBoxLayout()
        battlefield_layout.addWidget(self.land_area)
        battlefield_layout.addWidget(self.creature_area)
        battlefield_layout.addWidget(self.other_area)
        
        self.cards_layout.addLayout(battlefield_layout)
        
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)
    
    def _add_frame_to_widget(self, widget, title):
        """Fügt einen Rahmen mit Titel um ein Widget.
        
        Args:
            widget (QWidget): Das Widget, das einen Rahmen bekommen soll.
            title (str): Der Titel für den Rahmen.
        """
        widget.setStyleSheet(
            f"QWidget {{ border: 1px solid #999; border-radius: 3px; padding: 2px; }}"
        )
        
        # Füge Titel hinzu (am oberen Rand)
        if hasattr(widget, 'layout') and widget.layout() is not None:
            title_label = QLabel(title)
            title_label.setStyleSheet("border: none; font-weight: bold; background-color: white;")
            title_label.setAlignment(Qt.AlignCenter)
            widget.layout().insertWidget(0, title_label)
    
    def add_card(self, card_widget):
        """Fügt eine Karte zum Spielfeld hinzu.
        
        Args:
            card_widget (QWidget): Das Widget der hinzuzufügenden Karte.
        """
        self.cards.append(card_widget)
        
        # Bestimme den Kartentyp und füge die Karte zum entsprechenden Bereich hinzu
        card_data = card_widget.property('card_data')
        if card_data and 'type' in card_data:
            card_type = card_data['type']
            if 'Land' in card_type:
                self.land_layout.addWidget(card_widget)
            elif 'Creature' in card_type:
                self.creature_layout.addWidget(card_widget)
            else:
                self.other_layout.addWidget(card_widget)
        else:
            # Fallback, wenn kein Typ erkannt wird
            self.other_layout.addWidget(card_widget)
    
    def remove_card(self, card_widget):
        """Entfernt eine Karte aus dem Spielfeld.
        
        Args:
            card_widget (QWidget): Das Widget der zu entfernenden Karte.
        """
        if card_widget in self.cards:
            self.cards.remove(card_widget)
            
            # Entferne die Karte aus dem entsprechenden Layout
            card_data = card_widget.property('card_data')
            if card_data and 'type' in card_data:
                card_type = card_data['type']
                if 'Land' in card_type:
                    self.land_layout.removeWidget(card_widget)
                elif 'Creature' in card_type:
                    self.creature_layout.removeWidget(card_widget)
                else:
                    self.other_layout.removeWidget(card_widget)
            else:
                self.other_layout.removeWidget(card_widget)
            
            card_widget.setParent(None)
    
    def clear(self):
        """Entfernt alle Karten aus dem Spielfeld."""
        for card in self.cards[:]:
            self.remove_card(card)