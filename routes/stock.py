from flask import Blueprint, render_template
import services
import db

stock_bp = Blueprint("stock", __name__, url_prefix="/stock")

@stock_bp.route("/stock_list")
def stock_list():
    stocks = db.get_all_stocks()
    return render_template("partials/_stock_list.html", stocks=stocks)
