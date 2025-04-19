"""
Funktionen zur Darstellung von Karten auf dem Spielbrett.

Dieses Modul enthält Funktionen zur Anzeige und Interaktion mit Karten.
"""

from PySide6.QtWidgets import QLabel, QMenu, QMessageBox, QFrame, QVBoxLayout, QDialog, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QCursor

from app.gui.game_board.card_widget import CardWidget, DraggableCardWidget


def create_card_widget(card, zone, owner_id, parent_widget, show_face=True):
    """
    Erstellt ein Widget für eine Karte.
    
    Args:
        card (dict): Die Karteninformationen.
        zone (str): Die Zone, in der sich die Karte befindet.
        owner_id (str): Die ID des Besitzers.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
        show_face (bool, optional): Ob die Vorderseite der Karte angezeigt werden soll.
    
    Returns:
        CardWidget: Das erstellte Karten-Widget.
    """
    # Erstelle eine Kopie der Kartendaten, um die Originaldaten nicht zu verändern
    card_data = card.copy()
    
    # Setze den Besitzer und die Zone
    card_data['owner_id'] = owner_id
    card_data['zone'] = zone
    
    # Erstelle ein draggable CardWidget
    widget = DraggableCardWidget(card_data, zone, parent_widget)
    
    # Wenn die Karte nicht gezeigt werden soll (z.B. gegnerische Hand)
    if not show_face:
        widget.set_face_down(True)
    
    # Verbinde Signale
    widget.clicked.connect(lambda: on_card_clicked(widget, parent_widget))
    widget.double_clicked.connect(lambda: on_card_double_clicked(widget, parent_widget))
    widget.right_clicked.connect(lambda pos: show_card_context_menu(pos, widget, parent_widget))
    
    return widget


def on_card_clicked(card_widget, parent_widget):
    """
    Wird aufgerufen, wenn eine Karte angeklickt wird.
    
    Args:
        card_widget (CardWidget): Das Widget der angeklickten Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Hier kann später Logik für einfache Klicks implementiert werden
    # z.B. Karte auswählen für weitere Aktionen
    pass


def on_card_double_clicked(card_widget, parent_widget):
    """
    Wird aufgerufen, wenn eine Karte doppelt angeklickt wird.
    
    Args:
        card_widget (CardWidget): Das Widget der doppelt angeklickten Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Bei Doppelklick zeigen wir die Kartendetails an
    show_card_details(card_widget.get_card_data())


def show_card_context_menu(pos, card_widget, parent_widget):
    """
    Zeigt ein Kontextmenü für eine Karte an.
    
    Args:
        pos (QPoint): Die Position des Menüs.
        card_widget (CardWidget): Das Widget der Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    card_data = card_widget.get_card_data()
    zone = card_data.get('zone', '')
    owner_id = card_data.get('owner_id', '')
    
    menu = QMenu()
    
    # Details anzeigen
    details_action = menu.addAction("Details anzeigen")
    
    # Aktiver Spieler
    active_player_id = parent_widget.active_player_id
    current_phase = parent_widget.current_phase
    
    # Aktionen basierend auf Zone
    if zone == 'hand':
        # Nur für den aktiven Spieler und seine eigenen Karten
        if active_player_id == owner_id and active_player_id == str(parent_widget.player1_id):
            play_action = menu.addAction("Spielen")
            discard_action = menu.addAction("Abwerfen")
    elif zone == 'battlefield':
        # Nur für den aktiven Spieler und seine eigenen Karten
        if active_player_id == owner_id:
            if card_widget.is_tapped():
                tap_action = menu.addAction("Enttappen")
            else:
                tap_action = menu.addAction("Tappen")
            
            # Für Kreaturen
            if 'Creature' in card_data.get('type', ''):
                # In der Kampfphase
                if current_phase == 'combat_attackers' and active_player_id == owner_id:
                    attack_action = menu.addAction("Angreifen")
                elif current_phase == 'combat_blockers' and active_player_id != owner_id:
                    block_action = menu.addAction("Blocken")
    elif zone == 'graveyard':
        # Spezielle Aktionen für den Friedhof
        pass
    elif zone == 'exile':
        # Spezielle Aktionen für das Exil
        pass
    
    # Menü anzeigen
    action = menu.exec_(QCursor.pos())
    
    # Aktion verarbeiten
    if action:
        if action.text() == "Details anzeigen":
            show_card_details(card_data)
        elif action.text() == "Spielen":
            play_card(card_data, parent_widget)
        elif action.text() == "Abwerfen":
            discard_card(card_data, parent_widget)
        elif action.text() == "Tappen":
            tap_card(card_widget, parent_widget)
        elif action.text() == "Enttappen":
            untap_card(card_widget, parent_widget)
        elif action.text() == "Angreifen":
            attack_with_card(card_widget, parent_widget)
        elif action.text() == "Blocken":
            block_with_card(card_widget, parent_widget)


def show_card_details(card):
    """
    Zeigt die Details einer Karte in einem Dialog an.
    
    Args:
        card (dict): Die Karteninformationen.
    """
    dialog = QDialog()
    dialog.setWindowTitle(f"Kartendetails: {card.get('name', 'Unbekannt')}")
    dialog.setMinimumSize(300, 400)
    
    layout = QVBoxLayout(dialog)
    
    # Textfeld für Kartendetails
    details = QTextEdit()
    details.setReadOnly(True)
    
    # HTML-Formatierung für bessere Darstellung
    html_content = f"""
    <h2>{card.get('name', 'Unbekannt')}</h2>
    <p><b>Typ:</b> {card.get('type', 'Unbekannt')}</p>
    <p><b>Manakosten:</b> {card.get('mana_cost', 'Unbekannt')}</p>
    """
    
    # Stärke/Widerstandskraft für Kreaturen
    if 'Creature' in card.get('type', ''):
        html_content += f"<p><b>Stärke/Widerstandskraft:</b> {card.get('power', '-')}/{card.get('toughness', '-')}</p>"
    
    # Regeltext
    html_content += f"<p><b>Regeltext:</b></p><p>{card.get('rules_text', 'Kein Regeltext').replace('\\n', '<br>')}</p>"
    
    # Farben
    colors = card.get('colors', [])
    if colors:
        html_content += f"<p><b>Farben:</b> {', '.join(colors)}</p>"
    
    # Status
    status = []
    if card.get('tapped', False):
        status.append("Getappt")
    if card.get('attacking', False):
        status.append("Angreifend")
    if card.get('blocking', False):
        status.append("Blockierend")
    
    if status:
        html_content += f"<p><b>Status:</b> {', '.join(status)}</p>"
    
    details.setHtml(html_content)
    layout.addWidget(details)
    
    dialog.exec_()


def play_card(card, parent_widget):
    """
    Spielt eine Karte aus der Hand.
    
    Args:
        card (dict): Die zu spielende Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Überprüfe, ob die Karte gespielt werden kann
    # (Phasencheck, Manakosten, etc.)
    
    # ID des aktiven Spielers
    player_id = parent_widget.active_player_id
    
    # Bestätigungsdialog
    result = QMessageBox.question(
        parent_widget,
        "Karte spielen",
        f"Möchten Sie die Karte '{card.get('name', 'Unbekannt')}' spielen?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if result == QMessageBox.Yes:
        # Rufe die GameEngine auf, um die Karte zu spielen
        game_state, error = parent_widget.game_engine.move_card(
            card['id'], 'hand', 'battlefield', player_id
        )
        
        if error:
            QMessageBox.warning(
                parent_widget,
                "Fehler",
                f"Die Karte konnte nicht gespielt werden: {error}"
            )
            return
        
        # Aktualisiere den Spielzustand
        parent_widget.game_state = game_state
        parent_widget.game_engine.save_game_state()
        
        # UI aktualisieren
        parent_widget.update_ui()
        
        # Statusmeldung
        parent_widget.status_bar.showMessage(f"Karte '{card.get('name', 'Unbekannt')}' wurde gespielt.")


def discard_card(card, parent_widget):
    """
    Wirft eine Karte aus der Hand ab.
    
    Args:
        card (dict): Die abzuwerfende Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # ID des aktiven Spielers
    player_id = parent_widget.active_player_id
    
    # Bestätigungsdialog
    result = QMessageBox.question(
        parent_widget,
        "Karte abwerfen",
        f"Möchten Sie die Karte '{card.get('name', 'Unbekannt')}' abwerfen?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if result == QMessageBox.Yes:
        # Rufe die GameEngine auf, um die Karte abzuwerfen
        game_state, error = parent_widget.game_engine.move_card(
            card['id'], 'hand', 'graveyard', player_id
        )
        
        if error:
            QMessageBox.warning(
                parent_widget,
                "Fehler",
                f"Die Karte konnte nicht abgeworfen werden: {error}"
            )
            return
        
        # Aktualisiere den Spielzustand
        parent_widget.game_state = game_state
        parent_widget.game_engine.save_game_state()
        
        # UI aktualisieren
        parent_widget.update_ui()
        
        # Statusmeldung
        parent_widget.status_bar.showMessage(f"Karte '{card.get('name', 'Unbekannt')}' wurde abgeworfen.")


def tap_card(card_widget, parent_widget):
    """
    Tappt eine Karte.
    
    Args:
        card_widget (CardWidget): Das Widget der zu tappenden Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Karte tappen
    card_data = card_widget.get_card_data()
    
    # Bestätigungsdialog
    result = QMessageBox.question(
        parent_widget,
        "Karte tappen",
        f"Möchten Sie die Karte '{card_data.get('name', 'Unbekannt')}' tappen?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if result == QMessageBox.Yes:
        # Karte tappen
        card_widget.set_tapped(True)
        
        # Aktualisiere Karte im Spielzustand
        for card in parent_widget.game_state.get('battlefield', []):
            if card.get('id') == card_data.get('id'):
                card['tapped'] = True
                break
        
        # Spielzustand speichern
        parent_widget.game_engine.save_game_state()
        
        # UI aktualisieren
        parent_widget.update_ui()
        
        # Statusmeldung
        parent_widget.status_bar.showMessage(f"Karte '{card_data.get('name', 'Unbekannt')}' wurde getappt.")


def untap_card(card_widget, parent_widget):
    """
    Enttappt eine Karte.
    
    Args:
        card_widget (CardWidget): Das Widget der zu enttappenden Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Karte enttappen
    card_data = card_widget.get_card_data()
    
    # Bestätigungsdialog
    result = QMessageBox.question(
        parent_widget,
        "Karte enttappen",
        f"Möchten Sie die Karte '{card_data.get('name', 'Unbekannt')}' enttappen?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if result == QMessageBox.Yes:
        # Karte enttappen
        card_widget.set_tapped(False)
        
        # Aktualisiere Karte im Spielzustand
        for card in parent_widget.game_state.get('battlefield', []):
            if card.get('id') == card_data.get('id'):
                card['tapped'] = False
                break
        
        # Spielzustand speichern
        parent_widget.game_engine.save_game_state()
        
        # UI aktualisieren
        parent_widget.update_ui()
        
        # Statusmeldung
        parent_widget.status_bar.showMessage(f"Karte '{card_data.get('name', 'Unbekannt')}' wurde enttappt.")


def attack_with_card(card_widget, parent_widget):
    """
    Greift mit einer Karte an.
    
    Args:
        card_widget (CardWidget): Das Widget der angreifenden Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Karte angreifen lassen
    card_data = card_widget.get_card_data()
    
    # Prüfe, ob die Karte angreifen kann (nicht getappt, ist eine Kreatur, etc.)
    if card_widget.is_tapped():
        QMessageBox.warning(
            parent_widget,
            "Fehler",
            "Getappte Kreaturen können nicht angreifen."
        )
        return
    
    if 'Creature' not in card_data.get('type', ''):
        QMessageBox.warning(
            parent_widget,
            "Fehler",
            "Nur Kreaturen können angreifen."
        )
        return
    
    # Bestätigungsdialog
    result = QMessageBox.question(
        parent_widget,
        "Mit Karte angreifen",
        f"Möchten Sie mit der Karte '{card_data.get('name', 'Unbekannt')}' angreifen?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if result == QMessageBox.Yes:
        # Karte als angreifend markieren
        card_widget.set_attacking(True)
        card_widget.set_tapped(True)  # Angreifende Kreaturen werden getappt
        
        # Aktualisiere Karte im Spielzustand
        for card in parent_widget.game_state.get('battlefield', []):
            if card.get('id') == card_data.get('id'):
                card['attacking'] = True
                card['tapped'] = True
                break
        
        # Spielzustand speichern
        parent_widget.game_engine.save_game_state()
        
        # UI aktualisieren
        parent_widget.update_ui()
        
        # Statusmeldung
        parent_widget.status_bar.showMessage(f"Karte '{card_data.get('name', 'Unbekannt')}' greift an.")


def block_with_card(card_widget, parent_widget):
    """
    Blockt mit einer Karte.
    
    Args:
        card_widget (CardWidget): Das Widget der blockenden Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Karte blocken lassen
    card_data = card_widget.get_card_data()
    
    # Prüfe, ob die Karte blocken kann (nicht getappt, ist eine Kreatur, etc.)
    if card_widget.is_tapped():
        QMessageBox.warning(
            parent_widget,
            "Fehler",
            "Getappte Kreaturen können nicht blocken."
        )
        return
    
    if 'Creature' not in card_data.get('type', ''):
        QMessageBox.warning(
            parent_widget,
            "Fehler",
            "Nur Kreaturen können blocken."
        )
        return
    
    # Finde angreifende Kreaturen
    attacking_creatures = []
    for card in parent_widget.game_state.get('battlefield', []):
        if card.get('attacking', False) and 'Creature' in card.get('type', ''):
            attacking_creatures.append(card)
    
    if not attacking_creatures:
        QMessageBox.warning(
            parent_widget,
            "Fehler",
            "Es gibt keine angreifenden Kreaturen, die geblockt werden können."
        )
        return
    
    # Dialog für die Auswahl der zu blockenden Kreatur
    # Für jetzt einfach die erste angreifende Kreatur wählen
    attacking_card = attacking_creatures[0]
    
    # Bestätigungsdialog
    result = QMessageBox.question(
        parent_widget,
        "Mit Karte blocken",
        f"Möchten Sie mit der Karte '{card_data.get('name', 'Unbekannt')}' die angreifende Kreatur '{attacking_card.get('name', 'Unbekannt')}' blocken?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if result == QMessageBox.Yes:
        # Karte als blockend markieren
        card_widget.set_blocking(True)
        
        # Aktualisiere Karte im Spielzustand
        for card in parent_widget.game_state.get('battlefield', []):
            if card.get('id') == card_data.get('id'):
                card['blocking'] = True
                card['blocking_id'] = attacking_card.get('id')  # Speichern, welche Kreatur geblockt wird
                break
        
        # Spielzustand speichern
        parent_widget.game_engine.save_game_state()
        
        # UI aktualisieren
        parent_widget.update_ui()
        
        # Statusmeldung
        parent_widget.status_bar.showMessage(
            f"Karte '{card_data.get('name', 'Unbekannt')}' blockt '{attacking_card.get('name', 'Unbekannt')}'."
        )