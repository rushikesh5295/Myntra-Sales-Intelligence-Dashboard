-- MySQL schema for the Myntra Sales Intelligence dashboard.
-- NOTE: this table is created automatically by SQLAlchemy (app/models.py) when you run
--       `python scripts/load_database.py`. This file is kept as documentation of the structure.

CREATE DATABASE IF NOT EXISTS myntra_sales CHARACTER SET utf8mb4;
USE myntra_sales;

-- One row = one order line from the Myntra dataset.
CREATE TABLE IF NOT EXISTS sales (
    Order_ID         VARCHAR(20)  NOT NULL PRIMARY KEY,
    Order_Date       DATE         NOT NULL,
    Customer_ID      VARCHAR(20)  NOT NULL,
    Product_ID       VARCHAR(20)  NOT NULL,
    Product_Name     VARCHAR(150) NOT NULL,
    Brand            VARCHAR(50),
    Category         VARCHAR(30),
    Sub_Category     VARCHAR(50),
    Gender           VARCHAR(20),
    City             VARCHAR(50),
    State            VARCHAR(50),
    Color            VARCHAR(30),
    Size             VARCHAR(20),
    Material         VARCHAR(30),
    MRP              DOUBLE,
    Discount_Percent DOUBLE,
    Selling_Price    DOUBLE,
    Quantity         INT,
    Order_Value      DOUBLE,
    Rating           DOUBLE,
    Review_Count     INT,
    Stock_Status     VARCHAR(30),
    Payment_Method   VARCHAR(30),
    Delivery_Time    VARCHAR(20),
    Order_Status     VARCHAR(20),
    Coupon_Code      VARCHAR(30),
    Year             INT,
    Month            VARCHAR(15),
    Month_No         INT,
    Quarter          VARCHAR(5),
    Day_Name         VARCHAR(15),
    INDEX idx_sales_status_date (Order_Status, Order_Date),
    INDEX idx_sales_state (State),
    INDEX idx_sales_category (Category),
    INDEX idx_sales_brand (Brand),
    INDEX idx_sales_customer (Customer_ID)
);
