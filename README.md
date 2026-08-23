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
