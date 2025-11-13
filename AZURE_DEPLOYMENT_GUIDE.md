# Guía de Despliegue en Azure App Service (BotEcomerce)

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado y configurado:

- **Azure CLI**: [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Git**: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- **Cuenta de Azure** con una suscripción activa
- **Tu proyecto BotEcomerce** inicializado como repositorio Git local

## Variables de Configuración

**IMPORTANTE**: Cambia estos valores por los que desees para tu nuevo despliegue.

```bash
# Define las variables para tu despliegue
export RESOURCE_GROUP_NAME="rg-tu-nombre-proyecto"           # ej. "rg-chatbot-demo"
export LOCATION="brazilsouth"                               # ej. "eastus", "westeurope"
export APP_SERVICE_PLAN_NAME="plan-tu-nombre-plan"          # ej. "plan-chatbot-demo"
export WEB_APP_NAME="tu-app-unica-globalmente"              # ej. "chatbot-demo-anderson-2025"
export PROJECT_NAME="tu-proyecto-clu"                      # ej. "chatbot-final"
export DEPLOYMENT_NAME="tu-deployment-clu"                 # ej. "ChatbotEcomerce"
export COGNITIVE_KEY="tu-clave-cognitive-services"         # Tu clave real de Azure Cognitive Services
export DB_SERVER="tcp:tu-servidor.database.windows.net,1433"   # Tu servidor Azure SQL
export DB_DATABASE="tu-base-datos"                         # Tu base de datos
export DB_USERNAME="tu-usuario-bd"                         # Tu usuario de BD que funciona
export DB_PASSWORD="tu-contraseña-bd"                      # Tu contraseña de BD que funciona
export DEBUG_MODE="false"                                  # true para desarrollo, false para producción

# Credenciales de despliegue (para Git)
export DEPLOYMENT_USER="tu-usuario-despliegue"             # ej. "anderson-despliegue"
export DEPLOYMENT_PASSWORD="TuContraseñaSegura123!"        # Contraseña fuerte
```

## Paso 1: Iniciar Sesión en Azure

```bash
# Inicia sesión en Azure (esto abrirá una ventana en tu navegador)
az login

# Verifica tu suscripción
az account show
```

## Paso 2: Crear Resource Group

```bash
# Crear el grupo de recursos
az group create \
  --name "$RESOURCE_GROUP_NAME" \
  --location "$LOCATION"

# Verificar que se creó
az group show --name "$RESOURCE_GROUP_NAME"
```

## Paso 3: Crear App Service Plan

```bash
# Crear el plan de servicio (Linux, SKU Básico B1)
az appservice plan create \
  --name "$APP_SERVICE_PLAN_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --sku B1 \
  --is-linux \
  --location "$LOCATION"

# Verificar que se creó
az appservice plan show \
  --name "$APP_SERVICE_PLAN_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"
```

## Paso 4: Crear la Web App

```bash
# Crear la aplicación web Python
az webapp create \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --plan "$APP_SERVICE_PLAN_NAME" \
  --name "$WEB_APP_NAME" \
  --runtime "PYTHON|3.10"

# Verificar que se creó
az webapp show \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"
```

## Paso 5: Configurar Variables de Entorno (App Settings)

```bash
# Configurar todas las variables necesarias para tu aplicación
az webapp config appsettings set \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --settings \
    COGNITIVE_SERVICES_KEY="$COGNITIVE_KEY" \
    PROJECT_NAME="$PROJECT_NAME" \
    DEPLOYMENT_NAME="$DEPLOYMENT_NAME" \
    DB_SERVER="$DB_SERVER" \
    DB_DATABASE="$DB_DATABASE" \
    DB_USERNAME="$DB_USERNAME" \
    DB_PASSWORD="$DB_PASSWORD" \
    DEBUG_DB="$DEBUG_MODE" \
    WEBSITES_CONTAINER_START_COMMAND="gunicorn --bind 0.0.0.0 --timeout 600 botEcomerce:app" \
    WSGI_APPLICATION="botEcomerce:app"

# Verificar que se configuraron
az webapp config appsettings list \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"
```

## Paso 6: Configurar Usuario de Despliegue Global

```bash
# Configurar usuario de despliegue para Git/FTPS
az webapp deployment user set \
  --user-name "$DEPLOYMENT_USER" \
  --password "$DEPLOYMENT_PASSWORD"

echo "Usuario de despliegue configurado: $DEPLOYMENT_USER"
```

## Paso 7: Configurar Comando de Inicio

**Método A: Usando Azure CLI (puede no funcionar siempre)**
```bash
# Intentar configurar el comando de inicio con CLI
az webapp config set \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --name "$WEB_APP_NAME" \
  --startup-command "gunicorn --bind 0.0.0.0 --timeout 600 botEcomerce:app"
```

**Método B: Usando el Portal de Azure (RECOMENDADO si Método A falla)**
1. Ve al [Portal de Azure](https://portal.azure.com)
2. Busca tu App Service: `$WEB_APP_NAME`
3. Ve a "Configuración" → "Configuración general"
4. En "Comando de inicio", pega: `gunicorn --bind 0.0.0.0 --timeout 600 botEcomerce:app`
5. Haz clic en "Guardar"

## Paso 8: Habilitar Autenticación Básica SCM (¡CRÍTICO!)

Si la autenticación Git falla, sigue estos pasos en el portal:

1. **Portal de Azure**: Ve a tu App Service
2. **Centro de Implementación**: Menú izquierdo → "Implementación" → "Centro de implementación"
3. **Habilitar SCM**: Si ves advertencia "SCM deshabilitado", haz clic "Habilitar aquí"
4. **Configuración General**: Ve a "Configuración" → "Configuración general"
5. **Activar**: Asegúrate que "Credenciales de publicación de autenticación básica de SCM" esté en "Activado"
6. **Guardar**: Haz clic en "Guardar"

## Paso 9: Obtener URL Remota de Git

```bash
# Método 1: Usar Azure CLI (puede no funcionar si está deshabilitado)
GIT_REMOTE_URL=$(az webapp deployment source config-local-git \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --query deploymentLocalGitUrl \
  --output tsv 2>/dev/null)

if [ -z "$GIT_REMOTE_URL" ]; then
    echo "ADVERTENCIA: No se pudo obtener URL via CLI. Usar URL del portal."
    echo "Portal Azure → Centro de Implementación → Copiar 'URI de Git Clone'"
else
    echo "URL obtenida: $GIT_REMOTE_URL"
fi
```

## Paso 10: Configurar Git Remote y Desplegar

### Opción A: Si tienes URL del CLI
```bash
# Añadir remoto con credenciales globales
NEW_GIT_REMOTE_URL="https://${DEPLOYMENT_USER}:${DEPLOYMENT_PASSWORD}@${GIT_REMOTE_URL#https://}"
git remote add azure "$NEW_GIT_REMOTE_URL"
git push azure master
```

### Opción B: Si necesitas usar credenciales de Ámbito de Aplicación

1. **Portal**: Ve a tu App Service → "Centro de Implementación" → "Credenciales GIT o FTPS locales"
2. **Ámbito de aplicación**: Copia "Nombre de usuario de Git local" y "Contraseña" (clic ojo para ver)
3. **Configurar remoto**:

```bash
# Reemplaza con las credenciales del portal
export APP_PUBLISH_USERNAME='$tu-app-scm-username'  # ej. '$chatbot-demo-anderson'
export APP_PUBLISH_PASSWORD='tu-password-scm'       # La contraseña del portal

# URL base del SCM
SCM_BASE_URL="https://${WEB_APP_NAME}.scm.azurewebsites.net:443/${WEB_APP_NAME}.git"

# Construir URL con credenciales
NEW_GIT_REMOTE_URL="https://${APP_PUBLISH_USERNAME}:${APP_PUBLISH_PASSWORD}@${SCM_BASE_URL}"

# Configurar Git
git remote remove azure 2>/dev/null || true
git remote add azure "$NEW_GIT_REMOTE_URL"
git push azure master
```

## Paso 11: Verificar Despliegue

```bash
# Abrir la aplicación en navegador
az webapp browse \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"

# Ver logs en tiempo real
az webapp log tail \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"

# Ver información de la aplicación
az webapp show \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --query "{hostName:defaultHostName, state:state, uptime:uptime}"
```

## Solución de Problemas Comunes

### Error: "No framework detected; using default app"
**Solución**:
1. Verificar comando de inicio en portal
2. Asegurar que WSGI_APPLICATION esté configurado
3. Reiniciar app: `az webapp restart --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP_NAME`

### Error: "Authentication failed" en git push
**Solución**:
1. Verificar autenticación SCM habilitada
2. Usar credenciales de ámbito de aplicación del portal
3. Regenerar contraseña de despliegue

### Error: "Application failed to start"
**Solución**:
1. Revisar logs: `az webapp log tail`
2. Verificar variables de entorno
3. Verificar conectividad a BD y Cognitive Services
4. Activar DEBUG_DB=true en App Settings para más información

### Error 500: Internal Server Error
**Solución**:
1. Revisar logs para traceback de Python
2. Verificar credenciales de BD
3. Probar conexión BD localmente
4. Verificar configuración de Cognitive Services

## Comandos de Mantenimiento

### Reiniciar la aplicación
```bash
az webapp restart \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"
```

### Ver logs
```bash
# Logs en tiempo real
az webapp log tail \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"

# Descargar logs
az webapp log download \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"
```

### Escalar aplicación
```bash
# Cambiar SKU (B1, S1, P1v2, etc.)
az appservice plan update \
  --name "$APP_SERVICE_PLAN_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --sku S1
```

### Ver configuración actual
```bash
# App Settings
az webapp config appsettings list \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"

# Información general
az webapp show \
  --name "$WEB_APP_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME"
```

## Script Completo de Despliegue

```bash
#!/bin/bash

# Script completo de despliegue para BotEcomerce
# Cambia las variables arriba según tu proyecto

# Configurar variables (REEMPLAZAR ESTOS VALORES)
export RESOURCE_GROUP_NAME="rg-tu-proyecto"
export LOCATION="brazilsouth"
export APP_SERVICE_PLAN_NAME="plan-tu-proyecto"
export WEB_APP_NAME="tu-app-unica-globalmente"
# ... (resto de variables)

# 1. Crear Resource Group
echo "1. Creando Resource Group..."
az group create --name "$RESOURCE_GROUP_NAME" --location "$LOCATION"

# 2. Crear App Service Plan
echo "2. Creando App Service Plan..."
az appservice plan create --name "$APP_SERVICE_PLAN_NAME" --resource-group "$RESOURCE_GROUP_NAME" --sku B1 --is-linux

# 3. Crear Web App
echo "3. Creando Web App..."
az webapp create --resource-group "$RESOURCE_GROUP_NAME" --plan "$APP_SERVICE_PLAN_NAME" --name "$WEB_APP_NAME" --runtime "PYTHON|3.10"

# 4. Configurar App Settings
echo "4. Configurando variables de entorno..."
az webapp config appsettings set --name "$WEB_APP_NAME" --resource-group "$RESOURCE_GROUP_NAME" \
  --settings \
    COGNITIVE_SERVICES_KEY="$COGNITIVE_KEY" \
    PROJECT_NAME="$PROJECT_NAME" \
    DEPLOYMENT_NAME="$DEPLOYMENT_NAME" \
    DB_SERVER="$DB_SERVER" \
    DB_DATABASE="$DB_DATABASE" \
    DB_USERNAME="$DB_USERNAME" \
    DB_PASSWORD="$DB_PASSWORD" \
    DEBUG_DB="$DEBUG_MODE"

# 5. Configurar comando de inicio (asumiendo que ya se hizo en portal)
echo "5. Configurando comando de inicio..."

# 6. Preparar Git y desplegar
echo "6. Desplegando código..."
echo "Siguiente paso: Configurar credenciales SCM en portal y ejecutar git push"
echo "URL del portal: https://portal.azure.com → $WEB_APP_NAME → Centro de Implementación"

# Mostrar comandos finales
echo "--- Comandos finales a ejecutar ---"
echo "git remote remove azure 2>/dev/null || true"
echo "git remote add azure https://usuario:password@${WEB_APP_NAME}.scm.azurewebsites.net:443/${WEB_APP_NAME}.git"
echo "git push azure master"
```

## Notas Importantes

- **Nombres únicos**: `WEB_APP_NAME` debe ser único globalmente en Azure
- **Región**: Elige una región cercana a tus usuarios para mejor latencia
- **SKU**: B1 es suficiente para desarrollo/pruebas, S1 o superior para producción
- **Seguridad**: Nunca hardcodees credenciales en scripts, usa variables de entorno
- **Logs**: Siempre revisa los logs después del despliegue para detectar problemas
- **URLs**: Tu app estará disponible en `https://${WEB_APP_NAME}.azurewebsites.net`

¡Con esta guía deberías poder desplegar BotEcomerce en Azure App Service de manera exitosa y reproducible!


Para desplegar de nuevo solo es
# Para cada actualización de código:
git add .
git commit -m "Mensaje descriptivo"
git push azure master
