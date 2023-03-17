# database.py:

import sqlite3


def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, name TEXT, content TEXT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, content TEXT, timestamp TEXT)")
    conn.commit()
    conn.close()


def insert_document(name, content):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (name, content) VALUES (?, ?)", (name, content))
    conn.commit()
    conn.close()


def insert_message(content, timestamp):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (content, timestamp) VALUES (?, ?)", (content, timestamp))
    conn.commit()
    conn.close()
