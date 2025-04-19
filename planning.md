# Magic the Gathering Desktop App - Projektplanung

## Projektübersicht
Diese Anwendung ermöglicht es zwei Spielern, auf demselben Rechner Magic the Gathering gegeneinander zu spielen. Die Spieler können individuelle Decks zusammenstellen und in einem "Constructed Format" spielen. Die App implementiert die vollständigen offiziellen Regeln von Magic the Gathering.

## Technologien
- **Frontend**: PySide6 (Qt für Python)
- **Datenbank-ORM**: PonyORM
- **Datenbank**: SQLite
- **Bildverwaltung**: Referenzen auf Kartenbilder im Cards-Ordner

## Architektur

### Schichtenarchitektur
1. **Präsentationsschicht**: PySide6 GUI
2. **Geschäftslogikschicht**: Spielregeln, Spielzustände, Spielablauf
3. **Datenzugriffsschicht**: PonyORM und SQLite

### Modulare Struktur
```
magic_tg_desktop_app/
│
├── app/                        # Hauptanwendungspaket
│   ├── __init__.py
│   ├── main.py                 # Anwendungseinstiegspunkt
│   ├── gui/                    # GUI-Komponenten
│   │   ├── __init__.py
│   │   ├── main_window.py      # Hauptfenster
│   │   ├── deck_builder.py     # Deck-Builder Interface
│   │   ├── game_board.py       # Spielbrett Interface
│   │   └── widgets/            # Wiederverwendbare UI-Komponenten
│   │
│   ├── models/                 # Datenmodelle
│   │   ├── __init__.py
│   │   ├── database.py         # Datenbankverbindung und -konfiguration
│   │   ├── card.py             # Kartenmodell
│   │   ├── deck.py             # Deckmodell
│   │   ├── player.py           # Spielermodell
│   │   └── game.py             # Spielmodell
│   │
│   ├── logic/                  # Spiellogik
│   │   ├── __init__.py
│   │   ├── game_engine.py      # Hauptspielmotor
│   │   ├── phases.py           # Spielphasen
│   │   ├── actions.py          # Spielaktionen
│   │   ├── card_effects.py     # Karteneffekte
│   │   ├── targeting.py        # Zielbestimmung
│   │   └── rules/              # Regelimplementierungen
│   │       ├── __init__.py
│   │       ├── rule_parser.py  # Parser für die Regeltextdatei
│   │       └── rule_engine.py  # Regelmotor
│   │
│   └── utils/                  # Hilfsfunktionen
│       ├── __init__.py
│       ├── card_loader.py      # Laden von Karten aus der Datenbank
│       └── image_manager.py    # Verwaltung von Kartenbildern
│
├── data/                       # Datendateien
│   ├── database.sqlite         # SQLite-Datenbank
│   └── cards/                  # Kartenbilder
│
├── resources/                  # Statische Ressourcen
│   ├── images/                 # UI-Bilder
│   └── styles/                 # CSS-Stile
│
├── tests/                      # Testpaket
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_logic.py
│   └── test_gui.py
│
├── mtc_comprehensive_rules.txt # Magic Regeln (bereits vorhanden)
├── requirements.txt            # Abhängigkeiten
├── README.md                   # Projektdokumentation
└── setup.py                    # Installationsskript
```

## Datenmodell

### Entitäten
1. **Card (Karte)**
   - id: Integer (PK)
   - name: String
   - card_type: String (Creature, Instant, Sorcery, etc.)
   - subtype: String (Human, Elf, etc.)
   - mana_cost: String
   - colors: String
   - rules_text: String
   - power: Integer (für Kreaturen)
   - toughness: Integer (für Kreaturen)
   - rarity: String
   - set_code: String
   - image_path: String (Pfad zum Kartenbild)

2. **Deck**
   - id: Integer (PK)
   - name: String
   - player_id: Integer (FK)
   - format: String
   - cards: Relation zu CardInDeck

3. **CardInDeck**
   - id: Integer (PK)
   - deck_id: Integer (FK)
   - card_id: Integer (FK)
   - quantity: Integer

4. **Player (Spieler)**
   - id: Integer (PK)
   - name: String
   - stats: Relation zu PlayerStats

5. **PlayerStats**
   - id: Integer (PK)
   - player_id: Integer (FK)
   - games_played: Integer
   - games_won: Integer
   - games_lost: Integer

6. **Game (Spiel)**
   - id: Integer (PK)
   - player1_id: Integer (FK)
   - player2_id: Integer (FK)
   - winner_id: Integer (FK, optional)
   - start_time: DateTime
   - end_time: DateTime (optional)
   - game_state: JSON (Spielzustand)

## Entwicklungsphasen

### Phase 1: Grundlagen und Datenbank
- Einrichtung des Projekts
- Implementierung der Datenmodelle
- Erstellung der Datenbank
- Import der Karteninformationen

### Phase 2: Deck-Builder
- GUI für den Deck-Builder
- Kartenkatalog-Ansicht
- Deck-Erstellung und -Speicherung
- Deck-Import/-Export

### Phase 3: Spielbrett und Grundlegende Spiellogik
- GUI für das Spielbrett
- Darstellung der Spielzonen (Hand, Spielfeld, Bibliothek, etc.)
- Grundlegende Spielaktionen (Karten ziehen, Karten spielen)
- Phasenverwaltung

### Phase 4: Komplexe Spielregeln
- Parser für die umfassenden Regeln
- Implementierung der wichtigsten Regelgruppen
- Stack-Verwaltung für Zauber und Fähigkeiten
- Effektverarbeitung

### Phase 5: Vollständige Spiellogik
- Komplettierung aller Spielregeln
- Komplexe Karteneffekte und Interaktionen
- KI-Unterstützung für Regelhilfe

### Phase 6: Polieren und Testen
- Erweitertes Testen
- UI-Verbesserungen
- Performance-Optimierungen
- Dokumentation

## Herausforderungen
1. **Komplexität der Regeln**: Magic the Gathering hat ein umfangreiches Regelwerk, das sorgfältig implementiert werden muss.
2. **Karteninteraktionen**: Die Vielzahl an Karten und ihre Interaktionen erfordern ein flexibles Design.
3. **Zustandsverwaltung**: Der Spielzustand muss präzise verwaltet werden, einschließlich aller Spielobjekte und ihrer Eigenschaften.
4. **Performanz**: Trotz der komplexen Logik muss die Anwendung flüssig laufen.

## Lösungsansätze
1. **Regelmotor**: Entwicklung eines modularen Regelmotors, der die offiziellen Regeln interpretieren und anwenden kann.
2. **Ereignisbasiertes System**: Verwendung eines Ereignismodells für Karteneffekte und Spielaktionen.
3. **Zustandsmuster**: Implementierung des Zustandsmusters für die verschiedenen Spielphasen und -zustände.
4. **Datengetriebener Ansatz**: Implementierung von Karteneffekten durch Datenbeschreibungen, wo möglich, anstatt durch hartcodierten Code.
