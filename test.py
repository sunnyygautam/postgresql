import requests
import json
import psycopg2

# --------------------------------------
# 1. Fetch Sales Data from REST API
# --------------------------------------
def fetch_sales():
    url = "https://api.restful-api.dev/objects?id=1&id=2"

    print("Fetching sales data...")
    resp = requests.get(url)

    if resp.status_code != 200:
        raise Exception(f"API Error {resp.status_code}: {resp.text}")

    data = resp.json()   # <--- Your original line
#    print(json.dumps(data, indent=4))
    return data

# --------------------------------------
# 2. TRANSFORM - Clean / Process Data
# --------------------------------------
def transform_sales(raw_data):
    transformed = []

    for sale in raw_data:
        # example transformation:
        transformed.append({
            "product_id": int(sale.get("id", 0)),
            "product_name": sale.get("name", "Unknown").title(),  # normalize name
        })

#    print("Sample transformed record:")
#    print(transformed[0] if transformed else "No data found")

    return transformed

# --------------------------------------
# 3. LOAD - Insert into PostgreSQL
# --------------------------------------
def load_to_postgres(sales_data):
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="admin",
        dbname="salesdb"
    )

    cur = conn.cursor()

    # Create table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            product_id INT,
            product_name TEXT
        );
    """)

    # Insert data into table
    for sale in sales_data:
        cur.execute("""
            INSERT INTO sales (product_id, product_name)
            VALUES (%s, %s);
        """, (
            sale["product_id"],
            sale["product_name"]
        ))

    conn.commit()
    cur.close()
    conn.close()

    print("Sales data loaded into PostgreSQL.")

if __name__ == "__main__":
    raw_data = fetch_sales()
    transformed_data = transform_sales(raw_data)
    load_to_postgres(transformed_data)
