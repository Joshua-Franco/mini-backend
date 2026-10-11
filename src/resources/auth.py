import bcrypt
from flask import current_app, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Resource
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.extensions import db
from src.models import User
from src.resources.auth_schemas import (
    DeleteAccountPayload,
    LoginPayload,
    ProfileUpdatePayload,
    RegisterPayload,
)


def validate_payload(
    schema: type[RegisterPayload] | type[LoginPayload] | type[ProfileUpdatePayload] | type[DeleteAccountPayload],
):
    """Valida el JSON y convierte errores de Pydantic en respuestas HTTP 400."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, {"error": "Envía los datos en formato JSON."}, 400

    try:
        return schema.model_validate(data), None, None
    except ValidationError as error:
        # Conserva nombres de campos y mensajes para ayudar a corregir la solicitud.
        messages = [
            f"{'.'.join(str(part) for part in item['loc'])}: {item['msg']}"
            for item in error.errors(include_url=False)
        ]
        return None, {"error": " ".join(messages)}, 400


def auth_response(user: User, status: int):
    """Emite un JWT y devuelve la cuenta sin exponer su hash de contraseña."""
    expires_in = int(current_app.config["JWT_ACCESS_TOKEN_SECONDS"])
    return {
        "access_token": create_access_token(identity=str(user.id)),
        "token_type": "Bearer",
        "expires_in": expires_in,
        "user": public_user(user),
    }, status


def public_user(user: User) -> dict[str, int | str | bool]:
    """Incluye la capacidad administrativa sin exponer datos privados."""
    return {
        **user.to_dict(),
        "isAdmin": user.email in current_app.config["ADMIN_EMAILS"],
    }


def get_token_user() -> User | None:
    """Busca la cuenta asociada al token ya verificado por Flask-JWT-Extended."""
    identity = get_jwt_identity()
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None
    return db.session.get(User, user_id)


class RegisterResource(Resource):
    def post(self):
        # No crear cuentas si el servidor no puede emitir sus tokens de acceso.
        if not current_app.config.get("JWT_SECRET_KEY"):
            return {"error": "La autenticación no está configurada en el servidor."}, 503

        payload, validation_error, status = validate_payload(RegisterPayload)
        if validation_error:
            return validation_error, status
        assert isinstance(payload, RegisterPayload)
        name, email, password = payload.name, payload.email, payload.password

        # No permite reclamar por registro público un correo reservado para administración.
        if email in current_app.config["ADMIN_EMAILS"]:
            return {"error": "Esta cuenta administrativa debe existir antes de configurar ADMIN_EMAILS."}, 403

        existing_user = db.session.execute(
            select(User.id).where(User.email == email)
        ).scalar_one_or_none()
        if existing_user is not None:
            return {"error": "Ya existe una cuenta con ese correo."}, 409

        user = User(
            name=name,
            email=email,
            # bcrypt genera y almacena la sal junto con el hash.
            password_hash=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii"),
        )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            # La restricción única también cubre registros simultáneos del mismo correo.
            db.session.rollback()
            existing_user = db.session.execute(
                select(User.id).where(User.email == email)
            ).scalar_one_or_none()
            if existing_user is not None:
                return {"error": "Ya existe una cuenta con ese correo."}, 409
            raise

        return auth_response(user, 201)


class LoginResource(Resource):
    def post(self):
        # La validación de credenciales precede a cualquier consulta o hash.
        if not current_app.config.get("JWT_SECRET_KEY"):
            return {"error": "La autenticación no está configurada en el servidor."}, 503

        payload, validation_error, status = validate_payload(LoginPayload)
        if validation_error:
            return validation_error, status
        assert isinstance(payload, LoginPayload)

        user = db.session.execute(
            select(User).where(User.email == payload.email)
        ).scalar_one_or_none()
        if user is None or not bcrypt.checkpw(
            payload.password.encode("utf-8"),
            user.password_hash.encode("ascii"),
        ):
            return {"error": "Correo o contraseña incorrectos."}, 401

        return auth_response(user, 200)


class CurrentUserResource(Resource):
    def get_current_user(self) -> User | tuple[dict[str, str], int]:
        """Resuelve el usuario autenticado o devuelve un error de autorización."""
        user = get_token_user()
        if user is None:
            return {"error": "La cuenta asociada al token ya no existe."}, 401
        return user

    @jwt_required()
    def get(self):
        # Flask-JWT-Extended verifica firma y vencimiento antes de entrar aquí.
        user = self.get_current_user()
        if isinstance(user, tuple):
            return user
        return {"user": public_user(user)}, 200

    @jwt_required()
    def patch(self):
        user = self.get_current_user()
        if isinstance(user, tuple):
            return user

        payload, validation_error, status = validate_payload(ProfileUpdatePayload)
        if validation_error:
            return validation_error, status
        assert isinstance(payload, ProfileUpdatePayload)

        if payload.email is not None and payload.email != user.email:
            if payload.email in current_app.config["ADMIN_EMAILS"] and user.email not in current_app.config["ADMIN_EMAILS"]:
                return {"error": "No puedes cambiar tu correo a una cuenta administrativa."}, 403
            existing_user = db.session.execute(
                select(User.id).where(User.email == payload.email, User.id != user.id)
            ).scalar_one_or_none()
            if existing_user is not None:
                return {"error": "Ya existe una cuenta con ese correo."}, 409
            user.email = payload.email
        if payload.name is not None:
            user.name = payload.name

        try:
            db.session.commit()
        except IntegrityError:
            # La restricción única cubre cambios simultáneos al mismo correo.
            db.session.rollback()
            existing_user = db.session.execute(
                select(User.id).where(User.email == payload.email, User.id != user.id)
            ).scalar_one_or_none()
            if existing_user is not None:
                return {"error": "Ya existe una cuenta con ese correo."}, 409
            raise

        return {"user": public_user(user)}, 200

    @jwt_required()
    def delete(self):
        user = self.get_current_user()
        if isinstance(user, tuple):
            return user

        payload, validation_error, status = validate_payload(DeleteAccountPayload)
        if validation_error:
            return validation_error, status
        assert isinstance(payload, DeleteAccountPayload)

        if not bcrypt.checkpw(
            payload.password.encode("utf-8"),
            user.password_hash.encode("ascii"),
        ):
            return {"error": "La contraseña es incorrecta."}, 401

        db.session.delete(user)
        db.session.commit()
        return {"message": "La cuenta fue eliminada."}, 200
