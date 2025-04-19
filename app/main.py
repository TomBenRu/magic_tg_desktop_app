#!/usr/bin/env python3
"""
Magic the Gathering Desktop App - Hauptanwendung.

Eine Anwendung für zwei Spieler, um Magic the Gathering auf einem Rechner zu spielen.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir

# Pfad zum Projekt-Verzeichnis hinzufügen, um Imports zu ermöglichen
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Import der GUI-Komponenten
from app.gui.main_window import MainWindow


def setup_environment():
    """Richtet die Umgebungsvariablen und Pfade für die Anwendung ein."""
    # Stelle sicher, dass die Datendirektorie existiert
    data_dir = os.path.join(project_path, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Stelle sicher, dass das Cards-Verzeichnis existiert
    cards_dir = os.path.join(data_dir, 'cards')
    os.makedirs(cards_dir, exist_ok=True)
    
    # Setze den Arbeitsordner auf das Projektverzeichnis
    os.chdir(project_path)
    
    # Setze den Qt-Ressourcenpfad
    QDir.addSearchPath('resources', os.path.join(project_path, 'resources'))
    
    return data_dir, cards_dir


def main():
    """Hauptfunktion der Anwendung."""
    # Einrichtung der Anwendungsumgebung
    data_dir, cards_dir = setup_environment()
    
    # Initialisierung der Anwendung
    app = QApplication(sys.argv)
    app.setApplicationName("Magic the Gathering Desktop App")
    
    # Hauptfenster erstellen und anzeigen
    main_window = MainWindow()
    main_window.show()
    
    # Informationen ausgeben
    print("Magic the Gathering Desktop App gestartet.")
    print(f"Datenverzeichnis: {data_dir}")
    print(f"Kartenverzeichnis: {cards_dir}")
    
    # Anwendungsausführung starten
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
