"""Analytics queries (SQLAlchemy) behind the three dashboard pages.

Business rules
--------------
* Revenue, orders, customers and units count **Delivered** orders only.
* Average Order Value = delivered revenue / distinct delivered orders.
* New customers = customers whose first-ever delivered order matches the filters.
* Repeat customers = customers with more than one delivered order in the selection.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import case, distinct, func, select

from app.models import Sale
from app.services.filters import DELIVERED, Filters, conditions

sales = Sale.__table__


# ----------------------------------------------------------------- helpers
def _clean(value):
    """Convert database values (Decimal, date) into JSON-friendly Python values."""
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, date):
        return value.isoformat()
    return value


def _rows(session, stmt):
    return [
        {key: _clean(val) for key, val in row.items()}
        for row in session.execute(stmt).mappings().all()
    ]


def _one(session, stmt):
    row = session.execute(stmt).mappings().first()
    return {key: _clean(val) for key, val in row.items()} if row else {}


def _ratio(numerator, denominator):
    return round(numerator / denominator, 2) if denominator else 0


# ----------------------------------------------------------------- filters
def get_filter_options(session):
    def distinct_values(column):
        stmt = (
            select(column)
            .where(sales.c.Order_Status == DELIVERED, column.is_not(None))
            .distinct()
            .order_by(column)
        )
        return list(session.execute(stmt).scalars().all())

    date_range = _one(
        session,
        select(
            func.min(sales.c.Order_Date).label("min_date"),
            func.max(sales.c.Order_Date).label("max_date"),
        ).where(sales.c.Order_Status == DELIVERED),
    )

    return {
        "states": distinct_values(sales.c.State),
        "categories": distinct_values(sales.c.Category),
        "brands": distinct_values(sales.c.Brand),
        "date_range": date_range,
    }


# ------------------------------------------------------------ sales overview
def get_overview(session, f: Filters):
    where = conditions(f, sales)

    kpis = _one(
        session,
        select(
            func.round(func.coalesce(func.sum(sales.c.Order_Value), 0), 2).label("revenue"),
            func.count(distinct(sales.c.Order_ID)).label("orders"),
            func.count(distinct(sales.c.Customer_ID)).label("customers"),
            func.coalesce(func.sum(sales.c.Quantity), 0).label("units_sold"),
        ).where(*where),
    )
    kpis["average_order_value"] = _ratio(kpis["revenue"], kpis["orders"])

    revenue = func.round(func.sum(sales.c.Order_Value), 2).label("revenue")

    monthly = _rows(
        session,
        select(sales.c.Year, sales.c.Month_No, revenue)
        .where(*where)
        .group_by(sales.c.Year, sales.c.Month_No)
        .order_by(sales.c.Year, sales.c.Month_No),
    )
    monthly = [
        {"month": f"{r['Year']}-{int(r['Month_No']):02d}", "revenue": r["revenue"]}
        for r in monthly
    ]

    categories = _rows(
        session,
        select(sales.c.Category.label("label"), revenue)
        .where(*where)
        .group_by(sales.c.Category)
        .order_by(revenue.desc()),
    )

    # Drill down to cities once a state has been selected.
    geo_column = sales.c.City if f.state else sales.c.State
    geography = _rows(
        session,
        select(geo_column.label("label"), revenue)
        .where(*where)
        .group_by(geo_column)
        .order_by(revenue.desc())
        .limit(5),
    )

    orders = func.count(distinct(sales.c.Order_ID)).label("orders")
    order_status = _rows(
        session,
        select(sales.c.Order_Status.label("status"), orders)
        .group_by(sales.c.Order_Status)
        .order_by(orders.desc()),
    )

    return {
        "kpis": kpis,
        "monthly_revenue": monthly,
        "category_revenue": categories,
        "top_geography": geography,
        "geography_label": "City" if f.state else "State",
        "order_status": order_status,
    }


# --------------------------------------------------------- customer behaviour
def get_customers(session, f: Filters):
    where = conditions(f, sales)

    # One row per customer: number of delivered orders and total spend.
    per_customer = (
        select(
            sales.c.Customer_ID,
            func.count(distinct(sales.c.Order_ID)).label("order_count"),
            func.sum(sales.c.Order_Value).label("spend"),
        )
        .where(*where)
        .group_by(sales.c.Customer_ID)
        .subquery("per_customer")
    )

    kpis = _one(
        session,
        select(
            func.count().label("total_customers"),
            func.coalesce(
                func.sum(case((per_customer.c.order_count > 1, 1), else_=0)), 0
            ).label("repeat_customers"),
            func.coalesce(func.sum(per_customer.c.spend), 0).label("total_spend"),
        ).select_from(per_customer),
    )
    kpis["average_customer_spend"] = _ratio(kpis.pop("total_spend"), kpis["total_customers"])

    # New customers: rank each customer's delivered orders by date, keep the first,
    # then apply the dashboard filters to that first order.
    ranked = (
        select(
            sales.c.Customer_ID,
            sales.c.Order_Status,
            sales.c.State,
            sales.c.Category,
            sales.c.Brand,
            sales.c.Order_Date,
            func.row_number()
            .over(
                partition_by=sales.c.Customer_ID,
                order_by=(sales.c.Order_Date, sales.c.Order_ID),
            )
            .label("order_rank"),
        )
        .where(sales.c.Order_Status == DELIVERED)
        .subquery("ranked")
    )
    kpis["new_customers"] = (
        session.execute(
            select(func.count(distinct(ranked.c.Customer_ID))).where(
                ranked.c.order_rank == 1, *conditions(f, ranked)
            )
        ).scalar()
        or 0
    )

    customers = func.count(distinct(sales.c.Customer_ID)).label("customers")
    gender = _rows(
        session,
        select(sales.c.Gender.label("label"), customers)
        .where(*where)
        .group_by(sales.c.Gender)
        .order_by(customers.desc()),
    )

    # How many customers placed 1, 2, 3 ... orders -> grouped into buckets below.
    order_counts = session.execute(
        select(per_customer.c.order_count, func.count().label("customers"))
        .group_by(per_customer.c.order_count)
    ).all()

    frequency_buckets = [("1 order", 1, 1), ("2–3 orders", 2, 3), ("4–6 orders", 4, 6), ("7+ orders", 7, 10**9)]
    segment_buckets = [("One-time", 1, 1), ("Occasional", 2, 3), ("Frequent", 4, 10**9)]

    def bucketise(buckets):
        result = []
        for label, low, high in buckets:
            total = sum(int(c) for n, c in order_counts if low <= int(n) <= high)
            if total:
                result.append({"label": label, "customers": total})
        return result

    return {
        "kpis": kpis,
        "gender": gender,
        "purchase_frequency": bucketise(frequency_buckets),
        "segments": bucketise(segment_buckets),
    }


# ----------------------------------------------------------- product analysis
def get_products(session, f: Filters):
    where = conditions(f, sales)

    kpis = _one(
        session,
        select(
            func.count(distinct(sales.c.Product_ID)).label("total_products"),
            func.round(func.coalesce(func.sum(sales.c.Order_Value), 0), 2).label("product_revenue"),
            func.coalesce(func.sum(sales.c.Quantity), 0).label("units_sold"),
        ).where(*where),
    )
    kpis["average_selling_price"] = _ratio(kpis["product_revenue"], kpis["units_sold"])

    revenue = func.round(func.sum(sales.c.Order_Value), 2).label("revenue")
    units = func.sum(sales.c.Quantity).label("units_sold")

    categories = _rows(
        session,
        select(sales.c.Category.label("label"), revenue)
        .where(*where)
        .group_by(sales.c.Category)
        .order_by(revenue.desc()),
    )

    brands = _rows(
        session,
        select(sales.c.Brand.label("label"), revenue)
        .where(*where)
        .group_by(sales.c.Brand)
        .order_by(revenue.desc())
        .limit(5),
    )

    top_products = _rows(
        session,
        select(sales.c.Product_Name.label("label"), units, revenue)
        .where(*where)
        .group_by(sales.c.Product_Name)
        .order_by(units.desc(), revenue.desc())
        .limit(5),
    )

    return {
        "kpis": kpis,
        "category_revenue": categories,
        "top_brands": brands,
        "top_products": top_products,
    }
