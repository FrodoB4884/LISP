from flask import Blueprint, render_template
import services

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

@orders_bp.route("/test/<int:test>")
def test(test):
    data = test
    return render_template("partials/test.html", data=data)