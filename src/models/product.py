import uuid

from sqlalchemy import Uuid, true

from src.extensions import db


class Product(db.Model):
    """Representa un producto y los datos necesarios para mostrarlo en la tienda."""

    # Usa el nombre solicitado para la tabla del catálogo.
    __tablename__ = "productos"

    # El UUID identifica al producto.
    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Datos visibles de cada producto.
    name = db.Column(db.String(180), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    activado = db.Column(db.Boolean, nullable=False, default=True, server_default=true())

    # La imagen es un archivo estático; la base solo guarda su nombre.
    image_filename = db.Column(db.String(180), nullable=False)

    def to_dict(self, image_url: str) -> dict[str, str | int | float | bool | None]:
        """Devuelve los campos públicos en el formato esperado por la website."""
        return {
            "id": str(self.id),
            "name": self.name,
            "price": float(self.price),
            "activado": self.activado,
            "imageFilename": self.image_filename,
            "image": image_url,
        }
