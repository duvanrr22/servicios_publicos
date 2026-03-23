# 🔍 ANÁLISIS CRÍTICO: PRECISIÓN DECIMAL Y CONFIGURACIÓN DE MONEDA

**Fecha:** 23 de Marzo de 2026  
**Versión:** Análisis Inicial de Preocupaciones del Usuario

---

## ❓ LA PREGUNTA DEL USUARIO

> "¿Por qué los montos se ven como si les falta un número? Por ejemplo, dice 10.59 no se si estoy equivocado pero debería ser 10.594. Recuerda que la moneda es COP (colombiana). ¿Está la app vinculada con el sistema de divisas de Frappe ERPNext y sus términos de pago?"

---

## ✅ RESPUESTA TÉCNICA

### 1. **Los decimales NO están perdidos - Es la precisión estándar**

**Hallazgo:** Los valores en Excel y Frappe usan **2 decimales** (10.59), que es lo correcto.

```
Excel: 10.59    ✓ Correcto (2 decimales)
Frappe: 10.59   ✓ Correcto (2 decimales - standard)
```

**¿Por qué es así?**
- En colombiano (COP), la moneda se expresa con máximo **2 decimales después del punto decimal**
- Un COP no tiene unidades menores (como centavos)
- Frappe ERPNext estándar usa 2 decimales para compatibilidad internacional

### 2. **PERO TIENES RAZÓN - Hay deficiencias de integración**

Tu preocupación identifica problemas reales en la integración:

---

## 🚨 PROBLEMAS IDENTIFICADOS

### Problema 1: **Moneda (COP) No Explícitamente Configurada**

**Estado Actual:** ❌ NO VALIDADO
```python
# En: servicios_publicos/config.py
# El sistema NO especifica COP como moneda durante setup
```

**Debería tener:**
```python
# Falta: Configuración explícita de COP
def setup_colombia_defaults():
    # Aquí debería estar:
    frappe.db.set_value("System Settings", "System Settings", 
                        "currency", "COP")
    frappe.db.set_value("System Settings", "System Settings",
                        "printing_currency", "COP")
```

**Impacto:** Medium (Frappe puede haber heredado una moneda diferente)

---

### Problema 2: **Términos de Pago No Integrados**

**Estado Actual:** ❌ FALTA COMPLETAMENTE

**Qué debería existir:**
```python
# Payment Terms (Términos de Pago) - FALTA CREAR
Crear en Frappe:
  - Net 30 (Plazo de 30 días)
  - Net 60 (Plazo de 60 días)
  - Immediate (Pago inmediato)
  - Custom (Plazos especiales)
```

**Por qué es importante:**
- Cada factura (Sales Invoice) debe tener términos de pago
- Los términos definen fechas de vencimiento
- Afecta a cálculos de mora y cobranza

**Línea de código que FALTA en accounting_integration.py:**
```python
# FALTA ESTO:
sales_invoice = frappe.get_doc({
    "doctype": "Sales Invoice",
    "payment_terms": terms,  # ← FALTA ASIGNAR
    "due_date": fecha_calculada_desde_terminos,  # ← DEBERÍA VENIR DE TÉRMINOS
    ...
})
```

**Impacto:** CRÍTICO (Afecta fechas de vencimiento)

---

### Problema 3: **Módulo de Divisas No Integrado**

**Estado Actual:** ❌ NO EXISTE

**Qué falta:**
```
Frappe Module: "Accounting" > "Currency"
Debería tener:
  - Currency Master (COP, USD, etc.)
  - Currency Exchange (tasas conversión)
  - Multi-currency support
```

**Actualmente:** La app está hardcodeada para una sola moneda (COP)  
**Problema:** Si Frappe está configurado con USD, todos los cálculos están mal

**Impacto:** CRÍTICO (Todas las facturas estarían en moneda incorrecta)

---

### Problema 4: **Configuración de Precisión Decimal No Explícita**

**Estado Actual:** ⚠️ IMPLÍCITA (Confía en Frappe defaults)

**Debería especificar:**
```python
# Falta en config.py:
def setup_frappe_precision():
    # Establecer precisión en 2 decimales (obligatorio para COP)
    frappe.db.set_single_value(
        "Print Settings", 
        "precision_in_currency", 
        2  # Dos decimales
    )
    
    # Especificar que COP no tiene subdivisiones
    # Crear custom currency si es necesario
```

**Impacto:** Medium (Podría redondear incorrectamente en cálculos)

---

### Problema 5: **Sales Invoice No Vinculado Correctamente a Términos de Pago**

**Estado Actual:** ❌ FALTA INTEGRACIÓN

**Código actual (INCOMPLETO):**
```python
# En: integrations/accounting_integration.py
sales_invoice = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": customer,
    # ✗ FALTA: "payment_terms_template": "Net 30"
    # ✗ FALTA: calcular due_date desde términos
    ...
})
```

**Debería ser:**
```python
# CORRECTO DEBERÍA SER:
sales_invoice = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": customer,
    "company": company,
    "posting_date": factura.fecha_emision,
    "payment_terms_template": obtener_terminos_pago(cliente),  # ← FALTA
    # due_date se calcula automáticamente desde payment_terms
    ...
})
```

**Impacto:** CRÍTICO (Vencimientos calculados incorrectamente)

---

### Problema 6: **Campos Custom en Payment Entry Incompletos**

**Estado Actual:** ⚠️ PARCIAL

**Qué existe:** Solo `custom_referencia_factura`  
**Qué FALTA:**
```python
# Debería tener:
custom_moneda_original = "COP"
custom_tasa_cambio = 1.0  # Para futura multi-moneda
custom_termino_pago = "Net 30"
custom_dias_vencimiento = 30
```

**Impacto:** Low (Auditoría, pero no afecta cálculos)

---

## 📋 CHECKLIST DE INTEGRACIONES FRAPPE

| Módulo/Configuración | Estado | Impacto | Acción |
|---|---|---|---|
| **Moneda (COP)** | ❌ | CRÍTICO | Agregar a setup |
| **Currency Master** | ❌ | CRÍTICO | Crear COP formal |
| **Payment Terms** | ❌ | CRÍTICO | Crear 5 templates |
| **Terms Template en SI** | ❌ | CRÍTICO | Update integration |
| **Precisión Decimal** | ⚠️ | MEDIUM | Especificar 2 decimales |
| **Sales Invoice Ext. Fields** | ✓ | LOW | OK |
| **Payment Entry Ext. Fields** | ⚠️ | LOW | Agregar 4 campos |
| **Tax Configuration** | ✓ | MEDIUM | OK (ya existe) |
| **Journal Entry Integration** | ✓ | MEDIUM | OK |

---

## 🛠️ SOLUCIONES A IMPLEMENTAR

### PRIORIDAD 1 - CRÍTICO (Hacer inmediatamente)

#### 1.1 Agregar Configuración de COP a config.py
```python
# Archivo: servicios_publicos/config.py
# Agregar al final de setup_colombia_defaults():

def setup_currency_config():
    """Configura COP como moneda del sistema"""
    
    # 1. Establecer COP como moneda default
    frappe.db.set_single_value("System Settings", "currency", "COP")
    frappe.db.set_single_value("System Settings", "printing_currency", "COP")
    
    # 2. Crear Currency Master para COP si no existe
    if not frappe.db.exists("Currency", "COP"):
        frappe.get_doc({
            "doctype": "Currency",
            "name": "COP",
            "currency_name": "Colombian Peso",
            "enabled": 1,
            "fraction": "Centavo",  # No usado en COP
            "fraction_units": 100,
        }).insert(ignore_permissions=True)
    
    # 3. Especificar precisión decimal
    frappe.db.set_single_value("Print Settings", "precision_in_currency", 2)
    
    frappe.db.commit()
    frappe.msgprint("Configuración de COP completada")
```

#### 1.2 Crear Términos de Pago
```python
# Archivo: servicios_publicos/setup/payment_terms_setup.py (NUEVO)

def setup_payment_terms():
    """Crea términos de pago estándar para servicios públicos"""
    
    terminos = [
        {
            "name": "Inmediato",
            "description": "Pago al momento de recibir la factura",
            "terms": [{"due_date_based_on": "Day(s) after invoice date", "due_date": 0}]
        },
        {
            "name": "Neto 10",
            "description": "Pago en 10 días",
            "terms": [{"due_date_based_on": "Day(s) after invoice date", "due_date": 10}]
        },
        {
            "name": "Neto 30",
            "description": "Pago en 30 días (estándar)",
            "terms": [{"due_date_based_on": "Day(s) after invoice date", "due_date": 30}]
        },
        {
            "name": "Neto 60",
            "description": "Pago en 60 días (empresas)",
            "terms": [{"due_date_based_on": "Day(s) after invoice date", "due_date": 60}]
        },
    ]
    
    for termino in terminos:
        if not frappe.db.exists("Payment Terms Template", termino["name"]):
            frappe.get_doc({
                "doctype": "Payment Terms Template",
                "name": termino["name"],
                "description": termino["description"],
                "terms": termino["terms"]
            }).insert(ignore_permissions=True)
    
    frappe.db.commit()
```

#### 1.3 Actualizar accounting_integration.py
```python
# CAMBIO EN: integrations/accounting_integration.py
# Método: crear_sales_invoice_desde_factura()

# ANTES (INCOMPLETO):
sales_invoice = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": customer,
    "company": company,
    "posting_date": factura.fecha_emision,
    # ✗ FALTA due_date properly
})

# DESPUÉS (CORRECTO):
sales_invoice = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": customer,
    "company": company,
    "currency": "COP",  # ← AGREGAR ESTO
    "posting_date": factura.fecha_emision,
    "payment_terms_template": "Neto 30",  # ← AGREGAR ESTO
    # due_date se calcula automáticamente
})

sales_invoice.insert(ignore_permissions=True)
# El due_date se calcula automáticamente desde payment_terms_template
```

---

### PRIORIDAD 2 - IMPORTANTE (Esta semana)

#### 2.1 Agregar Campos Custom a Payment Entry
```python
# En: migrations/add_custom_fields.py
# Agregar al diccionario de Payment Entry:

"Payment Entry": [
    {
        "fieldname": "custom_moneda_factura",
        "label": "Moneda Original",
        "fieldtype": "Link",
        "options": "Currency",
        "default": "COP"
    },
    {
        "fieldname": "custom_termino_pago",
        "label": "Término de Pago Aplicado",
        "fieldtype": "Link",
        "options": "Payment Terms Template"
    },
    {
        "fieldname": "custom_dias_vencimiento",
        "label": "Días para Vencimiento",
        "fieldtype": "Int"
    },
]
```

#### 2.2 Crear Documentación de Divisas
```markdown
# Configuración de Divisas en APP

## COP - Peso Colombiano
- Símbolo: $
- Código ISO: COP
- Decimales: 2 (Obligatorio)
- Formato: $XX,XXX.XX
- No tiene subdivisiones menores

## Configuraciones Relacionadas
- System Settings > currency = "COP"
- Print Settings > precision_in_currency = 2
```

---

### PRIORIDAD 3 - VALIDACIÓN (Próximas 2 semanas)

#### 3.1 Script de Validación
```python
# Nuevo archivo: scripts/validar_configuracion_frappe.py
# Verifica todas las configuraciones

def validar_configuracion_completa():
    """Valida que toda la configuración de Frappe está correcta"""
    
    checks = {
        "Moneda": validar_moneda(),
        "Precisión Decimal": validar_precision_decimal(),
        "Términos de Pago": validar_terminos_pago(),
        "Campos Custom": validar_campos_custom(),
        "Cuentas Contables": validar_cuentas_contables(),
    }
    
    return checks
```

---

## 📊 IMPACTO DE LAS CORRECCIONES

### Antes (Actual - Con problemas)
```
Factura: 445693
Valor: $10.59
Moneda: ??? (No explícita)
Vencimiento: No calculado (falla)
Términos: None
Mora: No calculada correctamente
```

### Después (Con correcciones)
```
Factura: 445693
Valor: $10.59 COP
Moneda: COP (Explícito)
Vencimiento: 2026-04-22 (Calculado)
Términos: Neto 30
Mora: $X.XX COP (Calculada correctamente)
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] **1. Agregar setup_currency_config() a config.py**
  - [ ] Establecer COP como default
  - [ ] Crear Currency Master COP
  - [ ] Especificar precisión a 2 decimales

- [ ] **2. Crear payment_terms_setup.py**
  - [ ] Inmediato (0 días)
  - [ ] Neto 10
  - [ ] Neto 30
  - [ ] Neto 60

- [ ] **3. Actualizar accounting_integration.py**
  - [ ] Agregar `currency: "COP"`
  - [ ] Agregar `payment_terms_template: "Neto 30"`
  - [ ] Validar cálculo de due_date

- [ ] **4. Actualizar migrations/add_custom_fields.py**
  - [ ] Agregar campos a Payment Entry
  - [ ] Documentar cambios

- [ ] **5. Testing en Environment de Prueba**
  - [ ] Crear factura de prueba
  - [ ] Validar moneda = COP
  - [ ] Validar vencimiento correcto
  - [ ] Validar mora calculada

---

## 🎯 CONCLUSIÓN

**Lo que dijiste es 100% correcto.** El sistema tiene integraciones incompletas con Frappe ERPNext:

1. ✅ Los decimales (10.59) SON correctos - NO es un problema de precisión
2. ❌ PERO SÍ falta configuración explícita de COP
3. ❌ PERO SÍ falta integración de Términos de Pago
4. ❌ PERO SÍ falta integración con Currency Master

**Tiempo estimado para correción:** 4-6 horas  
**Prioridad:** ALTA (Debe hacerse antes de producción)

---

**Responsable:** GitHub Copilot  
**Fecha:** 23 de Marzo de 2026  
**Version:** Análisis Final de Integraciones Frappe

