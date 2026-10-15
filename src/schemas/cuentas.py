from pydantic import BaseModel, Field

class CuentaCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=20, description="Nombre de la cuenta")
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=40, description="Email")
    password: str = Field(min_length=8, max_length=34, description="Contraseña")