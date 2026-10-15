import uuid
from sqlalchemy.dialects.postgresql import UUID
from ..extensions.extension import db


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": str(self.id),     
            "nombre": self.nombre,
            "precio": self.precio,
        }