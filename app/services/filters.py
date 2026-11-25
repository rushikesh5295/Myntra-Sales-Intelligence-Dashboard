"""Dashboard filter handling: reads query-string values and builds SQL conditions."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

DELIVERED = "Delivered"


@dataclass(frozen=True)
class Filters:
    state: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @classmethod
    def from_args(cls, args) -> "Filters":
        """Create Filters from Flask's request.args ("All" or empty means no filter)."""

        def text(key):
            value = (args.get(key) or "").strip()
            return None if value in ("", "All") else value

        def day(key):
            value = (args.get(key) or "").strip()
            return date.fromisoformat(value) if value else None  # ValueError if invalid

        return cls(
            state=text("state"),
            category=text("category"),
            brand=text("brand"),
            start_date=day("start_date"),
            end_date=day("end_date"),
        )


def conditions(f: Filters, t):
    """Return the list of SQLAlchemy conditions for the given filters.

    `t` is any table / subquery that exposes the columns Order_Status, State,
    Category, Brand and Order_Date. Business rule: only Delivered orders count.
    """
    clauses = [t.c.Order_Status == DELIVERED]

    if f.state:
        clauses.append(t.c.State == f.state)
    if f.category:
        clauses.append(t.c.Category == f.category)
    if f.brand:
        clauses.append(t.c.Brand == f.brand)
    if f.start_date:
        clauses.append(t.c.Order_Date >= f.start_date)
    if f.end_date:
        clauses.append(t.c.Order_Date <= f.end_date)

    return clauses
