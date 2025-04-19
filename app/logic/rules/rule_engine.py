"""
Regelmotor für die Magic the Gathering Desktop App.

Dieses Modul implementiert den Regelmotor, der die Spielregeln interpretiert und anwendet.
"""

from app.logic.rules.rule_parser import RuleParser


class RuleEngine:
    """
    Ein Regelmotor, der die MTG-Regeln interpretiert und anwendet.
    
    Diese Klasse verwendet den RuleParser, um auf die Regeln zuzugreifen
    und stellt Methoden bereit, um Regeln auf Spielsituationen anzuwenden.
    """
    
    def __init__(self, rule_parser=None):
        """
        Initialisiert den Regelmotor.
        
        Args:
            rule_parser (RuleParser, optional): Eine Instanz des RuleParser.
                Wenn None, wird eine neue Instanz erstellt.
        """
        self.rule_parser = rule_parser or RuleParser()
        
        # Regelspezifische Implementierungen
        self.rule_implementations = {
            # Beispiel: Regel 101.1 - Das Spiel beginnt mit dem Ziehen von 7 Karten
            '101': self._apply_game_start_rules,
            # Weitere Regeln werden hier implementiert
        }
    
    def get_rule_text(self, rule_number):
        """
        Gibt den Text einer Regel zurück.
        
        Args:
            rule_number (str): Die Nummer der Regel.
        
        Returns:
            str: Der Text der Regel oder None, wenn nicht gefunden.
        """
        rule = self.rule_parser.get_rule_by_number(rule_number)
        if rule:
            return rule['content']
        return None
    
    def apply_rule(self, rule_number, game_state):
        """
        Wendet eine bestimmte Regel auf einen Spielzustand an.
        
        Args:
            rule_number (str): Die Nummer der Regel.
            game_state (dict): Der aktuelle Spielzustand.
        
        Returns:
            dict: Der aktualisierte Spielzustand.
        """
        # Bestimme die Hauptregelkategorie (z.B. "101" für "101.1")
        main_rule = rule_number.split('.')[0]
        
        # Suche nach einer Implementierung für die Regel
        rule_impl = self.rule_implementations.get(main_rule)
        
        if rule_impl:
            # Wende die Regelimplementierung an
            return rule_impl(rule_number, game_state)
        else:
            # Keine spezifische Implementierung gefunden
            print(f"Keine Implementierung für Regel {rule_number} gefunden.")
            return game_state
    
    def check_rule_compliance(self, rule_number, game_state):
        """
        Überprüft, ob ein Spielzustand einer bestimmten Regel entspricht.
        
        Args:
            rule_number (str): Die Nummer der Regel.
            game_state (dict): Der zu überprüfende Spielzustand.
        
        Returns:
            bool: True, wenn der Spielzustand der Regel entspricht, sonst False.
            str: Fehlermeldung, wenn der Spielzustand nicht der Regel entspricht, sonst None.
        """
        # Implementierung für verschiedene Regeln hier
        # Dies ist ein Platzhalter - eigentliche Implementierung folgt später
        return True, None
    
    def get_applicable_rules(self, game_state, action):
        """
        Ermittelt, welche Regeln für eine bestimmte Aktion im aktuellen Spielzustand relevant sind.
        
        Args:
            game_state (dict): Der aktuelle Spielzustand.
            action (dict): Die auszuführende Aktion.
        
        Returns:
            list: Liste der relevanten Regelnummern.
        """
        # Dies ist ein Platzhalter - eigentliche Implementierung folgt später
        return []
    
    def get_rule_explanation(self, rule_number):
        """
        Gibt eine benutzerfreundliche Erklärung einer Regel zurück.
        
        Args:
            rule_number (str): Die Nummer der Regel.
        
        Returns:
            str: Eine Erklärung der Regel oder None, wenn nicht gefunden.
        """
        rule = self.rule_parser.get_rule_by_number(rule_number)
        if not rule:
            return None
        
        # Hier könnte eine vereinfachte Erklärung der Regel zurückgegeben werden
        # Für jetzt geben wir einfach den Originaltext zurück
        return rule['content']
    
    # Implementierungen für spezifische Regeln
    
    def _apply_game_start_rules(self, rule_number, game_state):
        """
        Implementiert die Regeln für den Spielstart (Regel 101).
        
        Args:
            rule_number (str): Die genaue Regelnummer.
            game_state (dict): Der aktuelle Spielzustand.
        
        Returns:
            dict: Der aktualisierte Spielzustand.
        """
        # Beispielimplementierung - eigentliche Implementierung folgt später
        # Für jetzt nur eine einfache Platzhalterimplementierung
        
        # Regel 101.1: Jeder Spieler beginnt mit 20 Lebenspunkten
        if rule_number == '101.1':
            if 'players' in game_state:
                for player_id, player_data in game_state['players'].items():
                    player_data['life'] = 20
        
        # Regel 101.4: Jeder Spieler zieht zu Beginn 7 Karten
        elif rule_number == '101.4':
            if 'players' in game_state:
                for player_id, player_data in game_state['players'].items():
                    # Implementierung des Kartenziehens würde hier erfolgen
                    pass
        
        return game_state
