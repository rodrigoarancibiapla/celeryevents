from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker

app = FastAPI()

project_id = 'my-project'
instance_id = 'test-instance'
database_id = 'test-db'


db_url = f"spanner+spanner://spanner_emulator:9010/projects/{project_id}/instances/{instance_id}/databases/{database_id}"


engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()


transactions_table = Table('transactions', metadata,
                           autoload_with=engine)


@app.get("/transactions")
def obtener_transactions():
    with session.begin():
        result = session.execute(transactions_table.select())
        transactions = [{"transaction_id": row[0], "customer_id": row[1], "amount": row[2], "date": row[3]} for row in result]
    return transactions


@app.get("/health")
async def health_check():
    try:

        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        metadata = MetaData()
        Table('customers', metadata, autoload_with=engine)

        return JSONResponse(
            status_code=200,
            content={"status": "healthy", "database": "connected", "table": "accessible"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "database": "disconnected" if "connection" in str(e).lower() else "error"
            }
        )
