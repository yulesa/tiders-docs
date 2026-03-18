# Choosing a Database

tiders can write data to several backends. This guide helps you pick the right one and get it running.

## Which Database Should I Use?

| Database | Good for | Setup difficulty |
|---|---|---|
| **DuckDB** | Getting started, local analysis, prototyping | None — runs in-process |
| **PostgreSQL** | Relational queries, joining with existing app data | Easy with Docker |
| **ClickHouse** | Fast analytics on large datasets, aggregations | Easy with Docker |
| **Parquet files** | File-based storage, sharing data, data lakes | None — writes to disk |
| **CSV** | Quick export, spreadsheets, simple interoperability | None — writes to disk |
| **Iceberg / Delta Lake** | Production data lakes with ACID transactions | Moderate — requires catalog or storage setup |


*Just getting started?* Use DuckDB. It requires no external services — the [Your First Pipeline](first_pipeline.md) tutorial uses it.

*Need a production database?* Read on to set up PostgreSQL or ClickHouse with Docker.

---

## DuckDB

DuckDB runs inside your Python process. No server, no Docker, no configuration.

**Install**

Install tiders with the DuckDB extra dependency.

```bash
pip install "tiders[duckdb]"
```

**Querying your data in DuckDB**

Open the database file directly using [duckdb CLI](https://duckdb.org/docs/stable/clients/cli/overview):

```bash
duckdb data/output.duckdb
```

A few SQL commands to explore:

```sql
-- List all tables
SHOW TABLES;
-- Preview data
SELECT * FROM transfers LIMIT 10;
-- Count rows
SELECT count(*) FROM transfers;
-- Exit
.quit
```

---

## PostgreSQL with Docker

PostgreSQL is a battle-tested relational database going back to 1996. As a row-oriented store, it underperforms in heavy analytical workloads compared to columnar databases like ClickHouse. Use it when you need to read data straight from a pipeline without post-ingestion transformation, or when you want to connect your pipeline data to an existing PostgreSQL instance.

**Starting PostgreSQL with Docker**

Tiders provides a ready-made Docker Compose file in the `tiders/docker_postgres/` folder. Copy this file or paste its contents into your own `docker-compose.yaml`.

Copy the environment file and edit as needed:

```bash
cp .env.example .env
```

Start the container:

```bash
docker compose up -d
```

When you're done, stop the database containers:

```bash
# Stop the container (data is preserved in the volume)
docker compose down
# Stop and delete all data
docker compose down -v
```

Install tiders with the PostgreSQL extra dependency.

```bash
pip install "tiders[postgresql]"
```

**Querying your data in PostgreSQL with psql**

`psql` is the interactive terminal for PostgreSQL. You can access it through your Docker container:

```bash
# Connect via Docker
docker exec -it pg_database psql -U postgres -d tiders
# Or if you have psql installed locally
psql -U postgres -d tiders -h localhost -p 5432
```

Common `psql` commands:

| Command | Description |
|---|---|
| `\l` | List all databases |
| `\dt` | List tables in the current database |
| `\d transfers` | Describe a table's columns and types |
| `\c dbname` | Switch to a different database |
| `\?` | Show all meta-commands |
| `\q` | Exit psql |

Try some queries:

```sql
-- Preview your data
SELECT * FROM transfers LIMIT 10;
-- Count rows
SELECT count(*) FROM transfers;
-- Check the PostgreSQL version
SELECT version();
```

---

## ClickHouse with Docker

ClickHouse is a columnar database built for analytics. It excels at aggregating millions of rows quickly — ideal for blockchain data analysis.

**Starting ClickHouse with Docker**

Tiders provides a ready-made Docker Compose file in the `tiders/docker_clickhouse/` folder. Copy this file or paste its contents into your own `docker-compose.yaml`.

Copy the environment file and edit as needed:

```bash
cp .env.example .env
```

Start the container:

```bash
docker compose up -d
```

Install tiders with the ClickHouse extra dependency.

```bash
pip install "tiders[clickhouse]"
```

When you're done, stop the database containers:

```bash
# Stop the container (data is preserved in the volume)
docker compose down
# Stop and delete all data
docker compose down -v
```

**Querying your data in ClickHouse**

`clickhouse-client` is the interactive terminal for ClickHouse. Access it through your Docker container:

```bash
# Connect via Docker
docker exec -it clickhouse-server clickhouse-client --user default --password secret --database tiders
# Or if you have clickhouse-client installed locally
clickhouse-client --host localhost --port 9000 --user default --password secret --database tiders
```

You can also use the ClickHouse Web SQL UI at `http://localhost:8123/play` (assuming default host and port).

Try some queries:

```sql
-- List all databases
SHOW DATABASES;
-- List tables in the current database
SHOW TABLES;
-- Show a table's columns and types
DESCRIBE tiders.transfers;
-- Set the default database (so you don't have to prefix with `tiders.`)
USE tiders;
-- Preview your data
SELECT * FROM transfers LIMIT 10;
-- Count rows
SELECT count() FROM transfers;
-- Exit the client (type `exit` or press Ctrl+D)
```

---

## Parquet Files

Parquet is a column-oriented, binary file (not human-readable) format that offers significantly smaller file sizes, faster query performance, and built-in schema metadata compared to CSV (human-readable). Use it when you want file-based storage without running a database.

`Parquet Visualizer` is a VS Code extension that lets you browse and run SQL against Parquet files directly in the editor.

You can also read Parquet files with DuckDB, Pandas, Polars, or any tool that supports the format:

```python
# With DuckDB (no server needed)
import duckdb
duckdb.sql("SELECT * FROM 'data/output/transfers/*.parquet' LIMIT 10").show()

# With Pandas
import pandas as pd
df = pd.read_parquet("data/output/transfers/")

# With Polars
import polars as pl
df = pl.read_parquet("data/output/transfers/")
```

---

## Next Steps

- See the full [Writers reference](../tiders/writers.md) for all configuration options
- Build your first pipeline with the [Your First Pipeline](first_pipeline.md) tutorial
- Explore [examples](../tiders/examples.md) for complete working pipelines
