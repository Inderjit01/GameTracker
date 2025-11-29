from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
from threading import Thread
import configparser

# Methods
from controllers.api import steam_prices, epic_prices, xbox_prices, nintendo_prices, playstation_prices
from widgets.profile_menu import load_settings

# Grabs the users perfered stores from the ini file
store_preferences = load_settings()
        
class WorkerSignals(QObject):
    finished = pyqtSignal(dict)  # emits the result

class WishlistPriceRunnable(QRunnable):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.signals = WorkerSignals()
    
    # Only runs when called with thread.start from main_window
    def run(self):
        wishlist_prices = {}
        # grabs all the games in the wishlist category
        wishlist_games = self.controller.list_games(views=[4])
        
        for g in wishlist_games:
            game_id = g[0]
            platform = (g[2] or "").lower()
            # To only grab the store with the lowest price
            best_price = float('infinity')
            price_info = {'store': None, 'full_price': None, 'sale_price': None, 'subscription': []}
            
            # Edits price_info with the best price info
            def edit_price_info(platform_price_info, store):
                nonlocal best_price
                if platform_price_info == 'Free':
                    if price_info['full_price'] != 'Free':
                        price_info['store'] = store
                        price_info['full_price'] = 'Free'
                        best_price = 0
                elif platform_price_info:
                    full_price = platform_price_info.get('initial')
                    sale_price = platform_price_info.get('final')
                    # Exit if either is missing
                    if full_price is None or sale_price is None:
                        return
                    
                    if sale_price and sale_price < best_price:
                        price_info['store'] = store
                        price_info['full_price'] = full_price
                        if full_price != sale_price:
                            price_info['sale_price'] = sale_price
                        best_price = sale_price
                    if platform_price_info.get('game_pass'):
                        price_info['subscription'].append('Game Pass')
                    if platform_price_info.get('playstation_extra'):
                        price_info['subscription'].append('PS Extra')
                    if platform_price_info.get('playstation_premium'):
                        price_info['subscription'].append('PS Premium')
            
            # save the store and api method so we can thread it to be faster
            api_calls = []
            # Checks steam and epic store 
            if 'pc' in platform:
                if store_preferences.get("steam", True):
                    api_calls.append(('Steam', lambda: steam_prices(g[1], 'US')))
                if store_preferences.get("epic", True):
                    api_calls.append(('Epic Games', lambda: epic_prices(g[1], 'US')))
           
            # Checks microsoft store    
            if ('pc' in platform or 'xbox' in platform) and store_preferences.get("xbox", True):
                api_calls.append(('Xbox', lambda: xbox_prices(g[1], 'US')))
            
            # Checks playstation store
            if 'playstation' in platform and store_preferences.get('playstation', True):
                api_calls.append(('Playstation', lambda: playstation_prices(g[1], 'US')))
            
            # Checks nintendo store
            if 'nintendo' in platform and store_preferences.get('nintendo', True):
                api_calls.append(('Nintendo', lambda: nintendo_prices(g[1], 'US')))
                
            # Save all the thread objects to make sure they all finish
            threads = []
            # API results are store in results
            results = {}
            # Runs the api method
            def run_api(store, func):
                try:
                    results[store] = func()
                except Exception as e:
                    print(f'Error fetching {store} for {g[1]}: {e}')
                    results[store] = None
                    
            # Starts the thread      
            for store, func in api_calls:
                t = Thread(target=run_api, args=(store, func))
                t.start()
                threads.append(t)
            
            # Waits for every thread to finish    
            for t in threads:
                t.join()
            
            # update price_info for each store
            for store, result in results.items():
                edit_price_info(result, store)
                                
            # Stores each games best prices and store
            wishlist_prices[game_id] = price_info
        
        # Sends finsihed thread signal and returns the wishlist_prices
        self.signals.finished.emit(wishlist_prices)