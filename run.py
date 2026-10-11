import os

# Importa la fábrica de la aplicación.
# Importa la fábrica que configura extensiones y rutas del backend.
from src import create_app

# Gunicorn importa esta instancia; al ejecutar el archivo se inicia el servidor local.
app = create_app()


if __name__ == "__main__":
    # Exige una conexión PostgreSQL válida antes de iniciar el servidor.
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]
    if not database_url.startswith("postgresql+psycopg://"):
        raise RuntimeError("Configura DATABASE_URL con una URL PostgreSQL en el archivo .env.")

    # Host, puerto y modo de depuración se pueden ajustar con variables de entorno.
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "6072")),
        debug=app.config["DEBUG"],
    )
