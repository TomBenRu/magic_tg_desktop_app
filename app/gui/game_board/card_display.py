"""
Funktionen zur Darstellung von Karten auf dem Spielbrett.

Dieses Modul enthält Funktionen zur Anzeige und Interaktion mit Karten.
"""

from PySide6.QtWidgets import QLabel, QMenu, QMessageBox, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QCursor


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
        QLabel: Das erstellte Karten-Widget.
    """
    # Hier würde normalerweise ein spezielles CardWidget erstellt werden
    # Da wir das noch nicht implementiert haben, erstellen wir ein einfaches QLabel
    
    label = QLabel(card.get('name', 'Unbekannte Karte') if show_face else 'Karte')
    label.setAlignment(Qt.AlignCenter)
    label.setMinimumSize(100, 140)
    label.setMaximumSize(100, 140)
    label.setFrameShape(QFrame.Box)
    label.setLineWidth(1)
    
    # Hintergrundfarbe basierend auf dem Kartentyp setzen
    bg_color = QColor(255, 255, 255)  # Standard: Weiß
    
    if not show_face:
        # Kartenrückseite: Blau
        bg_color = QColor(0, 0, 128)
    elif 'Creature' in card.get('type', ''):
        # Kreatur: Hellrot
        bg_color = QColor(255, 200, 200)
    elif 'Land' in card.get('type', ''):
        # Land: Grün
        bg_color = QColor(200, 255, 200)
    elif 'Instant' in card.get('type', '') or 'Sorcery' in card.get('type', ''):
        # Spontanzauber oder Hexerei: Hellblau
        bg_color = QColor(200, 200, 255)
    elif 'Artifact' in card.get('type', ''):
        # Artefakt: Grau
        bg_color = QColor(220, 220, 220)
    elif 'Enchantment' in card.get('type', ''):
        # Verzauberung: Gelb
        bg_color = QColor(255, 255, 200)
    elif 'Planeswalker' in card.get('type', ''):
        # Planeswalker: Orange
        bg_color = QColor(255, 220, 180)
    
    # Hintergrundfarbe setzen
    palette = QPalette()
    palette.setColor(QPalette.Window, bg_color)
    label.setAutoFillBackground(True)
    label.setPalette(palette)
    
    # Wenn die Karte getappt ist, drehen wir den Text
    if card.get('tapped', False):
        label.setText(f"[GETAPPT]\n{label.text()}")
    
    # Wenn die Karte im Kampf ist, einen Hinweis hinzufügen
    if zone == 'battlefield' and card.get('attacking', False):
        label.setText(f"[ANGREIFEND]\n{label.text()}")
    elif zone == 'battlefield' and card.get('blocking', False):
        label.setText(f"[BLOCKIEREND]\n{label.text()}")
    
    # Speichere Karteninformationen im Widget
    label.setProperty('card_data', card)
    label.setProperty('zone', zone)
    label.setProperty('owner_id', owner_id)
    
    # Kontext-Menü für Aktionen
    label.setContextMenuPolicy(Qt.CustomContextMenu)
    label.customContextMenuRequested.connect(
        lambda pos: show_card_context_menu(pos, card, zone, owner_id, parent_widget, label)
    )
    
    return label


def show_card_context_menu(pos, card, zone, owner_id, parent_widget, card_widget):
    """
    Zeigt ein Kontextmenü für eine Karte an.
    
    Args:
        pos (QPoint): Die Position des Menüs.
        card (dict): Die Karteninformationen.
        zone (str): Die Zone, in der sich die Karte befindet.
        owner_id (str): Die ID des Besitzers.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
        card_widget: Das Widget der Karte.
    """
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
            if card.get('tapped', False):
                tap_action = menu.addAction("Enttappen")
            else:
                tap_action = menu.addAction("Tappen")
            
            # Für Kreaturen
            if 'Creature' in card.get('type', ''):
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
            show_card_details(card)
        elif action.text() == "Spielen":
            play_card(card, parent_widget)
        elif action.text() == "Abwerfen":
            discard_card(card, parent_widget)
        elif action.text() == "Tappen":
            tap_card(card, parent_widget)
        elif action.text() == "Enttappen":
            untap_card(card, parent_widget)
        elif action.text() == "Angreifen":
            attack_with_card(card, parent_widget)
        elif action.text() == "Blocken":
            block_with_card(card, parent_widget)


def show_card_details(card):
    """
    Zeigt die Details einer Karte an.
    
    Args:
        card (dict): Die Karteninformationen.
    """
    # Hier würde ein Dialog mit den Kartendetails angezeigt werden
    # Für jetzt nur eine Meldung
    QMessageBox.information(
        None,
        "Kartendetails",
        f"Name: {card.get('name', 'Unbekannt')}\n"
        f"Typ: {card.get('type', 'Unbekannt')}\n"
        f"Manakosten: {card.get('mana_cost', 'Unbekannt')}\n"
        f"Regeltext: {card.get('rules_text', 'Kein Regeltext')}\n"
        f"Stärke/Widerstandskraft: {card.get('power', '-')}/{card.get('toughness', '-')}"
    )


def play_card(card, parent_widget):
    """
    Spielt eine Karte aus der Hand.
    
    Args:
        card (dict): Die zu spielende Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Hier würde die Karte gespielt werden
    # Für jetzt nur eine Meldung
    QMessageBox.information(
        parent_widget,
        "Karte spielen",
        f"Die Karte {card.get('name', 'Unbekannt')} wird gespielt."
    )
    
    # Später würde hier der GameEngine aufgerufen werden
    # parent_widget.game_engine.play_card(parent_widget.active_player_id, card['id'])
    # parent_widget.update_ui()


def discard_card(card, parent_widget):
    """
    Wirft eine Karte aus der Hand ab.
    
    Args:
        card (dict): Die abzuwerfende Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Hier würde die Karte abgeworfen werden
    # Für jetzt nur eine Meldung
    QMessageBox.information(
        parent_widget,
        "Karte abwerfen",
        f"Die Karte {card.get('name', 'Unbekannt')} wird abgeworfen."
    )
    
    # Später würde hier der GameEngine aufgerufen werden
    # parent_widget.game_engine.move_card(card['id'], 'hand', 'graveyard', parent_widget.active_player_id)
    # parent_widget.update_ui()


def tap_card(card, parent_widget):
    """
    Tappt eine Karte.
    
    Args:
        card (dict): Die zu tappende Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Hier würde die Karte getappt werden
    # Für jetzt nur eine Meldung
    QMessageBox.information(
        parent_widget,
        "Karte tappen",
        f"Die Karte {card.get('name', 'Unbekannt')} wird getappt."
    )
    
    # Später würde hier der GameEngine aufgerufen werden
    # card['tapped'] = True
    # parent_widget.update_ui()


def untap_card(card, parent_widget):
    """
    Enttappt eine Karte.
    
    Args:
        card (dict): Die zu enttappende Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Hier würde die Karte enttappt werden
    # Für jetzt nur eine Meldung
    QMessageBox.information(
        parent_widget,
        "Karte enttappen",
        f"Die Karte {card.get('name', 'Unbekannt')} wird enttappt."
    )
    
    # Später würde hier der GameEngine aufgerufen werden
    # card['tapped'] = False
    # parent_widget.update_ui()


def attack_with_card(card, parent_widget):
    """
    Greift mit einer Karte an.
    
    Args:
        card (dict): Die angreifende Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Hier würde mit der Karte angegriffen werden
    # Für jetzt nur eine Meldung
    QMessageBox.information(
        parent_widget,
        "Mit Karte angreifen",
        f"Die Karte {card.get('name', 'Unbekannt')} greift an."
    )
    
    # Später würde hier der GameEngine aufgerufen werden
    # parent_widget.game_engine.attack_with_creatures(parent_widget.active_player_id, [card['id']], parent_widget.inactive_player_id)
    # parent_widget.update_ui()


def block_with_card(card, parent_widget):
    """
    Blockt mit einer Karte.
    
    Args:
        card (dict): Die blockende Karte.
        parent_widget: Das Eltern-Widget, das Zugriff auf die Spiellogik hat.
    """
    # Hier würde mit der Karte geblockt werden
    # Für jetzt nur eine Meldung
    QMessageBox.information(
        parent_widget,
        "Mit Karte blocken",
        f"Die Karte {card.get('name', 'Unbekannt')} blockt."
    )
    
    # Später würde hier der GameEngine aufgerufen werden
    # parent_widget.game_engine.declare_blockers(parent_widget.active_player_id, {card['id']: attacking_card_id})
    # parent_widget.update_ui()
