from src.extensions import db


class CatalogSeedState(db.Model):
    """Registra que los productos de ejemplo ya se inicializaron una vez."""

    __tablename__ = "catalog_seed_state"

    key = db.Column(db.String(40), primary_key=True)
