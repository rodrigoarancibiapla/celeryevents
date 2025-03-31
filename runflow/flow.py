from celery import chain
from celery import Celery
import os

redis_host = os.getenv('REDIS_HOST', 'redis') 
broker = f'redis://{redis_host}:6379/0'
backend = f'redis://{redis_host}:6379/0'

app = Celery('tasks', broker=broker, backend=backend)

def ejecutar_flujo():
    
    task1 = app.send_task('worker.generation.generate_customers') 
    task2 = app.send_task('worker.generation.generate_transactions', args=[task1.get()])
    task3 = app.send_task('worker.generation.consolidate_data', args=[task2.get()]) 

    print(f"Final result: {task3.get()}")

ejecutar_flujo()
