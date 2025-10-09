import os, sys, sqlite3
from pathlib import Path

# Grabs the path of resources based on if is running as an exe or development environment
def resource_path(rel):
    if getattr(sys, 'frozen', False):
        rel = rel.lstrip('../\\')
        if rel == 'games.db':
            # getenv gets os environment variable. EX. C:\Users\inder\AppData\Roaming
            base = Path(os.getenv('APPDATA')) / 'GameTracker'
            ''' mkdir is the easier version of makedirs.
                parents creates any files missing in the path
                exists_ok prevents any errors from the folders exisiting already
            '''
            base.mkdir(parents=True, exist_ok=True)
        else:
            base = sys._MEIPASS
    else:
        ''' __file__ is a special python dunder variable with the location of current file's code being executed
            abspath converts the relative path to a absolute path if it is not absolute already
            dirname removes the file name from the directory path
        '''
        base = os.path.dirname(os.path.abspath(__file__))
    # normpath considers .. and . in the path    
    return os.path.normpath(os.path.join(base, rel))
        
DB_FILE = resource_path('../games.db')

# Creates/connects to the games.db
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS games (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       platform TEXT,
                       main_hours REAL,
                       main_extras_hours REAL,
                       completionist_hours REAL,
                       all_styles_hours REAL,
                       review_score REAL,
                       owned INTEGER DEFAULT 0,
                       favorite INTEGER DEFAULT 0,
                       completed INTEGER DEFAULT 0,
                       completed_date TEXT,
                       added_date TEXT DEFAULT CURRENT_TIMESTAMP, 
                       image_url TEXT
        )
    """)
    conn.commit()
    conn.close()