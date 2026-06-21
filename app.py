import sqlite3
from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DB_NAME = 'cafe.db'


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()

    # 1. Получаем список заказов
    orders_rows = conn.execute("""
        SELECT o.id, e.full_name as employee_name, o.table_number, o.created, o.status, o.total_amount
        FROM Orders o
        LEFT JOIN Employees e ON o.employe_ID = e.id
        ORDER BY o.id DESC
    """).fetchall()

    orders = []
    for order in orders_rows:
        items = conn.execute("""
            SELECT oi.quantity, oi.price_order, m.name as dish_name
            FROM Orders_item oi
            JOIN Menu m ON oi.menu_id = m.id
            WHERE oi.order_id = ?
        """, (order['id'],)).fetchall()

        orders.append({
            "id": order['id'],
            "employee_name": order['employee_name'],
            "table_number": order['table_number'],
            "created": order['created'],
            "status": order['status'],
            "total_amount": order['total_amount'],
            "dishes": items
        })

    # 2. Получаем меню и сотрудников (они также нужны для списков в формах создания заказа)
    menu = conn.execute("SELECT * FROM Menu").fetchall()
    employees = conn.execute("SELECT * FROM Employees").fetchall()

    # 3. Статистика эффективности
    stats = conn.execute("""
        SELECT 
            e.id, e.full_name, e.position, e.salary,
            COUNT(o.id) as orders_count,
            COALESCE(SUM(o.total_amount), 0) as revenue
        FROM Employees e
        LEFT JOIN Orders o ON e.id = o.employe_ID
        GROUP BY e.id
        ORDER BY revenue DESC
    """).fetchall()

    conn.close()
    return render_template('index.html', orders=orders, menu=menu, employees=employees, stats=stats)


# ---------- ДЕЙСТВИЯ С ЗАКАЗАМИ ----------

@app.route('/order/add', methods=['POST'])
def add_order():
    employee_id = request.form.get('employee_id')
    table_number = request.form.get('table_number')
    dish_id = request.form.get('dish_id')
    quantity = int(request.form.get('quantity', 1))

    conn = get_db_connection()

    # Ищем цену выбранного блюда
    dish = conn.execute(
        "SELECT price FROM Menu WHERE id = ?", (dish_id,)).fetchone()
    if dish:
        price = dish['price']
        total_amount = price * quantity
        created_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Создаем заказ
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Orders (employe_ID, table_number, created, status, total_amount)
            VALUES (?, ?, ?, ?, ?)
        """, (employee_id, table_number, created_time, 'Готовится', total_amount))

        order_id = cursor.lastrowid

        # Добавляем блюдо в заказ
        cursor.execute("""
            INSERT INTO Orders_item (order_id, menu_id, quantity, price_order)
            VALUES (?, ?, ?, ?)
        """, (order_id, dish_id, quantity, price))

        conn.commit()

    conn.close()
    return redirect(url_for('index'))


@app.route('/order/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    conn = get_db_connection()
    # Сначала удаляем связанные элементы заказа, затем сам заказ (связи FOREIGN KEY)
    conn.execute("DELETE FROM Orders_item WHERE order_id = ?", (order_id,))
    conn.execute("DELETE FROM Orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# ---------- ДЕЙСТВИЯ С МЕНЮ ----------

@app.route('/menu/add', methods=['POST'])
def add_dish():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO Menu (name, description, price, category)
        VALUES (?, ?, ?, ?)
    """, (name, description, price, category))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/menu/delete/<int:dish_id>', methods=['POST'])
def delete_dish(dish_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM Menu WHERE id = ?", (dish_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# ---------- ДЕЙСТВИЯ С СОТРУДНИКАМИ ----------

@app.route('/employee/add', methods=['POST'])
def add_employee():
    full_name = request.form.get('full_name')
    position = request.form.get('position')
    salary = request.form.get('salary')

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO Employees (full_name, position, salary)
        VALUES (?, ?, ?)
    """, (full_name, position, salary))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/employee/delete/<int:emp_id>', methods=['POST'])
def delete_employee(emp_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM Employees WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)