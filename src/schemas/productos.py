from pydantic import BaseModel, Field

class ProductoSchema(BaseModel):
    nombre: str = Field(min_length=1, max_length=30, description="Nombre del producto")
    precio: float = Field(min_length=1, description="Precio del producto")
