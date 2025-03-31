import random
from datetime import datetime, timedelta
from google.cloud import spanner
import os
def initialize_spanner():
   
    client = spanner.Client(project="my-project")
    

    instance_config = "emulator-config"
    instance = client.instance("test-instance", instance_config)
    
    try:
        operation = instance.create()
        operation.result() 
        print("Instance created succesfully")
    except Exception as e:
        print(f"Instance already exists or other error: {e}")

  
    database = instance.database("test-db")
    try:
        operation = database.create()
        operation.result()
        print("Database created successfully")
    except Exception as e:
        print(f"Database already exists or other error:: {e}")

    return instance, database

def create_tables(database):
    
    ddl_statements = [
        """CREATE TABLE customers (
            customer_id INT64 NOT NULL,
            name STRING(100),
            email STRING(100)
        ) PRIMARY KEY(customer_id)""",
        
        """CREATE TABLE transactions (
            transaction_id INT64 NOT NULL,
            customer_id INT64 NOT NULL,
            amount FLOAT64 NOT NULL,
            date DATE NOT NULL
        ) PRIMARY KEY(transaction_id)"""
    ]
    
    try:
        operation = database.update_ddl(ddl_statements)
        operation.result()
        print("Tablas creadas exitosamente")
    except Exception as e:
        print(f"Error al crear tablas: {e}")

def insert_sample_data(database):
   
    with database.batch() as batch:
        for i in range(1, 11):
            customer_id = i
            name = f"Customer {i}"
            email = f"customer{i}@example.com"
            
            batch.insert(
                table="customers",
                columns=("customer_id", "name", "email"),
                values=[(customer_id, name, email)]
            )
    print("10 customers added")

   
    with database.batch() as batch:
        for i in range(1, 31):
            transaction_id = i
            customer_id = random.randint(1, 10)
            amount = round(random.uniform(10, 1000), 2) 
            
       
            random_days = random.randint(0, 3*365)
            date = (datetime.now() - timedelta(days=random_days)).date()
            
            batch.insert(
                table="transactions",
                columns=("transaction_id", "customer_id", "amount", "date"),
                values=[(transaction_id, customer_id, amount, date)]
            )
    print("30 transacctions added")

def main():
    instance, database = initialize_spanner()

    create_tables(database)

    insert_sample_data(database)
    
    print("Inicialization completed!")

if __name__ == "__main__":
    main()