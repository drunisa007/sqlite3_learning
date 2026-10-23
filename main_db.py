import sqlite3

conn = sqlite3.connect("car_database.db")
conn.execute("PRAGMA foreign_keys = ON")

ownerSchema = """
    CREATE TABLE IF NOT EXISTS owners(
    owner_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT  NOT NULL
    )
"""

conn.execute(ownerSchema)
print("Owner Schema created")

carSchema = """
    CREATE TABLE IF NOT EXISTS  cars(
    car_id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    brand TEXT NOT NULL ,
    model TEXT NOT NULL,
    plate_number TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES owners(owner_id)
    )
"""

conn.execute(carSchema)
print("Car Schema created")

serviceSchema = """
    CREATE TABLE IF NOT EXISTS  services(
    service_id INTEGER PRIMARY KEY,
    car_id INTEGER NOT NULL,
    service_type TEXT NOT NULL,
    costs REAL NOT NULL,
    FOREIGN KEY (car_id) REFERENCES cars(car_id)
    )
"""

conn.execute(serviceSchema)

print("SERVICE Schema created")


conn.executemany(
    """
    INSERT INTO owners(owner_id,name,phone)
    VALUES(?,?,?)
    """,
    [
        (1,"AUNG","09"),
        (2,"Naing","08"),
        (3,"Yet","02"),
    ]
)

print("INSERT OWNER") 

conn.executemany(
    """
    INSERT INTO cars(car_id,owner_id,brand,model,plate_number)
    VALUES(?,?,?,?,?)
    """,
    [
        (1,1,"Toyota","Model 1","Zx"),
        (2,2,"Mercedes","Model 2","ZY"),
        (3,3,"Ford","Model 3","ZL")
    ]
)

print("INSERT Car")    


conn.executemany(
    """
    INSERT INTO services(service_id,car_id,service_type,costs)
    VALUES(?,?,?,?)
    """,
    [
        (1,1,"Engine",1.0),
        (2,2,"AC",2.0),
        (3,3,"Wheel",3.0)
    ]
)

print("INSERT service")    



conn.execute("""
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
    ORDER BY o.owner_id, c.car_id, s.service_id

""")