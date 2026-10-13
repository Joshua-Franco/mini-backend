from decimal import Decimal

from sqlalchemy import select

from src.extensions import db
from src.models import Product

# Productos de ejemplo; cada imagen se sirve como archivo estático por separado.
SEED_PRODUCTS = [
    {
        "name": "ROG Strix RTX 4090 OC Edition 24GB",
        "price": "8499",
        "image_filename": "product-101.jpg",
    },
    {
        "name": 'Laptop Gamer ASUS ROG Strix G16 16" 240Hz',
        "price": "7499",
        "image_filename": "product-102.jpg",
    },
    {
        "name": "Procesador AMD Ryzen 7 7800X3D (AM5)",
        "price": "1649",
        "image_filename": "product-103.jpg",
    },
    {
        "name": 'Monitor Curved OLED 34" Samsung Odyssey G8 175Hz',
        "price": "3899",
        "image_filename": "product-104.jpg",
    },
    {
        "name": 'Laptop Lenovo Legion Pro 5 16" WQXGA',
        "price": "5699",
        "image_filename": "product-105.jpg",
    },
    {
        "name": "Procesador Intel Core i9-14900K 24-Cores",
        "price": "2299",
        "image_filename": "product-106.jpg",
    },
    {
        "name": "SSD M.2 NVMe Samsung 990 PRO 2TB PCIe 4.0",
        "price": "599",
        "image_filename": "product-107.jpg",
    },
    {
        "name": "Teclado Mecánico Custom Wireless RGB Red Switches",
        "price": "349",
        "image_filename": "product-108.jpg",
    },
]


def seed_products() -> None:
    """Carga los ejemplos solo cuando la tabla de productos está vacía."""
    # Las filas desactivadas también impiden que los ejemplos se carguen otra vez.
    existing = db.session.execute(select(Product.id).limit(1)).first()
    if existing:
        return

    # Convierte precios de texto a Decimal para conservar precisión monetaria.
    db.session.add_all(
        [
            Product(
                **{
                    **product,
                    "price": Decimal(product["price"]),
                }
            )
            for product in SEED_PRODUCTS
        ]
    )
    db.session.commit()
