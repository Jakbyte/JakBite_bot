import sqlite3
from create_bot import DB_NAME

# Ініціалізація бази даних та створення таблиць
def db_start():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT DEFAULT 'user'
        )
    """)
    # Завдання
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            task_text TEXT,
            deadline TEXT,
            remind_offset INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    conn.commit()
    conn.close()
    print("🗄 База даних успішно підключена, таблиці готові!")
