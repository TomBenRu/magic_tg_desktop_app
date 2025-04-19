"""
Dialog-Klassen für das Spielbrett der Magic the Gathering Desktop App.

Dieses Modul enthält Dialoge für die Interaktion mit dem Spielbrett.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QComboBox, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt, Slot

from app.models.player import Player
from app.models.deck import Deck
from app.models.game import Game

from pony.orm import db_session, select, desc, commit


class NewGameDialog(QDialog):
    """Dialog zum Erstellen eines neuen Spiels."""
    
    def __init__(self, parent=None):
        """
        Initialisiert den Dialog.
        
        Args:
            parent (QWidget, optional): Das Eltern-Widget.
        """
        super().__init__(parent)
        
        self.setWindowTitle("Neues Spiel")
        self.init_ui()
        self.load_players_and_decks()
    
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche."""
        layout = QFormLayout(self)
        
        # Spieler 1
        self.player1_combo = QComboBox()
        layout.addRow("Spieler 1:", self.player1_combo)
        
        # Deck für Spieler 1
        self.deck1_combo = QComboBox()
        layout.addRow("Deck für Spieler 1:", self.deck1_combo)
        
        # Spieler 2
        self.player2_combo = QComboBox()
        layout.addRow("Spieler 2:", self.player2_combo)
        
        # Deck für Spieler 2
        self.deck2_combo = QComboBox()
        layout.addRow("Deck für Spieler 2:", self.deck2_combo)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
        
        # Verbinde Spieler-Änderungen mit Deck-Updates
        self.player1_combo.currentIndexChanged.connect(self.on_player1_changed)
        self.player2_combo.currentIndexChanged.connect(self.on_player2_changed)
    
    @db_session
    def load_players_and_decks(self):
        """Lädt die verfügbaren Spieler und ihre Decks."""
        # Spieler laden
        players = select(p for p in Player).order_by(Player.name)[:]
        
        # Wenn keine Spieler vorhanden sind, Dummy-Spieler erstellen
        if not players:
            player1 = Player(name="Spieler 1")
            player2 = Player(name="Spieler 2")
            commit()
            players = [player1, player2]
        
        # Spieler zu den Combos hinzufügen
        for player in players:
            self.player1_combo.addItem(player.name, player.id)
            self.player2_combo.addItem(player.name, player.id)
        
        # Verschiedene Spieler auswählen, falls möglich
        if len(players) > 1:
            self.player2_combo.setCurrentIndex(1)
        
        # Decks für die ausgewählten Spieler laden
        self.on_player1_changed()
        self.on_player2_changed()
    
    @Slot()
    def on_player1_changed(self):
        """Wird aufgerufen, wenn Spieler 1 geändert wird."""
        player_id = self.player1_combo.currentData()
        self.load_decks_for_player(player_id, self.deck1_combo)
    
    @Slot()
    def on_player2_changed(self):
        """Wird aufgerufen, wenn Spieler 2 geändert wird."""
        player_id = self.player2_combo.currentData()
        self.load_decks_for_player(player_id, self.deck2_combo)
    
    @db_session
    def load_decks_for_player(self, player_id, deck_combo):
        """
        Lädt die Decks eines Spielers.
        
        Args:
            player_id (int): Die ID des Spielers.
            deck_combo (QComboBox): Die Combo-Box für die Decks.
        """
        # Combo leeren
        deck_combo.clear()
        
        # Spieler laden
        player = Player.get(id=player_id)
        
        if not player:
            return
        
        # Decks laden
        decks = select(d for d in Deck if d.player == player).order_by(Deck.name)[:]
        
        # Wenn keine Decks vorhanden sind, Dummy-Deck erstellen
        if not decks:
            deck = Deck(
                name=f"Deck von {player.name}",
                player=player,
                format="Standard"
            )
            commit()
            decks = [deck]
        
        # Decks zur Combo hinzufügen
        for deck in decks:
            deck_combo.addItem(f"{deck.name} ({deck.format})", deck.id)
    
    def get_game_info(self):
        """
        Gibt die ausgewählten Spieler und Decks zurück.
        
        Returns:
            tuple: (player1_id, player2_id, deck1_id, deck2_id)
        """
        return (
            self.player1_combo.currentData(),
            self.player2_combo.currentData(),
            self.deck1_combo.currentData(),
            self.deck2_combo.currentData()
        )


class LoadGameDialog(QDialog):
    """Dialog zum Laden eines Spiels."""
    
    def __init__(self, parent=None):
        """
        Initialisiert den Dialog.
        
        Args:
            parent (QWidget, optional): Das Eltern-Widget.
        """
        super().__init__(parent)
        
        self.setWindowTitle("Spiel laden")
        self.init_ui()
        self.load_games()
    
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche."""
        layout = QFormLayout(self)
        
        # Spiel-Auswahl
        self.game_combo = QComboBox()
        layout.addRow("Spiel:", self.game_combo)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
    
    @db_session
    def load_games(self):
        """Lädt die verfügbaren Spiele."""
        # Spiele laden
        games = select(g for g in Game if g.end_time is None).order_by(desc(Game.start_time))[:]
        
        # Spiele zur Combo hinzufügen
        for game in games:
            game_time = game.start_time.strftime("%d.%m.%Y %H:%M")
            self.game_combo.addItem(
                f"{game.player1.name} vs. {game.player2.name} ({game_time})",
                game.id
            )
        
        # Button deaktivieren, wenn keine Spiele vorhanden sind
        if not games:
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
    
    def get_game_id(self):
        """
        Gibt die ID des ausgewählten Spiels zurück.
        
        Returns:
            int: Die ID des ausgewählten Spiels oder None, wenn kein Spiel ausgewählt ist.
        """
        return self.game_combo.currentData() if self.game_combo.count() > 0 else None
