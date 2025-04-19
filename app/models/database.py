"""
Datenbankverbindung und -konfiguration für die Magic the Gathering Desktop App.

Dieses Modul initialisiert die Verbindung zur Datenbank und definiert grundlegende Funktionen
für den Datenbankzugriff.
"""

import os
from pony.orm import Database, db_session, commit

# Erstellt eine Datenbankinstanz
db = Database()


def init_database(data_dir=None):
    """
    Initialisiert die Datenbankverbindung.
    
    Args:
        data_dir: Das Verzeichnis, in dem die Datenbankdatei gespeichert werden soll.
                 Wenn None, wird das Standardverzeichnis verwendet.
    
    Returns:
        Die initialisierte Datenbankinstanz.
    """
    # Wenn kein Datenpfad angegeben ist, verwende das Standardverzeichnis
    if data_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
    
    # Datenbankdatei erstellen oder verbinden
    db_path = os.path.join(data_dir, 'magic_tg_app.sqlite')
    db.bind(provider='sqlite', filename=db_path, create_db=True)
    
    # Hier werden die Entitäten definiert (aus anderen Moduldateien importiert)
    # Nachdem alle Modelle importiert wurden, werden die Tabellen erstellt
    # Dieser Import muss nach dem db.bind() erfolgen!
    from app.models.card import Card
    from app.models.deck import Deck, CardInDeck
    from app.models.player import Player, PlayerStats
    from app.models.game import Game
    
    # Erstellt die Tabellen in der Datenbank
    db.generate_mapping(create_tables=True)
    
    return db


def get_database():
    """
    Gibt die Datenbankinstanz zurück.
    
    Returns:
        Die Datenbankinstanz.
    """
    return db


@db_session
def clear_database():
    """Löscht alle Daten aus der Datenbank (für Tests)."""
    # Diese Funktion sollte mit Vorsicht und nur in Testumgebungen verwendet werden!
    commit()  # Bestätigt alle ausstehenden Änderungen


@db_session
def populate_test_data():
    """Fügt Testdaten in die Datenbank ein."""
    # Hier werden später Beispieldaten eingefügt
    pass
