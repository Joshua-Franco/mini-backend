# Backend NovaTech

API Flask para entregar a la website el catálogo, sus datos y las imágenes de los productos.

## Preparar el entorno

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

El backend utiliza PostgreSQL y Psycopg, y no crea una carpeta `instance`. Configura en `.env` la contraseña del usuario PostgreSQL. Si contiene caracteres especiales, codifícalos para URL.

La base PostgreSQL se llama `mini-ecomerce-games`. Si todavía no existe, créala desde pgAdmin o `psql` antes de iniciar el backend:

```sql
CREATE DATABASE "mini-ecomerce-games";
```

Las tablas del backend se crean al iniciar el servidor. En bases existentes, el inicio agrega la columna `activado` a `productos` y marca como activos los productos ya guardados. Los ocho productos iniciales se cargan únicamente si la tabla está vacía; los productos desactivados permanecen en ella y no hacen que se carguen de nuevo. Antes de iniciar, configura en `.env` una clave JWT aleatoria y secreta. Por ejemplo, puedes generar una localmente con `py -c "import secrets; print(secrets.token_urlsafe(48))"` y asignarla a `JWT_SECRET_KEY`. Nunca publiques esa clave.

`JWT_ACCESS_TOKEN_SECONDS` controla la vigencia del token (por defecto, 1800 segundos). Flask-JWT-Extended firma y verifica los tokens; bcrypt genera y comprueba hashes de contraseñas. Las contraseñas se limitan a 72 bytes para evitar que bcrypt las trunque. Pydantic valida los datos de entrada. El frontend conserva el token solo en memoria, por lo que se pierde la sesión al recargar la página. El cierre de sesión descarta el token del navegador; al ser JWT sin estado, un token copiado sigue siendo válido hasta que venza.

Para habilitar la administración del catálogo, registra primero la cuenta administradora y luego configura `ADMIN_EMAILS` con su correo. Se aceptan varios correos separados por comas. Reinicia o despliega el backend después de configurar la variable. Los correos listados quedan reservados y no se pueden registrar o reclamar cambiando el correo de una cuenta normal.

## Iniciar el servidor

Para desarrollo local:

```powershell
py run.py
```

Para Render, configura el Start Command como:

```text
gunicorn run:app
```

En ambos casos, la aplicación crea las tablas y carga los ocho productos iniciales si el catálogo está vacío. La tabla almacena los datos y el nombre de cada imagen; los archivos JPG se conservan en `src/static/images` y Flask los entrega al frontend. En local, la API está disponible en `http://127.0.0.1:6072/api/products`.

La website en `C:\Users\joshu\Music\website\mini-ecomerce-games` usa el backend desplegado por defecto. Iníciala con `pnpm dev`; estará disponible en `http://localhost:5475`. Si el backend está en otro host, define `VITE_API_URL` en el entorno de Vite, incluyendo el prefijo `/api`. Agrega el origen exacto de la website a `FRONTEND_ORIGINS` si no coincide con los valores locales predeterminados.

## Endpoints

- `GET /`: confirma que el servidor está disponible con `{"server":"okay"}`.
- `GET /api/images`: lista los archivos de imagen disponibles con sus URLs públicas.
- `GET /api/products`: lista únicamente productos activos, ordenados por nombre.
- `GET /api/products/<uuid>`: consulta un producto activo; los desactivados responden como no encontrados.
- `POST /api/products`: crea un producto; requiere JWT de una cuenta incluida en `ADMIN_EMAILS`.
- `PUT /api/products/<uuid>`: reemplaza los datos del producto; requiere permisos de administrador.
- `DELETE /api/products/<uuid>`: desactiva el producto sin borrarlo de PostgreSQL; requiere permisos de administrador. Un producto ya desactivado responde como no encontrado.
- `POST /api/auth/register`: registra nombre, correo y contraseña; crea una cuenta y entrega un JWT.
- `POST /api/auth/login`: valida correo y contraseña, y entrega un JWT.
- `GET /api/auth/me`: devuelve la cuenta asociada al JWT enviado con un encabezado `Authorization: Bearer`.
- `PATCH /api/auth/me`: actualiza el nombre o correo de la cuenta autenticada; requiere JWT.
- `DELETE /api/auth/me`: elimina la cuenta autenticada con su contraseña actual; requiere JWT.
- `GET /static/images/<archivo>`: sirve las imágenes almacenadas en `src/static/images`.

Crear, editar y desactivar productos requiere un JWT válido de una cuenta existente cuyo correo esté en `ADMIN_EMAILS`; las cuentas registradas que no estén autorizadas reciben `403`, y las solicitudes sin un token válido reciben `401`. Las solicitudes de escritura requieren `name`, `price` e `imageFilename`. El archivo de imagen debe existir en `src/static/images`. Las respuestas de producto incluyen `id` UUID, `name`, `price`, `activado`, `imageFilename` e `image` (URL absoluta de la imagen). `activado` se establece en `true` al crear un producto; no se puede cambiar mediante el payload de escritura.
