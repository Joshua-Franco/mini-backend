from decimal import Decimal

from sqlalchemy import select

from src.extensions import db
from src.models import Product

# Datos iniciales; la imagen se guarda aparte y aquí solo se registra su nombre.
SEED_PRODUCTS = [
    {
        "sort_order": 1,
        "name": "ROG Strix RTX 4090 OC Edition 24GB",
        "category": "gpu",
        "price": "8499",
        "old_price": "9299",
        "badge": "Oferta Flash",
        "icon": "fa-microchip",
        "specs": "24GB GDDR6X | Ray Tracing | DLSS 3.5",
        "image_filename": "product-101.jpg",
    },
    {
        "sort_order": 2,
        "name": 'Laptop Gamer ASUS ROG Strix G16 16" 240Hz',
        "category": "laptop",
        "price": "7499",
        "old_price": "8199",
        "badge": "-S/ 700 OFF",
        "icon": "fa-laptop",
        "specs": "Intel i9-14900HX | RTX 4070 8GB | 32GB RAM | 1TB SSD",
        "image_filename": "product-102.jpg",
    },
    {
        "sort_order": 3,
        "name": "Procesador AMD Ryzen 7 7800X3D (AM5)",
        "category": "cpu",
        "price": "1649",
        "old_price": "1849",
        "badge": "Top Ventas",
        "icon": "fa-microchip",
        "specs": "8 Núcleos | 16 Hilos | 3D V-Cache",
        "image_filename": "product-103.jpg",
    },
    {
        "sort_order": 4,
        "name": 'Monitor Curved OLED 34" Samsung Odyssey G8 175Hz',
        "category": "monitor",
        "price": "3899",
        "old_price": "4299",
        "badge": "OLED QHD",
        "icon": "fa-desktop",
        "specs": "0.03ms Respuesta | HDR True Black 400",
        "image_filename": "product-104.jpg",
    },
    {
        "sort_order": 5,
        "name": 'Laptop Lenovo Legion Pro 5 16" WQXGA',
        "category": "laptop",
        "price": "5699",
        "old_price": "6199",
        "badge": "Popular",
        "icon": "fa-laptop",
        "specs": "Ryzen 7 7745HX | RTX 4060 8GB | 16GB RAM",
        "image_filename": "product-105.jpg",
    },
    {
        "sort_order": 6,
        "name": "Procesador Intel Core i9-14900K 24-Cores",
        "category": "cpu",
        "price": "2299",
        "old_price": "2499",
        "badge": "LGA1700",
        "icon": "fa-microchip",
        "specs": "Hasta 6.0 GHz Turbo | 32 Hilos",
        "image_filename": "product-106.jpg",
    },
    {
        "sort_order": 7,
        "name": "SSD M.2 NVMe Samsung 990 PRO 2TB PCIe 4.0",
        "category": "storage",
        "price": "599",
        "old_price": "689",
        "badge": "7450 MB/s",
        "icon": "fa-hard-drive",
        "specs": "Lectura Ultra Rápida | Compatible con PS5 y PC",
        "image_filename": "product-107.jpg",
    },
    {
        "sort_order": 8,
        "name": "Teclado Mecánico Custom Wireless RGB Red Switches",
        "category": "peripherals",
        "price": "349",
        "old_price": "399",
        "badge": "Hot-Swap",
        "icon": "fa-keyboard",
        "specs": "Bluetooth / 2.4Ghz | Batería 4000mAh",
        "image_filename": "product-108.jpg",
    },
]


def seed_products() -> None:
    """Carga el catálogo de demostración solo cuando la tabla está vacía."""
    existing = db.session.execute(select(Product.id).limit(1)).first()
    if existing:
        return

    db.session.add_all(
        [
            Product(
                **{
                    **product,
                    "price": Decimal(product["price"]),
                    "old_price": Decimal(product["old_price"]),
                }
            )
            for product in SEED_PRODUCTS
        ]
    )
    db.session.commit()
