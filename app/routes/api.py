"""JSON API used by the dashboard JavaScript.

Every endpoint accepts the optional query parameters:
state, category, brand, start_date, end_date (YYYY-MM-DD).
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import SessionLocal
from app.models import Sale
from app.services import analytics
from app.services.filters import Filters

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.errorhandler(ValueError)
def invalid_input(error):
    return jsonify({"status": "error", "message": f"Invalid filter value: {error}"}), 400


@api_bp.errorhandler(SQLAlchemyError)
def database_error(error):
    message = (
        "Database error. Check that MySQL is running, the credentials in .env are correct "
        "and that scripts/load_database.py has been run."
    )
    return jsonify({"status": "error", "message": message}), 500


@api_bp.get("/health")
def health():
    """Quick check that Flask can reach MySQL and the sales table has data."""
    with SessionLocal() as session:
        rows = session.execute(select(func.count()).select_from(Sale)).scalar()
    return jsonify({"status": "ok", "database_rows": rows})


@api_bp.get("/filters")
def filters():
    with SessionLocal() as session:
        return jsonify(analytics.get_filter_options(session))


@api_bp.get("/overview")
def overview():
    with SessionLocal() as session:
        return jsonify(analytics.get_overview(session, Filters.from_args(request.args)))


@api_bp.get("/customers")
def customers():
    with SessionLocal() as session:
        return jsonify(analytics.get_customers(session, Filters.from_args(request.args)))


@api_bp.get("/products")
def products():
    with SessionLocal() as session:
        return jsonify(analytics.get_products(session, Filters.from_args(request.args)))
