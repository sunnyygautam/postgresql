### Rest API sample
[restful-api.dev](https://restful-api.dev/)

### Run PostgreSQL
```bash
# Run PostgreSQL container
docker run --name postgres-db -e POSTGRES_PASSWORD=admin -p 5432:5432 -d postgres

# Access the container shell (Git Bash / Windows)
winpty docker exec -it postgres-db bash

# Connect to PostgreSQL CLI
psql -U postgres

# SQL commands
CREATE DATABASE salesdb;

# Meta-commands and queries
\l                          # Show all databases
\c salesdb                  # Switch to the salesdb database
\dt                         # Show tables in current database
SELECT * FROM sales;        # Query the sales table
```


# PostgreSQL Production Troubleshooting & Optimization Runbook

A comprehensive reference guide for Technical Operations and Production Support Engineers covering connection pool exhaustion, locking diagnostics, session management, date-time interval querying, and fail-fast performance guardrails.

---

## 1. Connection Pool Diagnostics

### Check Max Allowed vs. Active Connections
```sql
SELECT 
    count(*) AS used_connections,
    current_setting('max_connections')::int AS max_connections,
    (count(*)::float / current_setting('max_connections')::float * 100)::numeric(5,2) AS percent_used
FROM pg_stat_activity;
```
### Connection Distribution by State & Database
```sql
SELECT 
    datname, 
    state, 
    count(*) 
FROM pg_stat_activity 
GROUP BY datname, state 
ORDER BY count DESC;
```
### Detect Connection Pool Starvation ("Idle in Transaction")
Sessions stuck in idle in transaction hold open connection slots and lock resources:
```sql
SELECT 
    pid, 
    usename, 
    client_addr, 
    now() - state_change AS duration, 
    query 
FROM pg_stat_activity 
WHERE state = 'idle in transaction' 
ORDER BY duration DESC;
```
### 2. Lock Contention & Blocked Query Resolution
Identify Blocked Queries (PostgreSQL 9.6+)
```sql
SELECT 
    pid AS blocked_pid,
    usename AS blocked_user,
    pg_blocking_pids(pid) AS blocking_pids,
    now() - query_start AS duration,
    query AS blocked_query
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
```
### Comprehensive Lock Map (Blocked vs. Blocking Queries)
```sql
SELECT 
    blocked.pid                 AS blocked_pid,
    blocked.usename             AS blocked_user,
    blocked.query               AS blocked_statement,
    blocking.pid                AS blocking_pid,
    blocking.usename            AS blocking_user,
    blocking.query              AS blocking_statement,
    now() - blocked.query_start AS waiting_duration
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked ON blocked.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking ON blocking.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```
### 3. Session Termination Commands

| Command | Action | Impact |
| :--- | :--- | :--- |
| `SELECT pg_cancel_backend(<pid>);` | Cancels running query | Session remains connected |
| `SELECT pg_terminate_backend(<pid>);` | Force-terminates process | Drops connection immediately |

### Terminate All Idle Transactions Older than 5 Minutes
```sql
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > INTERVAL '5 minutes';
```
### Terminate Active Queries Exceeding 30 Seconds
```sql
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' 
  AND now() - query_start > INTERVAL '30 seconds';
```
### 4. Date & Interval Patterns for Operations
Long-Running Active Queries (> 5 Minutes)
```sql
SELECT pid, usename, client_addr, now() - query_start AS runtime, query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > INTERVAL '5 minutes'
ORDER BY runtime DESC;
```
### Tables Missing Autovacuum in the Last 7 Days
```sql
SELECT relname, last_vacuum, last_autovacuum
FROM pg_stat_user_tables
WHERE last_autovacuum < now() - INTERVAL '7 days'
   OR last_autovacuum IS NULL;
```
### Filter Records by Dynamic Rolling Time Window
```sql
-- Records created in the last 24 hours
SELECT application_id, partner_id, status, created_at
FROM loan_applications
WHERE status = 'FAILED'
  AND created_at >= now() - INTERVAL '24 hours';

-- Hourly log aggregation for current date
SELECT date_trunc('hour', log_timestamp) AS hour_bucket, count(*) AS error_count
FROM api_logs
WHERE status_code >= 500
  AND log_timestamp >= CURRENT_DATE
GROUP BY hour_bucket
ORDER BY hour_bucket ASC;
```
### 5. Performance Guardrails (postgresql.conf)
Add these production safeguards to enforce a "fail-fast" policy and prevent cascading pool starvation:
```bash
# Maximum execution time allowed for any individual statement (in milliseconds)
statement_timeout = 3000                           # 3 seconds

# Maximum wait time to acquire a table/row lock before failing
lock_timeout = 3000                                # 3 seconds

# Maximum time a session can sit idle inside an open transaction
idle_in_transaction_session_timeout = 5000         # 5 seconds
```
### Zero-Downtime Index Creation
When addressing unindexed query bottlenecks in production, avoid default table-locking operations:
```sql
CREATE INDEX CONCURRENTLY idx_table_column 
ON table_name (column_name);
```
