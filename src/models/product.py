import uuid

from sqlalchemy import Uuid

from src.extensions import db


class Product(db.Model):
    """Representa un producto y los datos necesarios para mostrarlo en la tienda."""

    # Usa el nombre solicitado para la tabla del catálogo.
    __tablename__ = "productos"

    # Cada producto tiene un identificador UUID independiente de su orden visual.
    id = db.Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sort_order = db.Column(db.Integer, nullable=False, unique=True)
    name = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(40), nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    old_price = db.Column(db.Numeric(10, 2), nullable=True)
    badge = db.Column(db.String(80), nullable=False, default="")
    icon = db.Column(db.String(80), nullable=False, default="fa-box")
    specs = db.Column(db.String(500), nullable=False, default="")
    image_filename = db.Column(db.String(180), nullable=False)

    def to_dict(self, image_url: str) -> dict[str, str | int | float | None]:
        """Devuelve los campos públicos en el formato esperado por la website."""
        return {
            "id": str(self.id),
            "name": self.name,
            "category": self.category,
            "price": float(self.price),
            "oldPrice": float(self.old_price) if self.old_price is not None else None,
            "badge": self.badge,
            "icon": self.icon,
            "specs": self.specs,
            "image": image_url,
        }
