import sys
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from winotify import Notification, audio
from pathlib import Path

# classes
from controllers.game_controller import GameController
from widgets.prices import WishlistPriceRunnable
# methods
from models.db import resource_path

class Signals(QObject):
    finished = pyqtSignal(dict)

# sets up GameController and grabs prices from prices.py
class HeadlessRunnable(WishlistPriceRunnable):
    def __init__(self, controller):
        super().__init__(controller)
        self.signals = Signals()
        
def get_notification_icon():
    if getattr(sys, "frozen", False):
        # Running as bundled EXE (installed version)
        base = Path(sys.executable).parent / "images"
    else:
        # Running from development environment
        base = Path(__file__).resolve().parent / "images"
    
    icon_path = base / "game_tracker_logo.png"

    # Fallback if it somehow doesn't exist
    if not icon_path.exists():
        # Try same directory as executable (e.g., installer location)
        icon_path = Path(sys.executable).parent / "images" / "game_tracker_logo.png"

    return str(icon_path)

# if any favorited wishlist game is on sale send a windows message
def send_notifications(prices, controller):
    icon_path = get_notification_icon()
    for game_id, price_info in prices.items():
        g = controller.get_game(game_id)
        is_favorited = g[9]
        if is_favorited and price_info.get('sale_price', None):
            old_price = price_info.get('full_price', None)
            new_price = price_info.get('sale_price', None)
            if new_price and old_price and new_price < old_price:
                store = price_info.get('store', 'Unknown')
                toast = Notification(
                    app_id="GameTracker",
                    title=f'{g[1]} is on sale at {store}!',
                    msg=f"Sale: {new_price} Full: {old_price}",
                    icon=icon_path
                )
                toast.set_audio(audio.Default, loop=False)
                toast.show()
                
# Starts the background service
def run_headless(app):
    controller = GameController()
    thread_pool = QThreadPool()
    runnable = HeadlessRunnable(controller)
    
    def on_finished(prices):
        send_notifications(prices, controller)
        app.quit()

    runnable.signals.finished.connect(on_finished)
    thread_pool.start(runnable)