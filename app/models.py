"""SQLAlchemy ORM model for the Myntra sales table.

One row represents one order line from the Myntra dataset.
"""

from datetime import date

from sqlalchemy import Date, Float, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Sale(Base):
    __tablename__ = "sales"

    Order_ID: Mapped[str] = mapped_column(String(20), primary_key=True)
    Order_Date: Mapped[date] = mapped_column(Date, nullable=False)
    Customer_ID: Mapped[str] = mapped_column(String(20), nullable=False)
    Product_ID: Mapped[str] = mapped_column(String(20), nullable=False)
    Product_Name: Mapped[str] = mapped_column(String(150), nullable=False)
    Brand: Mapped[str] = mapped_column(String(50))
    Category: Mapped[str] = mapped_column(String(30))
    Sub_Category: Mapped[str] = mapped_column(String(50))
    Gender: Mapped[str] = mapped_column(String(20))
    City: Mapped[str] = mapped_column(String(50))
    State: Mapped[str] = mapped_column(String(50))
    Color: Mapped[str] = mapped_column(String(30))
    Size: Mapped[str] = mapped_column(String(20))
    Material: Mapped[str] = mapped_column(String(30))
    MRP: Mapped[float] = mapped_column(Float)
    Discount_Percent: Mapped[float] = mapped_column(Float)
    Selling_Price: Mapped[float] = mapped_column(Float)
    Quantity: Mapped[int] = mapped_column(Integer)
    Order_Value: Mapped[float] = mapped_column(Float)
    Rating: Mapped[float] = mapped_column(Float)
    Review_Count: Mapped[int] = mapped_column(Integer)
    Stock_Status: Mapped[str] = mapped_column(String(30))
    Payment_Method: Mapped[str] = mapped_column(String(30))
    Delivery_Time: Mapped[str] = mapped_column(String(20))
    Order_Status: Mapped[str] = mapped_column(String(20))
    Coupon_Code: Mapped[str] = mapped_column(String(30))
    Year: Mapped[int] = mapped_column(Integer)
    Month: Mapped[str] = mapped_column(String(15))
    Month_No: Mapped[int] = mapped_column(Integer)
    Quarter: Mapped[str] = mapped_column(String(5))
    Day_Name: Mapped[str] = mapped_column(String(15))

    __table_args__ = (
        Index("idx_sales_status_date", "Order_Status", "Order_Date"),
        Index("idx_sales_state", "State"),
        Index("idx_sales_category", "Category"),
        Index("idx_sales_brand", "Brand"),
        Index("idx_sales_customer", "Customer_ID"),
    )
