# Configuración de Notificaciones por Email

## Para recibir notificaciones de nuevos registros

1. **Copia el archivo de ejemplo de variables de entorno:**
   ```bash
   cp .env.example .env
   ```

2. **Edita el archivo `.env` con tus datos:**
   ```bash
   # Configuración de Email
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-password-de-aplicacion
   ADMIN_EMAIL=tu-email@gmail.com
   ```

3. **Para Gmail, necesitarás:**
   - Activar la verificación en 2 pasos
   - Generar una "Contraseña de aplicación" específica
   - Usar esa contraseña en `EMAIL_HOST_PASSWORD`

4. **Para desarrollo (sin email real):**
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```
   Esto mostrará los emails en la consola del contenedor Docker.

## Funcionamiento

- Cuando un nuevo usuario se registra, se enviará automáticamente un email de notificación
- El email se envía al usuario 'sa' (si tiene email configurado) o al `ADMIN_EMAIL`
- El email incluye todos los datos del solicitante y un enlace directo al panel de administración

## Seguridad

- Nunca subas el archivo `.env` al repositorio
- El archivo `.env.example` no contiene datos reales, solo ejemplos
- Las contraseñas de email deben ser "contraseñas de aplicación", no tu contraseña principal