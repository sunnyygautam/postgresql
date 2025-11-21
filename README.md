docker run --name postgres-db -e POSTGRES_PASSWORD=admin -p 5432:5432 -d postgres

winpty docker exec -it postgres-db bash

psql -U postgres

CREATE DATABASE salesdb;

Show database: \l

show tables: \dt

switch to new database: \c <database_name>

select * from sales;

################################################
git init

git add README.md

git commit -m "first commit"

git branch -M main

git remote add origin https://github.com/sunnyygautam/postgresql.git

git push -u origin main
