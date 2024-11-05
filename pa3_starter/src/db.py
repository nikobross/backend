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

    # initialize the database driver object
    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_user_table()
        self.create_transaction_table()

    # create the user table
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

    def create_transaction_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    accepted BOOLEAN NULL,
                    message TEXT,
                    FOREIGN KEY(sender_id) REFERENCES user(id),
                    FOREIGN KEY(receiver_id) REFERENCES user(id)
                );
            """)
        except Exception as e:
            print(e)

    # get all users from the user table
    def get_all_users(self):
        cursor = self.conn.execute("SELECT * FROM user;")
        users = []

        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2], "balance": row[4]})

        return users
    
    # insert a user into the user table
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
    
    # get a user by their ID
    def get_user_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM user WHERE ID = ?", (id,))

        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[4]}

        return None
    
    # update a user by their ID
    def update_user_by_id(self, id, name, username, balance):
        self.conn.execute("""
            UPDATE user 
            SET name = ?, username = ?, balance = ?
            WHERE id = ?;
        """, (name, username, balance, id))
        self.conn.commit()

    # delete a user by their ID
    def delete_user_by_id(self, id):
        self.conn.execute("""
            DELETE FROM user
            WHERE id = ?;        
        """, (id,))
        self.conn.commit()
    
    # insert a transaction into the transactions table
    def insert_transaction(self, timestamp, sender_id, receiver_id, amount, accepted, message):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO transactions (TIMESTAMP, SENDER_ID, RECEIVER_ID, AMOUNT, ACCEPTED, MESSAGE) VALUES (?, ?, ?, ?, ?, ?);", 
            (timestamp, sender_id, receiver_id, amount, accepted, message))
        self.conn.commit()
        return cursor.lastrowid
    
    # get transaction by transaction ID
    def get_transaction_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM transactions WHERE ID = ?", (id,))

        for row in cursor:
            return {"id": row[0], "timestamp": row[1], "sender_id": row[2], "receiver_id": row[3], "amount": row[4], "accepted": row[5], "message": row[6]}

        return None
    
    # accept transaction
    def accept_transaction(self, id, timestamp):
        self.conn.execute("""
            UPDATE transactions 
            SET accepted = TRUE, timestamp = ?
            WHERE id = ?;
        """, (timestamp, id))
        self.conn.commit()

    # deny transaction
    def deny_transaction(self, id, timestamp):
        self.conn.execute("""
            UPDATE transactions 
            SET accepted = FALSE, timestamp = ?
            WHERE id = ?;
        """, (timestamp, id))
        self.conn.commit()

    # get all transactions the user is involved in
    def get_transactions_by_user_id(self, user_id):
        cursor = self.conn.execute("""
            SELECT * FROM transactions
            WHERE sender_id = ? OR receiver_id = ?;
        """, (user_id, user_id))
        
        transactions = []
        for row in cursor:
            transactions.append({
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "accepted": row[5],
                "message": row[6]
            })
        
        return transactions

    # get the last transaction ID
    def get_last_transaction_id(self):
        cursor = self.conn.execute("SELECT MAX(ID) FROM transactions;")
        for row in cursor:
            return row[0]
        
    # get all transactions for testing
    def get_all_transactions(self):
        cursor = self.conn.execute("SELECT * FROM transactions;")
        transactions = []

        for row in cursor:
            transactions.append({
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "accepted": row[5],
                "message": row[6]
            })

        return transactions

# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)