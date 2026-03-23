# Guía de Instalación - Servicios Públicos Colombia

## Requisitos Previos

- ERPNext 15 instalado y funcionando
- Python 3.8 o superior
- Frappe Framework v15

## Instalación en Frappe Bench

### 1. Clonar la Aplicación

```bash
cd ~/frappe-bench
git clone <URL_del_repositorio> apps/servicios_publicos
```

O si tienes la carpeta local:

```bash
cd ~/frappe-bench
bench get-app servicios_publicos /ruta/a/servicios_publicos
```

### 2. Instalar la Aplicación

```bash
bench install-app servicios_publicos
cd ~/frappe-bench
./env/bin/pip install -e apps/servicios_publicos
```

### 3. Migrar Base de Datos

```bash
bench migrate servicios_publicos
```

Esto creará todas las tablas y estructuras necesarias.

### 4. Reiniciar Frappe

```bash
bench restart
```

## Configuración Inicial

### 1. Crear Prestador de Servicios

1. Ir a: **Servicios Públicos > Administración > Prestador de Servicios**
2. Click en "+ Nuevo"
3. Llenar los datos:
   - **Razón Social**: Nombre de la empresa (ej: Acueducto Municipal)
   - **NIT**: Identificación de la empresa
   - **Tipo de Empresa**: Seleccionar tipo
   - **Email**: Correo de contacto
   - **Servicios**: Agregar tipos de servicios prestados
4. Guardar

### 2. Crear Tipos de Servicios

Si no los tiene configurados:

1. Ir a: **Servicios Públicos > Administración > Tipo de Servicio**
2. Crear los servicios que ofrece:
   - Agua Potable (m³)
   - Energía Eléctrica (kWh)
   - Gas Natural (m³)
   - etc.

### 3. Configurar Tarifas

1. Ir a: **Servicios Públicos > Facturación > Tarifa Servicios**
2. Click en "+ Nuevo"
3. Definir:
   - Tipo de Servicio
   - Prestador de Servicios
   - Rango de consumo (opcional)
   - Valor de tarifa por unidad
   - Valor fijo de factura
   - Categoría de cliente aplicable
   - Fecha de vigencia

### 4. Crear Clientes

1. Ir a: **Servicios Públicos > Clientes > Cliente Servicios Públicos**
2. Click en "+ Nuevo"
3. Llenar:
   - Nombre Completo
   - Tipo de Identificación y Número
   - Dirección
   - Email y Teléfono
   - Categoría del cliente (Residencial, Comercial, etc.)

### 5. Crear Conexiones de Servicio

1. Ir a: **Servicios Públicos > Clientes > Conexion de Servicio**
2. Click en "+ Nuevo"
3. Seleccionar:
   - Cliente
   - Prestador de Servicios
   - Tipo de Servicio
   - Medidor (si existe)
   - Fecha de instalación

### 6. Crear Medidores (Opcional)

1. Ir a: **Servicios Públicos > Operaciones > Medidor**
2. Crear medidores con:
   - Número de medidor (único)
   - Marca y modelo
   - Tipo de servicio
   - Estado

## Flujo de Trabajo Típico

### Lectura de Medidores

1. **Ir a**: Servicios Públicos > Operaciones > Lectura de Medidor
2. **Crear**: Nueva lectura ingresando:
   - Conexión de Servicio
   - Lectura Actual
   - Fecha de lectura
3. El sistema calcula automáticamente el consumo

### Facturación

1. Ir a: Servicios Públicos > Facturación > Factura de Servicios
2. Crear manualmente o usar la API para crear desde lectura
3. El sistema calcula automáticamente:
   - Consumo
   - Valor según tarifa
   - Impuestos (si aplica)
   - Total a pagar
4. Guardar y mantener como "Emitida"

### Registros de Pago

1. Cuando el cliente paga:
   - Ir a: Servicios Públicos > Facturación > Pago de Servicios
   - Crear nuevo pago vinculado a la factura
   - Registrar monto y método de pago
   - Adjuntar comprobante

### Reclamos

1. Cliente reporta problema:
   - Ir a: Servicios Públicos > Servicio al Cliente > Reclamo de Servicios
   - Crear reclamo con tipo, prioridad y descripción
2. Sistema asigna responsable
3. Se realiza seguimiento hasta resolución

## Permisos y Roles

### Roles Disponibles

- **Administrador de Servicios**: Acceso completo
- **Operario**: Puede registrar lecturas de medidores
- **Facturador**: Puede crear y aprobar facturas
- **Cliente**: Acceso limitado a su información

### Asignar Roles

1. Ir a: Configuración > Usuarios
2. Seleccionar usuario
3. En "Roles", agregar rol requerido

## APIs Disponibles

### Obtener Deuda de Cliente

```
GET /api/resource/servicios_publicos.api.obtener_deuda_cliente
?cliente=CLIENT-2024-001
```

### Obtener Últimas Lecturas

```
GET /api/resource/servicios_publicos.api.obtener_ultimas_lecturas
?conexion_de_servicio=CONN-2024-001&limite=5
```

### Crear Factura desde Lectura

```
POST /api/resource/servicios_publicos.api.crear_factura_desde_lectura
Body: {"numero_lectura": "LECT-2024-001"}
```

## Resolución de Problemas

### Las tablas no se crean

```bash
bench migrate servicios_publicos
bench clear-cache
bench restart
```

### La aplicación no aparece en el menú

1. Borrar caché de navegador (Ctrl+Shift+Delete)
2. En Frappe: Ctrl+K > Workspace
3. Verificar que el módulo esté habilitado

### Errores de permisos

- Verificar que el usuario tiene los roles correctos
- Ir a: Servicios Públicos > [DocType] > Permisos
- Asegurar que el rol tiene permisos de lectura/escritura

## Contacto y Soporte

Para reportar problemas o solicitar nuevas características,
contactar al equipo de desarrollo.

## Licencia

GNU General Public License v3.0 (GPL-3.0)
