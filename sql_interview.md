# SQL Interview Prep: Finding the Nth Highest Salary

This guide contains production-ready SQL scripts to find the **4th highest salary** (or any Nth highest salary) in a database. It includes a test dataset with duplicate values to simulate real-world interview edge cases.

---

## 1. Setup Test Dataset

Run this script to create the table and ingest sample data. This dataset includes duplicate salaries to properly test ranking behavior.

```sql
-- Create employees table
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    department VARCHAR(50),
    salary DECIMAL(10, 2)
);

-- Insert sample data with duplicate salaries
INSERT INTO employees (employee_id, first_name, last_name, department, salary) VALUES
(1, 'Alice', 'Smith', 'Engineering', 10000.00), -- 1st Highest
(2, 'Bob', 'Johnson', 'Engineering', 9500.00),   -- 2nd Highest
(3, 'Charlie', 'Brown', 'Marketing', 9500.00),   -- 2nd Highest (Duplicate)
(4, 'David', 'Lee', 'HR', 9000.00),              -- 3rd Highest
(5, 'Emma', 'Davis', 'Engineering', 8500.00),    -- 4th Highest (Expected Global Result)
(6, 'Frank', 'Miller', 'Marketing', 8500.00),   -- 4th Highest (Duplicate)
(7, 'Grace', 'Wilson', 'HR', 7000.00),           -- 5th Highest
(8, 'Henry', 'Jones', 'Marketing', 6500.00);     -- 6th Highest
```

---

## 2. Core Solutions

### Method 1: Using `DENSE_RANK()` (Recommended / Cross-Platform)
**Best for:** All modern databases (PostgreSQL, MySQL 8.0+, SQL Server, Oracle). 
This approach uses a Common Table Expression (CTE) and handles duplicate salaries perfectly by assigning the same rank to identical values without skipping numbers.

```sql
WITH RankedSalaries AS (
    SELECT salary, 
           DENSE_RANK() OVER (ORDER BY salary DESC) AS salary_rank
    FROM employees
)
SELECT DISTINCT salary 
FROM RankedSalaries 
WHERE salary_rank = 4;
```

### Method 2: Using `LIMIT` and `OFFSET` (MySQL & PostgreSQL)
**Best for:** Light-weight pagination queries in MySQL and PostgreSQL. 
It bypasses window functions by sorting unique values and skipping the top 3 rows.

```sql
SELECT DISTINCT salary 
FROM employees 
ORDER BY salary DESC 
LIMIT 1 OFFSET 3;
```

### Method 3: Using `OFFSET FETCH` (SQL Server)
**Best for:** Modern SQL Server instances. 
This utilizes ANSI-standard pagination syntax to achieve the same result as Method 2.

```sql
SELECT DISTINCT salary 
FROM employees 
ORDER BY salary DESC 
OFFSET 3 ROWS FETCH NEXT 1 ROWS ONLY;
```
---
# SQL Interview Guide: Removing Duplicates

This guide covers the **top 4 methods** to remove duplicate records in SQL, a classic and highly frequent interview topic. Choosing the right method depends heavily on the database dialect, volume of data, and table structure (e.g., whether a primary key exists).

---

## 🚀 Overview of the 4 Key Methods

| Method | Best For | Dialect Compatibility | Risk Level |
| :--- | :--- | :--- | :--- |
| **1. CTE & `ROW_NUMBER()`** | Large datasets, modern engines | PostgreSQL, SQL Server, Oracle | **Low** (Highly precise) |
| **2. Subquery with `MIN()` / `MAX()`** | Legacy systems, MySQL workarounds | MySQL, SQLite, Universal | **Low** (Safe with IDs) |
| **3. Self-JOIN** | Quick deletion, small to medium tables | Universal (MySQL, Postgres, etc.) | **Medium** (Check JOIN logic) |
| **4. `DISTINCT` & Temp Table** | Pure duplicates (no unique ID column) | Universal | **High** (Table is emptied) |

---

## 🛠️ Detailed Breakdown

### Method 1: The CTE & `ROW_NUMBER()` Window Function
This is the **industry standard** and most preferred answer in senior-level interviews. It partitions the data by the duplicate criteria and assigns a sequential ranking.

```sql
WITH CTE_Duplicates AS (
    SELECT *, 
           ROW_NUMBER() OVER (
               PARTITION BY email 
               ORDER BY id ASC -- Keeps the oldest record (lowest ID)
           ) AS row_num
    FROM users
)
DELETE FROM CTE_Duplicates 
WHERE row_num > 1;
```
* **Pros:** Highly readable; easily swaps `ASC` for `DESC` to keep the newest record instead.
* **Cons:** MySQL does not allow direct `DELETE` operations on a CTE referencing the target table.

---

### Method 2: Subquery with `MIN()` or `MAX()`
The classic approach that works everywhere. It groups data by the duplicated column, identifies the primary key to keep, and deletes everything else.

```sql
DELETE FROM users 
WHERE id NOT IN (
    SELECT min_id FROM (
        SELECT MIN(id) AS min_id 
        FROM users 
        GROUP BY email
    ) AS tmp
);
```
* **Pros:** Standard ANSI SQL that works across almost all database platforms, including MySQL.
* **Cons:** `NOT IN` with subqueries can suffer from performance degradation on massive tables.

---

### Method 3: The Self-JOIN Deletion
This method joins the table to itself on the duplicate column criteria and compares IDs to eliminate clones.

```sql
DELETE u1 
FROM users u1
INNER JOIN users u2 
    ON u1.email = u2.email 
    AND u1.id > u2.id; -- Keeps the smaller ID (older record)
```
* **Pros:** Fast and efficient for medium-sized tables, natively supported in MySQL.
* **Cons:** Syntax varies slightly between dialects (e.g., Postgres requires a `USING` clause or explicit reference).

---

### Method 4: `DISTINCT` and Temporary Table (For Pure Duplicates)
Used when rows are **100% identical** across every single column, meaning there is no unique `id` or `primary key` to differentiate them.

```sql
-- 1. Extract unique rows into a staging table
SELECT DISTINCT * INTO temp_users FROM users;

-- 2. Wipe the original table
TRUNCATE TABLE users;

-- 3. Restore the deduplicated data
INSERT INTO users SELECT * FROM temp_users;

-- 4. Clean up staging environment
DROP TABLE temp_users;
```
* **Pros:** The only robust way to handle completely identical rows without modifying table schemas.
* **Cons:** Risky for high-traffic production environments due to the `TRUNCATE` step.

---

## 💡 Pro Interview Tips
* **Always Mention Backups:** Start your interview response by stating you would take a snapshot or run a transaction before deleting data. 
* **Index Awareness:** Mention that the column used in `PARTITION BY` or `GROUP BY` (like `email`) should ideally be indexed to prevent full-table scans.
