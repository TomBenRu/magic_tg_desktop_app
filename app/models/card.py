"""
Kartenmodell für die Magic the Gathering Desktop App.

Dieses Modul definiert das Datenmodell für Magic the Gathering Karten.
"""

import os
from pony.orm import Required, Optional, Set, PrimaryKey
from app.models.database import db


class Card(db.Entity):
    """
    Repräsentiert eine Magic the Gathering Karte in der Datenbank.
    
    Attribute:
        id (int): Eindeutige ID der Karte
        name (str): Name der Karte
        card_type (str): Typ der Karte (Creature, Instant, Sorcery, etc.)
        mana_cost (str): Manakosten der Karte
        colors (str): Farben der Karte
        rules_text (str): Regeltext der Karte
        power (int, optional): Stärke für Kreaturen
        toughness (int, optional): Widerstandskraft für Kreaturen
        rarity (str): Seltenheit der Karte
        set_code (str): Set-Code der Karte
        image_path (str): Pfad zum Kartenbild
        decks (Set[CardInDeck]): Decks, in denen diese Karte enthalten ist
    """
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    card_type = Required(str)  # Creature, Instant, Sorcery, etc.
    mana_cost = Required(str)
    colors = Required(str)  # Komma-getrennte Liste von Farben oder JSON
    rules_text = Optional(str)
    power = Optional(int)  # Für Kreaturen
    toughness = Optional(int)  # Für Kreaturen
    rarity = Required(str)  # Common, Uncommon, Rare, Mythic Rare
    set_code = Required(str)
    image_path = Optional(str)
    decks = Set('CardInDeck')
    
    def get_image_full_path(self):
        """
        Gibt den vollständigen Pfad zum Kartenbild zurück.
        
        Returns:
            str: Vollständiger Pfad zum Kartenbild oder None wenn kein Bild existiert.
        """
        if not self.image_path:
            return None
            
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        cards_dir = os.path.join(base_dir, 'data', 'cards')
        return os.path.join(cards_dir, self.image_path)
    
    def get_colors_list(self):
        """
        Gibt eine Liste der Kartenfarben zurück.
        
        Returns:
            list: Liste der Kartenfarben
        """
        if not self.colors:
            return []
        return [color.strip() for color in self.colors.split(',')]
    
    def is_creature(self):
        """
        Prüft, ob die Karte eine Kreatur ist.
        
        Returns:
            bool: True, wenn die Karte eine Kreatur ist, sonst False
        """
        return 'Creature' in self.card_type
    
    def is_land(self):
        """
        Prüft, ob die Karte ein Land ist.
        
        Returns:
            bool: True, wenn die Karte ein Land ist, sonst False
        """
        return 'Land' in self.card_type
    
    def is_spell(self):
        """
        Prüft, ob die Karte ein Zauberspruch ist (Instant oder Sorcery).
        
        Returns:
            bool: True, wenn die Karte ein Zauberspruch ist, sonst False
        """
        return 'Instant' in self.card_type or 'Sorcery' in self.card_type
