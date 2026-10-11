from src.extensions import db


class User(db.Model):
    """Representa una cuenta de cliente con una contraseña almacenada como hash."""

    __tablename__ = "users"

    # El correo único permite identificar cuentas sin duplicados.
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    # Guarda el resultado de bcrypt, nunca la contraseña original.
    password_hash = db.Column(db.String(256), nullable=False)

    def to_dict(self) -> dict[str, int | str]:
        """Devuelve solo campos públicos, nunca el hash de la contraseña."""
        return {"id": self.id, "name": self.name, "email": self.email}
