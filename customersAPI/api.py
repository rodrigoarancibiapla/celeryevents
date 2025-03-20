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
clientes_table = Table('clientes', metadata, autoload_with=engine)

@app.get("/clientes")
def obtener_clientes():
    with session.begin():
        result = session.execute(clientes_table.select())
        clientes = [{"cliente_id": row[0], "nombre": row[1], "email": row[2]} for row in result]
    return clientes
