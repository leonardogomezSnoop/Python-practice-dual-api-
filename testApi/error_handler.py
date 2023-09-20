
import requests
import datetime

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
    except:
        log_local_error(f"Failed to log error remotely. Description: {description}")
        pass

# log para guardar errores locales
def log_local_error(error_message):
    try:
        with open("error_log.txt", "a") as log_file:
            log_file.write(f"Error: {error_message}\n")
    except Exception as e:
        print(f"Error al registrar el error localmente: {str(e)}")