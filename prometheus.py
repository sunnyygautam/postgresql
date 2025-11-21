import requests
import json
import psycopg2
import time
from prometheus_client import Counter, Histogram, start_http_server

# --------------------------------------
# PROMETHEUS METRICS
# --------------------------------------

# Count successful ETL runs
etl_runs = Counter("sales_etl_runs_total", "Total number of ETL runs")

# Count API failures
api_failures = Counter("sales_api_failures_total", "Number of failed API calls")

# Count loaded rows
rows_loaded = Counter("sales_rows_loaded_total", "Rows loaded into PostgreSQL")

# Track API response time
api_latency = Histogram("sales_api_latency_seconds", "API response time in seconds")

# Track load time to PostgreSQL
db_latency = Histogram("sales_db_load_latency_seconds", "DB Load time in seconds")


# --------------------------------------
# 1. Fetch Sales Data from REST API
# --------------------------------------
@api_latency.time()
def fetch_sales():
    url = "https://api.restful-api.dev/objects"

    print("Fetching sales data...")
    resp = requests.get(url)

    if resp.status_code != 200:
        api_failures.inc()
        raise Exception(f"API Error {resp.status_code}: {resp.text}")

    return resp.json()


# --------------------------------------
# 2. TRANSFORM - Clean / Process Data
# --------------------------------------
def transform_sales(raw_data):
    transformed = []
    for sale in raw_data:
        transformed.append({
            "product_id": int(sale.get("id", 0)),
            "product_name": sale.get("name", "Unknown").title(),
        })
    return transformed


# --------------------------------------
# 3. LOAD - Insert into PostgreSQL
# --------------------------------------
@db_latency.time()
def load_to_postgres(sales_data):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="admin",
        dbname="salesdb"
    )
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            product_id INT,
            product_name TEXT
        );
    """)

    for sale in sales_data:
        cur.execute("""
            INSERT INTO sales (product_id, product_name)
            VALUES (%s, %s);
        """, (
            sale["product_id"],
            sale["product_name"]
        ))
        rows_loaded.inc()   # <-- increment for each row

    conn.commit()
    cur.close()
    conn.close()

    print("Sales data loaded into PostgreSQL.")


# --------------------------------------
# MAIN
# --------------------------------------
if __name__ == "__main__":

    # Start Prometheus metrics server on port 8000
    print("Starting Prometheus metrics server on port 8000...")
    start_http_server(8000)   # <-- http://localhost:8000/metrics

    etl_runs.inc()  # count ETL execution

    raw_data = fetch_sales()
    transformed_data = transform_sales(raw_data)
    load_to_postgres(transformed_data)
    print("ETL completed. Metrics available at http://localhost:8000/metrics")

    # Keep server alive
    while True:
        time.sleep(1)
