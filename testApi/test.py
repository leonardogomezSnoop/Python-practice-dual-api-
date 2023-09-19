from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import requests
import datetime

app = FastAPI()


# Abrir una conexión a la base de datos en memoria
conn = sqlite3.connect("mi_basededatos.db")

# Crear una tabla de ejemplo en la base de datos
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT
    )
"""
)

# Crear una tabla de usuarios
conn.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT
    )
"""
)

conn.execute(
    """
    CREATE TABLE IF NOT EXISTS user_items (
        user_id INTEGER,
        item_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (item_id) REFERENCES items (id)
    )
"""
)


class Item(BaseModel):
    name: str
    description: str


class User(BaseModel):
    username: str

# log de errores de la api 2
def log_error(description, es_maestro_error, es_sap_error):
    try:
        current_datetime = datetime.datetime.now()
        error_data = {
            "description": description,
            "es_maestro_error": es_maestro_error,
            "es_sap_error": es_sap_error,
            "fecha_insert": current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        # utiliza el puerto 8001 la api de errores
        response = requests.post("http://localhost:8001/log-error", json=error_data)
        if response.status_code != 200:
         log_local_error(f"Failed to log error remotely. Description: {description}")
    except Exception as e:
        log_local_error(f"Failed to log error remotely. Description: {description}")
        pass

# log para guardar errores locales
def log_local_error(error_message):
    try:
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error: {error_message}\n")
    except Exception as e:
        print(f"Error al registrar el error localmente: {str(e)}")


@app.post("/users/")
async def create_user(user: User):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username) VALUES (?)", (user.username,))
    conn.commit()
    return {"username": user.username}


@app.post("/items/")
async def create_item(item: Item):
    cursor = conn.cursor()
    if item.name == "" or item.description == "":
        # metodo para guardar el error en la api 2
        log_error(
            "Empty description or name", es_maestro_error=True, es_sap_error=False
        )
        raise HTTPException(status_code=404, detail="Empty description or name")
    cursor.execute(
        "INSERT INTO items (name, description) VALUES (?, ?)",
        (item.name, item.description),
    )
    conn.commit()
    return {"item insert success  " "name": item.name, "description": item.description}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    # Realizar consultas en la base de datos aquí
    # Por ejemplo, aquí puedes buscar y devolver datos de la tabla "items"
    cursor = conn.cursor()
    cursor.execute("SELECT name, description FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    name, description = item
    return {"item_id": item_id, "name": name, "description": description}


@app.post("/user-items/")
async def create_user_item(user_id: int, item_id: int):
    cursor = conn.cursor()

    # Verificar si el usuario con user_id existe
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar si el elemento con item_id existe
    cursor.execute("SELECT id FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="item no encontrado")

    cursor.execute(
        "INSERT INTO user_items (user_id, item_id) VALUES (?, ?)", (user_id, item_id)
    )
    conn.commit()
    return {"status": "success", "user_id": user_id, "item_id": item_id}
