"""
Regelparser für die Magic the Gathering Desktop App.

Dieses Modul enthält Funktionen zum Parsen der umfangreichen Magic the Gathering Regeln.
"""

import os
import re
from pathlib import Path


class RuleParser:
    """
    Parser für die umfangreichen Magic the Gathering Regeln.
    
    Diese Klasse liest die Regeldatei ein und stellt Methoden bereit,
    um auf die Regeln zuzugreifen und sie zu durchsuchen.
    """
    
    def __init__(self, rules_file=None):
        """
        Initialisiert den Regelparser.
        
        Args:
            rules_file (str, optional): Pfad zur Regeldatei.
                Wenn None, wird die Standarddatei verwendet.
        """
        if rules_file is None:
            base_dir = Path(__file__).parent.parent.parent.parent
            rules_file = base_dir / "mtc_comprehensive_rules.txt"
        
        self.rules_file = str(rules_file)
        self.rules_text = ""
        self.rules_by_number = {}
        self.rules_by_section = {}
        self.glossary = {}
        
        # Lade die Regeln beim Initialisieren
        self.load_rules()
    
    def load_rules(self):
        """Lädt die Regeln aus der Regeldatei."""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                self.rules_text = f.read()
            
            # Parse die Regeln
            self._parse_rules()
            print(f"Regeln aus {self.rules_file} erfolgreich geladen.")
        except FileNotFoundError:
            print(f"Regeldatei {self.rules_file} nicht gefunden.")
            self.rules_text = ""
        except Exception as e:
            print(f"Fehler beim Laden der Regeln: {e}")
            self.rules_text = ""
    
    def _parse_rules(self):
        """Parsed die geladenen Regeln und indexiert sie."""
        if not self.rules_text:
            return
        
        # Regex-Muster für Regelnummern (z.B. "101. Starting the Game")
        rule_pattern = re.compile(r'^(\d+)(?:\.\d+)*\.\s+(.+)$', re.MULTILINE)
        
        # Finde alle Regeln mit ihren Nummern
        for match in rule_pattern.finditer(self.rules_text):
            rule_number = match.group(1)
            rule_title = match.group(2)
            
            # Finde den Inhalt der Regel (bis zur nächsten Regel)
            start_pos = match.start()
            next_match = rule_pattern.search(self.rules_text, match.end())
            end_pos = next_match.start() if next_match else len(self.rules_text)
            
            rule_content = self.rules_text[start_pos:end_pos].strip()
            
            # Speichere die Regel
            self.rules_by_number[rule_number] = {
                'title': rule_title,
                'content': rule_content
            }
            
            # Gruppiere nach Hauptabschnitt
            section = rule_number
            if section not in self.rules_by_section:
                self.rules_by_section[section] = []
            
            self.rules_by_section[section].append({
                'number': rule_number,
                'title': rule_title,
                'content': rule_content
            })
        
        # Versuche, das Glossar zu extrahieren (falls vorhanden)
        self._parse_glossary()
    
    def _parse_glossary(self):
        """Versucht, das Glossar aus den Regeln zu extrahieren."""
        # Suche nach dem Glossarteil in den Regeln
        glossary_pattern = re.compile(r'Glossary\s*\n+(.+?)(?:\n{2,}|$)', re.DOTALL)
        glossary_match = glossary_pattern.search(self.rules_text)
        
        if glossary_match:
            glossary_text = glossary_match.group(1)
            
            # Extrahiere Einträge aus dem Glossar
            entry_pattern = re.compile(r'([A-Za-z\s]+):\s+(.+?)(?=\n[A-Za-z\s]+:|$)', re.DOTALL)
            
            for entry_match in entry_pattern.finditer(glossary_text):
                term = entry_match.group(1).strip()
                definition = entry_match.group(2).strip().replace('\n', ' ')
                
                self.glossary[term] = definition
    
    def get_rule_by_number(self, rule_number):
        """
        Gibt eine Regel basierend auf ihrer Nummer zurück.
        
        Args:
            rule_number (str): Die Nummer der Regel.
        
        Returns:
            dict: Die Regel mit Titel und Inhalt oder None, wenn nicht gefunden.
        """
        return self.rules_by_number.get(rule_number)
    
    def get_rules_in_section(self, section):
        """
        Gibt alle Regeln in einem Abschnitt zurück.
        
        Args:
            section (str): Die Abschnittsnummer.
        
        Returns:
            list: Liste von Regeln im Abschnitt oder leere Liste, wenn nicht gefunden.
        """
        return self.rules_by_section.get(section, [])
    
    def search_rules(self, query):
        """
        Durchsucht die Regeln nach einem Suchbegriff.
        
        Args:
            query (str): Der Suchbegriff.
        
        Returns:
            list: Liste von Regeln, die den Suchbegriff enthalten.
        """
        results = []
        query = query.lower()
        
        for rule_number, rule_data in self.rules_by_number.items():
            title = rule_data['title'].lower()
            content = rule_data['content'].lower()
            
            if query in title or query in content:
                results.append({
                    'number': rule_number,
                    'title': rule_data['title'],
                    'content': rule_data['content']
                })
        
        return results
    
    def get_glossary_term(self, term):
        """
        Gibt die Definition eines Glossareintrags zurück.
        
        Args:
            term (str): Der gesuchte Begriff.
        
        Returns:
            str: Die Definition des Begriffs oder None, wenn nicht gefunden.
        """
        return self.glossary.get(term)
    
    def search_glossary(self, query):
        """
        Durchsucht das Glossar nach einem Suchbegriff.
        
        Args:
            query (str): Der Suchbegriff.
        
        Returns:
            dict: Dictionary mit den passenden Glossareinträgen.
        """
        results = {}
        query = query.lower()
        
        for term, definition in self.glossary.items():
            if query in term.lower() or query in definition.lower():
                results[term] = definition
        
        return results
