
def createOwner(conn):
    with conn:
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