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
