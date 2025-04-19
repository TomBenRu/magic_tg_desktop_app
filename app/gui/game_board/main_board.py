from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QGroupBox, QScrollArea, QSplitter, QFrame,
    QStatusBar, QDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QFont, QColor, QPalette

from app.gui.game_board.card_display import create_card_widget, show_card_details
from app.gui.game_board.game_dialogs import NewGameDialog, LoadGameDialog
from app.logic.game_engine import GameEngine
from app.gui.game_board.zones import GameZone, BattlefieldZone

from pony.orm import db_session
import random


class GameBoardWidget(QWidget):
    """Hauptspielfeld-Widget für Magic the Gathering."""

    # Signale
    phase_changed = Signal(str)  # Emittiert bei Phasenwechsel
    game_state_changed = Signal(dict)  # Emittiert bei Änderung des Spielstatus

    def __init__(self, parent=None):
        """
        Initialisiert
        das
        Spielbrett.

        Args:
        parent(QWidget, optional): Das
        Eltern - Widget.
        """
        super().__init__(parent)

        # Spielzustand und Engine
        self.game_engine = None
        self.game_state = None
        self.active_player_id = None
        self.inactive_player_id = None
        self.current_phase = None
        self.player1_id = None
        self.player2_id = None

        # Initialisiere das Layout
        self.init_ui()


    def init_ui(self):
        """Initialisiert die Benutzeroberfläche des Spielbretts."""
        # Hauptlayout
        main_layout = QVBoxLayout(self)

        # Spielinfo-Bereich am oberen Rand
        self.game_info_widget = self._create_game_info_widget()
        main_layout.addWidget(self.game_info_widget)

        # Hauptspielbrett (Splitter für flexible Aufteilung)
        self.board_splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(self.board_splitter, 1)  # Nimmt den verfügbaren Platz ein

        # Obere Spielerzone (Spieler 2)
        self.player2_zone = self._create_player_zone(is_top=True)
        self.board_splitter.addWidget(self.player2_zone)

        # Mittlerer Bereich (Stapel, neutrales Feld)
        self.middle_zone = self._create_middle_zone()
        self.board_splitter.addWidget(self.middle_zone)

        # Untere Spielerzone (Spieler 1)
        self.player1_zone = self._create_player_zone(is_top=False)
        self.board_splitter.addWidget(self.player1_zone)

        # Größen für den Splitter einstellen
        self.board_splitter.setSizes([250, 200, 250])

        # Aktionsleiste am unteren Rand
        self.action_bar = self._create_action_bar()
        main_layout.addWidget(self.action_bar)

        # Statusleiste
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)
        self.status_bar.showMessage("Spielbrett bereit. Starten Sie ein neues Spiel.")


    def _create_game_info_widget(self):
        """
        Erstellt
        das
        Widget
        für
        Spielinformationen.

        Returns:
        QWidget: Das
        Spielinfo - Widget.

        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Spielinfo links (Runde, Phase)
        game_info_box = QGroupBox("Spielinfo")
        game_info_layout = QGridLayout(game_info_box)

        # Runde
        turn_label = QLabel("Runde:")
        turn_label.setStyleSheet("font-weight: bold;")
        self.turn_value = QLabel("0")
        game_info_layout.addWidget(turn_label, 0, 0)
        game_info_layout.addWidget(self.turn_value, 0, 1)

        # Phase
        phase_label = QLabel("Phase:")
        phase_label.setStyleSheet("font-weight: bold;")
        self.phase_value = QLabel("Einrichtung")
        game_info_layout.addWidget(phase_label, 1, 0)
        game_info_layout.addWidget(self.phase_value, 1, 1)

        # Aktiver Spieler
        active_player_label = QLabel("Am Zug:")
        active_player_label.setStyleSheet("font-weight: bold;")
        self.active_player_value = QLabel("-")
        game_info_layout.addWidget(active_player_label, 2, 0)
        game_info_layout.addWidget(self.active_player_value, 2, 1)

        layout.addWidget(game_info_box)

        # Spielerinfos in der Mitte
        player_info_box = QGroupBox("Spieler")
        player_info_layout = QGridLayout(player_info_box)

        # Spieler 1
        player1_name_label = QLabel("Spieler 1:")
        player1_name_label.setStyleSheet("font-weight: bold;")
        self.player1_name_value = QLabel("-")
        player_info_layout.addWidget(player1_name_label, 0, 0)
        player_info_layout.addWidget(self.player1_name_value, 0, 1)

        player1_life_label = QLabel("Leben:")
        self.player1_life_value = QLabel("20")
        self.player1_life_value.setStyleSheet("font-weight: bold; color: green;")
        player_info_layout.addWidget(player1_life_label, 0, 2)
        player_info_layout.addWidget(self.player1_life_value, 0, 3)

        player1_lib_label = QLabel("Bibliothek:")
        self.player1_library_value = QLabel("0")
        player_info_layout.addWidget(player1_lib_label, 0, 4)
        player_info_layout.addWidget(self.player1_library_value, 0, 5)

        # Spieler 2
        player2_name_label = QLabel("Spieler 2:")
        player2_name_label.setStyleSheet("font-weight: bold;")
        self.player2_name_value = QLabel("-")
        player_info_layout.addWidget(player2_name_label, 1, 0)
        player_info_layout.addWidget(self.player2_name_value, 1, 1)

        player2_life_label = QLabel("Leben:")
        self.player2_life_value = QLabel("20")
        self.player2_life_value.setStyleSheet("font-weight: bold; color: green;")
        player_info_layout.addWidget(player2_life_label, 1, 2)
        player_info_layout.addWidget(self.player2_life_value, 1, 3)

        player2_lib_label = QLabel("Bibliothek:")
        self.player2_library_value = QLabel("0")
        player_info_layout.addWidget(player2_lib_label, 1, 4)
        player_info_layout.addWidget(self.player2_library_value, 1, 5)

        layout.addWidget(player_info_box, 1)  # Mehr Platz für Spielerinfos

        # Spielsteuerung rechts
        game_control_box = QGroupBox("Spielsteuerung")
        game_control_layout = QVBoxLayout(game_control_box)

        self.new_game_button = QPushButton("Neues Spiel")
        self.new_game_button.clicked.connect(self.on_new_game)
        game_control_layout.addWidget(self.new_game_button)

        self.load_game_button = QPushButton("Spiel laden")
        self.load_game_button.clicked.connect(self.on_load_game)
        game_control_layout.addWidget(self.load_game_button)

        self.end_game_button = QPushButton("Spiel beenden")
        self.end_game_button.clicked.connect(self.on_end_game)
        self.end_game_button.setEnabled(False)  # Zu Beginn deaktiviert
        game_control_layout.addWidget(self.end_game_button)

        layout.addWidget(game_control_box)

        return widget


    def _create_player_zone(self, is_top=False):
        """Erstellt die Spielerzone mit allen Spielbereichen.

        Args:
            is_top (bool): True für obere Spielerzone (Spieler 2),
                          False für untere Spielerzone (Spieler 1).

        Returns:
            QWidget: Das Widget der erstellten Spielerzone.
        """
        zone_widget = QWidget()
        zone_layout = QVBoxLayout(zone_widget)  # Geändert zu vertikalem Layout

        # Oberer Bereich für Hand, Bibliothek und Friedhof
        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)

        # Hand
        self.hand_zones = getattr(self, 'hand_zones', {})
        player_id = str(self.player2_id) if is_top else str(self.player1_id)
        player_name = f"Spieler {player_id}"
        self.hand_zones[player_id] = GameZone(f"Hand - {player_name}")
        upper_layout.addWidget(self.hand_zones[player_id], 2)  # Hand bekommt mehr Platz

        # Bibliothek
        self.library_zones = getattr(self, 'library_zones', {})
        self.library_zones[player_id] = GameZone(f"Bibliothek - {player_name}")
        upper_layout.addWidget(self.library_zones[player_id], 1)

        # Friedhof
        self.graveyard_zones = getattr(self, 'graveyard_zones', {})
        self.graveyard_zones[player_id] = GameZone(f"Friedhof - {player_name}")
        upper_layout.addWidget(self.graveyard_zones[player_id], 1)

        zone_layout.addWidget(upper_widget)

        # Battlefield
        self.battlefield_zones = getattr(self, 'battlefield_zones', {})
        self.battlefield_zones[player_id] = BattlefieldZone(f"Spielfeld - {player_name}", player_id)
        zone_layout.addWidget(self.battlefield_zones[player_id], 3)  # Battlefield bekommt viel Platz

        return zone_widget


    def _create_middle_zone(self):
        """Erstellt die mittlere Zone mit Stack und Exile.

        Returns:
            QWidget: Das Widget der erstellten mittleren Zone.
        """
        middle_widget = QWidget()
        middle_layout = QHBoxLayout(middle_widget)

        # Stack
        self.stack_zone = GameZone("Stack")
        middle_layout.addWidget(self.stack_zone)

        # Exile
        self.exile_zone = GameZone("Exile")
        middle_layout.addWidget(self.exile_zone)

        return middle_widget


    def _create_action_bar(self):
        """
        Erstellt
        die
        Aktionsleiste
        am
        unteren
        Rand.

        Returns:
        QWidget: Die
        Aktionsleiste
        als
        Widget.

    """
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 5, 5, 5)

        # Phasen-Steuerung
        phases_group = QGroupBox("Phasen")
        phases_layout = QHBoxLayout(phases_group)

        self.phase_buttons = {}

        # Phasen definieren
        phases = [
            ('untap', 'Enttappen'),
            ('upkeep', 'Versorgung'),
            ('draw', 'Ziehen'),
            ('main1', 'Hauptphase 1'),
            ('combat_begin', 'Kampf: Beginn'),
            ('combat_attackers', 'Kampf: Angreifer'),
            ('combat_blockers', 'Kampf: Blocker'),
            ('combat_damage', 'Kampf: Schaden'),
            ('combat_end', 'Kampf: Ende'),
            ('main2', 'Hauptphase 2'),
            ('end', 'Ende'),
            ('cleanup', 'Aufräumen')
        ]

        for phase_id, phase_name in phases:
            button = QPushButton(phase_name)
        button.setProperty('phase_id', phase_id)
        button.clicked.connect(self.on_phase_button_clicked)
        button.setEnabled(False)  # Zu Beginn deaktiviert
        phases_layout.addWidget(button)
        self.phase_buttons[phase_id] = button

        action_layout.addWidget(phases_group)

        # Spieleraktionen
        player_actions_group = QGroupBox("Spieleraktionen")
        player_actions_layout = QHBoxLayout(player_actions_group)

        self.draw_card_button = QPushButton("Karte ziehen")
        self.draw_card_button.clicked.connect(self.on_draw_card)
        self.draw_card_button.setEnabled(False)  # Zu Beginn deaktiviert
        player_actions_layout.addWidget(self.draw_card_button)

        self.untap_all_button = QPushButton("Alles enttappen")
        self.untap_all_button.clicked.connect(self.on_untap_all)
        self.untap_all_button.setEnabled(False)  # Zu Beginn deaktiviert
        player_actions_layout.addWidget(self.untap_all_button)

        self.next_turn_button = QPushButton("Nächster Zug")
        self.next_turn_button.clicked.connect(self.on_next_turn)
        self.next_turn_button.setEnabled(False)  # Zu Beginn deaktiviert
        player_actions_layout.addWidget(self.next_turn_button)

        action_layout.addWidget(player_actions_group)

        return action_widget


    @Slot()
    def on_new_game(self):
        """Wird aufgerufen, wenn ein neues Spiel gestartet werden soll."""
        dialog = NewGameDialog(self)
        result = dialog.exec()

        if result == QDialog.Accepted:
            player1_id, player2_id, deck1_id, deck2_id = dialog.get_game_info()

            # Erstelle eine neue Game Engine
            self.game_engine = GameEngine()

            # Erstelle ein neues Spiel
            game_id = self.game_engine.create_game(player1_id, player2_id, deck1_id, deck2_id)

            if game_id:
                self.player1_id = player1_id
                self.player2_id = player2_id
                self.game_state = self.game_engine.game_state
                self.active_player_id = self.game_state['active_player_id']
                self.inactive_player_id = str(player2_id) if self.active_player_id == str(player1_id) else str(player1_id)
                self.current_phase = self.game_state['phase']

                # UI aktualisieren
                self.update_ui()
                self.enable_game_controls(True)

                # Statusmeldung
                self.status_bar.showMessage(f"Neues Spiel gestartet (ID: {game_id})")
            else:
                QMessageBox.critical(self, "Fehler", "Fehler beim Erstellen des Spiels.") \
    @ Slot()
    def on_load_game(self):
        """Wird aufgerufen, wenn ein Spiel geladen werden soll."""
        dialog = LoadGameDialog(self)
        result = dialog.exec()

        if result == QDialog.Accepted:
            game_id = dialog.get_game_id()

            if not game_id:
                QMessageBox.warning(self, "Warnung", "Kein Spiel ausgewählt.")
                return

            # Erstelle eine neue Game Engine und lade das Spiel
            self.game_engine = GameEngine(game_id)

            if self.game_engine.game_state:
                self.game_state = self.game_engine.game_state
                self.active_player_id = self.game_state['active_player_id']

                # Bestimme die Spieler-IDs
                player_ids = list(self.game_state['players'].keys())
                self.player1_id = int(player_ids[0])
                self.player2_id = int(player_ids[1])

                # Bestimme den inaktiven Spieler
                self.inactive_player_id = player_ids[1] if self.active_player_id == player_ids[0] else player_ids[0]

                self.current_phase = self.game_state['phase']

                # UI aktualisieren
                self.update_ui()
                self.enable_game_controls(True)

                # Statusmeldung
                self.status_bar.showMessage(f"Spiel geladen (ID: {game_id})")
            else:
                QMessageBox.critical(self, "Fehler", "Fehler beim Laden des Spiels.") \

    @Slot()
    def on_end_game(self):
        """Wird aufgerufen, wenn das Spiel beendet werden soll."""
        if not self.game_engine:
            return

        # Frage, ob wirklich beendet werden soll
        result = QMessageBox.question(
            self,
        "Spiel beenden",
        "Möchten Sie das Spiel wirklich beenden?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
        )

        if result == QMessageBox.Yes:
            # Frage nach dem Gewinner
            winner_id = None

            winner_result = QMessageBox.question(
                self,
            "Gewinner auswählen",
            "Gibt es einen Gewinner?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
            )

            if winner_result == QMessageBox.Yes:
                # Frage welcher Spieler gewonnen hat
                player1_name = self.game_state['players'][str(self.player1_id)]['name']
                player2_name = self.game_state['players'][str(self.player2_id)]['name']

                winner_dialog = QMessageBox(self)
                winner_dialog.setWindowTitle("Gewinner auswählen")
                winner_dialog.setText("Welcher Spieler hat gewonnen?")

                player1_button = winner_dialog.addButton(player1_name, QMessageBox.ActionRole)
                player2_button = winner_dialog.addButton(player2_name, QMessageBox.ActionRole)
                cancel_button = winner_dialog.addButton(QMessageBox.Cancel)

                winner_dialog.exec()

                clicked_button = winner_dialog.clickedButton()

                if clicked_button == player1_button:
                    winner_id = self.player1_id
                elif clicked_button == player2_button:
                    winner_id = self.player2_id

                # Spiel beenden
                success = self.game_engine.end_game(winner_id)

                if success:
                    # UI aktualisieren
                    self.game_state = self.game_engine.game_state
                    self.update_ui()
                    self.enable_game_controls(False)

                    # Statusmeldung
                    winner_text = f"Gewinner: {self.game_state['players'][str(winner_id)]['name']}" if winner_id else "Unentschieden"
                    self.status_bar.showMessage(f"Spiel beendet. {winner_text}")
                else:
                    QMessageBox.critical(self, "Fehler", "Fehler beim Beenden des Spiels.") \

    @Slot()
    def on_phase_button_clicked(self):
        """Wird aufgerufen, wenn eine Phasen-Schaltfläche geklickt wird."""
        if not self.game_engine:
            return

        # Ermittle die ausgewählte Phase
        sender = self.sender()
        phase_id = sender.property('phase_id')

        # Phasenwechsel
        self.game_state, error = self.game_engine.change_phase(phase_id)

        if error:
            QMessageBox.warning(self, "Warnung", f"Fehler beim Phasenwechsel: {error}")
            return

        # Aktualisiere die aktuelle Phase
        self.current_phase = phase_id

        # Speichere den Spielzustand
        self.game_engine.save_game_state()

        # UI aktualisieren
        self.update_ui()

        # Phasenspezifische Aktionen
        self._handle_phase_specific_actions(phase_id)

        # Statusmeldung
        self.status_bar.showMessage(f"Phase gewechselt zu: {self._get_phase_name(phase_id)}")


    def _get_phase_name(self, phase_id):
        """
        Gibt
        den
        Namen
        einer
        Phase
        zurück.

        Args:
        phase_id(str): Die
        ID
        der
        Phase.


        Returns:
        str: Der
        Name
        der
        Phase.
        """
        phase_names = {
            'untap': 'Enttappen',
            'upkeep': 'Versorgung',
            'draw': 'Ziehen',
            'main1': 'Hauptphase 1',
            'combat_begin': 'Kampf: Beginn',
            'combat_attackers': 'Kampf: Angreifer',
            'combat_blockers': 'Kampf: Blocker',
            'combat_damage': 'Kampf: Schaden',
            'combat_end': 'Kampf: Ende',
            'main2': 'Hauptphase 2',
            'end': 'Ende',
            'cleanup': 'Aufräumen',
            'setup': 'Einrichtung'
        }

        return phase_names.get(phase_id, phase_id)


    def _handle_phase_specific_actions(self, phase_id):
        """
        Führt
        phasenspezifische
        Aktionen
        aus.

        Args:
        phase_id(str): Die
        ID
        der
        Phase.

        """
        # In der Enttapp-Phase: Alle Karten des aktiven Spielers enttappen
        if phase_id == 'untap':
            self.on_untap_all()

        # In der Ziehphase: Eine Karte ziehen
        elif phase_id == 'draw':
            self.on_draw_card()


    @Slot()
    def on_draw_card(self):
        """Wird aufgerufen, wenn der aktive Spieler eine Karte ziehen soll."""
        if not self.game_engine or not self.active_player_id:
            return

        # Karte ziehen
        self.game_state, error = self.game_engine.draw_cards(self.active_player_id, 1)

        if error:
            QMessageBox.warning(self, "Warnung", f"Fehler beim Kartenziehen: {error}")
            return

        # Speichere den Spielzustand
        self.game_engine.save_game_state()

        # UI aktualisieren
        self.update_ui()

        # Statusmeldung
        player_name = self.game_state['players'][self.active_player_id]['name']
        self.status_bar.showMessage(f"{player_name} hat eine Karte gezogen.") \

    @Slot()
    def on_untap_all(self):
        """Wird aufgerufen, wenn alle Karten des aktiven Spielers enttappt werden sollen."""
        if not self.game_engine or not self.active_player_id:
            return

        # Alle getappten Karten des aktiven Spielers im Spielfeld suchen
        battlefield = self.game_state['battlefield']
        for card in battlefield:
            if card.get('controller_id') == self.active_player_id and card.get('tapped', False):
                # Karte enttappen
                card['tapped'] = False

        # Speichere den Spielzustand
        self.game_engine.save_game_state()

        # UI aktualisieren
        self.update_ui()

        # Statusmeldung
        player_name = self.game_state['players'][self.active_player_id]['name']
        self.status_bar.showMessage(f"Alle Karten von {player_name} wurden enttappt.") \

    @Slot()
    def on_next_turn(self):
        """Wird aufgerufen, wenn zum nächsten Zug gewechselt werden soll."""
        if not self.game_engine:
            return
            
        # Wechsle den aktiven Spieler
        if self.active_player_id == str(self.player1_id):
            new_active_player_id = str(self.player2_id)
            new_inactive_player_id = str(self.player1_id)
        else:
            new_active_player_id = str(self.player1_id)
            new_inactive_player_id = str(self.player2_id)
        
        # Starte den neuen Zug
        self.game_state = self.game_engine.start_turn(new_active_player_id)
        self.active_player_id = new_active_player_id
        self.inactive_player_id = new_inactive_player_id
        
        # Speichere den Spielzustand
        self.game_engine.save_game_state()
        
        # UI aktualisieren
        self.update_ui()
        
        # Statusmeldung
        player_name = self.game_state['players'][new_active_player_id]['name']
        self.status_bar.showMessage(f"Nächster Zug: {player_name} ist am Zug.")
        
    def update_ui(self):
        """Aktualisiert die Benutzeroberfläche basierend auf dem aktuellen Spielzustand."""
        if not self.game_state:
            return
            
        # Aktualisiere Spielinfo
        self.turn_value.setText(str(self.game_state.get('turn_number', 0)))
        self.phase_value.setText(self._get_phase_name(self.game_state.get('phase', 'setup')))
        
        # Aktiver Spieler
        active_player_id = self.game_state.get('active_player_id', '')
        if active_player_id and active_player_id in self.game_state['players']:
            active_player_name = self.game_state['players'][active_player_id]['name']
            self.active_player_value.setText(active_player_name)
        else:
            self.active_player_value.setText("-")
        
        # Spielerinformationen aktualisieren
        if self.player1_id and str(self.player1_id) in self.game_state['players']:
            player1_data = self.game_state['players'][str(self.player1_id)]
            self.player1_name_value.setText(player1_data['name'])
            self.player1_life_value.setText(str(player1_data['life']))
            self.player1_library_value.setText(str(len(player1_data['library'])))
            
            # Lebens-Status-Farbe anpassen
            if player1_data['life'] > 10:
                self.player1_life_value.setStyleSheet("font-weight: bold; color: green;")
            elif player1_data['life'] > 5:
                self.player1_life_value.setStyleSheet("font-weight: bold; color: orange;")
            else:
                self.player1_life_value.setStyleSheet("font-weight: bold; color: red;")
        
        if self.player2_id and str(self.player2_id) in self.game_state['players']:
            player2_data = self.game_state['players'][str(self.player2_id)]
            self.player2_name_value.setText(player2_data['name'])
            self.player2_life_value.setText(str(player2_data['life']))
            self.player2_library_value.setText(str(len(player2_data['library'])))
            
            # Lebens-Status-Farbe anpassen
            if player2_data['life'] > 10:
                self.player2_life_value.setStyleSheet("font-weight: bold; color: green;")
            elif player2_data['life'] > 5:
                self.player2_life_value.setStyleSheet("font-weight: bold; color: orange;")
            else:
                self.player2_life_value.setStyleSheet("font-weight: bold; color: red;")
        
        # Zonen aktualisieren
        self._update_zones()
        
        # Aktualisiere die Phasen-Buttons
        self._update_phase_buttons()
        
        # Aktualisiere Spieleraktionen
        self._update_player_actions()
        
        # Emittiere Signal für Spielzustandsänderung
        self.game_state_changed.emit(self.game_state)
        
    def _update_zones(self):
        """Aktualisiert alle Spielzonen mit dem aktuellen Spielzustand."""
        if not self.game_state:
            return
            
        # Leere alle Zonen
        for zone_dict in [self.hand_zones, self.library_zones, self.graveyard_zones, self.battlefield_zones]:
            for zone in zone_dict.values():
                zone.clear()
                
        self.stack_zone.clear()
        self.exile_zone.clear()
        
        # Aktualisiere Spielerzonen
        for player_id, player_data in self.game_state['players'].items():
            # Hand
            if player_id in self.hand_zones:
                for card in player_data['hand']:
                    # Für Spieler 1 zeigen wir die Karten, für Spieler 2 nicht (bei beiden Spielern am gleichen Gerät)
                    show_face = (str(player_id) == str(self.player1_id))
                    card_widget = create_card_widget(card, 'hand', player_id, self, show_face)
                    self.hand_zones[player_id].add_card(card_widget)
            
            # Bibliothek
            if player_id in self.library_zones and player_data['library']:
                # Hier zeigen wir nur die Anzahl der Karten, nicht die Karten selbst
                library_count = len(player_data['library'])
                library_label = QLabel(f"{library_count} Karten")
                library_label.setAlignment(Qt.AlignCenter)
                library_label.setStyleSheet("font-weight: bold;")
                self.library_zones[player_id].add_card(library_label)
                
                # Wir könnten auch die oberste Karte als verdeckt anzeigen
                if library_count > 0:
                    card = player_data['library'][0]  # Oberste Karte
                    card_widget = create_card_widget(card, 'library', player_id, self, False)
                    self.library_zones[player_id].add_card(card_widget)
            
            # Friedhof
            if player_id in self.graveyard_zones:
                for card in player_data['graveyard']:
                    card_widget = create_card_widget(card, 'graveyard', player_id, self, True)
                    self.graveyard_zones[player_id].add_card(card_widget)
        
        # Aktualisiere Battlefield
        for card in self.game_state.get('battlefield', []):
            controller_id = card.get('controller_id', '')
            if controller_id in self.battlefield_zones:
                card_widget = create_card_widget(card, 'battlefield', controller_id, self, True)
                self.battlefield_zones[controller_id].add_card(card_widget)
        
        # Aktualisiere Stack
        for card in self.game_state.get('stack', []):
            card_widget = create_card_widget(card, 'stack', card.get('controller_id', ''), self, True)
            self.stack_zone.add_card(card_widget)
        
        # Aktualisiere Exile
        for card in self.game_state.get('exile', []):
            card_widget = create_card_widget(card, 'exile', card.get('owner_id', ''), self, True)
            self.exile_zone.add_card(card_widget)
        
    def _update_phase_buttons(self):
        """Aktualisiert die Phasen-Buttons basierend auf der aktuellen Phase."""
        if not self.game_state:
            return
            
        current_phase = self.game_state.get('phase', 'setup')
        
        # Aktiviere/Deaktiviere Phasen-Buttons basierend auf dem Spielzustand
        phase_order = [
            'untap', 'upkeep', 'draw', 'main1', 
            'combat_begin', 'combat_attackers', 'combat_blockers', 'combat_damage', 'combat_end',
            'main2', 'end', 'cleanup'
        ]
        
        # Finde den Index der aktuellen Phase
        if current_phase in phase_order:
            current_phase_index = phase_order.index(current_phase)
        else:
            current_phase_index = -1
        
        # Setze Status der Buttons
        for phase_id, button in self.phase_buttons.items():
            # Aktiviere nur die aktuelle und die nächste Phase
            if current_phase_index >= 0 and phase_id in phase_order:
                phase_index = phase_order.index(phase_id)
                enabled = (phase_index == current_phase_index or phase_index == current_phase_index + 1)
                button.setEnabled(enabled)
                
                # Markiere die aktuelle Phase
                if phase_index == current_phase_index:
                    button.setStyleSheet("background-color: lightblue;")
                else:
                    button.setStyleSheet("")
            else:
                # Wenn wir uns in der Setup-Phase befinden, aktiviere keine Phasen-Buttons
                button.setEnabled(False)
                button.setStyleSheet("")
                
    def _update_player_actions(self):
        """Aktualisiert die Spieleraktionen basierend auf dem Spielzustand."""
        if not self.game_state:
            return
            
        # Aktiviere/Deaktiviere Aktionen basierend auf der Phase und dem aktiven Spieler
        current_phase = self.game_state.get('phase', 'setup')
        active_player_id = self.game_state.get('active_player_id', '')
        
        # Karte ziehen ist nur in der Ziehphase aktiv
        self.draw_card_button.setEnabled(current_phase == 'draw' and active_player_id)
        
        # Alles enttappen ist nur in der Enttapp-Phase aktiv
        self.untap_all_button.setEnabled(current_phase == 'untap' and active_player_id)
        
        # Nächster Zug ist nur in der Aufräumphase aktiv
        self.next_turn_button.setEnabled(current_phase == 'cleanup' and active_player_id)
        
    def enable_game_controls(self, enabled=True):
        """Aktiviert oder deaktiviert die Spielsteuerungselemente."""
        # Aktiviere/Deaktiviere Steuerelemente
        for button in self.phase_buttons.values():
            button.setEnabled(enabled)
            
        self.draw_card_button.setEnabled(enabled)
        self.untap_all_button.setEnabled(enabled)
        self.next_turn_button.setEnabled(enabled)
        self.end_game_button.setEnabled(enabled)
        
        if enabled:
            # Wenn aktiviert, aktualisiere den Status basierend auf dem Spielzustand
            self._update_phase_buttons()
            self._update_player_actions()
        else:
            # Wenn deaktiviert, alle Steuerelemente ausschalten
            self.draw_card_button.setEnabled(False)
            self.untap_all_button.setEnabled(False)
            self.next_turn_button.setEnabled(False)
