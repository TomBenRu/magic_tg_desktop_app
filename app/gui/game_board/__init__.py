"""
Spielbrett-Paket für die Magic the Gathering Desktop App.

Dieses Paket enthält alle Module, die für das Spielbrett benötigt werden.
"""

from app.gui.game_board.main_board import GameBoardWidget
from app.gui.game_board.zones import GameZone, BattlefieldZone
from app.gui.game_board.card_widget import CardWidget, DraggableCardWidget
from app.gui.game_board.card_display import create_card_widget, show_card_details
from app.gui.game_board.game_dialogs import NewGameDialog, LoadGameDialog

__all__ = [
    'GameBoardWidget',
    'GameZone',
    'BattlefieldZone',
    'CardWidget',
    'DraggableCardWidget',
    'create_card_widget', 
    'show_card_details',
    'NewGameDialog',
    'LoadGameDialog'
]