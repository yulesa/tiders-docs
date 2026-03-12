1. The "Built-in" Playground: Terminal Access
You already have a "playground" built into your Docker container. `psql` is the interactive terminal and command-line interface for PostgreSQL.  It allows users to connect to a PostgreSQL server, execute SQL queries interactively, and manage databases.

Key Features of psql:
Interactive Query Execution: Type SQL commands directly and see results immediately. 
Meta-Commands: Built-in commands (prefixed with \) for managing connections, listing databases/tables, viewing help, and more. 
Scripting Support: Can read and execute commands from files using \i filename. 
Shell-like Features: Includes command history (\s), editing (\e), and output formatting options (e.g., HTML with \H). 
Common psql Commands:
\l – List all databases.
\dt – List tables in the current database.
\du – List all users and roles.
\c dbname – Connect to a different database.
\? – Show all available meta-commands, q to exit.
\q – Exit the psql session.
SELECT version(); – Check the PostgreSQL server version. 

```Bash
#runnig through docker
docker exec -it pg_database psql -U postgres -d postgres
# or if you have postgresql instaled in your machine
psql -U postgres -d postgres
# -d: Database name.
# -U: Database user.
# -h: Host (default: localhost).
# -p: Port (default: 5432).
```