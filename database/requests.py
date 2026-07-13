import sqlite3
from datetime import datetime, timedelta
from create_bot import DB_NAME

# Реєстрація нового юзера в базі
def add_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

# Створюємо таблицю для ведення статистики користувачів
def create_users_table():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        completed INTEGER DEFAULT 0,
        snoozed INTEGER DEFAULT 0,
        toxicity TEXT DEFAULT 'Кат'
    )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        task_text TEXT,
        deadline TEXT,
        remind_offset INTEGER
    )''')
    
    try:
        cur.execute("ALTER TABLE users ADD COLUMN completed INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE users ADD COLUMN snoozed INTEGER DEFAULT 0")
        cur.execute("ALTER TABLE users ADD COLUMN toxicity TEXT DEFAULT 'Кат'")
    except sqlite3.OperationalError:
        pass 
        
    conn.commit()
    conn.close()

# Отримання кількості користувачів для адмінки
def get_users_count() -> int:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count

# Загальна кількість тасків у базі
def get_tasks_count() -> int:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks")
    count = cur.fetchone()[0]
    conn.close()
    return count

# Додавання нового завдання з дедлайном та нагадуванням
def add_task_to_db(user_id: int, category: str, task_text: str, deadline: str, remind_offset: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (user_id, category, task_text, deadline, remind_offset) VALUES (?, ?, ?, ?, ?)",
        (user_id, category, task_text, deadline, remind_offset)
    )
    conn.commit()
    conn.close()

# Отримання всіх активних завдань
def get_user_tasks(user_id: int) -> list:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT task_id, category, task_text, deadline FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cur.fetchall()
    conn.close()
    return tasks

# Видалення завдання з бази (коли його виконано)
def delete_task(task_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()

# Витягує абсолютно всі завдання з бази для перевірки часу
def get_all_active_tasks() -> list:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT task_id, user_id, category, task_text, deadline, remind_offset FROM tasks")
    tasks = cur.fetchall()
    conn.close()
    return tasks

# Пересуває дедлайн завдання на вказану кількість хвилин від ПОТОЧНОГО моменту
def postpone_task(task_id: int, minutes_to_add: int = 5):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT deadline FROM tasks WHERE task_id = ?", (task_id,))
    result = cur.fetchone()
    if result:
        new_deadline = datetime.now() + timedelta(minutes=minutes_to_add)
        new_deadline_str = new_deadline.strftime("%Y-%m-%d %H:%M")
        cur.execute("UPDATE tasks SET deadline = ? WHERE task_id = ?", (new_deadline_str, task_id))
        conn.commit()
    conn.close()

# Отримання завдань користувача з фільтром по категорії
def get_tasks_by_category(user_id: int, category: str) -> list:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if category == "Усі":
        cur.execute("SELECT task_id, category, task_text, deadline FROM tasks WHERE user_id = ?", (user_id,))
    else:
        cur.execute("SELECT task_id, category, task_text, deadline FROM tasks WHERE user_id = ? AND category =?", (user_id, category))
    tasks = cur.fetchall()
    conn.close()
    return tasks

# Змінює кінцевий час (дедлайн) конкретного завдання
def update_task_deadline(task_id: int, new_deadline: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET deadline = ? WHERE task_id = ?", (new_deadline, task_id))
    conn.commit()
    conn.close()

# Реєструє користувача в базі, якщо його там ще немає
def add_user_if_not_exists(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

# Додає +1 до виконаних (completed) або прострочених (snoozed) завдань
# Додає +1 до виконаних (completed) або прострочених (snoozed) завдань
def update_stat(user_id: int, stat_type: str):
    add_user_if_not_exists(user_id)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    if stat_type == 'completed':
        # Плюс в карму: додаємо до виконаних
        cur.execute("UPDATE users SET completed = completed + 1 WHERE user_id = ?", (user_id,))
        # Відпущення гріхів: мінусуємо одну прокрастинацію (якщо вона є)
        cur.execute("UPDATE users SET snoozed = snoozed - 1 WHERE user_id = ? AND snoozed > 0", (user_id,))
        
    elif stat_type == 'snoozed':
        cur.execute("UPDATE users SET snoozed = snoozed + 1 WHERE user_id = ?", (user_id,))
        
    conn.commit()
    conn.close()

# Повертає статистику користувача (completed, snoozed)
def get_user_stats(user_id: int) -> tuple:
    add_user_if_not_exists(user_id)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT completed, snoozed FROM users WHERE user_id = ?", (user_id,))
    stats = cur.fetchone()
    conn.close()
    return stats

# Скидає статистику користувача до нуля
def reset_user_stats(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET completed = 0, snoozed = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# =========================================================
# НАЛАШТУВАННЯ ТОКСИЧНОСТІ (НЯНЬКА / КАТ / УЛЬТРА)
# =========================================================

# додає колонку toxicity
def upgrade_db_toxicity():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE users ADD COLUMN toxicity TEXT DEFAULT 'Кат'")
        conn.commit()
    except Exception:
        pass
    conn.close()

# Зберігає обраний рівень токсичності
def set_user_toxicity(user_id: int, level: str):
    add_user_if_not_exists(user_id)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET toxicity = ? WHERE user_id = ?", (level, user_id))
    conn.commit()
    conn.close()

# Отримує рівень токсичності юзера (за замовчуванням 'Кат')
def get_user_toxicity(user_id: int) -> str:
    add_user_if_not_exists(user_id)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT toxicity FROM users WHERE user_id = ?", (user_id,))
    res = cur.fetchone()
    conn.close()
    return res[0] if res and res[0] else 'Кат'