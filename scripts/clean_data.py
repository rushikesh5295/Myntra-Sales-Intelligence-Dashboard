"""Step 1 - clean the raw Myntra dataset and save it to data/processed/.

Run from the project root:  python scripts/clean_data.py
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CLEANED_CSV, RAW_CSV  # noqa: E402

NUMERIC_COLUMNS = [
    "MRP", "Discount_Percent", "Selling_Price", "Quantity",
    "Order_Value", "Rating", "Review_Count", "Year", "Month_No",
]


def clean_data() -> None:
    print("Loading raw dataset...")
    df = pd.read_csv(RAW_CSV)
    print("Original dataset shape:", df.shape)

    # Tidy column names and trim spaces in every text column
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
            df[col] = df[col].str.strip()

    # Fix data types
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Data quality report
    print("\nMissing values per column:")
    missing = df.isnull().sum()
    print(missing[missing > 0].to_string() if missing.any() else "None")
    print("\nDuplicate records:", df.duplicated().sum())
    print("Invalid quantities:", (df["Quantity"] <= 0).sum())
    print("Invalid ratings:", (~df["Rating"].between(0, 5)).sum())
    print("Invalid discounts:", (~df["Discount_Percent"].between(0, 100)).sum())
    expected = df["Selling_Price"] * df["Quantity"]
    print("Order value mismatches:", (df["Order_Value"].round(2) != expected.round(2)).sum())

    # Regenerate the date-related columns from Order_Date
    df["Year"] = df["Order_Date"].dt.year
    df["Month"] = df["Order_Date"].dt.month_name()
    df["Month_No"] = df["Order_Date"].dt.month
    df["Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype("Int64").astype(str)
    df["Day_Name"] = df["Order_Date"].dt.day_name()

    CLEANED_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEANED_CSV, index=False)
    print("\nData cleaning completed. Final shape:", df.shape)
    print("Saved to:", CLEANED_CSV)


if __name__ == "__main__":
    clean_data()
