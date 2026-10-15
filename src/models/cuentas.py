import uuid
from sqlalchemy.dialects.postgresql import UUID
import bcrypt
from ..extensions.extension import db


class Cuenta(db.Model):
    __tablename__ = 'cuentas'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.contrasena = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.contrasena.encode("utf-8")
        )

    def to_dict(self, access_token):
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "email": self.email,
            "access_token": access_token
        }