from models import *
import db

# 1. Reset DB
db.delete_db()
db.setup_db()

# 2. Add Item Types
screwdriver = ItemType(name="Screwdriver", part_no="SD001", item_group="Tools", cost=4.99)
hammer = ItemType(name="Hammer", part_no="HM001", item_group="Tools", cost=9.99)
wrench = ItemType(name="Wrench", part_no="WR001", item_group="Tools", cost=7.99)

screwdriver.id = db.create_new_item_type(screwdriver)
hammer.id = db.create_new_item_type(hammer)
wrench.id = db.create_new_item_type(wrench)

# 3. Add Locations
main_wh = Location(name="Main Warehouse", address="123 Industrial Way")
sec_storage = Location(name="Secondary Storage", address="456 Backup Blvd")

main_wh.id = db.create_location(main_wh)
sec_storage.id = db.create_location(sec_storage)

# 4. Add Stock
db.create_new_stock(Stock(item_type=screwdriver, location=main_wh, in_stock=100, reserved=5, reorder_point=20))
db.create_new_stock(Stock(item_type=hammer, location=main_wh, in_stock=50, reserved=2, reorder_point=10))
db.create_new_stock(Stock(item_type=wrench, location=sec_storage, in_stock=75, reserved=0, reorder_point=15))

# 5. Add Customers
john = Customer(name="John Doe", email="john@example.com", address="1 Example Rd")
jane = Customer(name="Jane Smith", email="jane@example.com", address="2 Example Ln")

john.id = db.create_customer(john)
john.id = db.create_customer(jane)

# 6. Create Order
order_items = {
    screwdriver: 2,
    hammer: 1
}
order = Order(customer=john, items=order_items, status=OrderStatus.PENDING)
db.create_order(order)
