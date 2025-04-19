"""
Spiel-Modell für die Magic the Gathering Desktop App.

Dieses Modul definiert das Datenmodell für Spiele.
"""

import json
import datetime
from pony.orm import Required, Optional, PrimaryKey
from app.models.database import db


class Game(db.Entity):
    """
    Repräsentiert ein Magic the Gathering Spiel in der Datenbank.
    
    Attribute:
        id (int): Eindeutige ID des Spiels
        player1 (Player): Erster Spieler
        player2 (Player): Zweiter Spieler
        winner (Player, optional): Gewinner des Spiels (None wenn noch nicht beendet)
        start_time (datetime): Startzeit des Spiels
        end_time (datetime, optional): Endzeit des Spiels
        game_state (str): JSON-String mit dem Spielzustand
    """
    id = PrimaryKey(int, auto=True)
    player1 = Required('Player', reverse='games_as_player1')
    player2 = Required('Player', reverse='games_as_player2')
    winner = Optional('Player', reverse='games_won')
    start_time = Required(datetime.datetime, default=lambda: datetime.datetime.now())
    end_time = Optional(datetime.datetime)
    game_state = Optional(str)  # JSON-String mit dem Spielzustand
    
    def set_game_state(self, state_dict):
        """
        Speichert den Spielzustand als JSON-String.
        
        Args:
            state_dict (dict): Dictionary mit dem Spielzustand
        """
        self.game_state = json.dumps(state_dict)
    
    def get_game_state(self):
        """
        Gibt den Spielzustand als Dictionary zurück.
        
        Returns:
            dict: Dictionary mit dem Spielzustand oder leeres Dictionary, wenn kein Zustand existiert
        """
        if not self.game_state:
            return {}
        
        try:
            return json.loads(self.game_state)
        except json.JSONDecodeError:
            return {}
    
    def end_game(self, winner=None):
        """
        Beendet das Spiel und setzt den Gewinner und die Endzeit.
        
        Args:
            winner (Player, optional): Gewinner des Spiels
        """
        self.winner = winner
        self.end_time = datetime.datetime.now()
        
        # Aktualisiere die Spielerstatistiken
        self.player1.update_stats()
        self.player2.update_stats()
    
    def get_duration(self):
        """
        Berechnet die Dauer des Spiels.
        
        Returns:
            timedelta: Dauer des Spiels oder None, wenn das Spiel noch läuft
        """
        if not self.end_time:
            return None
        
        return self.end_time - self.start_time
