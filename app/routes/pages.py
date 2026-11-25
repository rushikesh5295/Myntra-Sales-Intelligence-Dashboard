"""HTML pages of the dashboard (rendered with Jinja2 templates)."""

from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def overview():
    return render_template("pages/overview.html", active="overview")


@pages_bp.get("/customers")
def customers():
    return render_template("pages/customers.html", active="customers")


@pages_bp.get("/products")
def products():
    return render_template("pages/products.html", active="products")
