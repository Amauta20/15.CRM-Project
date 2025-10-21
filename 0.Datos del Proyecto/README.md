# CRM de Propuestas y Proyectos — Desktop (PyQt6)

## 🧭 Descripción
CRM de escritorio en **Python + PyQt6** para gestionar **leads y clientes**, **propuestas → proyectos**, y una **base de conocimiento** con documentos en **Google Drive**. 
Incluye **Hub de Mensajería**, **Gestor de Actividades con Outlook (Microsoft Graph)**, **Checklists por proyecto**, **búsqueda global (FTS5)**, **auditoría**, **soft delete**, **instalador Inno Setup** y **auto-update** desde Google Drive.

> No es una herramienta PMO; está centrado en trazabilidad y conocimiento.

## 🏗️ Arquitectura
- **Lenguaje:** Python 3.11+  
- **UI:** PyQt6 (Qt Widgets/QML, MVVM/MVP)  
- **BD:** SQLite (WAL + FTS5)  
- **ORM:** SQLAlchemy + Alembic  
- **Integraciones:** Google Drive API v3, Microsoft Graph (Calendars.ReadWrite)  
- **Seguridad:** Argon2, AES-GCM (Fernet), auditoría completa, soft delete  
- **Empaquetado:** PyInstaller + Inno Setup  
- **CI/CD:** GitHub Actions (lint, tests, build, release → Drive)

## 📂 Estructura del Proyecto
```
/app
  /ui            # Interfaces PyQt6
  /core          # Casos de uso y servicios
  /data          # SQLAlchemy, Alembic, FTS5
  /drive         # Google Drive API
  /activities    # Microsoft Graph + .ics
  /messaging     # Deep-links + plantillas
  /checklists    # Checklists por proyecto
  /campaigns     # Renovaciones/mantenimientos
  /audit         # Auditoría
  /auth          # Login, roles, cifrado
  /config        # Config segura (pydantic + cifrado)
  /update        # Auto-update (manifest.json)
  /tests         # PyTest (unit/integración/UI)
  /installer     # PyInstaller + Inno Setup
/docs
```

## ⚙️ Configuración Rápida (dev)
1. **Python & venv**
```bash
python -m venv .venv
.\.venv\Scriptsctivate
pip install -U pip
pip install -r requirements.txt
```
2. **Base de datos**
```bash
alembic upgrade head
```
3. **Variables de entorno (.env)**
```env
APP_ENV=dev
SQLITE_DB_PATH=C:\DriveCRM\db\crm.db

# Google Drive
DRIVE_MODE=service_account
DRIVE_ROOT_FOLDER_ID=xxxxxxxxxxxxxxxx
GOOGLE_SERVICE_ACCOUNT_JSON=C:\secrets\sa.json

# Outlook (Microsoft Graph)
MSAL_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MSAL_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MSAL_REDIRECT_URI=http://localhost:53100
MSAL_SCOPES=Calendars.ReadWrite

# Crypto
FERNET_MASTER_KEY_BASE64=
```

## ▶️ Ejecutar
```bash
python -m app.ui
```

## 🧩 Funcionalidades Clave
- Fases CRM configurables; conversión **Lead → Cliente** al ganar 1ª propuesta.
- Propuestas → Proyectos con **carpeta en Drive** y **versionado lógico** de adjuntos.
- **Hub de Mensajería** (WhatsApp/Teams/Meet/Email/Tel) con plantillas y registro de interacción.
- **Actividades** con sincronización a **Outlook** (Graph) y fallback `.ics`.
- **Checklists** por proyecto con plantillas y evidencias.
- **Búsqueda global (FTS5)** y **auditoría** exhaustiva.
- **Auto-update** desde Google Drive; instalador con **Inno Setup**.

## 🔐 Seguridad
- Hash de contraseñas con **Argon2**.  
- Secretos y tokens cifrados (**AES-GCM/Fernet**).  
- **Soft delete** en todas las entidades.  
- Backups automáticos de la BD en `/Backups` (Drive).

## 🧪 Calidad y CI/CD
- **Ruff + Black + MyPy** (lint/format/type).  
- **PyTest** (unit, integración, `pytest-qt` smoke con PyQt6).  
- **GitHub Actions** para CI/CD (build PyInstaller; release con manifest.json + sha256 a Drive).

## 📝 Licencia
Definir en `LICENSE` (MIT o Apache-2.0 recomendado).
