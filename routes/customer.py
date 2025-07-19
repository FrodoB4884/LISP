from flask import Blueprint, render_template
import services

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")

@customer_bp.route("/test/<int:test>")
def test(test):
    data = test
    return render_template("partials/test.html", data=data)