-- MySQL queries equivalent to what the dashboard runs through SQLAlchemy.
-- Core business queries. Sales KPIs use Delivered orders only.

-- 1. Delivered sales KPIs
SELECT
    ROUND(SUM(Order_Value), 2) AS total_revenue,
    COUNT(DISTINCT Order_ID) AS total_orders,
    COUNT(DISTINCT Customer_ID) AS total_customers,
    ROUND(SUM(Order_Value) / COUNT(DISTINCT Order_ID), 2) AS average_order_value,
    SUM(Quantity) AS units_sold
FROM sales
WHERE Order_Status = 'Delivered';

-- 2. Revenue by state
SELECT State, ROUND(SUM(Order_Value), 2) AS revenue
FROM sales
WHERE Order_Status = 'Delivered'
GROUP BY State
ORDER BY revenue DESC;

-- 3. Revenue by category
SELECT Category, ROUND(SUM(Order_Value), 2) AS revenue
FROM sales
WHERE Order_Status = 'Delivered'
GROUP BY Category
ORDER BY revenue DESC;

-- 4. Order status summary (all statuses)
SELECT Order_Status, COUNT(DISTINCT Order_ID) AS orders
FROM sales
GROUP BY Order_Status
ORDER BY orders DESC;
