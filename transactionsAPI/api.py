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
transacciones_table = Table('transacciones', metadata,
                      autoload_with=engine)

@app.get("/transacciones")
def obtener_transacciones():
    with session.begin():
        result = session.execute(transacciones_table.select())
        transacciones = [{"transaccion_id": row[0], "cliente_id": row[1], "monto": row[2], "fecha": row[3]} for row in result]
    return transacciones
