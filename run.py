import os

# Importa la fábrica de la aplicación y los pasos de inicialización del catálogo.
from src import create_app
from src.extensions import db
from src.seed import seed_products

# Crea la aplicación una vez para usarla al iniciar el servidor.
app = create_app()


if __name__ == "__main__":
    # Exige una conexión PostgreSQL válida antes de iniciar el servidor.
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]
    if not database_url.startswith("postgresql+psycopg://"):
        raise RuntimeError("Configura DATABASE_URL con una URL PostgreSQL en el archivo .env.")
    if "CAMBIA_TU_PASSWORD" in database_url:
        raise RuntimeError("Reemplaza CAMBIA_TU_PASSWORD en DATABASE_URL dentro del archivo .env.")

    # Crea el esquema e inserta el catálogo inicial en la base PostgreSQL configurada.
    with app.app_context():
        db.create_all()
        seed_products()

    # Permite ajustar host y puerto con variables de entorno.
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "6072")),
        debug=app.config["DEBUG"],
    )
