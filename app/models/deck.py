"""
Deck-Modell für die Magic the Gathering Desktop App.

Dieses Modul definiert das Datenmodell für Spielerdecks.
"""

from pony.orm import Required, Optional, Set, PrimaryKey
from app.models.database import db


class Deck(db.Entity):
    """
    Repräsentiert ein Magic the Gathering Deck in der Datenbank.
    
    Attribute:
        id (int): Eindeutige ID des Decks
        name (str): Name des Decks
        player (Player): Spieler, dem das Deck gehört
        format (str): Format des Decks (Standard, Modern, etc.)
        cards (Set[CardInDeck]): Karten im Deck
    """
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    player = Required('Player')
    format = Required(str)  # Standard, Modern, Commander, etc.
    cards = Set('CardInDeck')
    
    def get_card_count(self):
        """
        Gibt die Gesamtzahl der Karten im Deck zurück.
        
        Returns:
            int: Anzahl der Karten im Deck
        """
        return sum(card_in_deck.quantity for card_in_deck in self.cards)
    
    def get_unique_card_count(self):
        """
        Gibt die Anzahl der einzigartigen Karten im Deck zurück.
        
        Returns:
            int: Anzahl der einzigartigen Karten im Deck
        """
        return len(self.cards)
    
    def is_valid_for_format(self):
        """
        Überprüft, ob das Deck für das angegebene Format gültig ist.
        
        Returns:
            bool: True, wenn das Deck gültig ist, sonst False
            str: Fehlermeldung, wenn das Deck ungültig ist, sonst None
        """
        # Implementierung der Format-Validierung hier
        # Beispiel für Standard-Format:
        if self.format.lower() == 'standard':
            # Mindestgröße prüfen
            if self.get_card_count() < 60:
                return False, "Das Deck muss mindestens 60 Karten enthalten"
            
            # Karten-Limits prüfen (max. 4 Karten mit demselben Namen, außer Grundländer)
            card_counts = {}
            for card_in_deck in self.cards:
                card_name = card_in_deck.card.name
                # Grundländer ignorieren
                if card_in_deck.card.is_land() and "Basic" in card_in_deck.card.card_type:
                    continue
                    
                if card_name not in card_counts:
                    card_counts[card_name] = 0
                card_counts[card_name] += card_in_deck.quantity
                
                if card_counts[card_name] > 4:
                    return False, f"Das Deck enthält mehr als 4 Exemplare von {card_name}"
            
            return True, None
        
        # Weitere Formate können hier implementiert werden
        return True, None


class CardInDeck(db.Entity):
    """
    Repräsentiert eine Karte in einem Deck mit Anzahl.
    
    Attribute:
        id (int): Eindeutige ID
        deck (Deck): Deck, zu dem die Karte gehört
        card (Card): Die Karte selbst
        quantity (int): Anzahl dieser Karte im Deck
    """
    id = PrimaryKey(int, auto=True)
    deck = Required(Deck)
    card = Required('Card')
    quantity = Required(int, default=1)
