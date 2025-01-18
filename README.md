# Proyecto de Backend - Generador de PDFs - graphix-backend


Este proyecto es un sistema backend diseñado para gestionar usuarios temporales, generar y personalizar PDFs a través de un flujo de trabajo definido en etapas. Utiliza Django como framework principal, junto con librerías adicionales para la autenticación, generación de PDFs y vistas previas. También ofrece endpoints seguros para la interacción con los datos.

## Tecnologías principales
- **Django**: Framework principal del proyecto.
- **Django REST Framework (DRF)**: Para la construcción de APIs.
- **SimpleJWT**: Para autenticación basada en tokens.
- **WeasyPrint**: Para la generación de PDFs.
- **PDF2Image**: Para la conversión de PDFs en imágenes.
- **DRF Spectacular**: Para la documentación de la API.

## Instalación y configuración
1. Clona este repositorio.
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura las variables de entorno necesarias, como las credenciales de la base de datos y claves secretas de JWT.
5. Aplica las migraciones:
   ```bash
   python manage.py migrate
   ```
6. Inicia el servidor:
   ```bash
   python manage.py runserver
   ```

## Funcionalidades principales

### Módulo de Usuarios
#### Modelo
El modelo `CustomUser` extiende el modelo `AbstractUser` de Django para incluir los siguientes campos adicionales:
- `is_temporary`: Indica si el usuario es temporal.
- `package`: Plan del usuario (básico, medio o premium).
- `pdf_progress`: Progreso en el flujo de generación de PDFs.
- `page_limit`: Límite de páginas según el paquete seleccionado.
- `raw_password`: Contraseña generada para usuarios temporales.

#### Endpoints
1. **Crear usuario temporal**
   - **URL**: `/api/users/create-user/`
   - **Método**: `POST`
   - **Descripción**: Crea un usuario temporal con un plan específico y devuelve sus credenciales.
   - **Permisos**: Autenticado.

2. **Obtener información de un usuario**
   - **URL**: `/api/users/get-user/<int:pk>/`
   - **Método**: `GET`
   - **Descripción**: Retorna información sobre un usuario específico.
   - **Permisos**: Autenticado.

---

### Módulo de Generación de PDFs
#### Modelo
El modelo `GeneratedPDFModel` almacena información sobre los PDFs generados, incluyendo:
- Usuario asociado.
- Archivo PDF generado.
- Fecha de creación.

#### Serializador
El serializador `GeneratePDFSerializer` gestiona la validación y procesamiento de las etapas y contenido para la generación de PDFs.

#### Endpoints
1. **Generar vistas previas**
   - **URL**: `/api/pdf/generate-previews/`
   - **Método**: `POST`
   - **Descripción**: Genera vistas previas de las etapas del PDF.
   - **Permisos**: Autenticado.

2. **Confirmar y generar PDF**
   - **URL**: `/api/pdf/confirm-generate-pdf/`
   - **Método**: `POST`
   - **Descripción**: Genera el PDF final basado en las vistas previas confirmadas.
   - **Permisos**: Autenticado.

---

### Módulo de Etapas
#### Modelo
El modelo `StageDataModel` almacena datos específicos de cada etapa del flujo de generación de PDFs:
- Usuario asociado.
- Número de etapa (1 a 6).
- Contenido HTML.
- Cantidad de páginas asignadas.

#### Endpoints
1. **Guardar etapa**
   - **URL**: `/api/pdf/save/save-stage/`
   - **Método**: `POST`
   - **Descripción**: Crea o actualiza una etapa específica del usuario.
   - **Permisos**: Autenticado.

2. **Obtener etapas**
   - **URL**: `/api/pdf/save/save-stage/`
   - **Método**: `GET`
   - **Descripción**: Retorna las etapas del usuario actual.
   - **Permisos**: Autenticado.

---

### Autenticación
La autenticación está basada en **JSON Web Tokens (JWT)** usando `SimpleJWT`. Los endpoints disponibles son:
- `/token/login/`: Obtención de token de acceso y refresco.
- `/token/refresh/`: Refresco del token de acceso.

---

## Estructura de URLs
- **Usuarios**: `/api/users/`
- **Generación de PDFs**: `/api/pdf/`
- **Etapas**: `/api/pdf/save/`
- **Autenticación**:
  - Login: `/token/login/`
  - Refresh: `/token/refresh/`
- **Documentación**:
  - Esquema: `/api/schema/`
  - Swagger: `/api/schema/swagger/`

---

## Documentación de la API
La documentación interactiva de la API está disponible en Swagger:
- **URL**: `/api/schema/swagger/`

---

## TODO
Aun pendiente de integrar el manejo de reglamentos subiendolos a Google Drive y generando un QR para el PDF final.

---

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request en este repositorio.

---

## Licencia
Este proyecto está bajo la licencia [MIT](LICENSE).


