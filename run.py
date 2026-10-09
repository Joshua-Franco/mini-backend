import os

# Importa la fábrica de la aplicación.
from src import create_app

# Crea la aplicación una vez para usarla al iniciar el servidor.
app = create_app()


if __name__ == "__main__":
    # Exige una conexión PostgreSQL válida antes de iniciar el servidor.
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]
    if not database_url.startswith("postgresql+psycopg://"):
        raise RuntimeError("Configura DATABASE_URL con una URL PostgreSQL en el archivo .env.")

    # Permite ajustar host y puerto durante el desarrollo local.
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "6072")),
        debug=app.config["DEBUG"],
    )
