from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QSizePolicy
    )
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

# class
from widgets.strike_label import StrikeLabel

class GameCard(QWidget):
    selected = pyqtSignal(int)
    
    def __init__(self, game, controller, price_info=None, parent=None):
        super().__init__(parent)
        self.game = game
        self.game_id = game[0]
        self.controller = controller
        
        self.setObjectName('GameCard')
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(170)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 5, 30, 5)  # this acts like padding
                
        # Cover Art
        self.cover = QLabel()
        self.cover.setFixedSize(120, 160)
        self.cover.setObjectName('GameArt')
        self.cover.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.cover)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top row for title and trigger buttons
        top_row_layout = QHBoxLayout()
        top_row_layout.setAlignment(Qt.AlignRight)
        
        # Title
        self.title = QLabel(f'{game[1]}') # Game Name
        self.title.setObjectName('GameTitle')
        top_row_layout.addWidget(self.title)
        top_row_layout.addStretch()
        
        # Favorite Button
        self.favorite_btn = QPushButton('⭐' if game[9] else '☆')
        self.favorite_btn.setCheckable(True)
        self.favorite_btn.setChecked(bool(game[9]))
        self.favorite_btn.setFixedSize(35, 35)
        self.favorite_btn.setObjectName('Trigger')
        self.favorite_btn.setToolTip('Mark game as favorite')
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        top_row_layout.addWidget(self.favorite_btn)
        
        # Owned Button
        self.owned_btn = QPushButton('✅' if game[8] else '❌')
        self.owned_btn.setCheckable(True)
        self.owned_btn.setChecked(bool(game[8]))
        self.owned_btn.setFixedSize(35, 35)
        self.owned_btn.setObjectName('Trigger')
        self.owned_btn.setToolTip('Mark game as owned')
        self.owned_btn.clicked.connect(self.toggle_owned)
        top_row_layout.addWidget(self.owned_btn)
        
        # Completed button
        self.completed_btn = QPushButton('✅' if game[10] else '❌')
        self.completed_btn.setCheckable(True)
        self.completed_btn.setFixedSize(35, 35)
        self.completed_btn.setObjectName('Trigger')
        self.completed_btn.setToolTip('Mark game as completed')
        self.completed_btn.setChecked(bool(game[10]))
        self.completed_btn.clicked.connect(self.toggle_completed)  # you'll define this
        top_row_layout.addWidget(self.completed_btn)
        
        info_layout.addLayout(top_row_layout)
        
        # Addes platforms
        if game[2]:
            grouped_platforms = {}
            platforms = sorted(game[2].split(', '))
            for platform in platforms:
                parts = platform.split(maxsplit=1)
                game_company = parts[0]
                system_versions = parts[1] if len(parts) > 1 else ''
                
                grouped_platforms.setdefault(game_company, set()).add(system_versions)
                    
            formatted = []
            for game_company, system_versions in grouped_platforms.items():
                if system_versions and '' not in system_versions:
                    if len(system_versions) > 1:
                        versions = sorted(system_versions)
                        formatted.append(f"{game_company} ({', '.join(versions)})")
                    else:
                        formatted.append(f"{game_company} {''.join(system_versions)}")
                else:
                    formatted.append(f'{game_company}')
                    
            platforms_string = ', '.join(formatted)
        else:
            platforms_string = 'Platforms: Unknown'
            
        self.platform = QLabel(platforms_string)
        self.platform.setObjectName('GamePlatform')
        info_layout.addWidget(self.platform)
        
        # Adds review score
        score_value = self.score_to_percentage(game[7])
        self.review = QLabel(f"Score: {score_value}/100")
        self.review.setObjectName('GameReview')
        info_layout.addWidget(self.review)
        self.review.setProperty('scoreTier', 'unreleased')
        if isinstance(score_value, int):
            if score_value >= 80:
                self.review.setProperty('scoreTier', 'high')
            elif score_value >= 60:
                self.review.setProperty('scoreTier', 'mid')
            else:
                self.review.setProperty('scoreTier', 'low')
        self.review.style().unpolish(self.review)
        self.review.style().polish(self.review)
        
        # Adds the hours types of hours
        self.hours = QLabel(
            f"""
            <table style="font-size:10pt;">
              <tr>
                <td><b>⏱️ Main:</b></td>
                <td valign="middle">{self.format_hours(game[3])}</td>
                <td style="padding-left:25px;"><b>➕ Extras:</b></td>
                <td valign="middle">{self.format_hours(game[4])}</td>
              </tr>
              <tr>
                <td><b>🏆 Completionist:</b></td>
                <td valign="middle">{self.format_hours(game[5])}</td>
                <td style="padding-left:25px;"><b>🎮 All Styles:</b></td>
                <td valign="middle">{self.format_hours(game[6])}</td>
              </tr>
            </table>
            """
        )
        self.hours.setObjectName('GameHours')
        info_layout.addWidget(self.hours)
        
        # Adds added date and completed date if completed date is in database
        if game[11]:
            self.dates = QLabel(f'Added: {self.grab_only_date(game[12])} \n Completed: {self.grab_only_date(game[11])}')
            self.dates.setObjectName('GameDate')
            self.dates.setAlignment(Qt.AlignRight)
            info_layout.addWidget(self.dates)
        else: 
            self.dates = QLabel(f'Added: {self.grab_only_date(game[12])}')
            self.dates.setObjectName('GameDate')
            self.dates.setAlignment(Qt.AlignRight)
            info_layout.addWidget(self.dates)
        
        # Formating for the these widgets
        for label in [self.platform, self.hours, self.review, self.dates]:
            label.setContentsMargins(0, 0, 0, 0)
            label.setSizePolicy(label.sizePolicy().horizontalPolicy(), QSizePolicy.Fixed)
        
        main_layout.addLayout(info_layout)
        
        # right side of the game card has the price info
        price_labels = []
        if price_info:
            # Adds the vertical line 
            separator = QFrame()
            separator.setObjectName('PriceSeparator')
            separator.setFrameShape(QFrame.VLine)
            separator.setFrameShadow(QFrame.Sunken)
            main_layout.addWidget(separator)
            
            # Adds the price info
            price_container = QWidget()
            price_labels.append(price_container)
            price_container.setMinimumWidth(142)
            price_container.setMaximumWidth(142)
            price_layout = QVBoxLayout(price_container)
            price_layout.setAlignment(Qt.AlignCenter)
            
            store = price_info.get("store", "Unknown")
            full_price = price_info.get("full_price", "-")
            sale_price = price_info.get("sale_price", None)
            on_subscription_service = price_info.get('subscription', None)
            
            if not store:
                self.store_label = QLabel('Unknown')
                self.store_label.setObjectName('GameStore')
                price_labels.append(self.store_label)
                self.store_label.setAlignment(Qt.AlignCenter)
                price_layout.addWidget(self.store_label)
            else:
                self.store_label = QLabel(f'{store}')
                self.store_label.setObjectName('GameStore')
                price_labels.append(self.store_label)
                self.store_label.setAlignment(Qt.AlignCenter)
                price_layout.addWidget(self.store_label)
                
                if full_price == 'Free':
                    self.full_label = QLabel('Free')
                    self.full_label.setProperty('priceStatus', 'Free')
                else:
                    self.full_label = StrikeLabel(f'Full Price: ${full_price}')
                self.full_label.setObjectName('GamePrice')
                price_labels.append(self.full_label)
                self.full_label.setAlignment(Qt.AlignCenter)
                price_layout.addWidget(self.full_label)
                
                if sale_price and sale_price < full_price:
                    self.full_label.enable_strike(True)
                    self.sale_label = QLabel(f"SALE: ${sale_price}")
                    self.sale_label.setObjectName('GameSalePrice')
                    price_labels.append(self.sale_label)
                    self.sale_label.setAlignment(Qt.AlignCenter)
                    price_layout.addWidget(self.sale_label)
                    
                if on_subscription_service:
                    subscription_string = ',<br>'.join(on_subscription_service)
                    label_text =    f'<span style="color:white; font-weight:bold;">Subscriptions:</span><br>' \
                                    f'<span style="color:#0097A7;">{subscription_string}</span>'
                    self.subscription_service_label = QLabel(label_text)
                    self.subscription_service_label.setObjectName('GameSubscriptionService')
                    price_labels.append(self.subscription_service_label)
                    self.subscription_service_label.setAlignment(Qt.AlignCenter)
                    price_layout.addWidget(self.subscription_service_label)
            
            for w in price_labels:
                w.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # optional if you want clicks to pass to the card
                w.setStyleSheet("background: transparent;")
            
            main_layout.addWidget(price_container)
        
        # makes all button transparent so it uses the GameCard background. Allows me to easily change background
        make_transparent_labels = [self.title, self.platform, self.hours, self.review, self.cover, self.dates] + price_labels
        for label_widget in make_transparent_labels:
            label_widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)  # optional if you want clicks to pass to the card
            label_widget.setStyleSheet("background: transparent;")
        
        # loads game image
        image_url = game[13] if len(game) > 12 else None
        if image_url:
            self.load_image(image_url)
            
    # Grabs the image from the url   
    def load_image(self, url):
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.on_image_loaded)
        self.manager.get(QNetworkRequest(QUrl(url)))
    # loads the image
    def on_image_loaded(self, reply):
        pixmap = QPixmap()
        pixmap.loadFromData(reply.readAll())
        self.cover.setPixmap(
            pixmap.scaled(self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
    
    # If a game card gets selected emit the game_id for main_window
    def mousePressEvent(self, event):
        self.selected.emit(self.game_id)
    
    # Allows user to toggle favorite
    def toggle_favorite(self, checked):
        self.controller.update_status(self.game_id, 'favorite', 1 if checked else 0)
        self.favorite_btn.setText('⭐' if checked else '☆')
    
    # Allows user to toggle owned   
    def toggle_owned(self, checked):
        self.controller.update_status(self.game_id, 'owned', 1 if checked else 0)
        self.owned_btn.setText('✅' if checked else '❌')
    
    # Allows user to toggle completed
    def toggle_completed(self, checked):
        self.controller.update_status(self.game_id, 'completed', 1 if checked else 0)
        self.completed_btn.setText('✅' if checked else '❌')
    
    # convert the hours decimal to minutes
    def format_hours(self, hours):
        if hours is None:
            return 'Unknown'
        try: 
            h = int(hours)
            m = int(round((hours - h) * 60))
            if m > 0:
                return f"{h}h {m}m"
            else: 
                return f"{h}h"
        except:
            return str(hours)
        
    # convert the score which is out of 5 to be out of 100 
    def score_to_percentage(self, score):
        try: 
            return round((float(score) / 5) * 100)
        except:
            return 'Unknown'
        
    # Formating for date
    def grab_only_date(self, date_time):
        return date_time.split(' ')[0]