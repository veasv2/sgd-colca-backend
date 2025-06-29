# 🚀 SGD Colca - Guía de Comandos

## 📋 Comandos Directos

```bash
python manage-db.py --help                    # Ayuda general
python manage-db.py <comando> --help          # Ayuda específica
```

---

## 🔧 Gestión Básica

| Comando | Descripción |
|---------|-------------|
| `python manage-db.py init-db` | Inicializar BD completa |
| `python manage-db.py seed-data --scenario basico` | Datos de prueba básicos |
| `python manage-db.py seed-data --extended-org --scenario completo` | Datos completos |
| `python manage-db.py status` | Estado del sistema |
| `python manage-db.py status --detailed` | Estado detallado |

---

## 🔄 Migraciones

| Comando | Descripción |
|---------|-------------|
| `python manage-db.py migrate upgrade` | Aplicar migraciones |
| `python manage-db.py migrate revision -m "mensaje"` | Nueva migración |
| `python manage-db.py migrate current` | Revisión actual |
| `python manage-db.py migrate history` | Historial |

---

## 💾 Respaldos

| Comando | Descripción |
|---------|-------------|
| `python manage-db.py backup --compress` | Respaldo comprimido |
| `python manage-db.py backup --no-data --compress` | Solo estructura |
| `python scripts/database/backup_db.py restore archivo.sql` | Restaurar |

---

## ⚠️ Reset (PELIGROSO)

| Comando | Descripción |
|---------|-------------|
| `python manage-db.py reset-db` | Reset con confirmación |
| `python manage-db.py reset-db --force` | Reset sin confirmación |
| `python manage-db.py reset-db --force --reinit` | Reset y reinit |

---

## 🛠️ Desarrollo

| Comando | Descripción |
|---------|-------------|
| `pip install -r requirements.txt` | Instalar dependencias |
| **Comando combinado:** | Setup completo: |
| `pip install -r requirements.txt && python manage-db.py init-db && python manage-db.py seed-data --scenario basico` | |

---

## 📚 Flujos de Trabajo Comunes

### 🚀 **Primera vez (proyecto nuevo)**
```bash
pip install -r requirements.txt
python manage-db.py init-db
python manage-db.py seed-data --scenario basico
```

### 🔄 **Desarrollo diario**
```bash
python manage-db.py status          # Ver estado
python manage-db.py migrate upgrade # Aplicar migraciones nuevas
python manage-db.py seed-data --scenario basico  # Recargar datos si es necesario
```

### 📝 **Crear nueva migración**
```bash
# Después de modificar modelos
python manage-db.py migrate revision -m "agregar campo usuario activo"
python manage-db.py migrate upgrade
```

### 💾 **Antes de cambios importantes**
```bash
python manage-db.py backup --compress  # Crear respaldo
# hacer cambios...
# si algo sale mal: python scripts/database/backup_db.py restore backup_xxx.sql.gz
```

### 🧪 **Testing/Experimentos**
```bash
python manage-db.py backup --compress          # Respaldo de seguridad
python manage-db.py reset-db --force --reinit  # Reset completo
# experimentar...
python scripts/database/backup_db.py restore backup_xxx.sql.gz  # Volver al estado anterior
```

### 🏭 **Deploy a producción**
```bash
pip install -r requirements.txt
python manage-db.py migrate upgrade  # Solo migraciones, sin datos de prueba
```

---

## 🆘 Comandos de Emergencia

### 🚨 **Base de datos corrupta**
```bash
python manage-db.py reset-db --force     # Eliminar todo
python manage-db.py init-db             # Recrear estructura
# restaurar desde respaldo si existe
```

### 🔍 **Debug de problemas**
```bash
python manage-db.py status --detailed   # Información completa
python manage-db.py migrate current     # Ver migración actual
python manage-db.py migrate history     # Ver historial
```

### 🔧 **Problemas de dependencias**
```bash
# Limpiar cache manualmente
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
pip install -r requirements.txt        # Reinstalar dependencias
```

---

## ⚡ Atajos Útiles

### 🔗 **Aliases recomendados para .bashrc/.zshrc:**
```bash
alias sgd-status="python manage-db.py status"
alias sgd-migrate="python manage-db.py migrate upgrade"
alias sgd-backup="python manage-db.py backup --compress"
alias sgd-init="python manage-db.py init-db"
alias sgd-seed="python manage-db.py seed-data --scenario basico"
```

### 📝 **Comandos más usados:**
```bash
# Los 5 comandos que más vas a usar:
python manage-db.py init-db              # Inicializar
python manage-db.py status               # Ver estado
python manage-db.py migrate upgrade      # Aplicar migraciones
python manage-db.py seed-data --scenario basico  # Datos de prueba
python manage-db.py backup --compress    # Respaldo
```

---

## 📱 Acceso Rápido

### 🔑 **Credenciales por defecto**
- **Usuario:** `admin`
- **Email:** `admin@colca.gob.pe`
- **Password:** `admin123`

⚠️ **CAMBIAR EN PRODUCCIÓN**

### 📞 **Ayuda**
```bash
python manage-db.py --help          # Lista completa de comandos
python manage-db.py status --help   # Ayuda específica de comando
```

---

## 🚀 **Comandos de un vistazo**

```bash
# Básicos
python manage-db.py init-db
python manage-db.py status
python manage-db.py seed-data --scenario basico

# Migraciones  
python manage-db.py migrate upgrade
python manage-db.py migrate revision -m "mensaje"

# Respaldos
python manage-db.py backup --compress
python manage-db.py reset-db --force --reinit
```# 🚀 SGD Colca - Guía de Comandos

## 📋 Comandos Rápidos

### Con Makefile (Recomendado)
```bash
make help           # Ver todos los comandos disponibles
make init           # Inicializar BD completa
make seed           # Datos de prueba básicos
make status         # Estado del sistema
make migrate        # Aplicar migraciones
make backup         # Crear respaldo
```

### Comandos Directos
```bash
python manage.py --help                    # Ayuda general
python manage.py <comando> --help          # Ayuda específica
```

---

## 🔧 Gestión Básica

| Comando | Makefile | Descripción |
|---------|----------|-------------|
| `python manage.py init-db` | `make init` | Inicializar BD completa |
| `python manage.py seed-data --scenario basico` | `make seed` | Datos de prueba básicos |
| `python manage.py seed-data --extended-org --scenario completo` | `make seed-full` | Datos completos |
| `python manage.py status` | `make status` | Estado del sistema |
| `python manage.py status --detailed` | `make status-detail` | Estado detallado |

---

## 🔄 Migraciones

| Comando | Makefile | Descripción |
|---------|----------|-------------|
| `python manage.py migrate upgrade` | `make migrate` | Aplicar migraciones |
| `python manage.py migrate revision -m "mensaje"` | `make migration MSG="mensaje"` | Nueva migración |
| `python manage.py migrate current` | `make migrate-current` | Revisión actual |
| `python manage.py migrate history` | `make migrate-history` | Historial |

---

## 💾 Respaldos

| Comando | Makefile | Descripción |
|---------|----------|-------------|
| `python manage.py backup --compress` | `make backup` | Respaldo comprimido |
| `python manage.py backup --no-data --compress` | `make backup-schema` | Solo estructura |
| `python scripts/database/backup_db.py restore archivo.sql` | `make restore FILE="archivo.sql"` | Restaurar |

---

## ⚠️ Reset (PELIGROSO)

| Comando | Makefile | Descripción |
|---------|----------|-------------|
| `python manage.py reset-db` | `make reset` | Reset con confirmación |
| `python manage.py reset-db --force` | `make reset-force` | Reset sin confirmación |
| `python manage.py reset-db --force --reinit` | `make reset-reinit` | Reset y reinit |

---

## 🛠️ Desarrollo

| Comando | Makefile | Descripción |
|---------|----------|-------------|
| `pip install -r requirements.txt` | `make install` | Instalar dependencias |
| `make install && make init && make seed` | `make dev` | Setup completo |
| - | `make clean` | Limpiar temporales |

---

## 📚 Flujos de Trabajo Comunes

### 🚀 **Primera vez (proyecto nuevo)**
```bash
make dev
# o manualmente:
# pip install -r requirements.txt
# python manage.py init-db
# python manage.py seed-data --scenario basico
```

### 🔄 **Desarrollo diario**
```bash
make status          # Ver estado
make migrate         # Aplicar migraciones nuevas
make seed            # Recargar datos si es necesario
```

### 📝 **Crear nueva migración**
```bash
# Después de modificar modelos
make migration MSG="agregar campo usuario activo"
make migrate
```

### 💾 **Antes de cambios importantes**
```bash
make backup          # Crear respaldo
# hacer cambios...
# si algo sale mal: make restore FILE="backup_xxx.sql.gz"
```

### 🧪 **Testing/Experimentos**
```bash
make backup          # Respaldo de seguridad
make reset-reinit    # Reset completo
# experimentar...
make restore FILE="backup_xxx.sql.gz"  # Volver al estado anterior
```

### 🏭 **Deploy a producción**
```bash
make setup-prod      # Solo migraciones, sin datos de prueba
```

---

## 🆘 Comandos de Emergencia

### 🚨 **Base de datos corrupta**
```bash
make reset-force     # Eliminar todo
make init           # Recrear estructura
# restaurar desde respaldo si existe
```

### 🔍 **Debug de problemas**
```bash
make status-detail   # Información completa
python manage.py migrate current  # Ver migración actual
python manage.py migrate history  # Ver historial
```

### 🔧 **Problemas de dependencias**
```bash
make clean          # Limpiar cache
make install        # Reinstalar dependencias
```

---

## ⚡ Atajos Útiles

```bash
# Alias recomendados para tu .bashrc/.zshrc
alias sgd-status="python manage.py status"
alias sgd-migrate="python manage.py migrate upgrade"
alias sgd-backup="python manage.py backup --compress"

# O simplemente
alias ms="make status"
alias mm="make migrate"  
alias mb="make backup"
```

---

## 📱 Acceso Rápido

### 🔑 **Credenciales por defecto**
- **Usuario:** `admin`
- **Email:** `admin@colca.gob.pe`
- **Password:** `admin123`

⚠️ **CAMBIAR EN PRODUCCIÓN**

### 📞 **Ayuda**
```bash
make help           # Lista completa de comandos
python manage.py --help  # Ayuda del CLI
```