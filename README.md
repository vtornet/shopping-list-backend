 # Shopping List Backend API

  Backend FastAPI para la aplicación de Lista de Compras.

  ## Características

  - Base de datos PostgreSQL
  - API REST con FastAPI
  - Sincronización de listas de compra
  - Gestión de items y listas compartidas

  ## Endpoints

  ### Health Check
  - `GET /` - Estado del API
  - `GET /health` - Health check

  ### Listas
  - `GET /lists?user_id={uid}` - Obtener listas de un usuario
  - `POST /lists` - Crear nueva lista
  - `PUT /lists/{id}` - Actualizar lista
  - `DELETE /lists/{id}` - Eliminar lista
  - `POST /lists/{id}/members?email={email}` - Añadir miembro

  ### Items
  - `GET /items?list_id={id}` - Obtener items de una lista
  - `POST /items` - Crear nuevo item
  - `PUT /items/{id}` - Actualizar item
  - `DELETE /items/{id}` - Eliminar item
  - `PUT /items/batch` - Actualizar múltiples items

  ## Despliegue en Railway

  Este repositorio está configurado para desplegarse automáticamente en Railway.

  ## Variables de Entorno

  - `DATABASE_URL` - URL de conexión a PostgreSQL (Railway la inyecta automáticamente)