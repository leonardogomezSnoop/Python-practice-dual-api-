from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyodbc
from error_handler import log_error, log_local_error
app = FastAPI()


# Abrir una conexión a la base de datos 
try:
    connection_string=('DRIVER={SQL Server};SERVER=DESKTOP-590PN4I;DATABASE=python_app;Trusted_Connection=yes')
    conn = pyodbc.connect(connection_string)
    print('conexion exitosa')
except Exception as ex:
    print(ex)



class Item(BaseModel):
    name: str
    description: str


class User(BaseModel):
    username: str



##########################################ENDPOINTS###########################################################
@app.post("/users/")
async def create_user(user: User):
    cursor = conn.cursor()
    if user.username == "":
        log_error(
            "empty username", es_maestro_error=True, es_sap_error=False
        )
        raise HTTPException(status_code=404, detail="empty username")

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
