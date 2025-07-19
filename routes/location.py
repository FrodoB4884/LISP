from flask import Blueprint, render_template
import services

location_bp = Blueprint("location", __name__, url_prefix="/location")

@location_bp.route("/test/<int:test>")
def test(test):
    data = test
    return render_template("partials/test.html", data=data)