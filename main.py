# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime

app = FastAPI(title="Cafe Management System")

# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- МОДЕЛИ ДАННЫХ ----------
class EmployeeCreate(BaseModel):
    full_name: str
    position: str
    salary: int


class MenuCreate(BaseModel):
    name: str
    description: str
    price: int
    category: str


class OrderItemCreate(BaseModel):
    menu_id: int
    quantity: int
    price_order: int


class OrderCreate(BaseModel):
    employe_ID: int
    table_number: int
    items: List[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: str


# ---------- ПОДКЛЮЧЕНИЕ К БД ----------
def get_db():
    conn = sqlite3.connect('cafe.db')
    conn.row_factory = sqlite3.Row
    return conn


# ---------- API: СОТРУДНИКИ ----------
@app.get("/api/employees")
def get_employees():
    conn = get_db()
    employees = conn.execute("SELECT * FROM Employees").fetchall()
    conn.close()
    return [dict(e) for e in employees]


@app.post("/api/employees")
def add_employee(employee: EmployeeCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Employees (full_name, position, salary) VALUES (?, ?, ?)",
                   (employee.full_name, employee.position, employee.salary))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"message": "Сотрудник добавлен", "id": new_id}


# ---------- API: МЕНЮ ----------
@app.get("/api/menu")
def get_menu():
    conn = get_db()
    menu = conn.execute("SELECT * FROM Menu").fetchall()
    conn.close()
    return [dict(m) for m in menu]


@app.post("/api/menu")
def add_dish(dish: MenuCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Menu (name, description, price, category) VALUES (?, ?, ?, ?)",
                   (dish.name, dish.description, dish.price, dish.category))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"message": "Блюдо добавлено", "id": new_id}


@app.delete("/api/menu/{menu_id}")
def delete_dish(menu_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Menu WHERE id = ?", (menu_id,))
    conn.commit()
    conn.close()
    return {"message": "Блюдо удалено"}


# ---------- API: ЗАКАЗЫ ----------
@app.get("/api/orders")
def get_orders():
    conn = get_db()
    orders = conn.execute("""
        SELECT o.*, e.full_name as employee_name
        FROM Orders o
        LEFT JOIN Employees e ON o.employe_ID = e.id
        ORDER BY o.created DESC
    """).fetchall()

    result = []
    for order in orders:
        items = conn.execute("""
            SELECT oi.*, m.name
            FROM Orders_item oi
            JOIN Menu m ON oi.menu_id = m.id
            WHERE oi.order_id = ?
        """, (order['id'],)).fetchall()

        result.append({
            "id": order['id'],
            "employee_name": order['employee_name'],
            "table_number": order['table_number'],
            "created": order['created'],
            "status": order['status'],
            "total_amount": order['total_amount'],
            "items": [dict(i) for i in items]
        })

    conn.close()
    return result


@app.post("/api/orders")
def create_order(order: OrderCreate):
    conn = get_db()
    cursor = conn.cursor()

    total_amount = sum(item.price_order * item.quantity for item in order.items)
    created_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    cursor.execute("""
        INSERT INTO Orders (employe_ID, table_number, created, status, total_amount)
        VALUES (?, ?, ?, ?, ?)
    """, (order.employe_ID, order.table_number, created_time, "В зале", total_amount))

    order_id = cursor.lastrowid

    for item in order.items:
        cursor.execute("""
            INSERT INTO Orders_item (order_id, menu_id, quantity, price_order)
            VALUES (?, ?, ?, ?)
        """, (order_id, item.menu_id, item.quantity, item.price_order))

    conn.commit()
    conn.close()
    return {"message": "Заказ создан", "order_id": order_id}


@app.put("/api/orders/{order_id}/status")
def update_order_status(order_id: int, status_update: OrderStatusUpdate):
    valid_statuses = ["Готовится", "В зале", "Оплачено"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Статус должен быть: {valid_statuses}")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE Orders SET status = ? WHERE id = ?", (status_update.status, order_id))
    conn.commit()
    conn.close()
    return {"message": f"Статус заказа #{order_id} изменён"}


# ---------- API: СТАТИСТИКА ----------
@app.get("/api/stats/employee-orders")
def get_employee_stats():
    conn = get_db()
    stats = conn.execute("""
        SELECT 
            e.full_name,
            e.position,
            COUNT(o.id) as orders_count,
            COALESCE(SUM(o.total_amount), 0) as revenue
        FROM Employees e
        LEFT JOIN Orders o ON e.id = o.employe_ID
        GROUP BY e.id
        ORDER BY orders_count DESC
    """).fetchall()
    conn.close()
    return [dict(s) for s in stats]


if __name__ == "__main__":
    import uvicorn

    print("Запуск Cafe Management API...")
    print("Документация: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)