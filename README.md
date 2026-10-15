# Mini backend

API REST construida con Flask para gestionar cuentas y productos. Usa PostgreSQL como base de datos y SQLAlchemy para el acceso a los datos.

## Requisitos

- Python.
- PostgreSQL.

## Instalación y configuración

Desde PowerShell, en la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Crea una base de datos PostgreSQL y configura `.env` con sus datos de conexión. Por ejemplo:

```dotenv
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/mini-ecomerce-games
PORT=6072
FLASK_DEBUG=true
FRONTEND_ORIGINS=http://localhost:5475,http://127.0.0.1:5475
```

`DATABASE_URL` debe apuntar a una base de datos existente y `PORT` es obligatorio. Si la contraseña contiene caracteres especiales, codifícalos para URL. Al iniciar, la aplicación crea las tablas `cuentas` y `productos` si todavía no existen; no carga productos iniciales ni modifica el esquema de tablas existentes.

## Iniciar

```powershell
py run.py
```

El servidor escucha en `http://127.0.0.1:6072` con la configuración de ejemplo. La comprobación de estado está en `/`.

## Endpoints

Las rutas no tienen el prefijo `/api`.

| Método | Ruta | Descripción | Acceso |
| --- | --- | --- | --- |
| `GET` | `/` | Comprueba que el servidor está activo. | Público |
| `GET` | `/productos` | Devuelve todos los productos. | Público |
| `POST` | `/productos` | Crea un producto. | Requiere JWT |
| `GET` | `/productos/<id>` | Busca un producto por ID. | Público |
| `PUT` | `/productos/<id>` | Actualiza datos de un producto. | Requiere JWT |
| `DELETE` | `/productos/<id>` | Elimina un producto. | Requiere JWT |
| `POST` | `/registro` | Registra una cuenta. | Público |
| `POST` | `/login` | Comprueba las credenciales e intenta emitir un JWT. | Público |
| `DELETE` | `/cuentas/<cuenta_id>` | Elimina la cuenta indicada. | Sin autenticación |

### Cuentas

Para registrar una cuenta, envía `nombre`, `email` y `password`:

```json
{
  "nombre": "Ana",
  "email": "ana@example.com",
  "password": "una-clave-segura"
}
```

El registro valida que el nombre tenga entre 1 y 20 caracteres, el correo tenga un formato de email básico y no supere 40 caracteres, y la contraseña tenga entre 8 y 34 caracteres. Las contraseñas se guardan con bcrypt. El endpoint responde con los datos públicos de la cuenta (`id`, `nombre` y `email`), sin emitir un token.

Para iniciar sesión, envía `email` y `contrasena`:

```json
{
  "email": "ana@example.com",
  "contrasena": "una-clave-segura"
}
```

Si las credenciales son válidas, la respuesta incluye `access_token` y `cuenta`. Los endpoints de escritura de productos requieren que envíes el token en el encabezado HTTP `Authorization` con el esquema Bearer.

### Productos

El formato de un producto es:

```json
{
  "id": "UUID",
  "nombre": "Teclado",
  "precio": 49.99
}
```

Para crear un producto, envía `nombre` y `precio`. Para actualizarlo, `PUT` acepta esos mismos campos; se pueden enviar solo los que se quieran cambiar. `precio` debe poder convertirse a número.

## Notas sobre el estado actual

- `DELETE /productos/<id>` borra el registro de la base de datos; no lo desactiva.
- `POST /login` genera tokens JWT, pero la configuración actual no asigna `JWT_SECRET_KEY` ni `SECRET_KEY`. Se debe configurar una clave secreta en la aplicación antes de que el inicio de sesión pueda emitir tokens.
- `DELETE /cuentas/<cuenta_id>` no requiere JWT y elimina la cuenta indicada por el ID.
- `FRONTEND_ORIGINS` se lee en la configuración, pero no se aplica a CORS en el código actual; la aplicación inicializa CORS con `CORS(app)`.
- `FLASK_DEBUG` se pasa directamente desde el entorno a Flask. Úsalo solo en desarrollo.
