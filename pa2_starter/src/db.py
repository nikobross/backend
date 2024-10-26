import os
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance

class DatabaseDriver(object):
    """
    Database driver for the Venmo app.
    Handles reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_user_table()

    def create_user_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    NAME TEXT NOT NULL,
                    USERNAME TEXT NOT NULL,
                    PASSWORD TEXT,
                    BALANCE REAL NOT NULL
                );
            """)
        except Exception as e:
            print(e)

    def get_all_users(self):
        cursor = self.conn.execute("SELECT * FROM user;")
        users = []

        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2], "balance": row[4]})

        return users
    
    def insert_user(self, name, username, balance, password=None):
        cursor = self.conn.cursor()
        if password:
            cursor.execute("INSERT INTO user (NAME, USERNAME, PASSWORD, BALANCE) VALUES (?, ?, ?, ?);", 
                (name, username, password, balance))
        else:
            cursor.execute("INSERT INTO user (NAME, USERNAME, BALANCE) VALUES (?, ?, ?);", 
                (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM user WHERE ID = ?", (id,))

        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[4]}

        return None
    
    def update_user_by_id(self, id, name, username, balance):
        self.conn.execute("""
            UPDATE user 
            SET name = ?, username = ?, balance = ?
            WHERE id = ?;
        """, (name, username, balance, id))
        self.conn.commit()

    def delete_user_by_id(self, id):
        self.conn.execute("""
            DELETE FROM user
            WHERE id = ?;        
        """, (id,))
        self.conn.commit()

    # ------Extra Credit------

    def update_user_by_id_extra(self, id, name, username, password, balance):
        self.conn.execute("""
            UPDATE user 
            SET name = ?, username = ?, password = ?, balance = ?
            WHERE id = ?;
        """, (name, username, password, balance, id))
        self.conn.commit()

    def get_user_by_id_extra(self, id):
        cursor = self.conn.execute("SELECT * FROM user WHERE ID = ?", (id,))

        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "password": row[3], "balance": row[4]}

        return None

    def insert_user_extra(self, name, username, password, balance):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO user (NAME, USERNAME, PASSWORD, BALANCE) VALUES (?, ?, ?, ?);", 
            (name, username, password, balance))
        self.conn.commit()
        return cursor.lastrowid

# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)