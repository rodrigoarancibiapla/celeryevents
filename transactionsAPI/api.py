from fastapi import FastAPI
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Configuración de SQLAlchemy con Spanner
project_id = 'my-project'   # Reemplaza con tu ID de proyecto
instance_id = 'test-instance'   # Reemplaza con tu ID de instancia
database_id = 'test-db'         # Reemplaza con tu ID de base de datos


# Crear la URL de conexión para SQLAlchemy
#spanner+spanner:///projects/{project_id}/instances/{instance_id}/databases/{database_id}"
db_url = f"spanner+spanner://spanner_emulator:9010/projects/{project_id}/instances/{instance_id}/databases/{database_id}"


engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()

# Definir tabla
transactions_table = Table('transactions', metadata,
                      autoload_with=engine)

@app.get("/transactions")
def obtener_transactions():
    with session.begin():
        result = session.execute(transactions_table.select())
        transactions = [{"transaction_id": row[0], "customer_id": row[1], "amount": row[2], "date": row[3]} for row in result]
    return transactions
