"""
Spieler-Modell für die Magic the Gathering Desktop App.

Dieses Modul definiert das Datenmodell für Spieler und ihre Statistiken.
"""

from pony.orm import Required, Optional, Set, PrimaryKey
from app.models.database import db


class Player(db.Entity):
    """
    Repräsentiert einen Spieler in der Datenbank.
    
    Attribute:
        id (int): Eindeutige ID des Spielers
        name (str): Name des Spielers
        decks (Set[Deck]): Decks des Spielers
        stats (PlayerStats): Statistiken des Spielers
        games_as_player1 (Set[Game]): Spiele, in denen der Spieler als Spieler 1 teilgenommen hat
        games_as_player2 (Set[Game]): Spiele, in denen der Spieler als Spieler 2 teilgenommen hat
        games_won (Set[Game]): Spiele, die der Spieler gewonnen hat
    """
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    decks = Set('Deck')
    stats = Optional('PlayerStats')
    games_as_player1 = Set('Game', reverse='player1')
    games_as_player2 = Set('Game', reverse='player2')
    games_won = Set('Game', reverse='winner')
    
    def get_win_rate(self):
        """
        Berechnet die Gewinnrate des Spielers.
        
        Returns:
            float: Gewinnrate (0.0 - 1.0) oder 0.0, wenn keine Spiele gespielt wurden
        """
        if not self.stats:
            return 0.0
            
        total_games = self.stats.games_played
        if total_games == 0:
            return 0.0
            
        return self.stats.games_won / total_games
    
    def get_total_games(self):
        """
        Gibt die Gesamtzahl der gespielten Spiele zurück.
        
        Returns:
            int: Anzahl der gespielten Spiele
        """
        return len(self.games_as_player1) + len(self.games_as_player2)
    
    def update_stats(self):
        """Aktualisiert die Spielerstatistiken basierend auf den Spielergebnissen."""
        if not self.stats:
            self.stats = PlayerStats(player=self)
            
        total_games = self.get_total_games()
        won_games = len(self.games_won)
        lost_games = total_games - won_games
        
        self.stats.games_played = total_games
        self.stats.games_won = won_games
        self.stats.games_lost = lost_games


class PlayerStats(db.Entity):
    """
    Repräsentiert die Statistiken eines Spielers in der Datenbank.
    
    Attribute:
        id (int): Eindeutige ID des Statistik-Eintrags
        player (Player): Spieler, zu dem die Statistiken gehören
        games_played (int): Anzahl der gespielten Spiele
        games_won (int): Anzahl der gewonnenen Spiele
        games_lost (int): Anzahl der verlorenen Spiele
    """
    id = PrimaryKey(int, auto=True)
    player = Required(Player)
    games_played = Required(int, default=0)
    games_won = Required(int, default=0)
    games_lost = Required(int, default=0)
