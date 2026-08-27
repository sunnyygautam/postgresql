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
