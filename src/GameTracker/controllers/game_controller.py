import sqlite3
from datetime import datetime

# variable
from models.db import DB_FILE

class GameController:
    # Creates an instance of db_file
    def __init__(self):
        self.db_file = DB_FILE
    
    # local method to connect to games.db
    def _connect(self):
        return sqlite3.connect(self.db_file)
    
    # When a new game is added include game_name, platforms, hours (the four types), score, if they own it(if they add to backlog or wishlist), rawg image location url
    # id auto increments, (favorite, completed, and completed date) is added by the user manually, and added_date is auto added when entered to the db
    def add_game(self, name, platform=None, main_hours=None, main_extras_hours=None, completionist_hours=None, all_styles_hours=None, review_score=None, owned=0, image_url=None):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO games 
                       (name, platform, main_hours, main_extras_hours, completionist_hours, all_styles_hours, review_score, owned, image_url) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) """, 
                       (name, platform, main_hours, main_extras_hours, completionist_hours, all_styles_hours, review_score, owned, image_url))
        conn.commit()
        game_id = cursor.lastrowid
        conn.close()
        return game_id
    
    # delete game by id
    def delete_game(self, game_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM games WHERE id = (?)""", (game_id,))
        conn.commit()
        conn.close()
        
    # grabs all the information on a game by id
    def get_game(self, game_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM games WHERE id = (?)""", (game_id,))
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        return row
    
    # changes favorite, owned, completed, and completed_date. The user selects these themselves.
    def update_status(self, game_id, field, value):
        conn = self._connect()
        cursor = conn.cursor()
        if field == 'completed':
            if value == 1:
                completed_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("""UPDATE games SET completed = ?, completed_date = ?, owned = 1, favorite = 0 WHERE id = ?""", (1, completed_date, game_id), )
            else:
                cursor.execute("""UPDATE games SET completed = ?, completed_date = ? WHERE id = ?""", (0, None, game_id))
        else:
            cursor.execute(f""""UPDATE games SET {field} = ? WHERE id = ?""", (value, game_id))
        conn.commit()
        conn.close()
        
    # This is the filter system on the left side of the program. It grabs the games based on the filters selected by the user
    def list_games(self, views=None, filter_text=""):
        '''
            0=backlog, 1=favorites, 2=score, 3=hours, 4=wishlist, 5=completed
        '''
        conn = self._connect()
        cursor = conn.cursor()
        
        query = "SELECT * FROM games"
        conditions = []
        params = []
        
        # completed games will always be completed and owned
        if views and 5 in views:
            conditions.append('completed = 1')
            conditions.append('owned = 1')    
        else:
            # completed will always be 0 outside of the completed filter
            conditions.append('completed = 0')
            
            # if the game is wishlisted then it can't be owned
            if views and 4 in views:
                conditions.append('owned = 0')
            else:
                conditions.append('owned = 1')
                
            # if favorite is selected then only show favorited games
            if views and 1 in views:
                conditions.append('favorite = 1')
            
        # If anything is added to the search bar add it to the filter.
        # put filter in separate variable to prevent injection
        if filter_text:
            conditions.append('name LIKE ?')
            params.append(f'%{filter_text}%')
            
        # adds all the conditions to the query with an and
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
            
        # If completed is selected order by most recent date completed
        if views and 5 in views:
            query += ' ORDER BY completed_date DESC'
        # if score is selected order by highest to lowest score
        elif views and 2 in views:
            query += ' ORDER BY review_score DESC'
        # if hours is selected order by lowest to highest to compelete main story
        elif views and 3 in views:
            query += ' ORDER BY main_hours'
        # default to game name
        else:
            query += ' ORDER BY name'
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        conn.close()
        return rows