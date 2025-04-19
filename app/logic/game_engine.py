"""
Spielmotor für die Magic the Gathering Desktop App.

Dieses Modul implementiert den Hauptspielmotor, der den Spielablauf steuert.
"""

import json
import datetime
from app.logic.rules.rule_engine import RuleEngine
from app.models.game import Game
from pony.orm import db_session


class GameEngine:
    """
    Hauptspielmotor für Magic the Gathering.
    
    Diese Klasse verwaltet den Spielablauf und den Spielzustand.
    Sie interagiert mit dem Regelmotor, um die Spielregeln anzuwenden.
    """
    
    def __init__(self, game_id=None):
        """
        Initialisiert den Spielmotor.
        
        Args:
            game_id (int, optional): Die ID eines existierenden Spiels.
                Wenn None, wird ein neues Spiel erstellt.
        """
        self.rule_engine = RuleEngine()
        self.game_id = game_id
        self.game_state = None
        
        # Lade ein existierendes Spiel oder erstelle ein neues
        if game_id:
            self.load_game(game_id)
        else:
            self.initialize_new_game()
    
    @db_session
    def load_game(self, game_id):
        """
        Lädt ein existierendes Spiel aus der Datenbank.
        
        Args:
            game_id (int): Die ID des zu ladenden Spiels.
        
        Returns:
            bool: True, wenn das Spiel erfolgreich geladen wurde, sonst False.
        """
        game = Game.get(id=game_id)
        if not game:
            print(f"Spiel mit ID {game_id} nicht gefunden.")
            return False
        
        self.game_id = game_id
        self.game_state = game.get_game_state()
        
        if not self.game_state:
            # Falls kein Spielzustand existiert, initialisiere einen neuen
            self.initialize_new_game()
            
            # Speichere den neuen Zustand
            game.set_game_state(self.game_state)
        
        print(f"Spiel mit ID {game_id} geladen.")
        return True
    
    def initialize_new_game(self):
        """Initialisiert ein neues Spiel mit einem leeren Spielzustand."""
        self.game_state = {
            'turn_number': 0,
            'active_player_id': None,
            'phase': 'setup',
            'stack': [],
            'players': {},
            'battlefield': [],
            'exile': [],
            'command': [],
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        print("Neues Spiel initialisiert.")
    
    @db_session
    def create_game(self, player1_id, player2_id, player1_deck_id, player2_deck_id):
        """
        Erstellt ein neues Spiel in der Datenbank.
        
        Args:
            player1_id (int): Die ID des ersten Spielers.
            player2_id (int): Die ID des zweiten Spielers.
            player1_deck_id (int): Die ID des Decks des ersten Spielers.
            player2_deck_id (int): Die ID des Decks des zweiten Spielers.
        
        Returns:
            int: Die ID des neuen Spiels oder None bei einem Fehler.
        """
        from app.models.player import Player
        from app.models.deck import Deck
        
        # Prüfe, ob die Spieler und Decks existieren
        player1 = Player.get(id=player1_id)
        player2 = Player.get(id=player2_id)
        deck1 = Deck.get(id=player1_deck_id)
        deck2 = Deck.get(id=player2_deck_id)
        
        if not all([player1, player2, deck1, deck2]):
            print("Spieler oder Decks nicht gefunden.")
            return None
        
        # Prüfe, ob die Decks den Spielern gehören
        if deck1.player.id != player1_id or deck2.player.id != player2_id:
            print("Decks gehören nicht den angegebenen Spielern.")
            return None
        
        # Erstelle ein neues Spiel
        game = Game(
            player1=player1,
            player2=player2,
            start_time=datetime.datetime.now()
        )
        
        # Initialisiere den Spielzustand
        self.initialize_new_game()
        
        # Füge Spielerinfos hinzu
        self.game_state['players'] = {
            str(player1.id): {
                'name': player1.name,
                'life': 20,
                'mana_pool': {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Colorless': 0},
                'library': [],  # Wird später mit Karten gefüllt
                'hand': [],
                'graveyard': []
            },
            str(player2.id): {
                'name': player2.name,
                'life': 20,
                'mana_pool': {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Colorless': 0},
                'library': [],  # Wird später mit Karten gefüllt
                'hand': [],
                'graveyard': []
            }
        }
        
        # Lade die Karten der Decks
        self._load_deck_cards(deck1, str(player1.id))
        self._load_deck_cards(deck2, str(player2.id))
        
        # Speichere den Spielzustand
        game.set_game_state(self.game_state)
        
        # Setze die aktiven Spieler
        # Der erste Spieler wird zufällig bestimmt (hier einfach player1)
        self.game_state['active_player_id'] = str(player1.id)
        
        # Speichere die Spiel-ID
        self.game_id = game.id
        
        print(f"Neues Spiel erstellt mit ID {game.id}")
        return game.id
    
    def _load_deck_cards(self, deck, player_id):
        """
        Lädt die Karten eines Decks in den Spielzustand.
        
        Args:
            deck (Deck): Das zu ladende Deck.
            player_id (str): Die ID des Spielers, dem das Deck gehört.
        """
        from pony.orm import select
        
        # Sammle alle Karten aus dem Deck
        library = []
        
        for card_in_deck in deck.cards:
            card = card_in_deck.card
            
            # Füge jede Karte entsprechend ihrer Anzahl zum Deck hinzu
            for _ in range(card_in_deck.quantity):
                card_instance = {
                    'id': f"{card.id}_{len(library)}",  # Eindeutige ID für diese Karteninstanz
                    'card_id': card.id,
                    'name': card.name,
                    'type': card.card_type,
                    'mana_cost': card.mana_cost,
                    'colors': card.get_colors_list(),
                    'rules_text': card.rules_text,
                    'power': card.power,
                    'toughness': card.toughness,
                    'image_path': card.image_path,
                    'tapped': False,
                    'counters': {},
                    'attachments': []
                }
                
                library.append(card_instance)
        
        # Mische das Deck
        import random
        random.shuffle(library)
        
        # Füge das Deck zum Spielzustand hinzu
        self.game_state['players'][player_id]['library'] = library
    
    @db_session
    def save_game_state(self):
        """
        Speichert den aktuellen Spielzustand in der Datenbank.
        
        Returns:
            bool: True, wenn der Spielzustand erfolgreich gespeichert wurde, sonst False.
        """
        if not self.game_id:
            print("Kein aktives Spiel zum Speichern.")
            return False
        
        game = Game.get(id=self.game_id)
        if not game:
            print(f"Spiel mit ID {self.game_id} nicht gefunden.")
            return False
        
        # Aktualisiere den Zeitstempel
        self.game_state['timestamp'] = datetime.datetime.now().isoformat()
        
        # Speichere den Spielzustand
        game.set_game_state(self.game_state)
        
        print(f"Spielzustand für Spiel {self.game_id} gespeichert.")
        return True
    
    @db_session
    def end_game(self, winner_id=None):
        """
        Beendet das aktuelle Spiel und setzt den Gewinner.
        
        Args:
            winner_id (int, optional): Die ID des Gewinners.
                Wenn None, wird kein Gewinner gesetzt.
        
        Returns:
            bool: True, wenn das Spiel erfolgreich beendet wurde, sonst False.
        """
        if not self.game_id:
            print("Kein aktives Spiel zum Beenden.")
            return False
        
        game = Game.get(id=self.game_id)
        if not game:
            print(f"Spiel mit ID {self.game_id} nicht gefunden.")
            return False
        
        from app.models.player import Player
        
        winner = None
        if winner_id:
            winner = Player.get(id=winner_id)
            if not winner:
                print(f"Spieler mit ID {winner_id} nicht gefunden.")
        
        # Beende das Spiel
        game.end_game(winner)
        
        # Aktualisiere den Spielzustand
        self.game_state['phase'] = 'ended'
        self.game_state['winner_id'] = str(winner_id) if winner_id else None
        self.game_state['end_time'] = datetime.datetime.now().isoformat()
        
        # Speichere den finalen Spielzustand
        game.set_game_state(self.game_state)
        
        print(f"Spiel {self.game_id} beendet. Gewinner: {winner.name if winner else 'Unentschieden'}")
        return True
    
    def start_turn(self, player_id):
        """
        Startet den Zug eines Spielers.
        
        Args:
            player_id (str): Die ID des aktiven Spielers.
        
        Returns:
            dict: Der aktualisierte Spielzustand.
        """
        if player_id not in self.game_state['players']:
            print(f"Spieler mit ID {player_id} nicht im Spiel.")
            return self.game_state
        
        # Inkrementiere die Zugnummer
        self.game_state['turn_number'] += 1
        
        # Setze den aktiven Spieler
        self.game_state['active_player_id'] = player_id
        
        # Setze die Phase auf "untap"
        self.game_state['phase'] = 'untap'
        
        print(f"Zug {self.game_state['turn_number']} für Spieler {player_id} gestartet.")
        return self.game_state
    
    def change_phase(self, new_phase):
        """
        Wechselt die aktuelle Spielphase.
        
        Args:
            new_phase (str): Die neue Phase.
        
        Returns:
            dict: Der aktualisierte Spielzustand.
        """
        valid_phases = [
            'untap', 'upkeep', 'draw', 'main1', 
            'combat_begin', 'combat_attackers', 'combat_blockers', 'combat_damage', 'combat_end',
            'main2', 'end', 'cleanup'
        ]
        
        if new_phase not in valid_phases:
            print(f"Ungültige Phase: {new_phase}")
            return self.game_state
        
        # Setze die neue Phase
        old_phase = self.game_state['phase']
        self.game_state['phase'] = new_phase
        
        print(f"Phase gewechselt von {old_phase} zu {new_phase}")
        
        # Führe phasenspezifische Aktionen aus
        if new_phase == 'untap':
            self._handle_untap_phase()
        elif new_phase == 'draw':
            self._handle_draw_phase()
        elif new_phase == 'cleanup':
            self._handle_cleanup_phase()
        
        return self.game_state
    
    def _handle_untap_phase(self):
        """Führt die Aktionen der Enttapp-Phase aus."""
        active_player_id = self.game_state['active_player_id']
        
        # Enttappe alle Karten des aktiven Spielers auf dem Schlachtfeld
        for card in self.game_state['battlefield']:
            if card.get('controller_id') == active_player_id:
                card['tapped'] = False
        
        print(f"Karten für Spieler {active_player_id} enttappt.")
    
    def _handle_draw_phase(self):
        """Führt die Aktionen der Ziehphase aus."""
        active_player_id = self.game_state['active_player_id']
        
        # Ziehe eine Karte für den aktiven Spieler
        player_data = self.game_state['players'][active_player_id]
        
        if player_data['library']:
            # Nehme die oberste Karte von der Bibliothek
            card = player_data['library'].pop(0)
            
            # Füge die Karte der Hand hinzu
            player_data['hand'].append(card)
            
            print(f"Spieler {active_player_id} hat eine Karte gezogen: {card['name']}")
        else:
            # Keine Karten mehr in der Bibliothek - Spieler verliert
            print(f"Spieler {active_player_id} kann keine Karte ziehen und verliert!")
            
            # Setze den anderen Spieler als Gewinner
            other_player_id = next(
                pid for pid in self.game_state['players'].keys() 
                if pid != active_player_id
            )
            
            # Markiere das Spiel als beendet mit dem Gewinner
            self.game_state['phase'] = 'ended'
            self.game_state['winner_id'] = other_player_id
    
    def _handle_cleanup_phase(self):
        """Führt die Aktionen der Aufräumphase aus."""
        active_player_id = self.game_state['active_player_id']
        player_data = self.game_state['players'][active_player_id]
        
        # Setze "Bis zum Ende des Zuges"-Effekte zurück
        # (Wird später implementiert)
        
        # Prüfe Handkartenlimit (normalerweise 7)
        if len(player_data['hand']) > 7:
            # Hier wird später die Auswahl der abzuwerfenden Karten implementiert
            # Für jetzt einfach eine Meldung
            print(f"Spieler {active_player_id} muss Karten abwerfen (Handkartenlimit: 7)")
        
        print(f"Aufräumphase für Spieler {active_player_id} abgeschlossen.")
    
    def play_card(self, player_id, card_instance_id, target_ids=None):
        """
        Spielt eine Karte aus der Hand eines Spielers.
        
        Args:
            player_id (str): Die ID des Spielers, der die Karte spielt.
            card_instance_id (str): Die Instanz-ID der zu spielenden Karte.
            target_ids (list, optional): Liste von Ziel-IDs für die Karte.
        
        Returns:
            dict: Der aktualisierte Spielzustand.
            str: Fehlermeldung bei einem Fehler, sonst None.
        """
        # Implementierung folgt später
        # Dies ist ein Platzhalter
        
        return self.game_state, None
    
    def attack_with_creatures(self, player_id, attacking_creature_ids, target_player_id):
        """
        Greift mit Kreaturen einen Spieler an.
        
        Args:
            player_id (str): Die ID des angreifenden Spielers.
            attacking_creature_ids (list): Liste von Kreaturen-IDs, die angreifen.
            target_player_id (str): Die ID des angegriffenen Spielers.
        
        Returns:
            dict: Der aktualisierte Spielzustand.
            str: Fehlermeldung bei einem Fehler, sonst None.
        """
        # Implementierung folgt später
        # Dies ist ein Platzhalter
        
        return self.game_state, None
    
    def declare_blockers(self, player_id, blocking_assignments):
        """
        Deklariert Blocker für angreifende Kreaturen.
        
        Args:
            player_id (str): Die ID des blockenden Spielers.
            blocking_assignments (dict): Mapping von blockenden Kreaturen zu angreifenden Kreaturen.
                Format: {blocker_id: attacker_id}
        
        Returns:
            dict: Der aktualisierte Spielzustand.
            str: Fehlermeldung bei einem Fehler, sonst None.
        """
        # Implementierung folgt später
        # Dies ist ein Platzhalter
        
        return self.game_state, None
    
    def add_mana_to_pool(self, player_id, mana_type, amount=1):
        """
        Fügt Mana zum Manapool eines Spielers hinzu.
        
        Args:
            player_id (str): Die ID des Spielers.
            mana_type (str): Der Typ des Manas (White, Blue, Black, Red, Green, Colorless).
            amount (int, optional): Die Menge des hinzuzufügenden Manas. Default ist 1.
        
        Returns:
            dict: Der aktualisierte Spielzustand.
            str: Fehlermeldung bei einem Fehler, sonst None.
        """
        if player_id not in self.game_state['players']:
            return self.game_state, f"Spieler mit ID {player_id} nicht im Spiel."
        
        player_data = self.game_state['players'][player_id]
        
        if mana_type not in player_data['mana_pool']:
            return self.game_state, f"Ungültiger Mana-Typ: {mana_type}"
        
        # Füge Mana hinzu
        player_data['mana_pool'][mana_type] += amount
        
        print(f"Spieler {player_id} hat {amount} {mana_type} Mana erhalten.")
        return self.game_state, None
    
    def pay_mana_from_pool(self, player_id, mana_cost):
        """
        Bezahlt Mana aus dem Manapool eines Spielers.
        
        Args:
            player_id (str): Die ID des Spielers.
            mana_cost (dict): Die zu bezahlenden Manakosten.
                Format: {'White': 1, 'Blue': 0, 'Black': 2, 'Red': 0, 'Green': 0, 'Colorless': 3}
        
        Returns:
            bool: True, wenn die Kosten bezahlt werden konnten, sonst False.
            str: Fehlermeldung bei einem Fehler, sonst None.
        """
        if player_id not in self.game_state['players']:
            return False, f"Spieler mit ID {player_id} nicht im Spiel."
        
        player_data = self.game_state['players'][player_id]
        
        # Prüfe, ob genug Mana vorhanden ist
        for mana_type, amount in mana_cost.items():
            if mana_type not in player_data['mana_pool']:
                return False, f"Ungültiger Mana-Typ: {mana_type}"
            
            if player_data['mana_pool'][mana_type] < amount:
                return False, f"Nicht genug {mana_type} Mana verfügbar."
        
        # Bezahle Mana
        for mana_type, amount in mana_cost.items():
            player_data['mana_pool'][mana_type] -= amount
        
        print(f"Spieler {player_id} hat Mana bezahlt.")
        return True, None
    
    def draw_cards(self, player_id, count=1):
        """
        Lässt einen Spieler Karten ziehen.
        
        Args:
            player_id (str): Die ID des Spielers, der Karten zieht.
            count (int, optional): Die Anzahl der zu ziehenden Karten. Default ist 1.
        
        Returns:
            dict: Der aktualisierte Spielzustand.
            str: Fehlermeldung bei einem Fehler, sonst None.
        """
        if player_id not in self.game_state['players']:
            return self.game_state, f"Spieler mit ID {player_id} nicht im Spiel."
        
        player_data = self.game_state['players'][player_id]
        
        # Ziehe Karten
        cards_drawn = []
        for _ in range(count):
            if not player_data['library']:
                # Keine Karten mehr in der Bibliothek - Spieler verliert
                print(f"Spieler {player_id} kann keine Karte ziehen und verliert!")
                
                # Setze den anderen Spieler als Gewinner
                other_player_id = next(
                    pid for pid in self.game_state['players'].keys() 
                    if pid != player_id
                )
                
                # Markiere das Spiel als beendet mit dem Gewinner
                self.game_state['phase'] = 'ended'
                self.game_state['winner_id'] = other_player_id
                
                return self.game_state, f"Spieler {player_id} hat verloren (kann keine Karte ziehen)."
            
            # Nehme die oberste Karte von der Bibliothek
            card = player_data['library'].pop(0)
            
            # Füge die Karte der Hand hinzu
            player_data['hand'].append(card)
            cards_drawn.append(card['name'])
        
        print(f"Spieler {player_id} hat {count} Karte(n) gezogen: {', '.join(cards_drawn)}")
        return self.game_state, None
    
    def get_card_by_id(self, card_instance_id):
        """
        Findet eine Karte im Spielzustand anhand ihrer Instanz-ID.
        
        Args:
            card_instance_id (str): Die Instanz-ID der Karte.
        
        Returns:
            dict: Die Karteninstanz oder None, wenn nicht gefunden.
            str: Zone, in der die Karte gefunden wurde oder None, wenn nicht gefunden.
            str: Besitzer-ID der Karte oder None, wenn nicht gefunden.
        """
        # Suche auf dem Schlachtfeld
        for card in self.game_state['battlefield']:
            if card['id'] == card_instance_id:
                return card, 'battlefield', card.get('controller_id')
        
        # Suche im Exil
        for card in self.game_state['exile']:
            if card['id'] == card_instance_id:
                return card, 'exile', card.get('owner_id')
        
        # Suche im Command-Bereich
        for card in self.game_state['command']:
            if card['id'] == card_instance_id:
                return card, 'command', card.get('owner_id')
        
        # Suche in den Spielerbereichen
        for player_id, player_data in self.game_state['players'].items():
            # Suche in der Hand
            for card in player_data['hand']:
                if card['id'] == card_instance_id:
                    return card, 'hand', player_id
            
            # Suche in der Bibliothek
            for card in player_data['library']:
                if card['id'] == card_instance_id:
                    return card, 'library', player_id
            
            # Suche im Friedhof
            for card in player_data['graveyard']:
                if card['id'] == card_instance_id:
                    return card, 'graveyard', player_id
        
        return None, None, None
    
    def move_card(self, card_instance_id, from_zone, to_zone, player_id=None):
        """
        Bewegt eine Karte von einer Zone in eine andere.
        
        Args:
            card_instance_id (str): Die Instanz-ID der zu bewegenden Karte.
            from_zone (str): Die Ausgangszone.
            to_zone (str): Die Zielzone.
            player_id (str, optional): Die ID des Spielers (für spielerspezifische Zonen).
        
        Returns:
            dict: Der aktualisierte Spielzustand.
            str: Fehlermeldung bei einem Fehler, sonst None.
        """
        # Finde die Karte
        card, current_zone, owner_id = self.get_card_by_id(card_instance_id)
        
        if not card:
            return self.game_state, f"Karte mit ID {card_instance_id} nicht gefunden."
        
        if current_zone != from_zone:
            return self.game_state, f"Karte ist nicht in der angegebenen Zone {from_zone}, sondern in {current_zone}."
        
        # Bestimme den Spieler für spielerspezifische Zonen
        target_player_id = player_id or owner_id
        
        if target_player_id not in self.game_state['players']:
            return self.game_state, f"Spieler mit ID {target_player_id} nicht im Spiel."
        
        # Entferne die Karte aus der Ausgangszone
        if from_zone == 'battlefield':
            self.game_state['battlefield'] = [c for c in self.game_state['battlefield'] if c['id'] != card_instance_id]
        elif from_zone == 'exile':
            self.game_state['exile'] = [c for c in self.game_state['exile'] if c['id'] != card_instance_id]
        elif from_zone == 'command':
            self.game_state['command'] = [c for c in self.game_state['command'] if c['id'] != card_instance_id]
        elif from_zone in ['hand', 'library', 'graveyard']:
            self.game_state['players'][owner_id][from_zone] = [
                c for c in self.game_state['players'][owner_id][from_zone] if c['id'] != card_instance_id
            ]
        
        # Füge die Karte zur Zielzone hinzu
        if to_zone == 'battlefield':
            card['controller_id'] = target_player_id
            self.game_state['battlefield'].append(card)
        elif to_zone == 'exile':
            self.game_state['exile'].append(card)
        elif to_zone == 'command':
            self.game_state['command'].append(card)
        elif to_zone in ['hand', 'library', 'graveyard']:
            self.game_state['players'][target_player_id][to_zone].append(card)
        
        print(f"Karte {card['name']} wurde von {from_zone} nach {to_zone} bewegt.")
        return self.game_state, None
