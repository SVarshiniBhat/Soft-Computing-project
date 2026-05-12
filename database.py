import sqlite3

# CREATE DATABASE
conn = sqlite3.connect("quiz_app.db")

cursor = conn.cursor()

# USERS TABLE
cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,
    email TEXT,
    password TEXT

)

""")

# QUIZ HISTORY TABLE
cursor.execute("""

CREATE TABLE IF NOT EXISTS quiz_history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    domain TEXT,
    language TEXT,
    concept TEXT,

    score INTEGER,
    total INTEGER,
    percentage INTEGER

)

""")

conn.commit()

conn.close()

print("Database Created Successfully")