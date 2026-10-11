import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Valida formato básico sin requerir dependencias adicionales de correo.
EMAIL_PATTERN = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}")


class AuthPayload(BaseModel):
    """Campos compartidos por registro e inicio de sesión."""

    # Rechaza conversiones implícitas y propiedades no esperadas en el JSON.
    model_config = ConfigDict(strict=True, extra="forbid")

    email: str = Field(max_length=254)
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        """Normaliza el correo para que mayúsculas y espacios no creen otra cuenta."""
        return value.strip().casefold() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.fullmatch(value):
            raise ValueError("ingresa un correo válido")
        return value

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(cls, value: str) -> str:
        """Evita el truncamiento de contraseñas que bcrypt limita a 72 bytes."""
        if not value:
            raise ValueError("la contraseña es obligatoria")
        if len(value.encode("utf-8")) > 72:
            raise ValueError("la contraseña no puede superar 72 bytes")
        return value


class RegisterPayload(AuthPayload):
    """Valida los campos adicionales y la fortaleza del registro."""

    name: str = Field(min_length=2, max_length=120)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        """Quita espacios sobrantes del nombre antes de validar su longitud."""
        return value.strip() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Exige longitud mínima y al menos una letra y un número."""
        if len(value) < 8 or not any(character.isalpha() for character in value) or not any(
            character.isdigit() for character in value
        ):
            raise ValueError("usa al menos 8 caracteres, con letras y números")
        return value


class LoginPayload(AuthPayload):
    """Valida las credenciales requeridas para iniciar sesión."""

    pass


class ProfileUpdatePayload(BaseModel):
    """Valida cambios parciales al nombre o correo de una cuenta."""

    model_config = ConfigDict(strict=True, extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=120)
    email: str | None = Field(default=None, max_length=254)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().casefold() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is not None and not EMAIL_PATTERN.fullmatch(value):
            raise ValueError("ingresa un correo válido")
        return value

    @model_validator(mode="after")
    def require_changes(self):
        if self.name is None and self.email is None:
            raise ValueError("indica un nombre o correo para actualizar")
        return self


class DeleteAccountPayload(BaseModel):
    """Exige la contraseña actual para confirmar la eliminación de la cuenta."""

    model_config = ConfigDict(strict=True, extra="forbid")

    password: str = Field(min_length=1)

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("la contraseña no puede superar 72 bytes")
        return value


class ProductPayload(BaseModel):
    """Valida los datos completos que se crean o reemplazan en el catálogo."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    sort_order: int = Field(alias="sortOrder", gt=0)
    name: str = Field(min_length=1, max_length=180)
    category: str = Field(min_length=1, max_length=40)
    price: float = Field(gt=0, allow_inf_nan=False)
    old_price: float | None = Field(default=None, alias="oldPrice", gt=0, allow_inf_nan=False)
    badge: str = Field(default="", max_length=80)
    icon: str = Field(default="fa-box", min_length=1, max_length=80)
    specs: str = Field(default="", max_length=500)
    image_filename: str = Field(alias="imageFilename", min_length=1, max_length=180)

    @field_validator("name", "category", "icon", "image_filename", mode="before")
    @classmethod
    def trim_required_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("badge", "specs", mode="before")
    @classmethod
    def trim_optional_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("image_filename")
    @classmethod
    def validate_image_filename(cls, value: str) -> str:
        if value in {".", ".."} or not re.fullmatch(r"[A-Za-z0-9._-]+", value):
            raise ValueError("el nombre de imagen solo puede contener letras, números, puntos, guiones o guiones bajos")
        return value
