"""
Hauptfenster der Magic the Gathering Desktop App.

Dieses Modul enthält die Implementierung des Hauptfensters der Anwendung.
"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QMessageBox, QStatusBar, QMenu, QMenuBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

from app.gui.game_board.main_board import GameBoardWidget


class MainWindow(QMainWindow):
    """Hauptfenster der Magic the Gathering Desktop App."""
    
    def __init__(self):
        """Initialisiert das Hauptfenster."""
        super().__init__()
        
        # Fenstereigenschaften
        self.setWindowTitle("Magic the Gathering Desktop App")
        self.setMinimumSize(1024, 768)
        
        # Zentrales Widget und Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Menüleiste erstellen
        self.create_menu_bar()
        
        # Tab-Widget für verschiedene Bereiche
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Tabs hinzufügen
        self.init_home_tab()
        self.init_deck_builder_tab()
        self.init_game_tab()
        
        # Statusleiste
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Bereit")
    
    def create_menu_bar(self):
        """Erstellt die Menüleiste."""
        # Menüleiste
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)
        
        # Datei-Menü
        file_menu = QMenu("&Datei", self)
        menu_bar.addMenu(file_menu)
        
        # Aktionen zum Datei-Menü hinzufügen
        new_deck_action = QAction("&Neues Deck", self)
        new_deck_action.triggered.connect(self.on_new_deck)
        file_menu.addAction(new_deck_action)
        
        open_deck_action = QAction("Deck &öffnen", self)
        open_deck_action.triggered.connect(self.on_open_deck)
        file_menu.addAction(open_deck_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Spiel-Menü
        game_menu = QMenu("&Spiel", self)
        menu_bar.addMenu(game_menu)
        
        new_game_action = QAction("&Neues Spiel", self)
        new_game_action.triggered.connect(self.on_new_game)
        game_menu.addAction(new_game_action)
        
        # Hilfe-Menü
        help_menu = QMenu("&Hilfe", self)
        menu_bar.addMenu(help_menu)
        
        about_action = QAction("Ü&ber", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
        
        rules_action = QAction("&Spielregeln", self)
        rules_action.triggered.connect(self.on_rules)
        help_menu.addAction(rules_action)
    
    def init_home_tab(self):
        """Initialisiert den Home-Tab."""
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        
        # Begrüßung und Informationen
        welcome_label = QLabel("Willkommen bei Magic the Gathering Desktop App!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        home_layout.addWidget(welcome_label)
        
        info_label = QLabel(
            "Mit dieser Anwendung können zwei Spieler Magic the Gathering "
            "auf demselben Rechner spielen. Die Spieler können ihre eigenen "
            "Decks zusammenstellen und in einem 'Constructed Format' spielen."
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 16px; margin: 10px;")
        home_layout.addWidget(info_label)
        
        # Buttons für Schnellzugriff
        buttons_layout = QHBoxLayout()
        home_layout.addLayout(buttons_layout)
        
        new_deck_button = QPushButton("Neues Deck erstellen")
        new_deck_button.clicked.connect(self.on_new_deck)
        buttons_layout.addWidget(new_deck_button)
        
        new_game_button = QPushButton("Neues Spiel starten")
        new_game_button.clicked.connect(self.on_new_game)
        buttons_layout.addWidget(new_game_button)
        
        # Füge Tab hinzu
        self.tab_widget.addTab(home_widget, "Home")
    
    def init_deck_builder_tab(self):
        """Initialisiert den Deck-Builder-Tab."""
        # Hier wird später der Deck-Builder implementiert
        deck_builder_widget = QWidget()
        deck_builder_layout = QVBoxLayout(deck_builder_widget)
        
        deck_builder_label = QLabel("Deck-Builder (in Entwicklung)")
        deck_builder_label.setAlignment(Qt.AlignCenter)
        deck_builder_layout.addWidget(deck_builder_label)
        
        # Füge Tab hinzu
        self.tab_widget.addTab(deck_builder_widget, "Deck-Builder")
    
    def init_game_tab(self):
        """Initialisiert den Spiel-Tab."""
        # Das Spielbrett-Widget erstellen
        self.game_board = GameBoardWidget()
        
        # Füge Tab hinzu
        self.tab_widget.addTab(self.game_board, "Spiel")
    
    def on_new_deck(self):
        """Wird aufgerufen, wenn ein neues Deck erstellt werden soll."""
        # Hier wird später der Deck-Builder geöffnet
        self.status_bar.showMessage("Neues Deck wird erstellt...")
        self.tab_widget.setCurrentIndex(1)  # Wechsle zum Deck-Builder-Tab
    
    def on_open_deck(self):
        """Wird aufgerufen, wenn ein Deck geöffnet werden soll."""
        # Hier wird später der Deck-Öffnen-Dialog geöffnet
        self.status_bar.showMessage("Deck wird geöffnet...")
    
    def on_new_game(self):
        """Wird aufgerufen, wenn ein neues Spiel gestartet werden soll."""
        # Wechsle zum Spiel-Tab
        self.tab_widget.setCurrentIndex(2)  # Zum Spiel-Tab wechseln
        
        # Starte ein neues Spiel
        self.game_board.on_new_game()
        
        # Statusmeldung
        self.status_bar.showMessage("Neues Spiel gestartet.")
    
    def on_about(self):
        """Zeigt Informationen über die Anwendung an."""
        QMessageBox.about(
            self,
            "Über Magic the Gathering Desktop App",
            "Magic the Gathering Desktop App\n\n"
            "Eine Anwendung für zwei Spieler, um Magic the Gathering "
            "auf demselben Rechner zu spielen.\n\n"
            "Entwickelt von Thomas"
        )
    
    def on_rules(self):
        """Zeigt die Spielregeln an."""
        # Hier wird später ein Regelviewer implementiert
        self.status_bar.showMessage("Spielregeln werden angezeigt...")
