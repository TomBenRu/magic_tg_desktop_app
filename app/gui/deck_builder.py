"""
Deck-Builder für die Magic the Gathering Desktop App.

Dieses Modul implementiert den Deck-Builder für die Anwendung.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QComboBox, QSpinBox, QSplitter,
    QScrollArea, QGroupBox, QMessageBox, QDialog, QDialogButtonBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QFont

from app.gui.widgets.card_widget import CardWidget
from app.models.card import Card
from app.models.deck import Deck, CardInDeck
from app.models.player import Player

from pony.orm import db_session, select, commit


class DeckBuilderWidget(QWidget):
    """Widget für den Deck-Builder."""
    
    deck_saved = Signal(int)  # Emittiert die ID des gespeicherten Decks
    
    def __init__(self, parent=None):
        """
        Initialisiert das Deck-Builder-Widget.
        
        Args:
            parent (QWidget, optional): Das Eltern-Widget.
        """
        super().__init__(parent)
        
        self.current_player = None
        self.current_deck = None
        self.current_deck_id = None
        self.card_catalog = []
        self.deck_cards = []
        
        self.init_ui()
        self.load_card_catalog()
        self.load_players()
    
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche."""
        main_layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        main_layout.addLayout(toolbar_layout)
        
        # Spielerauswahl
        self.player_combo = QComboBox()
        self.player_combo.setMinimumWidth(150)
        toolbar_layout.addWidget(QLabel("Spieler:"))
        toolbar_layout.addWidget(self.player_combo)
        
        # Deck-Name und Auswahl
        self.deck_combo = QComboBox()
        self.deck_combo.setMinimumWidth(200)
        toolbar_layout.addWidget(QLabel("Deck:"))
        toolbar_layout.addWidget(self.deck_combo)
        
        # Format-Auswahl
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Standard", "Modern", "Commander", "Legacy", "Vintage", "Pauper", "Brawl"])
        toolbar_layout.addWidget(QLabel("Format:"))
        toolbar_layout.addWidget(self.format_combo)
        
        # Buttons
        self.new_deck_button = QPushButton("Neues Deck")
        toolbar_layout.addWidget(self.new_deck_button)
        
        self.save_deck_button = QPushButton("Deck speichern")
        toolbar_layout.addWidget(self.save_deck_button)
        
        # Hauptbereich mit Splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)
        
        # Linke Seite: Kartenkatalog
        catalog_widget = QWidget()
        catalog_layout = QVBoxLayout(catalog_widget)
        catalog_layout.setContentsMargins(0, 0, 0, 0)
        
        # Suchfeld
        search_layout = QHBoxLayout()
        catalog_layout.addLayout(search_layout)
        
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Suche nach Karten...")
        search_layout.addWidget(self.search_field)
        
        self.search_button = QPushButton("Suchen")
        search_layout.addWidget(self.search_button)
        
        # Filter
        filter_layout = QHBoxLayout()
        catalog_layout.addLayout(filter_layout)
        
        filter_layout.addWidget(QLabel("Typ:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Alle", "Creature", "Instant", "Sorcery", "Artifact", "Enchantment", "Land", "Planeswalker"])
        filter_layout.addWidget(self.type_combo)
        
        filter_layout.addWidget(QLabel("Farbe:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(["Alle", "White", "Blue", "Black", "Red", "Green", "Multicolor", "Colorless"])
        filter_layout.addWidget(self.color_combo)
        
        # Kartenkatalog
        catalog_group = QGroupBox("Kartenkatalog")
        catalog_layout.addWidget(catalog_group, 1)
        
        catalog_group_layout = QVBoxLayout(catalog_group)
        
        self.catalog_list = QListWidget()
        self.catalog_list.setSelectionMode(QListWidget.SingleSelection)
        catalog_group_layout.addWidget(self.catalog_list)
        
        # Button zum Hinzufügen
        add_layout = QHBoxLayout()
        catalog_layout.addLayout(add_layout)
        
        add_layout.addWidget(QLabel("Anzahl:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 99)
        self.quantity_spin.setValue(1)
        add_layout.addWidget(self.quantity_spin)
        
        self.add_button = QPushButton("Zum Deck hinzufügen")
        add_layout.addWidget(self.add_button)
        
        # Rechte Seite: Deck
        deck_widget = QWidget()
        deck_layout = QVBoxLayout(deck_widget)
        deck_layout.setContentsMargins(0, 0, 0, 0)
        
        # Deck-Informationen
        deck_info_layout = QHBoxLayout()
        deck_layout.addLayout(deck_info_layout)
        
        self.deck_name_label = QLabel("Kein Deck ausgewählt")
        deck_info_layout.addWidget(self.deck_name_label)
        
        deck_info_layout.addStretch()
        
        self.card_count_label = QLabel("0 Karten")
        deck_info_layout.addWidget(self.card_count_label)
        
        # Deck-Inhalt
        deck_group = QGroupBox("Deck-Inhalt")
        deck_layout.addWidget(deck_group, 1)
        
        deck_group_layout = QVBoxLayout(deck_group)
        
        self.deck_list = QListWidget()
        self.deck_list.setSelectionMode(QListWidget.SingleSelection)
        deck_group_layout.addWidget(self.deck_list)
        
        # Button zum Entfernen
        remove_layout = QHBoxLayout()
        deck_layout.addLayout(remove_layout)
        
        remove_layout.addStretch()
        
        self.remove_button = QPushButton("Aus Deck entfernen")
        remove_layout.addWidget(self.remove_button)
        
        # Widgets zum Splitter hinzufügen
        splitter.addWidget(catalog_widget)
        splitter.addWidget(deck_widget)
        
        # Größenverhältnis der Splitter festlegen
        splitter.setSizes([500, 500])
        
        # Signale verbinden
        self.new_deck_button.clicked.connect(self.on_new_deck)
        self.save_deck_button.clicked.connect(self.on_save_deck)
        self.player_combo.currentIndexChanged.connect(self.on_player_changed)
        self.deck_combo.currentIndexChanged.connect(self.on_deck_changed)
        self.search_button.clicked.connect(self.on_search)
        self.search_field.returnPressed.connect(self.on_search)
        self.type_combo.currentIndexChanged.connect(self.on_filter_changed)
        self.color_combo.currentIndexChanged.connect(self.on_filter_changed)
        self.catalog_list.itemClicked.connect(self.on_catalog_item_clicked)
        self.deck_list.itemClicked.connect(self.on_deck_item_clicked)
        self.add_button.clicked.connect(self.on_add_to_deck)
        self.remove_button.clicked.connect(self.on_remove_from_deck)
    
    @db_session
    def load_players(self):
        """Lädt die verfügbaren Spieler in die Spielerauswahl."""
        # Aktuelle Spieler-ID merken
        current_player_id = None
        if self.current_player:
            current_player_id = self.current_player.id
        
        # Combo leeren
        self.player_combo.clear()
        
        # Spieler laden
        players = select(p for p in Player).order_by(Player.name)
        
        # Spieler zur Combo hinzufügen
        selected_index = 0
        for i, player in enumerate(players):
            self.player_combo.addItem(player.name, player.id)
            
            if current_player_id and player.id == current_player_id:
                selected_index = i
        
        # Wenn keine Spieler vorhanden sind, Dummy-Spieler hinzufügen
        if self.player_combo.count() == 0:
            self.player_combo.addItem("Spieler 1", -1)
            
            # "Kein Spieler" als aktuellen Spieler setzen
            self.current_player = None
        else:
            # Vorherigen Spieler auswählen, falls vorhanden
            self.player_combo.setCurrentIndex(selected_index)
    
    @db_session
    def load_decks(self):
        """Lädt die verfügbaren Decks des aktuellen Spielers in die Deck-Auswahl."""
        # Aktuelle Deck-ID merken
        current_deck_id = self.current_deck_id
        
        # Combo leeren
        self.deck_combo.clear()
        
        # Dummy-Eintrag hinzufügen
        self.deck_combo.addItem("-- Deck auswählen --", -1)
        
        # Wenn kein Spieler ausgewählt ist, abbrechen
        if not self.current_player:
            return
        
        # Decks laden
        decks = select(d for d in Deck if d.player == self.current_player).order_by(Deck.name)
        
        # Decks zur Combo hinzufügen
        selected_index = 0
        for i, deck in enumerate(decks):
            self.deck_combo.addItem(f"{deck.name} ({deck.format})", deck.id)
            
            if current_deck_id and deck.id == current_deck_id:
                selected_index = i + 1  # +1 wegen Dummy-Eintrag
        
        # Vorheriges Deck auswählen, falls vorhanden
        if current_deck_id and selected_index > 0:
            self.deck_combo.setCurrentIndex(selected_index)
        else:
            self.deck_combo.setCurrentIndex(0)
    
    @db_session
    def load_card_catalog(self):
        """Lädt den Kartenkatalog aus der Datenbank."""
        # Karten laden
        self.card_catalog = list(select(c for c in Card).order_by(Card.name)[:])
        
        # Kartenkataloganzeige aktualisieren
        self.update_catalog_display()
    
    def update_catalog_display(self):
        """Aktualisiert die Anzeige des Kartenkatalogs basierend auf den Filtern."""
        # Liste leeren
        self.catalog_list.clear()
        
        # Filter anwenden
        filtered_cards = self.apply_filters(self.card_catalog)
        
        # Karten zur Liste hinzufügen
        for card in filtered_cards:
            item = QListWidgetItem(f"{card.name} ({card.card_type})")
            item.setData(Qt.UserRole, card.id)
            self.catalog_list.addItem(item)
    
    def apply_filters(self, cards):
        """
        Wendet die aktuellen Filter auf die Kartenliste an.
        
        Args:
            cards (list): Die zu filternden Karten.
        
        Returns:
            list: Die gefilterten Karten.
        """
        filtered_cards = []
        
        # Typ-Filter
        selected_type = self.type_combo.currentText()
        
        # Farb-Filter
        selected_color = self.color_combo.currentText()
        
        # Suchtext
        search_text = self.search_field.text().lower()
        
        for card in cards:
            # Typ-Filter
            if selected_type != "Alle" and selected_type not in card.card_type:
                continue
            
            # Farb-Filter
            if selected_color != "Alle":
                if selected_color == "Multicolor" and len(card.get_colors_list()) <= 1:
                    continue
                elif selected_color == "Colorless" and len(card.get_colors_list()) > 0:
                    continue
                elif selected_color != "Multicolor" and selected_color != "Colorless" and selected_color not in card.colors:
                    continue
            
            # Suchtext
            if search_text and (
                search_text not in card.name.lower() and 
                (not card.rules_text or search_text not in card.rules_text.lower())
            ):
                continue
            
            filtered_cards.append(card)
        
        return filtered_cards
    
    @db_session
    def update_deck_display(self):
        """Aktualisiert die Anzeige des aktuellen Decks."""
        # Liste leeren
        self.deck_list.clear()
        
        # Wenn kein Deck ausgewählt ist, abbrechen
        if not self.current_deck:
            self.deck_name_label.setText("Kein Deck ausgewählt")
            self.card_count_label.setText("0 Karten")
            return
        
        # Deck-Informationen anzeigen
        self.deck_name_label.setText(f"{self.current_deck.name} ({self.current_deck.format})")
        
        # Karten nach Typ sortieren
        cards_by_type = {}
        total_cards = 0
        
        for card_in_deck in self.current_deck.cards:
            card = card_in_deck.card
            card_type = card.card_type.split("—")[0].strip()  # Haupttyp (vor dem Strich)
            
            if card_type not in cards_by_type:
                cards_by_type[card_type] = []
            
            cards_by_type[card_type].append((card, card_in_deck.quantity))
            total_cards += card_in_deck.quantity
        
        # Kartenanzahl anzeigen
        self.card_count_label.setText(f"{total_cards} Karten")
        
        # Karten nach Typ zur Liste hinzufügen
        for card_type in sorted(cards_by_type.keys()):
            # Typ-Überschrift
            type_item = QListWidgetItem(f"--- {card_type} ({sum(q for _, q in cards_by_type[card_type])}) ---")
            type_item.setFlags(Qt.NoItemFlags)  # Nicht auswählbar
            font = type_item.font()
            font.setBold(True)
            type_item.setFont(font)
            self.deck_list.addItem(type_item)
            
            # Karten dieses Typs
            for card, quantity in sorted(cards_by_type[card_type], key=lambda x: x[0].name):
                item = QListWidgetItem(f"{quantity}x {card.name}")
                item.setData(Qt.UserRole, card.id)
                item.setData(Qt.UserRole + 1, quantity)
                self.deck_list.addItem(item)
    
    @Slot()
    def on_player_changed(self):
        """Wird aufgerufen, wenn der Spieler geändert wird."""
        player_id = self.player_combo.currentData()
        
        # Wenn kein Spieler ausgewählt ist oder der Dummy-Spieler, Dummy-Spieler erstellen
        if player_id is None or player_id == -1:
            self.create_dummy_player()
            return
        
        # Spieler laden
        with db_session:
            self.current_player = Player.get(id=player_id)
        
        # Decks des Spielers laden
        self.load_decks()
    
    @db_session
    def create_dummy_player(self):
        """Erstellt einen Dummy-Spieler, wenn keiner vorhanden ist."""
        # Neuen Spieler erstellen
        player = Player(name="Spieler 1")
        commit()
        
        self.current_player = player
        
        # Spielerliste neu laden
        self.load_players()
    
    @Slot()
    def on_deck_changed(self):
        """Wird aufgerufen, wenn das Deck geändert wird."""
        deck_id = self.deck_combo.currentData()
        
        # Wenn kein Deck ausgewählt ist oder der Dummy-Eintrag, Deck zurücksetzen
        if deck_id is None or deck_id == -1:
            self.current_deck = None
            self.current_deck_id = None
            self.update_deck_display()
            return
        
        # Deck laden
        with db_session:
            self.current_deck = Deck.get(id=deck_id)
            self.current_deck_id = deck_id
        
        # Format im Combo-Box setzen
        if self.current_deck:
            index = self.format_combo.findText(self.current_deck.format)
            if index >= 0:
                self.format_combo.setCurrentIndex(index)
        
        # Deck-Anzeige aktualisieren
        self.update_deck_display()
    
    @Slot()
    def on_new_deck(self):
        """Wird aufgerufen, wenn ein neues Deck erstellt werden soll."""
        # Dialog für den Deck-Namen
        dialog = NewDeckDialog(self)
        
        if dialog.exec() == QDialog.Accepted:
            deck_name, deck_format = dialog.get_deck_info()
            
            if not deck_name:
                QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Deck-Namen ein.")
                return
            
            # Neues Deck erstellen
            self.create_new_deck(deck_name, deck_format)
    
    @db_session
    def create_new_deck(self, name, format_name):
        """
        Erstellt ein neues Deck.
        
        Args:
            name (str): Der Name des Decks.
            format_name (str): Das Format des Decks.
        """
        # Wenn kein Spieler ausgewählt ist, Dummy-Spieler erstellen
        if not self.current_player:
            self.create_dummy_player()
        
        # Neues Deck erstellen
        deck = Deck(
            name=name,
            player=self.current_player,
            format=format_name
        )
        
        commit()
        
        # Neues Deck als aktuelles Deck setzen
        self.current_deck = deck
        self.current_deck_id = deck.id
        
        # Decks neu laden
        self.load_decks()
        
        # Deck-Anzeige aktualisieren
        self.update_deck_display()
        
        # Signal senden
        self.deck_saved.emit(deck.id)
    
    @Slot()
    def on_save_deck(self):
        """Wird aufgerufen, wenn das Deck gespeichert werden soll."""
        # Wenn kein Deck ausgewählt ist, abbrechen
        if not self.current_deck:
            QMessageBox.warning(self, "Fehler", "Kein Deck ausgewählt.")
            return
        
        # Deck speichern
        with db_session:
            deck = Deck.get(id=self.current_deck_id)
            
            if not deck:
                QMessageBox.warning(self, "Fehler", "Deck nicht gefunden.")
                return
            
            # Format aktualisieren
            deck.format = self.format_combo.currentText()
            
            commit()
        
        # Signal senden
        self.deck_saved.emit(self.current_deck_id)
        
        QMessageBox.information(self, "Erfolg", f"Deck '{self.current_deck.name}' wurde gespeichert.")
    
    @Slot()
    def on_search(self):
        """Wird aufgerufen, wenn nach Karten gesucht werden soll."""
        self.update_catalog_display()
    
    @Slot()
    def on_filter_changed(self):
        """Wird aufgerufen, wenn ein Filter geändert wird."""
        self.update_catalog_display()
    
    @Slot(QListWidgetItem)
    def on_catalog_item_clicked(self, item):
        """
        Wird aufgerufen, wenn auf ein Element im Kartenkatalog geklickt wird.
        
        Args:
            item (QListWidgetItem): Das angeklickte Element.
        """
        # Karten-ID aus dem Item abrufen
        card_id = item.data(Qt.UserRole)
        
        # TODO: Kartenvorschau anzeigen
    
    @Slot(QListWidgetItem)
    def on_deck_item_clicked(self, item):
        """
        Wird aufgerufen, wenn auf ein Element im Deck geklickt wird.
        
        Args:
            item (QListWidgetItem): Das angeklickte Element.
        """
        # Karten-ID aus dem Item abrufen
        card_id = item.data(Qt.UserRole)
        
        # Wenn das Element keine Karten-ID hat (z.B. die Typ-Überschrift), abbrechen
        if card_id is None:
            return
        
        # TODO: Kartenvorschau anzeigen
    
    @Slot()
    def on_add_to_deck(self):
        """Wird aufgerufen, wenn eine Karte zum Deck hinzugefügt werden soll."""
        # Wenn kein Deck ausgewählt ist, abbrechen
        if not self.current_deck:
            QMessageBox.warning(self, "Fehler", "Kein Deck ausgewählt. Bitte erstellen oder wählen Sie zuerst ein Deck.")
            return
        
        # Ausgewählte Karte abrufen
        selected_items = self.catalog_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Fehler", "Keine Karte ausgewählt.")
            return
        
        # Karten-ID aus dem Item abrufen
        card_id = selected_items[0].data(Qt.UserRole)
        
        # Anzahl abrufen
        quantity = self.quantity_spin.value()
        
        # Karte zum Deck hinzufügen
        self.add_card_to_deck(card_id, quantity)
    
    @db_session
    def add_card_to_deck(self, card_id, quantity):
        """
        Fügt eine Karte zum Deck hinzu.
        
        Args:
            card_id (int): Die ID der Karte.
            quantity (int): Die Anzahl der Karten.
        """
        # Karte abrufen
        card = Card.get(id=card_id)
        
        if not card:
            QMessageBox.warning(self, "Fehler", "Karte nicht gefunden.")
            return
        
        # Deck abrufen
        deck = Deck.get(id=self.current_deck_id)
        
        if not deck:
            QMessageBox.warning(self, "Fehler", "Deck nicht gefunden.")
            return
        
        # Prüfen, ob die Karte bereits im Deck ist
        card_in_deck = select(cid for cid in CardInDeck if cid.deck == deck and cid.card == card).first()
        
        if card_in_deck:
            # Anzahl erhöhen
            card_in_deck.quantity += quantity
        else:
            # Neue Karte zum Deck hinzufügen
            CardInDeck(
                deck=deck,
                card=card,
                quantity=quantity
            )
        
        commit()
        
        # Deck-Anzeige aktualisieren
        self.update_deck_display()
    
    @Slot()
    def on_remove_from_deck(self):
        """Wird aufgerufen, wenn eine Karte aus dem Deck entfernt werden soll."""
        # Wenn kein Deck ausgewählt ist, abbrechen
        if not self.current_deck:
            return
        
        # Ausgewählte Karte abrufen
        selected_items = self.deck_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Fehler", "Keine Karte ausgewählt.")
            return
        
        # Karten-ID aus dem Item abrufen
        card_id = selected_items[0].data(Qt.UserRole)
        
        # Wenn das Element keine Karten-ID hat (z.B. die Typ-Überschrift), abbrechen
        if card_id is None:
            return
        
        # Karte aus dem Deck entfernen
        self.remove_card_from_deck(card_id)
    
    @db_session
    def remove_card_from_deck(self, card_id):
        """
        Entfernt eine Karte aus dem Deck.
        
        Args:
            card_id (int): Die ID der Karte.
        """
        # Karte abrufen
        card = Card.get(id=card_id)
        
        if not card:
            QMessageBox.warning(self, "Fehler", "Karte nicht gefunden.")
            return
        
        # Deck abrufen
        deck = Deck.get(id=self.current_deck_id)
        
        if not deck:
            QMessageBox.warning(self, "Fehler", "Deck nicht gefunden.")
            return
        
        # Karte im Deck suchen
        card_in_deck = select(cid for cid in CardInDeck if cid.deck == deck and cid.card == card).first()
        
        if not card_in_deck:
            QMessageBox.warning(self, "Fehler", "Karte nicht im Deck gefunden.")
            return
        
        # Dialog für die Anzahl zu entfernender Karten
        quantity_dialog = QDialog(self)
        quantity_dialog.setWindowTitle("Karte entfernen")
        
        quantity_layout = QFormLayout(quantity_dialog)
        
        # Anzahl
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, card_in_deck.quantity)
        quantity_spin.setValue(1)
        quantity_layout.addRow(f"Anzahl (1-{card_in_deck.quantity}):", quantity_spin)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(quantity_dialog.accept)
        button_box.rejected.connect(quantity_dialog.reject)
        quantity_layout.addRow(button_box)
        
        # Dialog anzeigen
        if quantity_dialog.exec() == QDialog.Accepted:
            remove_quantity = quantity_spin.value()
            
            # Anzahl reduzieren oder Karte entfernen
            if remove_quantity >= card_in_deck.quantity:
                # Karte vollständig entfernen
                card_in_deck.delete()
            else:
                # Anzahl reduzieren
                card_in_deck.quantity -= remove_quantity
            
            commit()
            
            # Deck-Anzeige aktualisieren
            self.update_deck_display()


class NewDeckDialog(QDialog):
    """Dialog zum Erstellen eines neuen Decks."""
    
    def __init__(self, parent=None):
        """
        Initialisiert den Dialog.
        
        Args:
            parent (QWidget, optional): Das Eltern-Widget.
        """
        super().__init__(parent)
        
        self.setWindowTitle("Neues Deck")
        self.init_ui()
    
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche."""
        layout = QFormLayout(self)
        
        # Deck-Name
        self.name_edit = QLineEdit()
        layout.addRow("Deck-Name:", self.name_edit)
        
        # Format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Standard", "Modern", "Commander", "Legacy", "Vintage", "Pauper", "Brawl"])
        layout.addRow("Format:", self.format_combo)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
    
    def get_deck_info(self):
        """
        Gibt die eingegebenen Deck-Informationen zurück.
        
        Returns:
            tuple: (name, format) oder (None, None), wenn der Dialog abgebrochen wurde.
        """
        if self.result() == QDialog.Accepted:
            return self.name_edit.text().strip(), self.format_combo.currentText()
        return None, None
