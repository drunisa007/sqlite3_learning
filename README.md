# SQLite JOINs: Owners, Cars, and Services

A practical guide to SQL joins using Python's `sqlite3` module and a car-service database.

This README contains **sections 1–16** of the join tutorial, with **Python code for every query**, explanations, practice data, and expected results. The examples execute SQL through Python's `sqlite3` connection. Start with `INNER JOIN` and `LEFT JOIN`, then work through the remaining examples.

## Contents

1. [Understand how your tables connect](#1-understand-how-your-tables-connect)
2. [Run the queries from Python](#2-run-the-queries-from-python)
3. [Add practice rows](#3-add-practice-rows)
4. [INNER JOIN](#4-inner-join)
5. [LEFT JOIN](#5-left-join)
6. [RIGHT JOIN](#6-right-join)
7. [FULL OUTER JOIN](#7-full-outer-join)
8. [CROSS JOIN](#8-cross-join)
9. [SELF JOIN](#9-self-join)
10. [JOIN with USING](#10-join-with-using)
11. [NATURAL JOIN](#11-natural-join)
12. [List every owner, including owners without cars or services](#12-list-every-owner-including-owners-without-cars-or-services)
13. [Find cars that have no services](#13-find-cars-that-have-no-services)
14. [Find cars that have services, with each car listed once](#14-find-cars-that-have-services-with-each-car-listed-once)
15. [Count cars and services, and calculate each owner's total cost](#15-count-cars-and-services-and-calculate-each-owners-total-cost)
16. [Learn the difference between ON and WHERE](#16-learn-the-difference-between-on-and-where)

## Run the complete Python tutorial

The companion [sqlite_joins_tutorial.py](sqlite_joins_tutorial.py) creates the sample tables, inserts the data, and runs the examples in order.

```bash
python sqlite_joins_tutorial.py
```

It uses Python's standard library and SQLite 3.39.0 or later. Each run starts with a fresh in-memory database, so the script can be rerun without duplicate IDs from a previous run.

You can also copy the Python examples from this README into one Python session. Run the setup first, then add the practice rows once before sections 4–16.

## Before you begin

- If you have already run your schema-and-insert script, use its existing `conn` connection.
- If you are starting fresh, section 2 includes an optional setup that creates the same original data in an in-memory database.
- The result in section 2 uses the **original data**.
- The results in sections 4–16 use the **expanded data**, after adding the optional rows in section 3.
- `RIGHT JOIN` and `FULL OUTER JOIN` require **SQLite 3.39.0 or later**. Check the version used by Python with `sqlite3.sqlite_version`. [SQLite release notes](https://www.sqlite.org/releaselog/3_39_0.html)

The query results in this guide were checked against the schema and sample records shown below.

---

## 1. Understand how your tables connect

Your database contains three tables:

| Table | Columns |
|---|---|
| `owners` | `owner_id`, `name`, `phone` |
| `cars` | `car_id`, `owner_id`, `brand`, `model`, `plate_number` |
| `services` | `service_id`, `car_id`, `service_type`, `costs` |

The relationships are:

| First table and column | Related table and column | Meaning |
|---|---|---|
| `owners.owner_id` | `cars.owner_id` | An owner can have multiple cars. |
| `cars.car_id` | `services.car_id` | A car can have multiple services. |

To connect a service to its car, use:

`ON s.car_id = c.car_id`

Here, `s.car_id` identifies the car receiving the service. `s.service_id` identifies the individual service record.

Throughout the examples:

- `o` is an alias for `owners`.
- `c` is an alias for `cars`.
- `s` is an alias for `services`.

An alias is a short name used within a query. For example, `cars AS c` lets you write `c.brand` instead of `cars.brand`.

### Original sample data

**Owners**

| owner_id | name | phone |
|---:|---|---|
| 1 | AUNG | 09 |
| 2 | Naing | 08 |
| 3 | Yet | 02 |

**Cars**

| car_id | owner_id | brand | model | plate_number |
|---:|---:|---|---|---|
| 1 | 1 | Toyota | Model 1 | Zx |
| 2 | 2 | Mercedes | Model 2 | ZY |
| 3 | 3 | Ford | Model 3 | ZL |

**Services**

| service_id | car_id | service_type | costs |
|---:|---:|---|---:|
| 1 | 1 | Engine | 1.0 |
| 2 | 2 | AC | 2.0 |
| 3 | 3 | Wheel | 3.0 |

---

## 2. Run the queries from Python

### Optional setup for a fresh database

Skip this block if you already have the `conn` connection and original records from your own script.

This setup creates a fresh **in-memory practice database**. It does not change your existing `car_database.db` file. Its data lasts only while the connection remains open.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON")

conn.executescript("""
    CREATE TABLE owners (
        owner_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL
    );

    CREATE TABLE cars (
        car_id INTEGER PRIMARY KEY,
        owner_id INTEGER NOT NULL,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        plate_number TEXT NOT NULL,
        FOREIGN KEY (owner_id) REFERENCES owners(owner_id)
    );

    CREATE TABLE services (
        service_id INTEGER PRIMARY KEY,
        car_id INTEGER NOT NULL,
        service_type TEXT NOT NULL,
        costs REAL NOT NULL,
        FOREIGN KEY (car_id) REFERENCES cars(car_id)
    );
""")

conn.executemany(
    "INSERT INTO owners (owner_id, name, phone) VALUES (?, ?, ?)",
    [
        (1, "AUNG", "09"),
        (2, "Naing", "08"),
        (3, "Yet", "02"),
    ]
)

conn.executemany(
    """
    INSERT INTO cars (car_id, owner_id, brand, model, plate_number)
    VALUES (?, ?, ?, ?, ?)
    """,
    [
        (1, 1, "Toyota", "Model 1", "Zx"),
        (2, 2, "Mercedes", "Model 2", "ZY"),
        (3, 3, "Ford", "Model 3", "ZL"),
    ]
)

conn.executemany(
    """
    INSERT INTO services (service_id, car_id, service_type, costs)
    VALUES (?, ?, ?, ?)
    """,
    [
        (1, 1, "Engine", 1.0),
        (2, 2, "AC", 2.0),
        (3, 3, "Wheel", 3.0),
    ]
)

conn.commit()
```

### Helper for running queries

After your existing inserts, or after the optional setup above, add:

```python
# Commit the inserted records.
conn.commit()

# Check the SQLite version used by Python.
print("SQLite version:", sqlite3.sqlite_version)

# Run a SELECT query and print its results.
def show(sql):
    cursor = conn.execute(sql)

    # Print column names.
    print([column[0] for column in cursor.description])

    # Print each result row.
    for row in cursor:
        print(row)
```

With the connection settings used here, `conn.commit()` commits pending inserts. On a file-backed connection, this makes the inserted records persist. Queries on the same connection can already see their own pending inserts before committing. [Python sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html)

The query examples below call `conn.execute()` directly and print each row. You can also use `show()` to display column names for a query:

```python
show("""
    SELECT *
    FROM cars;
""")
```

The `show()` function prints column names and Python tuples. The direct `conn.execute()` examples print tuples. The Markdown tables in this guide display those results more readably.

### Start with a query across all three tables

Run this before adding the extra practice rows in section 3:

```python
show("""
    SELECT
        o.name AS owner_name,
        c.brand,
        c.model,
        c.plate_number,
        s.service_type,
        s.costs
    FROM owners AS o
    INNER JOIN cars AS c
        ON c.owner_id = o.owner_id
    INNER JOIN services AS s
        ON s.car_id = c.car_id
    ORDER BY o.owner_id, c.car_id, s.service_id;
""")
```

**Result with the original data:**

| owner_name | brand | model | plate_number | service_type | costs |
|---|---|---|---|---|---:|
| AUNG | Toyota | Model 1 | Zx | Engine | 1.0 |
| Naing | Mercedes | Model 2 | ZY | AC | 2.0 |
| Yet | Ford | Model 3 | ZL | Wheel | 3.0 |

Read the query in this order:

1. Start with `owners`.
2. Find each owner's cars using `owner_id`.
3. Find each car's services using `car_id`.
4. Return the columns listed under `SELECT`.

---

## 3. Add practice rows

Your original sample has a match everywhere: every owner has a car, and every car has a service. That makes several join types return identical results.

To see the differences clearly, add these three rows **once**:

```python
# An owner who has no car.
conn.execute(
    """
    INSERT INTO owners (owner_id, name, phone)
    VALUES (?, ?, ?)
    """,
    (4, "Su", "04")
)

# AUNG's second car, which has no service.
conn.execute(
    """
    INSERT INTO cars (
        car_id, owner_id, brand, model, plate_number
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (4, 1, "Honda", "Model 4", "ZH")
)

# A second service for the Toyota.
conn.execute(
    """
    INSERT INTO services (
        service_id, car_id, service_type, costs
    )
    VALUES (?, ?, ?, ?)
    """,
    (4, 1, "Oil", 4.0)
)

conn.commit()
```

This gives us useful cases:

| Practice case | What it helps demonstrate |
|---|---|
| Su has no car | Keeping an owner without a matching car |
| Honda has no service | Keeping a car without a matching service |
| Toyota has two services | Producing multiple rows for one car |
| AUNG owns Toyota and Honda | Joining cars to other cars owned by the same person |

**All result examples in sections 4–16 assume you added these practice rows.**

Because the IDs are explicit, running this insertion block again will attempt to reuse existing primary keys. The same applies to rerunning the original inserts against an already populated database.

### Join reference

For a query written as `FROM A ... JOIN B`, `A` is the left input and `B` is the right input.

| Join | Rows included |
|---|---|
| `INNER JOIN` | Matching pairs |
| `LEFT JOIN` | Matching pairs, plus unmatched rows from the left |
| `RIGHT JOIN` | Matching pairs, plus unmatched rows from the right |
| `FULL OUTER JOIN` | Matching pairs, plus unmatched rows from either side |
| `CROSS JOIN` | Every possible pairing |

Outer joins fill the missing side with `NULL`. The word `OUTER` is optional in `LEFT OUTER JOIN`, `RIGHT OUTER JOIN`, and `FULL OUTER JOIN`. [SQLite SELECT documentation](https://www.sqlite.org/lang_select.html)

---

## 4. INNER JOIN

**Find cars that have services.**

```python
cursor = conn.execute("""
    SELECT
        c.car_id,
        c.brand,
        s.service_type,
        s.costs
    FROM cars AS c
    INNER JOIN services AS s
        ON s.car_id = c.car_id
    ORDER BY c.car_id, s.service_id;
""")

for row in cursor:
    print(row)
```

Result:

| car_id | brand | service_type | costs |
|---:|---|---|---:|
| 1 | Toyota | Engine | 1.0 |
| 1 | Toyota | Oil | 4.0 |
| 2 | Mercedes | AC | 2.0 |
| 3 | Ford | Wheel | 3.0 |

Notice:

- Honda is absent because it has no service.
- Toyota appears twice because it has two matching services.

A join returns a row for every matching pair. The repeated Toyota details represent two different services.

You can write `JOIN` instead of `INNER JOIN`. [SQLite SELECT documentation](https://www.sqlite.org/lang_select.html)

---

## 5. LEFT JOIN

**List every car, including cars without services.**

```python
cursor = conn.execute("""
    SELECT
        c.car_id,
        c.brand,
        s.service_type,
        s.costs
    FROM cars AS c
    LEFT JOIN services AS s
        ON s.car_id = c.car_id
    ORDER BY c.car_id, s.service_id;
""")

for row in cursor:
    print(row)
```

Result:

| car_id | brand | service_type | costs |
|---:|---|---|---:|
| 1 | Toyota | Engine | 1.0 |
| 1 | Toyota | Oil | 4.0 |
| 2 | Mercedes | AC | 2.0 |
| 3 | Ford | Wheel | 3.0 |
| 4 | Honda | `NULL` | `NULL` |

Honda remains because `cars` is the left table.

Its service columns are `NULL` because there is no matching service row. When printing through Python's `sqlite3`, these values appear as `None`. [Python sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html)

Use this query for a report that must list every registered car, whether or not it has received a service.

---

## 6. RIGHT JOIN

**Preserve the table on the right.**

To keep every car using a right join, put `cars` on the right:

```python
cursor = conn.execute("""
    SELECT
        c.car_id,
        c.brand,
        s.service_type,
        s.costs
    FROM services AS s
    RIGHT JOIN cars AS c
        ON s.car_id = c.car_id
    ORDER BY c.car_id, s.service_id;
""")

for row in cursor:
    print(row)
```

This produces the same five rows as section 5, including Honda.

Compare the table positions:

| Query structure | Table whose rows are preserved |
|---|---|
| `cars LEFT JOIN services` | `cars` |
| `services RIGHT JOIN cars` | `cars` |

To rewrite a right join for older SQLite versions, swap the two tables and use `LEFT JOIN`, keeping the same matching condition.

Native `RIGHT JOIN` support requires SQLite 3.39.0 or later. [SQLite release notes](https://www.sqlite.org/releaselog/3_39_0.html)

---

## 7. FULL OUTER JOIN

**Preserve rows from both inputs.**

```python
cursor = conn.execute("""
    SELECT
        c.car_id AS car_id,
        c.brand,
        s.car_id AS service_car_id,
        s.service_type
    FROM cars AS c
    FULL OUTER JOIN services AS s
        ON s.car_id = c.car_id
    ORDER BY COALESCE(c.car_id, s.car_id), s.service_id;
""")

for row in cursor:
    print(row)
```

This keeps cars without services and services without a matching car.

With our expanded sample, it returns five rows:

| car_id | brand | service_car_id | service_type |
|---:|---|---:|---|
| 1 | Toyota | 1 | Engine |
| 1 | Toyota | 1 | Oil |
| 2 | Mercedes | 2 | AC |
| 3 | Ford | 3 | Wheel |
| 4 | Honda | `NULL` | `NULL` |

Every service has a matching car, so Honda is the only unmatched row.

In your intended relationship, a service must reference an existing car. With foreign key enforcement enabled, an orphan service cannot be inserted. [SQLite foreign key documentation](https://www.sqlite.org/foreignkeys.html)

The `COALESCE(c.car_id, s.car_id)` in `ORDER BY` uses the first non-null ID, allowing rows from either input to be ordered by the associated car ID. [SQLite core functions](https://www.sqlite.org/lang_corefunc.html#coalesce)

### Show unmatched rows on both sides

We can demonstrate the full join by filtering the inputs while keeping the underlying data valid:

```python
cursor = conn.execute("""
    WITH selected_cars AS (
        SELECT *
        FROM cars
        WHERE car_id IN (1, 4)
    ),
    selected_services AS (
        SELECT *
        FROM services
        WHERE service_id IN (1, 2)
    )
    SELECT
        c.brand,
        s.service_type
    FROM selected_cars AS c
    FULL OUTER JOIN selected_services AS s
        ON s.car_id = c.car_id
    ORDER BY COALESCE(c.car_id, s.car_id), s.service_id;
""")

for row in cursor:
    print(row)
```

`WITH` names two query results that we use as the join's inputs:

- Cars: Toyota and Honda.
- Services: Engine for Toyota, and AC for Mercedes.

Result:

| brand | service_type |
|---|---|
| Toyota | Engine |
| `NULL` | AC |
| Honda | `NULL` |

There are three cases:

1. Toyota matches its Engine service.
2. The AC service has no car in the filtered car input.
3. Honda has no service in the filtered service input.

Mercedes still exists in the database; it was excluded from this particular input.

Native `FULL OUTER JOIN` support requires SQLite 3.39.0 or later. [SQLite release notes](https://www.sqlite.org/releaselog/3_39_0.html)

---

## 8. CROSS JOIN

**Produce every possible combination.**

```python
cursor = conn.execute("""
    SELECT
        c.brand,
        s.service_type
    FROM cars AS c
    CROSS JOIN services AS s
    ORDER BY c.car_id, s.service_id;
""")

for row in cursor:
    print(row)
```

We now have four cars and four service records, so this returns:

```text
4 × 4 = 16 rows
```

The first four rows are:

| brand | service_type |
|---|---|
| Toyota | Engine |
| Toyota | AC |
| Toyota | Wheel |
| Toyota | Oil |

Then Mercedes is paired with all four services, followed by Ford and Honda.

This query does not check `car_id`, so these combinations do not represent the services each car actually received.

Use a cross join when you deliberately need every combination, such as all combinations of available sizes and colors.

---

## 9. SELF JOIN

**Join a table to itself.**

Suppose you want to find pairs of cars belonging to the same owner:

```python
cursor = conn.execute("""
    SELECT
        c1.owner_id,
        c1.brand AS first_car,
        c2.brand AS second_car
    FROM cars AS c1
    INNER JOIN cars AS c2
        ON c1.owner_id = c2.owner_id
       AND c1.car_id < c2.car_id
    ORDER BY c1.owner_id, c1.car_id, c2.car_id;
""")

for row in cursor:
    print(row)
```

Result:

| owner_id | first_car | second_car |
|---:|---|---|
| 1 | Toyota | Honda |

The same table is used in two roles: `c1` and `c2`. This is called a self join. You write it using an ordinary join and separate aliases. [SQL table expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html)

The conditions do different jobs:

`c1.owner_id = c2.owner_id`

Find cars with the same owner.

`c1.car_id < c2.car_id`

Exclude a car paired with itself, and show Toyota/Honda only once instead of also showing Honda/Toyota.

You may also hear **equi join** for equality conditions and **non-equi join** for conditions such as `<` or `>`. These describe the matching condition.

---

## 10. JOIN with USING

**Use shorter matching syntax when the column names are the same.**

When the matching column has the same name on both sides, you can use `USING`. [SQLite SELECT documentation](https://www.sqlite.org/lang_select.html)

```python
cursor = conn.execute("""
    SELECT
        c.car_id,
        c.brand,
        s.service_type,
        s.costs
    FROM cars AS c
    INNER JOIN services AS s
        USING (car_id)
    ORDER BY c.car_id, s.service_id;
""")

for row in cursor:
    print(row)
```

For this query:

`USING (car_id)`

performs the same matching as:

`ON c.car_id = s.car_id`

It returns the same four rows as the inner join in section 4.

`USING` specifies the matching columns. You still choose the join behavior separately, such as `INNER JOIN` or `LEFT JOIN`.

---

## 11. NATURAL JOIN

**Automatically match shared column names.**

```python
cursor = conn.execute("""
    SELECT
        o.name,
        c.brand
    FROM owners AS o
    NATURAL JOIN cars AS c
    ORDER BY o.owner_id, c.car_id;
""")

for row in cursor:
    print(row)
```

Result:

| name | brand |
|---|---|
| AUNG | Toyota |
| AUNG | Honda |
| Naing | Mercedes |
| Yet | Ford |

`NATURAL JOIN` matches using every column name shared by both inputs. In the current `owners` and `cars` tables, the shared name is `owner_id`. [SQLite SELECT documentation](https://www.sqlite.org/lang_select.html)

For code you plan to maintain, prefer `ON` or `USING`: they state the matching columns explicitly. With a natural join, adding another same-named column to both tables can change which rows match.

---

## 12. List every owner, including owners without cars or services

Use a chain of left joins:

```python
cursor = conn.execute("""
    SELECT
        o.name AS owner_name,
        c.brand,
        s.service_type,
        s.costs
    FROM owners AS o
    LEFT JOIN cars AS c
        ON c.owner_id = o.owner_id
    LEFT JOIN services AS s
        ON s.car_id = c.car_id
    ORDER BY o.owner_id, c.car_id, s.service_id;
""")

for row in cursor:
    print(row)
```

Result:

| owner_name | brand | service_type | costs |
|---|---|---|---:|
| AUNG | Toyota | Engine | 1.0 |
| AUNG | Toyota | Oil | 4.0 |
| AUNG | Honda | `NULL` | `NULL` |
| Naing | Mercedes | AC | 2.0 |
| Yet | Ford | Wheel | 3.0 |
| Su | `NULL` | `NULL` | `NULL` |

This preserves both kinds of missing relationships:

- Honda exists but has no service.
- Su exists but has no car.

Both joins are left joins. Changing the second join to an inner join on `s.car_id = c.car_id` would remove rows that have no matching service, including Honda's row and Su's row.

---

## 13. Find cars that have no services

Use a left join, then keep only the unmatched rows:

```python
cursor = conn.execute("""
    SELECT
        c.car_id,
        c.brand
    FROM cars AS c
    LEFT JOIN services AS s
        ON s.car_id = c.car_id
    WHERE s.service_id IS NULL
    ORDER BY c.car_id;
""")

for row in cursor:
    print(row)
```

Result:

| car_id | brand |
|---:|---|
| 4 | Honda |

Why check `s.service_id`?

A real matching service has a non-null primary key. Therefore, `NULL` in that result column identifies an unmatched car.

This is commonly called an **anti join pattern**.

You can express the same request with `NOT EXISTS`:

```python
cursor = conn.execute("""
    SELECT
        c.car_id,
        c.brand
    FROM cars AS c
    WHERE NOT EXISTS (
        SELECT 1
        FROM services AS s
        WHERE s.car_id = c.car_id
    )
    ORDER BY c.car_id;
""")

for row in cursor:
    print(row)
```

---

## 14. Find cars that have services, with each car listed once

```python
cursor = conn.execute("""
    SELECT
        c.car_id,
        c.brand
    FROM cars AS c
    WHERE EXISTS (
        SELECT 1
        FROM services AS s
        WHERE s.car_id = c.car_id
    )
    ORDER BY c.car_id;
""")

for row in cursor:
    print(row)
```

Result:

| car_id | brand |
|---:|---|
| 1 | Toyota |
| 2 | Mercedes |
| 3 | Ford |

Toyota appears once, even though it has two services.

`EXISTS` checks whether the subquery finds at least one row. The `1` in `SELECT 1` is just a convenient value; the existence of a row is what matters. [SQLite EXISTS documentation](https://www.sqlite.org/lang_expr.html#the_exists_operator)

This is commonly called a **semi join pattern**. In SQLite, you express these existence checks using constructs such as `EXISTS` and `NOT EXISTS`.

---

## 15. Count cars and services, and calculate each owner's total cost

```python
cursor = conn.execute("""
    SELECT
        o.owner_id,
        o.name,
        COUNT(DISTINCT c.car_id) AS car_count,
        COUNT(s.service_id) AS service_count,
        COALESCE(SUM(s.costs), 0) AS total_cost
    FROM owners AS o
    LEFT JOIN cars AS c
        ON c.owner_id = o.owner_id
    LEFT JOIN services AS s
        ON s.car_id = c.car_id
    GROUP BY o.owner_id, o.name
    ORDER BY o.owner_id;
""")

for row in cursor:
    print(row)
```

Result:

| owner_id | name | car_count | service_count | total_cost |
|---:|---|---:|---:|---:|
| 1 | AUNG | 2 | 2 | 5.0 |
| 2 | Naing | 1 | 1 | 2.0 |
| 3 | Yet | 1 | 1 | 3.0 |
| 4 | Su | 0 | 0 | 0 |

There are three details to understand.

### Count each car once

`COUNT(DISTINCT c.car_id)` counts each car once.

Toyota appears twice in the joined rows because of its two services. Without `DISTINCT`, AUNG's car count would incorrectly be three: Toyota twice and Honda once.

### Count actual services

`COUNT(s.service_id)` ignores the `NULL` values produced for missing services.

`COUNT(*)` counts result rows, including an unmatched outer-join row, so it would give Su a count of one. SQLite distinguishes between counting a column's non-null values and counting all rows. [SQLite aggregate functions](https://www.sqlite.org/lang_aggfunc.html)

### Display zero when there are no costs

`COALESCE(SUM(s.costs), 0)` gives zero when there are no service costs to sum. This makes Su's total display as `0`. [SQLite aggregate functions](https://www.sqlite.org/lang_aggfunc.html) and [COALESCE](https://www.sqlite.org/lang_corefunc.html#coalesce)

---

## 16. Learn the difference between ON and WHERE

This is one of the most useful lessons about outer joins.

### Keep every car, but attach only Engine services

```python
cursor = conn.execute("""
    SELECT
        c.brand,
        s.service_type
    FROM cars AS c
    LEFT JOIN services AS s
        ON s.car_id = c.car_id
       AND s.service_type = 'Engine'
    ORDER BY c.car_id;
""")

for row in cursor:
    print(row)
```

Result:

| brand | service_type |
|---|---|
| Toyota | Engine |
| Mercedes | `NULL` |
| Ford | `NULL` |
| Honda | `NULL` |

The extra condition is part of deciding which service rows match. Every car is still preserved.

### Keep only rows whose service is Engine

```python
cursor = conn.execute("""
    SELECT
        c.brand,
        s.service_type
    FROM cars AS c
    LEFT JOIN services AS s
        ON s.car_id = c.car_id
    WHERE s.service_type = 'Engine'
    ORDER BY c.car_id;
""")

for row in cursor:
    print(row)
```

Result:

| brand | service_type |
|---|---|
| Toyota | Engine |

Here, the `WHERE` condition filters the joined result. The other rows fail that condition, including rows whose service value is `NULL`.

Moving a condition between `ON` and `WHERE` can therefore change an outer join's result. [SQL table expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html)

---

## References

- [SQLite SELECT and join documentation](https://www.sqlite.org/lang_select.html)
- [SQLite 3.39.0 release notes: RIGHT and FULL OUTER JOIN support](https://www.sqlite.org/releaselog/3_39_0.html)
- [Python sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite foreign key documentation](https://www.sqlite.org/foreignkeys.html)
- [SQLite aggregate functions](https://www.sqlite.org/lang_aggfunc.html)
- [SQLite core functions](https://www.sqlite.org/lang_corefunc.html)
- [SQLite expressions and EXISTS](https://www.sqlite.org/lang_expr.html)
- [PostgreSQL documentation on standard SQL table expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html)

