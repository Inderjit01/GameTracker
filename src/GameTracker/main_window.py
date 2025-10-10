import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QLineEdit, QMessageBox, QScrollArea
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFile, QTextStream, Qt, QThreadPool

# Classes
from widgets.game_card import GameCard
from dialogs.add_game import AddGameDialog
from controllers.game_controller import GameController
from widgets.prices import WishlistPriceRunnable
# 
from controllers.api import search_games, fetch_hltb_data, fetch_steam_review_score
from models.db import resource_path
# Variables
from version import __version__

class MainWindow(QMainWindow):
    def __init__(self):
        # super grabs the attributes of QMainWindow such as isCentralWidget
        super().__init__()
        
        # methods of QWidget which QMainWindow inherits
        self.setWindowTitle(f'GameTracker v{__version__}')
        self.resize(1000, 640)
        self.setWindowIcon(QIcon(resource_path('../images/game_tracker_logo.png')))
        
        # Class I made to modify games.db
        self.controller = GameController()
        
        # Grabs the prices of wishlisted games
        self.wishlist_prices = {}
        self.thread_pool = QThreadPool()
        self.start_fetch_wishlist_prices()
        
        # creates the UI
        self._setup_ui()
        
        # loads all of the styling for the UI
        self.load_stylesheet()
        
    def start_fetch_wishlist_prices(self):
        # This line is initializing the object
        runnable = WishlistPriceRunnable(self.controller)
        
        # Connect the 'finished' signal to the method that handles the results
        # on_prices_fetched will be called when the thread finishes
        runnable.signals.finished.connect(self.on_prices_fetched)
        
        # This calls the 'run' method of WishlistPriceRunnable in a background thread
        self.thread_pool.start(runnable)
    
    # If wishlist is selected and the thread for prices just finished reload the game_cards with the store prices
    def on_prices_fetched(self, prices):
        self.wishlist_prices = prices
        selected_indexes = [self.nav_list.row(item) for item in self.nav_list.selectedItems()]
        if 4 in selected_indexes:
            self.load_games()
        
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # Left side of the page
        # Filter bar
        sidebar = QVBoxLayout()
        
        # The title for the list of filters
        self.nav_title = QLabel('Filter by Status')
        self.nav_title.setAlignment(Qt.AlignCenter)
        self.nav_title.setObjectName('NavTitle')
        sidebar.addWidget(self.nav_title)
        
        self.nav_list = QListWidget()
        self.nav_list.addItems(['Backlog', 'Favorites', 'Score', 'Hours', 'Wishlist', 'Completed'])
        self.nav_list.setSelectionMode(QListWidget.MultiSelection)
        self.nav_list.item(0).setSelected(True)
        self.nav_list.setFixedWidth(100)
        self.nav_list.setFixedHeight(120)
        self.nav_list.itemSelectionChanged.connect(self.on_nav_changed)
        sidebar.addWidget(self.nav_list)
        
        sidebar.addStretch()
        main_layout.addLayout(sidebar)
        
        # Right side of the page
        right_area = QVBoxLayout()
        
        # Search bar to add games or find games in backlog
        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search games')
        self.search_input.textChanged.connect(self.on_search)
        top_bar.addWidget(self.search_input)
        
        # Add new games button
        self.add_btn = QPushButton('Add')
        self.add_btn.clicked.connect(self.on_add_game)
        top_bar.addWidget(self.add_btn)
        
        # Delete game from backlog
        self.delete_btn = QPushButton('Delete')
        self.delete_btn.clicked.connect(self.on_delete_game)
        top_bar.addWidget(self.delete_btn)
        
        # Add everything to the right side of the page
        right_area.addLayout(top_bar)
        
        # Dispalys the games from the database
        # Allows scrolling through the widget one the page fills
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # Where the games will display
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.cards_container)
        right_area.addWidget(self.scroll_area)
        # To know which card has been selected by user
        self.selected_card = None
        
        main_layout.addLayout(right_area)
        self.load_games()
    
    # Loads the apps css (for pyqt5 it is called qss)
    def load_stylesheet(self):
        path = resource_path("../styles/styles.qss")
        if os.path.exists(path):
            file = QFile(path)
            file.open(QFile.ReadOnly | QFile.Text)
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())
            file.close()
        
    
    # -----Event Handlers-----
    
    # Loads the list of games when a new filter is selected from sidebar
    # If Completed is selected it will deselect all other filters
    def on_nav_changed(self):
        selected_items = self.nav_list.selectedItems()
        completed_item = self.nav_list.item(5)
        if completed_item in selected_items:
            for i in range(self.nav_list.count()):
                item = self.nav_list.item(i)
                if item != completed_item:
                    item.setSelected(False)
                    
        self.load_games()
        
    def on_search(self, text):
        self.load_games(filter_text=text)
    
    def on_add_game(self):
        # search_text is the text in the search bar currently
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, 'Error', 'Type a game in the search bar to add!')
            return
        
        # search_games returns rawg search engine names, platforms, ratings, and release date
        suggestions = search_games(search_text, max_results=10)
        
        # Displays the suggestions in a new window
        dlg = AddGameDialog(self, search_text=search_text, suggestions=suggestions)
        # If user clicks backlog or wishlist this runs
        if dlg.exec_():
            # returns the selected suggestion from the new window
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, 'Validation', 'Game is required!')
                return
            
            # Update the search game to the one selected by the user
            search_text = data['name']
            # Grab HowLongToBeatData Based on user's selected game
            hltb_data = fetch_hltb_data(search_text)
            if hltb_data is None:
                hltb_data = {}    
                
            # See if the game has a steam score else use rawg score when adding
            steam_score = fetch_steam_review_score(data['name'], 'US')
            print('steam score', steam_score)
            
            # add this game to the wishlist category of the database
            if data['action'] == 'wishlist':
                self.controller.add_game(
                    name=data['name'], 
                    platform=data.get('platform', None),
                    main_hours=hltb_data.get('main_story_hours', None),
                    main_extras_hours=hltb_data.get('main_extras_hours', None),
                    completionist_hours=hltb_data.get('completionist_hours', None),
                    all_styles_hours=hltb_data.get('all_styles_hours', None),
                    review_score=steam_score if steam_score else data.get('rating', None),
                    owned=0,
                    image_url=data.get('background_image', None)
                )
                # refresh the displayed database
                self.start_fetch_wishlist_prices()
                self.load_games()
                QMessageBox.information(self, 'Added', f"Added {data['name']} to WishList.")  
            # add this game to the backlog category  of the database
            else:
                self.controller.add_game(
                    name=data['name'], 
                    platform=data.get('platform', None),
                    main_hours=hltb_data.get('main_story_hours', None),
                    main_extras_hours=hltb_data.get('main_extras_hours', None),
                    completionist_hours=hltb_data.get('completionist_hours', None),
                    all_styles_hours=hltb_data.get('all_styles_hours', None),
                    review_score=steam_score if steam_score else data.get('rating', None),
                    owned=1,
                    image_url=data.get('background_image', None)
                )
                # refresh the displayed database
                self.load_games()
                QMessageBox.information(self, 'Added', f"Added {data['name']} to Backlog.")
            
    
    def on_delete_game(self):
        if not self.selected_card:
            QMessageBox.warning(self, 'Select a row', 'Please select a row to delete!')
            return
        
        game_id = self.selected_card.game_id
        g = self.controller.get_game(game_id)
        if not g:
            QMessageBox.warning(self, 'Not found', 'Could not find that game!')
            return
        
        ok = QMessageBox.question(self, 'Delete', f'Delete {g[1]} permanently?')
        if ok == QMessageBox.Yes:
            self.controller.delete_game(game_id)
            self.load_games()
            self.selected_card = None
            
    def on_card_selected(self, game_id):
        # Change any selected card to unselected
        if self.selected_card:
            self.selected_card.setProperty('selected', False)
            self.selected_card.style().unpolish(self.selected_card)
            self.selected_card.style().polish(self.selected_card)
            self.selected_card.update()
            
        # Changed the new selected card with the updated style
        for i in range(self.cards_layout.count()):
            widget = self.cards_layout.itemAt(i).widget()
            if hasattr(widget, 'game_id') and widget.game_id == game_id:
                self.selected_card = widget
                widget.setProperty('selected', True)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.update()
                break
            
    def mousePressEvent(self, event):
        # Get the widget at the clicked position
        pos_in_scroll = self.scroll_area.viewport().mapFrom(self, event.pos())
        clicked_widget = self.scroll_area.viewport().childAt(pos_in_scroll)
        
        if not isinstance(clicked_widget, GameCard):
            #Deselect current card if anything other than the game card was selected
            if self.selected_card:
                self.selected_card.setProperty('selected', False)
                self.selected_card.style().unpolish(self.selected_card)
                self.selected_card.style().polish(self.selected_card)
                self.selected_card.update()
                self.selected_card = None
                
        super().mousePressEvent(event)
                
        
    # -----Populates the games table-----
    
    def load_games(self, filter_text=""):
        selected_indexes = [self.nav_list.row(item) for item in self.nav_list.selectedItems()]
        games = self.controller.list_games(views=selected_indexes, filter_text=filter_text)
        
        # clears all games currently loaded on page
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
    
        # Add new cards
        for g in games:
            try:
                price_info = None
                if 4 in selected_indexes:
                    price_info = self.wishlist_prices.get(g[0], None)
                
                card = GameCard(g, self.controller, price_info=price_info)
                # GameCard emits the game_id when selected in game_card
                card.selected.connect(self.on_card_selected)
                self.cards_layout.addWidget(card)
            except Exception as e:
                print(f'Failed to generate game card for {g[1]}')
                print(f'Error: {e}')

                