import schema_create
import owner_create

connection = schema_create.createSchema()

owner_create.createOwner(connection)



