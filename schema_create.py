import sqlite3


def createSchema():
    conn = sqlite3.connect("car_database.db")

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
    return conn
   
