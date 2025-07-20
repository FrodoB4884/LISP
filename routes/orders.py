from flask import Blueprint, render_template
import services
import db

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

@orders_bp.route("/orders_list")
def orders_list():
    orders = db.get_all_orders()
    return render_template("partials/_orders_list.html", orders=orders)