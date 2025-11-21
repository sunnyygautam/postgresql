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

### Git commands

- **git init

- **git add README.md

- **git commit -m "first commit"

git branch -M main

git remote add origin https://github.com/sunnyygautam/postgresql.git

git push -u origin main

git add . && git commit -m "updated"
git reflogs

git reset --hard 3c77717 >>will reverts your repository to a specific commit.
[Resets the HEAD: Moves the HEAD pointer (and thus the current branch) to the specified <commit>]
[Clears the staging area, Discards all changes in the working directory.]

git reset --soft
[Leaves the staging area , Leaves the working directory completely unchanged]

git revert 3c77717 (will remove only that commit)

git stash command saves your local modifications (both staged and unstaged) and reverts your working directory to match the HEAD commit.
git stash pop command retrieves the most recently stashed changes and applies them to your current working directory.
git stash apply leaves it in the stash list for potential reuse. 

git pull command. This command fetches the latest changes from the remote repository and automatically merges them into your current local branch.
git fetch: This command downloads the latest changes from the remote repository to your local repository
git pull is a convenience command that effectively combines git fetch and git merge into a single operation
