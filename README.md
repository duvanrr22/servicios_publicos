# Servicios Públicos Colombia

Aplicación completa para gestión de servicios públicos en Colombia, implementada en Frappe ERPNext 15.

## Características

- **Gestión de múltiples prestadores de servicios**
- **Administración de clientes/suscriptores**
- **Facturación y gestión de cobros**
- **Lectura de medidores**
- **Sistema de reclamos y soporte técnico**
- **Reportes de consumo**
- **Integración con impuestos colombianos**

## Servicios Soportados

- Agua potable
- Energía eléctrica
- Gas natural
- Telecom/Internet
- Saneamiento

## Requisitos

- Frappe Framework (v14 o superior)
- ERPNext 15
- Python 3.8+

## Instalación

1. Clonar o descargar la aplicación:
```bash
cd frappe-bench
bench get-app servicios_publicos /ruta/a/servicios_publicos
```

2. Instalar la aplicación:
```bash
bench install-app servicios_publicos
```

3. Migrar la base de datos:
```bash
bench migrate
```

## Módulos y DocTypes

### Administrativo
- **Prestador de Servicios** - Información de las empresas prestadoras
- **Tipo de Servicio** - Clasificación de servicios (agua, luz, gas, etc.)
- **Tarifa de Servicios** - Estructura de precios por servicio

### Clientes
- **Cliente Servicios Públicos** - Información de suscriptores
- **Conexión de Servicio** - Detalles de conexiones activas
- **Documento de Identidad** - Validación de identidad (CC, NIT, etc.)

### Operaciones
- **Lectura de Medidor** - Registro de consumo periódico
- **Medidor** - Información técnica de medidores

### Facturación
- **Factura de Servicios** - Facturación de servicios consumidos
- **Pago de Servicios** - Registro de pagos

### Servicio al Cliente
- **Reclamo de Servicios** - Gestión de quejas y reclamos
- **Ticket de Soporte** - Seguimiento técnico

## Permisos y Roles

- **Administrador de Servicios** - Gestión completa
- **Operario** - Lectura de medidores y reclamos
- **Facturador** - Generación de facturas
- **Cliente** - Acceso a su información

## Configuración Inicial

1. Crear al menos un prestador de servicios
2. Definir tipos de servicios
3. Establecer tarifas
4. Crear clientes
5. Asignar conexiones de servicio

## Soporte

Para reportar problemas o solicitar características, contactar al equipo de desarrollo.

## Licencia

Licencia Pública General GNU v3.0 (GPL-3.0)
