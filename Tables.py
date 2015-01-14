import sqlite3
import logging

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
            logging.exception('Unable to add Swap to database.')
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
                .format(Swap.table), (user.lower(),)
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

class Inventory():
    table = 'inventories'

    @staticmethod
    def add(submission_id, user, url, db):
        cursor = db.cursor()
        try:
            cursor.execute(
                'INSERT INTO {} VALUES(NULL, ?, ?, ?)'
                .format(Inventory.table),
                (submission_id, user, url)
            )
        except sqlite3.IntegrityError:
            logging.error('Inventory already in database. Skipping insertion.')
        except:
            logging.exception('Unable to add Inventory to database.')
        else:
            db.commit()

    @staticmethod
    def get(user, db):
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT url FROM {} WHERE user = ?' 
                .format(Inventory.table), (user,)
            )
        except:
            logging.exception('Unable to retrieve {}\'s Inventory.'.format(user))
        else:
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None

    @staticmethod
    def createTable(db):
        cursor = db.cursor();
        cursor.execute('''CREATE TABLE IF NOT EXISTS {} (
            id INTEGER NOT NULL,
            submission_id VARCHAR,
            user VARCHAR,
            url VARCHAR,
            PRIMARY KEY (id)
        )'''.format(Inventory.table))
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS inventory ON {}(user)'.format(Inventory.table))
        db.commit()
