import sqlite3

# Подключение к базе данных (создаёт файл базы данных, если его нет)
conn = sqlite3.connect('chats_database.db')
cursor = conn.cursor()

conn.commit()

# Функция для добавления запроса
def add_request(chat_id, user_request, neural_response, neural_type):
    cursor.execute('''
        INSERT INTO Requests (chat_id, user_request, neural_response, neural_type)
        VALUES (?, ?, ?, ?)
    ''', (chat_id, user_request, neural_response, neural_type))
    conn.commit()
    print("Запрос добавлен.")

# Функция для удаления запроса по request_id
def delete_request(request_id):
    cursor.execute('''
        DELETE FROM Requests WHERE request_id = ?
    ''', (request_id,))
    conn.commit()
    print("Запрос удалён.")

# Функция для добавления пути к текстовой версии чата
def add_chat_path(chat_id, chat_path):
    cursor.execute('''
        INSERT OR REPLACE INTO ChatPaths (chat_id, chat_path)
        VALUES (?, ?)
    ''', (chat_id, chat_path))
    conn.commit()
    print("Путь к чату добавлен или обновлён.")

# Функция для удаления пути к текстовой версии чата по chat_id

def load_chats_from_base():
    cursor.execute('''
        SELECT chat_id, chat_path FROM ChatPaths
    ''')
    rows = cursor.fetchall()
    return rows
def delete_chat_path(chat_id):
    cursor.execute('''
        DELETE FROM ChatPaths WHERE chat_id = ?
    ''', (chat_id,))
    conn.commit()
    print("Путь к чату удалён.")

# Закрытие соединения с базой данных
def close_connection():
    conn.close()
    print("Соединение с базой данных закрыто.")



# Создание таблицы запросов и ответов
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS Requests (
#     request_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     chat_id INTEGER NOT NULL,
#     user_request TEXT NOT NULL,
#     neural_response TEXT NOT NULL,
#     neural_type TEXT NOT NULL
# )
# ''')
#
# # Создание таблицы с путями к полным текстовым версиям чатов
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS ChatPaths (
#     chat_id INTEGER PRIMARY KEY,
#     chat_path TEXT NOT NULL
# )
# ''')