from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, 
    QLabel, QPushButton, QHBoxLayout
    )

class AddGameDialog(QDialog):
    def __init__(self, parent=None, search_text="", suggestions=[]):
        super().__init__(parent)
        self.setWindowTitle('Add Game')
        self.setMinimumWidth(700)
        self.setMinimumHeight(300)
        
        # returned attributes 
        self.suggestions = suggestions
        self.selected_game = None
        self.selected_game_platforms = None
        self.selected_game_rating = None
        self.selected_game_url = None
        self.action = None
        
        layout = QVBoxLayout(self)
        
        # Adds title
        self.info_label = QLabel('Select a game from the suggestions or type a new one:')
        layout.addWidget(self.info_label)
        
        # Adds search bar
        self.name_input = QLineEdit(self)
        self.name_input.setText(search_text)
        layout.addWidget(self.name_input)
        
        # Displays list of suggested games
        self.suggestion_list = QListWidget()
        for g in suggestions:
            display_text = f"{g['name']} ({','.join(g['platforms']) if g['platforms'] else 'Unknown Platforms'})"
            self.suggestion_list.addItem(display_text)
        layout.addWidget(self.suggestion_list)
        
        self.suggestion_list.itemClicked.connect(self.on_item_clicked)
        
        # Adds accept or reject buttons
        btn_layout = QHBoxLayout()
        
        self.backlog_btn = QPushButton('Add to Backlog')
        self.backlog_btn.clicked.connect(lambda: self.accept_with_action('backlog'))
        btn_layout.addWidget(self.backlog_btn)
        
        self.wishlist_btn = QPushButton('Add to Wishlist')
        self.wishlist_btn.clicked.connect(lambda: self.accept_with_action('wishlist'))
        btn_layout.addWidget(self.wishlist_btn)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    # Assigns the action attribute so I know to add to backlog or to wishlist
    def accept_with_action(self, action):
        self.action = action
        self.accept()
    
    # Assigns attributes for the game being selected
    def on_item_clicked(self, item):
        row = self.suggestion_list.row(item)
        game = self.suggestions[row]
        self.name_input.setText(game['name'])
        self.selected_game = game['name']
        self.selected_game_platforms = ', '.join(game['platforms'])
        self.selected_game_rating = game['rating']
        self.selected_game_url = game['background_image']
    
    # Returns the games attributes to be added to the database
    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "platform": self.selected_game_platforms or None,
            'rating': self.selected_game_rating or None,
            'background_image': self.selected_game_url or None,
            'action': self.action
        }