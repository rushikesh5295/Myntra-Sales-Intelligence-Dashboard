# Myntra Sales Intelligence Dashboard

A three-page sales analytics dashboard built on a Myntra order dataset (100,000 orders, Oct 2025 – Sep 2026).
Data is stored in **MySQL**, queried with **SQLAlchemy** from a **Flask** backend, and shown with HTML, CSS, JavaScript and Chart.js.

**Tech stack:** Python · Flask · SQLAlchemy · MySQL · Pandas · HTML · CSS · JavaScript · Chart.js

<!-- Add a screenshot after pushing: create a docs/ folder, save a screenshot as docs/dashboard.png, then uncomment the next line -->
<!-- ![Dashboard screenshot](docs/dashboard.png) -->

## Features
| Page | URL | What it shows |
|---|---|---|
| Sales Overview | `/` | Revenue, orders, customers, AOV, units · monthly trend · category share · top 5 states/cities · order-status summary |
| Customer Behaviour | `/customers` | Total / new / repeat customers, average spend · gender · purchase frequency · segments |
| Product Analysis | `/products` | Products, revenue, units, average price · category revenue · top 5 brands · top 5 products |

All pages share the filters **State, Category, Brand and a date range**.

## Business rules
- Revenue, orders, customers and units count **Delivered** orders only.
- Average Order Value = delivered revenue ÷ distinct delivered orders.
- New customers = customers whose first-ever delivered order matches the selected filters.
- Repeat customers = customers with more than one delivered order in the selection.
- The order-status summary shows every status and is not part of delivered revenue.

## Project structure
```
Myntra_Sales_Intelligence_Dashboard/
├── run.py                  # starts the Flask server
├── config.py               # reads .env, builds the MySQL connection URL
├── .env.example            # template for your MySQL settings (copy to .env)
├── requirements.txt
├── app/
│   ├── __init__.py         # Flask application factory
│   ├── extensions.py       # SQLAlchemy engine + session factory
│   ├── models.py           # ORM model: Sale  (table `sales`)
│   ├── routes/
│   │   ├── pages.py        # HTML pages  (/, /customers, /products)
│   │   └── api.py          # JSON API    (/api/...)
│   ├── services/
│   │   ├── filters.py      # filter parsing + SQL conditions
│   │   └── analytics.py    # all dashboard queries (SQLAlchemy)
│   ├── templates/          # Jinja2: base layout + 3 pages
│   └── static/             # css/, js/, img/
├── scripts/
│   ├── clean_data.py       # step 1: raw CSV  -> cleaned CSV
│   └── load_database.py    # step 2: cleaned CSV -> MySQL
├── database/               # schema.sql + analysis_queries.sql (reference)
├── data/raw, data/processed
└── notebooks/01_eda.ipynb
```

## How data flows
`data/raw` CSV → `clean_data.py` → `data/processed` CSV → `load_database.py` → MySQL table `sales`
→ SQLAlchemy queries in `services/analytics.py` → JSON from `routes/api.py` → Chart.js in the browser.

## Requirements
- Python 3.10 or newer
- **MySQL Server 8.0 or newer** (the Customer Behaviour page uses a window function)
- Internet connection (Chart.js and the Inter font load from a CDN)

## Getting started

### 1. Get the code
```
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```
(Or download the ZIP from GitHub and extract it.)

### 2. Install the packages
**Option A – with a virtual environment (recommended)**
```
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate        # macOS / Linux
pip install -r requirements.txt
```
You must activate the environment again in every new terminal window before running the app.
(If PowerShell blocks the activation script, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once.)

**Option B – without a virtual environment**
```
python -m pip install -r requirements.txt
```
Then `python run.py` works in any terminal, with nothing to activate.

In PyCharm: open the folder, then **Settings → Project → Python Interpreter → Add Interpreter → Virtualenv**, and run `pip install -r requirements.txt` in the Terminal tab.

### 3. Configure MySQL
Copy `.env.example` to a new file named `.env` and set your MySQL password:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=myntra_sales
```
`.env` is git-ignored, so your password is never committed.

### 4. Load the data into MySQL (one time, about a minute)
```
python scripts/load_database.py
```
This creates the `myntra_sales` database and the `sales` table and loads the cleaned dataset.
(Optional: `python scripts/clean_data.py` regenerates the cleaned CSV from the raw file; a cleaned copy is already included.)

### 5. Run the app
```
python run.py
```
(With Option A, activate the environment first, or run `.venv\Scripts\python.exe run.py` without activating.)
Or right-click `run.py` in PyCharm → **Run 'run'**. Then open **http://127.0.0.1:5000**.

Check the database connection at http://127.0.0.1:5000/api/health — it should show `"status": "ok"` and 100000 rows.

## API endpoints
All accept optional `state`, `category`, `brand`, `start_date`, `end_date` (YYYY-MM-DD).

| Endpoint | Returns |
|---|---|
| `GET /api/health` | Database connection check |
| `GET /api/filters` | Values for the filter dropdowns |
| `GET /api/overview` | Sales Overview data |
| `GET /api/customers` | Customer Behaviour data |
| `GET /api/products` | Product Analysis data |

## Troubleshooting
- **ModuleNotFoundError: No module named 'flask'** → the packages are not installed for the Python you are using. Activate the virtual environment (`.venv\Scripts\Activate.ps1`) or run `python -m pip install -r requirements.txt`.
- **Access denied for user 'root'** → wrong `DB_PASSWORD` in `.env`.
- **Can't connect to MySQL server** → the MySQL service is not running (start it from Windows Services / MySQL Workbench).
- **"Unable to load dashboard data"** on a page → run `python scripts/load_database.py`, then reload with Ctrl + F5.
- **Database error on Customer Behaviour only** → your MySQL is older than 8.0.
- **Charts missing** → no internet connection (Chart.js loads from a CDN).
- Do not open the HTML files directly; always use the Flask address.

## Dataset
`data/raw/Myntra_Dataset.csv` – 100,000 order lines, 31 columns (orders, customers, products, location, pricing, status).