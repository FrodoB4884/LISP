import sqlite3

from config import *

def debug_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        print("Checking stock table:")
        cursor.execute("SELECT * FROM stock")
        stock_rows = cursor.fetchall()
        print(f"Stock rows count: {len(stock_rows)}")
        for row in stock_rows:
            print(row)
        
        print("\nChecking item_types table:")
        cursor.execute("SELECT * FROM item_types")
        item_rows = cursor.fetchall()
        print(f"Item types rows count: {len(item_rows)}")
        for row in item_rows:
            print(row)
        
        print("\nChecking locations table:")
        cursor.execute("SELECT * FROM locations")
        location_rows = cursor.fetchall()
        print(f"Locations rows count: {len(location_rows)}")
        for row in location_rows:
            print(row)
        
        print("\nChecking joined stock info with INNER JOINs:")
        cursor.execute("""
            SELECT stock.id, item_types.id, item_types.name, item_types.part_no, item_types.item_group, item_types.cost,
                   locations.id, locations.name, locations.address,
                   stock.in_stock, stock.reserved, stock.reorder_point
            FROM stock
            JOIN item_types ON stock.item_type_id = item_types.id
            JOIN locations ON stock.location_id = locations.id
        """)
        joined_rows = cursor.fetchall()
        print(f"Joined rows count: {len(joined_rows)}")
        for row in joined_rows:
            print(row)

if __name__ == "__main__":
    debug_db()
