import sqlite3 as sql
from config import *
from models import *
import os

def get_connection():
    conn = sql.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def delete_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Database removed: {DB_PATH}")
    else:
        print(f"No database found at: {DB_PATH}")

def setup_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS item_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            part_no TEXT UNIQUE NOT NULL,
            item_group TEXT,
            cost REAL NOT NULL
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY,
            item_type_id INTEGER REFERENCES item_types(id),
            location_id INTEGER REFERENCES locations(id),
            in_stock INTEGER NOT NULL DEFAULT 0,
            reserved INTEGER NOT NULL DEFAULT 0,
            reorder_point INTEGER NOT NULL DEFAULT 5
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            item_type_id INTEGER NOT NULL REFERENCES item_types(id),
            quantity INTEGER NOT NULL
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS order_change_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            status TEXT NOT NULL,
            change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT NOT NULL DEFAULT "change made"
        )
        """)

def get_item_name_id_dict() -> dict[str, int] | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, id FROM item_types")
        rows = cursor.fetchall()

        if not rows:
            return None
        
        item_id_dict = {}
        for row in rows:
            name, id = row[0], row[1]
            item_id_dict[name] = id
        
        return item_id_dict

def get_item_type_by_id(id) -> ItemType | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM item_types WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            return None
        return ItemType(row[1], row[2], row[3], row[4], id=row[0])

def create_new_item_type(item_type:ItemType) -> int | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO item_types (name, part_no, item_group, cost) VALUES (?, ?, ?, ?) ON CONFLICT(part_no) DO NOTHING", (item_type.name, item_type.part_no, item_type.item_group, item_type.cost))
            return cursor.lastrowid
        except sql.IntegrityError as e:
            print(f"Insert failed for item type {item_type.part_no}: {e}")
            return None

def _fetch_stocks(where_clause="", params=()) -> list[Stock] | None:
    query = f"""
        SELECT 
            stock.id, 
            item_types.id, item_types.name, item_types.part_no, item_types.item_group, item_types.cost,
            locations.id, locations.name, locations.address,
            stock.in_stock, stock.reserved, stock.reorder_point
        FROM stock
        JOIN item_types ON stock.item_type_id = item_types.id
        JOIN locations ON stock.location_id = locations.id
        {where_clause}
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            return None
        
        stocks = []
        for (stock_id, item_type_id, name, part_no, group, cost, location_id, loc_name, loc_address, in_stock, reserved, reorder_point) in rows:
            item_type = ItemType(name, part_no, group, cost, item_type_id)
            location = Location(loc_name, loc_address, location_id)
            stock = Stock(
                item_type=item_type,
                location=location,
                in_stock=in_stock,
                reserved=reserved,
                reorder_point=reorder_point,
                id=stock_id
            )
            stocks.append(stock)
        return stocks

def get_all_stocks() -> list[Stock] | None:
    return _fetch_stocks()

def get_stocks_by_item(item_type_id:int) -> list[Stock] | None:
    return _fetch_stocks("WHERE item_type_id = ?", (item_type_id,))
    
def create_new_stock(stock:Stock) -> int | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO stock (item_type_id, in_stock, reserved, reorder_point) VALUES (?, ?, ?, ?)", (stock.item_type.id, stock.in_stock, stock.reserved, stock.reorder_point))
            return cursor.lastrowid
        except sql.Error as e:
            print(f"Stock creation failed: {e}")
            return None
        
def update_stock(item_type_id, updated_stock:Stock) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE stock SET item_type_id = ?, in_stock = ?, reserved = ?, reorder_point = ? WHERE item_type_id = ?", (updated_stock.item_type.id, updated_stock.in_stock, updated_stock.reserved, updated_stock.reorder_point, item_type_id))
            return True
        except sql.Error as e:
            print(f"Stock update failed: {e}")
            return False

def get_order_by_id(id) -> Order | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (id,))
        row = cursor.fetchone()

        if not row:
            return None

        customer_id = row[1]
        customer = get_customer_by_id(customer_id)

        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found for Order ID {id}")
        
        try:
            status = OrderStatus(row[2])
        except ValueError:
            print(f"Unknown order status: {row[2]}. Defaulting to UNKNOWN")
            status = OrderStatus.UNKNOWN
        
        # get changelog
        change_log = []
        cursor.execute("""
            SELECT change_date, status, notes
            FROM order_change_log
            WHERE order_id = ?
            ORDER BY change_date ASC
                       """, (id,))
        rows = cursor.fetchall()
        for row in rows:
            try:
                log_status = OrderStatus(row[1])
            except ValueError:
                print(f"Unknown change log status: {row[1]}. Defaulting to UNKNOWN")
                log_status = OrderStatus.UNKNOWN
            change_log.append((row[0], log_status, row[2]))

        # get items
        items = {}
        cursor.execute("""
            SELECT 
                order_items.item_type_id,
                item_types.name, item_types.part_no, item_types.item_group, item_types.cost,
                order_items.quantity
            FROM order_items
            JOIN item_types ON order_items.item_type_id = item_types.id
            WHERE order_items.order_id = ?
                        """, (id,))
        rows = cursor.fetchall()
        for row in rows:
            items[ItemType(row[1], row[2], row[3], row[4], row[0])] = row[5]

        return Order(customer, items, status, change_log, id)

def create_order(order:Order) -> int | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO orders (customer_id, status) VALUES (?, ?)", (order.customer.id, order.status.value))

            cursor.execute("INSERT OR IGNORE INTO order_change_log (order_id, status) VALUES (?, ?)", (cursor.lastrowid, order.status.value))

            for item in order.items:
                cursor.execute("INSERT INTO order_items (order_id, item_type_id, quantity) VALUES (?, ?, ?)", (cursor.lastrowid, item.id, order.items[item]))
            
            return cursor.lastrowid
        
        except sql.Error as e:
            print(f"Order creation failed: {e}")
            return None

def update_order(order:Order) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (order.status.value, order.id))

            cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order.id,))
            for item in order.items:
                cursor.execute("INSERT INTO order_items (order_id, item_type_id, quantity) VALUES (?, ?, ?)", (order.id, item.id, order.items[item]))

            for change in order.change_log:
                cursor.execute("INSERT OR IGNORE INTO order_change_log (order_id, change_date, status, notes) VALUES (?, ?, ?)", (order.id, change[0], change[1], change[2]))
            return True
        
        except sql.Error as e:
            print(f"Order update failed: {e}")
            return False

def create_customer(customer:Customer) -> int | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO customers (name, email, address) VALUES (?, ?, ?)", (customer.name, customer.email, customer.address))
            return cursor.lastrowid
        except sql.Error as e:
            print(f"Customer creation failed: {e}")
            return None
    
def get_customer_by_id(id:int) -> Customer | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (id,))
        row = cursor.fetchone()

        if not row:
            return None
        
        return Customer(row[1], row[2], row[3], row[0])
    
def create_location(location:Location) -> int | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO locations (name, address) VALUES (?, ?)", (location.name, location.address))
            return cursor.lastrowid
        except sql.Error as e:
            print(f"Location creation failed: {e}")
            return None

def get_location_by_id(id) -> Location | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM locations WHERE id = ?", (id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return Location(row[1], row[2], row[0])