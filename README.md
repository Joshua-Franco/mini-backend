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

La tabla `productos` y sus ocho registros iniciales se crean al iniciar el servidor. Las pruebas automatizadas no están incluidas en este proyecto.

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

La website configurada en `C:\Users\joshu\Desktop\mini-ecomerce-games` usa esa URL por defecto. Iníciala con `pnpm dev`; estará disponible en `http://localhost:5475`. Si el backend está en otro host, define `VITE_API_URL` en el entorno de Vite, incluyendo el prefijo `/api`.

## Endpoints

- `GET /api/products`: lista el catálogo; acepta `?category=gpu` y `?category=all`.
- `GET /api/products/<uuid>`: consulta un producto.
- `GET /static/images/<archivo>`: sirve las imágenes almacenadas en `src/static/images`.

Las respuestas de producto incluyen `id` UUID, `name`, `category`, `price`, `oldPrice`, `badge`, `icon`, `specs` e `image` (URL absoluta de la imagen).
