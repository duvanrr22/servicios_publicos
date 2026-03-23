# Arquitectura de la Aplicación

## Estructura de Carpetas

```
servicios_publicos/
├── servicios_publicos/              # Módulo principal
│   ├── __init__.py                 # Inicialización
│   ├── hooks.py                    # Configuración de hooks de Frappe
│   ├── config.py                   # Configuración personalizada
│   ├── install.py                  # Script de instalación
│   ├── doctype/                    # Todos los DocTypes
│   │   ├── prestador_de_servicios/
│   │   ├── tipo_de_servicio/
│   │   ├── cliente_servicios_publicos/
│   │   ├── conexion_de_servicio/
│   │   ├── medidor/
│   │   ├── lectura_de_medidor/
│   │   ├── factura_de_servicios/
│   │   ├── pago_de_servicios/
│   │   ├── reclamo_de_servicios/
│   │   ├── tarifa_servicios/
│   │   └── [child_tables]/
│   ├── api/                        # APIs REST personalizadas
│   │   ├── __init__.py
│   │   └── api.py
│   └── utils/                      # Utilidades compartidas
│       ├── __init__.py
│       └── utils.py
├── setup.py                        # Configuración de setuptools
├── README.md                       # Documentación principal
└── INSTALLATION_GUIDE.md           # Guía de instalación
```

## Diagrama de Entidades

```
Prestador de Servicios (1) -----> (N) Tipo de Servicio
        |
        |
        └-----> (N) Tarifa Servicios
        |           |
        |           └----> (1) Tipo de Servicio
        |
        └-----> (N) Cliente Conexión
                    |
                    └----> (1) Cliente Servicios Públicos
                    |
                    └----> (1) Medidor
                               |
                               └----> (N) Lectura de Medidor
                                          |
                                          └----> (1) Factura de Servicios
                                                     |
                                                     └----> (N) Pago de Servicios

Cliente Servicios Públicos (1) -----> (N) Reclamo de Servicios
```

## Flujo de Datos Principal

### 1. Lectura a Facturación

```
Lectura de Medidor
    ↓ (API crear_factura_desde_lectura)
    ↓ (obtiene tarifa vigente)
    ↓ (calcula consumo y valor)
Factura de Servicios
    ↓ (cliente recibe factura)
    ↓ (realiza pago)
Pago de Servicios
    ↓ (actualiza estado factura)
Factura Pagada
```

### 2. Reclamo y Resolución

```
Cliente reporta problema
    ↓
Reclamo de Servicios (creado)
    ↓ (se asigna a responsable)
    ↓ (cambio de estado: En Análisis → En Proceso)
    ↓ (se documenta solución)
Reclamo de Servicios (resuelto)
    ↓ (cliente valida satisfacción)
Reclamo de Servicios (cerrado)
```

## Módulos Principales

### 1. Administración (Administration)
- Prestador de Servicios
- Tipo de Servicio
- Tarifa Servicios

### 2. Clientes (Customers)
- Cliente Servicios Públicos
- Conexion de Servicio

### 3. Operaciones (Operations)
- Medidor
- Lectura de Medidor

### 4. Facturación (Billing)
- Factura de Servicios
- Pago de Servicios
- Reporte de Deuda

### 5. Servicio al Cliente (Customer Service)
- Reclamo de Servicios

## Características de Seguridad

1. **Control de Acceso Basado en Roles (RBAC)**
   - Administrador de Servicios
   - Operario
   - Facturador
   - Cliente

2. **Auditoría**
   - Track Changes habilitado en todos los DocTypes
   - Seguimiento de creación y modificación
   - Historial de cambios

3. **Validaciones**
   - Validación de identificación única
   - Fechas coherentes
   - Valores numéricos válidos

## Configuración de Impuestos

Se puede integrar con ERPNext:
- Usar Taxes and Charges en Facturas
- Configurar retenciones si aplica

## Reportes Disponibles

1. **Consumo por Período**
   - Reporte de consumo agregado
   - Filtrable por servicio, periodo, prestador

2. **Morosidad de Clientes**
   - Clientes con deuda
   - Montos vencidos
   - Últimas fechas de pago

3. **Facturación**
   - Facturas emitidas
   - Facturas vencidas
   - Ingresos por periodo

## Extensiones Futuras

- Integración con pasarelas de pago
- Portal de cliente web
- Generación de PDF de facturas
- SMS y Email automáticos
- Integración con sistemas IOT para medición automática
- Reportes avanzados con gráficos
- Integración con BancóldoSinpe para SSPD

## Notas de Desarrollo

- La aplicación usa convenciones de Frappe
- Todos los DocTypes incluyen traducción a español
- Las referencias a City y State usan ubicaciones de Frappe
- El sistema de permisos es configurable por rol
