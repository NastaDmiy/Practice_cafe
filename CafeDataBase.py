import sqlite3

DB_NAME = 'cafe.db'


def create_tabl():
    conn = sqlite3.connect('cafe.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Employees (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   full_name TEXT NOT NULL,
                   position TEXT NOT NULL,
                   salary INTEGER NOT NULL
                   )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Menu (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   description TEXT NOT NULL,
                   price INTEGER NOT NULL,
                   category TEXT NOT NULL
                   )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   employe_ID INTEGER NOT NULL,
                   table_number INTEGER NOT NULL,
                   created TEXT NOT NULL,
                   status TEXT NOT NULL,
                   total_amount INTEGER NOT NULL,
                   FOREIGN KEY (employe_ID) REFERENCES Employees(id)
                   )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders_item (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   order_id INTEGER NOT NULL,
                   menu_id INTEGER NOT NULL,
                   quantity INTEGER NOT NULL,
                   price_order INTEGER NOT NULL,
                   FOREIGN KEY (order_id) REFERENCES Orders(id),
                   FOREIGN KEY (menu_id) REFERENCES Menu(id)
                   )
    ''')

    conn.commit()
    conn.close()
    print("Таблицы созданы")


def insert_in_table():
    conn = sqlite3.connect('cafe.db')
    cursor = conn.cursor()

    Employees = [
        (1, 'Альберт Иван Котов', 'Повар', 65000),
        (2, 'Анна Николаевна Капусткина', 'Официант', 35000),
        (3, 'Иван Александрович Кнопкин', 'Бармен', 47000),
        (4, 'Мария Валерьевна Нефедова', 'Помощник повара', 35000)
    ]
    cursor.executemany('''
            INSERT OR IGNORE INTO Employees (id, full_name, position, salary)
            VALUES (?, ?, ?, ?)
    ''', Employees)
    
    Menu = [
        (1, 'Цезарь', 'Салат с курицей, салатом и соусом цезарь', 350, 'Салаты'),
        (2, 'Куриный суп', 'Куриный бульон, овощи и лапша', 430, 'Супы'),
        (3, 'Чизбургер', 'Котлета из говяжьего фарша, салат, сыр чедер, булочка с кунжутом', 520, 'Горячее'),
        (4, 'Лонг-Айленд', 'Джин, текила, ром и лед', 360, 'Напитки'),
        (5, 'Жаркое', 'Болгарский перец, лук, фасоль под мясным соусом', 630, 'Горячее')
    ]
    cursor.executemany('''
            INSERT OR IGNORE INTO Menu (id, name, description, price, category)
            VALUES (?, ?, ?, ?, ?)
    ''', Menu)
    
    Orders = [
        (1, 1, 3, '04-06-2026 13:45:00', 'Готовиться', 780),
        (2, 3, 2, '04-06-2026 15:25:00', 'Оплачено', 360),
        (3, 2, 5, '04-06-2026 12:12:00', 'В зале', 990),
        (4, 4, 1, '04-06-2026 16:36:00', 'Готовиться', 520),
        (5, 1, 3, '04-06-2026 20:40:00', 'Готовиться', 870),
        (6, 3, 3, '04-06-2026 20:40:00', 'Готовиться', 720),
    ]
    cursor.executemany('''
            INSERT OR IGNORE INTO Orders (id, employe_ID, table_number, created, status, total_amount)
            VALUES (?, ?, ?, ?, ?, ?)
    ''', Orders)
    
    Orders_item = [
        (1, 1, 2, 1, 430),
        (2, 2, 1, 1, 350),
        (3, 3, 4, 1, 360),
        (4, 3, 5, 1, 630),
        (5, 4, 3, 1, 520),
        (6, 5, 1, 1, 350),
        (7, 5, 3, 1, 520),
        (8, 6, 4, 2, 360)
    ]
    cursor.executemany('''
            INSERT OR IGNORE INTO Orders_item (id, order_id, menu_id, quantity, price_order)
            VALUES (?, ?, ?, ?, ?)
    ''', Orders_item)
    
    conn.commit()
    conn.close()
    print("Данные добавлены")


if __name__ == "__main__":
    create_tabl()      
    insert_in_table()  