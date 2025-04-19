# Magic the Gathering Desktop App - Aufgabenliste

## Phase 1: Grundlagen und Datenbank

### Projekteinrichtung
- [x] Projektverzeichnis erstellen
- [x] Magic the Gathering Regeln hinzufügen
- [x] Virtual Environment einrichten
- [x] PySide6, PonyORM und andere Abhängigkeiten installieren
- [x] Verzeichnisstruktur erstellen
- [x] Git-Repository initialisieren (optional)

### Datenmodelle
- [ ] Grundlegende Entity-Modelle erstellen:
  - [ ] Card
  - [ ] Deck
  - [ ] CardInDeck
  - [ ] Player
  - [ ] PlayerStats
  - [ ] Game
- [ ] PonyORM-Konfiguration einrichten
- [ ] Datenbankschema erstellen und migrieren
- [ ] CRUD-Operationen für alle Entitäten implementieren
- [ ] Testdaten erstellen

### Datenimport
- [ ] Script für den Import von Karteninformationen erstellen
- [ ] Ordnerstruktur für Kartenbilder einrichten
- [ ] Erste Teilmenge von Karten importieren
- [ ] Testen der Datenbank-Abfragen

## Phase 2: Deck-Builder

### Deck-Builder-GUI
- [ ] Hauptfenster für den Deck-Builder erstellen
- [ ] Kartenkatalog-Ansicht implementieren
- [ ] Filterung und Suche für Karten implementieren
- [ ] Drag-and-Drop-Funktionalität für Karten hinzufügen
- [ ] Deck-Statistiken anzeigen (Mana-Kurve, Farbenverteilung)

### Deck-Verwaltung
- [ ] Speichern und Laden von Decks
- [ ] Deck-Validierung (Format-Regeln)
- [ ] Import/Export-Funktionalität
- [ ] Deck-Bearbeitungsfunktionen

## Phase 3: Spielbrett und grundlegende Spiellogik

### Spielbrett-GUI
- [ ] Hauptfenster für das Spielbrett erstellen
- [ ] Spielbereiche definieren:
  - [ ] Hand
  - [ ] Spielfeld
  - [ ] Bibliothek
  - [ ] Friedhof
  - [ ] Exil
  - [ ] Stack
- [ ] Visualisierung des Spielzustands
- [ ] Spielerinfo-Anzeige (Leben, Mana, etc.)

### Grundlegende Spielaktionen
- [ ] Spielinitialisierung
- [ ] Kartenziehen
- [ ] Karten spielen
- [ ] Angriff und Verteidigung
- [ ] Mana-Verwaltung

### Phasenverwaltung
- [ ] Implementierung der Spielphasen
  - [ ] Enttappen
  - [ ] Ziehen
  - [ ] Hauptphase 1
  - [ ] Kampf
  - [ ] Hauptphase 2
  - [ ] Endsegment
- [ ] Phasenwechsel-UI
- [ ] Phasenspezifische Aktionen

## Phase 4: Komplexe Spielregeln

### Regelparser
- [ ] Parser für die umfassenden Regeln entwickeln
- [ ] Kategorisierung der Regeln
- [ ] Interpretationsmotor für Regeltext erstellen

### Kernregeln
- [ ] Stack-Implementierung
- [ ] Prioritätsregeln
- [ ] Timing-Regeln
- [ ] Zustandsbasierte Aktionen

### Karteneffekte
- [ ] System für Karteneffekte implementieren
- [ ] Fähigkeitstypen (ausgelöst, aktiviert, statisch)
- [ ] Ersetzungseffekte
- [ ] Gegenstandseffekte
- [ ] Effektverabeitungspipeline

## Phase 5: Vollständige Spiellogik

### Erweiterte Spielregeln
- [ ] Verschiedene Kartentypen und deren Verhalten
- [ ] Spezielle Fähigkeitswörter (Exaltiert, Verursacht Todesberührungsschaden, etc.)
- [ ] Format-spezifische Regeln
- [ ] Multiplayer-Regeln (optional)

### Komplexe Karteninteraktionen
- [ ] Zielerfassung und -validierung
- [ ] Kostenberechnung und -bezahlung
- [ ] Effektauflösung
- [ ] Kontinuierliche Effekte

### KI-Unterstützung
- [ ] Regelassistent
- [ ] Hinweise für gültige Aktionen
- [ ] Erklärungen zu Regelinteraktionen

## Phase 6: Polieren und Testen

### Testen
- [ ] Unit-Tests für Kernfunktionen
- [ ] Integrationstests für Spielabläufe
- [ ] UI-Tests
- [ ] Benutzertests

### UI-Verbesserungen
- [ ] Design verfeinern
- [ ] Animationen hinzufügen
- [ ] Responsives Layout
- [ ] Barrierefreiheit verbessern

### Performance
- [ ] Speicher- und CPU-Nutzung optimieren
- [ ] Ladezeiten reduzieren
- [ ] Große Datasets effizient verwalten

### Dokumentation
- [ ] Benutzerhandbuch
- [ ] Codedokumentation
- [ ] API-Dokumentation
- [ ] Installationsanleitung

## Nächste Schritte (Sofort anzugehen)

1. Projektumgebung einrichten:
   - Virtual Environment aktivieren oder erstellen
   - Abhängigkeiten installieren (PySide6, PonyORM)
   - Grundlegende Projektstruktur anlegen

2. Datenmodelle entwickeln:
   - Erstellen der ersten Entity-Klassen mit PonyORM
   - Datenbankschema generieren
   - Verbindung zur SQLite-Datenbank herstellen

3. Einfachen Prototyp entwickeln:
   - Minimale GUI für Kartenanzeige
   - Grundlegende Datenbankoperationen testen
   - Erste Version des Deck-Builders
