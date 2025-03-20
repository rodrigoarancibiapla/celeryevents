from celery import chain
from celery import Celery
import os
# Configura Celery (igual que lo tienes en tu archivo de tareas)
redis_host = os.getenv('REDIS_HOST', 'redis')  # Cambiar si Redis está en otro servidor
broker = f'redis://{redis_host}:6379/0'
backend = f'redis://{redis_host}:6379/0'

app = Celery('tasks', broker=broker, backend=backend)

def ejecutar_flujo():
    # Usando send_task para encadenar las tareas por su nombre
    # Pasando los argumentos entre las tareas utilizando apply_async y link
    task1 = app.send_task('generation.generar_clientes')  # Primera tarea
    task2 = app.send_task('generation.generar_transacciones', args=[task1.get()])  # Segunda tarea
    task3 = app.send_task('generation.consolidar_archivos', args=[task2.get()])  # Tercera tarea

    # Esperar el resultado de la última tarea
    print(f"Resultado de la tarea final: {task3.get()}")

ejecutar_flujo()
