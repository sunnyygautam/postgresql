### Rest API sample
https://restful-api.dev/

### Run postgresql
docker run --name postgres-db -e POSTGRES_PASSWORD=admin -p 5432:5432 -d postgres

winpty docker exec -it postgres-db bash

psql -U postgres

CREATE DATABASE salesdb;

Show database: \l

show tables: \dt

switch to new database: \c <database_name>

select * from sales;

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

