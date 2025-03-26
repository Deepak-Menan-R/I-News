import sqlite3
from datetime import datetime

def init_db():
    try:
        db_path = 'db/db.db'
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS Country (country_id INTEGER PRIMARY KEY, country_name TEXT NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS Category (category_id INTEGER PRIMARY KEY, category_name TEXT NOT NULL)")
            
            # Check if Country table is empty, then insert initial data
            cursor.execute("SELECT COUNT(*) FROM Country")
            if cursor.fetchone()[0] == 0:  # If the Country table is empty
                cursor.executemany("INSERT INTO Country (country_name) VALUES (?)",
                                   [('us',), ('gb',), ('ca',), ('au',), ('de',), ('fr',), ('jp',), 
                                    ('in',), ('it',), ('br',), ('mx',), ('ru',), ('kr',), ('cn',), ('za',)])
            
            # Check if Category table is empty, then insert initial data
            cursor.execute("SELECT COUNT(*) FROM Category")
            if cursor.fetchone()[0] == 0:  # If the Category table is empty
                cursor.executemany("INSERT INTO Category (category_name) VALUES (?)",
                                   [('technology',), ('science',), ('business',), ('entertainment',),
                                    ('health',), ('sports',), ('general',)])
            
            # Create other tables and indexes
            cursor.executescript(QUERY)
            
    except sqlite3.Error as e:
        print("SQLite error:", e.args[0])
        with open('logs/error.log', 'a') as f:
            f.write(f'{datetime.now()} - SQLite error: {e.args[0]}\n')
    except Exception as e:
        print("Error:", str(e))
        with open('logs/error.log', 'a') as f:
            f.write(f'{datetime.now()} - Error: {str(e)}\n')

QUERY = """
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS User_Preference (
    user_preference_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    category_id INTEGER,
    country_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id),
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);

CREATE TABLE IF NOT EXISTS Feedback (
    feedback_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    feedback_text TEXT,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS Comment (
    comment_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    comment_text TEXT,
    comment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS Activity (
    activity_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    login_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_timestamp TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);
"""

if __name__ == '__main__':
    init_db()
