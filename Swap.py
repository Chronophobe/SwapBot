import sqlite3

class Swap():
    table = 'swaps'

    @staticmethod
    def add(submission_id, title, user, url, date, db):
        cursor = db.cursor()
        try:
            cursor.execute(
                'INSERT INTO {} VALUES(NULL, ?, ?, ?, ?, ?)'
                .format(Swap.table),
                (submission_id, title, user, url, date)
            )
        except sqlite3.IntegrityError:
            logging.error('Swap already in database. Skipping insertion.')
        except:
            logging.exception('Unable to add swap to database.')
        else:
            db.commit()

    @staticmethod
    def find(submission_id, db):
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT submission_id FROM {} WHERE submission_id = ?'
                .format(Swap.table), (submission_id,)
            )
        except:
            logging.exception('Unable to select from Swap table')
        else:
            return cursor.fetchone()

    @staticmethod
    def get(user, db):
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT title, url FROM {} WHERE user = ? ORDER BY date DESC' 
                .format(Swap.table), (user,)
            )
        except:
            logging.exception('Unable to retrieve {}\'s Swaps.'.format(user))
        else:
            return cursor.fetchall()

    @staticmethod
    def createTable(db):
        cursor = db.cursor();
        cursor.execute('''CREATE TABLE IF NOT EXISTS {} (
            id INTEGER NOT NULL,
            submission_id VARCHAR,
            title VARCHAR,
            user VARCHAR,
            url VARCHAR,
            date INTEGER,
            PRIMARY KEY (id)
        )'''.format(Swap.table))
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS swap ON {}(user,url)'.format(Swap.table))
        db.commit()