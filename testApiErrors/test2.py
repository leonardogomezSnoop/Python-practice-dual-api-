from fastapi import FastAPI
import sqlite3

app = FastAPI()

conn = sqlite3.connect("baseerrors.db")
cursor = conn.cursor()
cursor.execute(
    """
   CREATE TABLE IF NOT EXISTS log_Errores (
    id INTEGER PRIMARY KEY,
    Descripcion TEXT,
    Fecha_Insert TIMESTAMP,
    Es_MaestroError BOOLEAN,
    Es_SapError BOOLEAN
    )
"""
)

@app.post("/log-error")
async def log_error(error_data: dict):
    try:
        descripcion = error_data["description"]
        fecha_insert = error_data.get("fecha_insert")
        es_maestro_error = error_data.get("es_maestro_error", False)
        es_sap_error = error_data.get("es_sap_error", False)

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO log_Errores (Descripcion, Fecha_Insert, Es_MaestroError, Es_SapError) VALUES (?, ?, ?, ?)",
            (descripcion, fecha_insert, es_maestro_error, es_sap_error)
        )
        conn.commit()

        return {"message": "Error registrado con éxito"}
    except Exception as e:
        # Manejar errores al registrar el error en la base de datos, si es necesario
        return {"error": "No se pudo registrar el error", "detail": str(e)}