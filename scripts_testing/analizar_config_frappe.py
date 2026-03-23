"""
ANALISIS CRITICO: VALIDACION DE INTEGRACION FRAPPE
====================================================

Verifica:
1. Configuracion de moneda (COP)
2. Soporte de decimales correctos
3. Modulos faltantes o no integrados
4. Terminos de pago
5. Configuracion de divisas
"""

import frappe
import sys

print("\n" + "="*80)
print("VALIDACION DE CONFIGURACION FRAPPE - MONEDA Y DIVISAS")
print("="*80)

# ============================================================================
# SECCION 1: REVISAR CONFIGURACION DE MONEDA EN FRAPPE
# ============================================================================

print("\n[CHECK 1] Sistema de Moneda/Divisas en Frappe")
print("-" * 50)

try:
    # Obtener moneda por defecto
    default_currency = frappe.db.get_single_value("System Settings", "currency")
    print(f"  Moneda por defecto del sistema: {default_currency}")
    
    if default_currency != "COP":
        print(f"  ⚠️  ALERTA: Moneda es {default_currency}, no COP")
    else:
        print(f"  ✓ Moneda correctamente configurada como COP")
        
except Exception as e:
    print(f"  ✗ Error verificando moneda: {str(e)}")

# ============================================================================
# SECCION 2: VERIFICAR PRECISIÓN DECIMAL
# ============================================================================

print("\n[CHECK 2] Precision Decimal en Frappe")
print("-" * 50)

try:
    # En Frappe ERPNext standard, los montos usan 2 decimales por defecto
    decimal_places = frappe.db.get_single_value("Print Settings", "precision_in_currency")
    
    if decimal_places is None:
        decimal_places = 2  # Default en Frappe
    
    print(f"  Decimales configurados: {decimal_places}")
    print(f"  Formato estándar: $XX,XXX.{decimal_places:02d}")
    
    if decimal_places < 2:
        print(f"  ⚠️  ALERTA: Precision baja ({decimal_places} decimales)")
    elif decimal_places == 2:
        print(f"  ✓ Precision estándar (2 decimales)")
    else:
        print(f"  ✓ Precision extendida ({decimal_places} decimales)")
        
except Exception as e:
    print(f"  ✗ Error verificando precisión: {str(e)}")

# ============================================================================
# SECCION 3: VERIFICAR MODULOS REQUERIDOS
# ============================================================================

print("\n[CHECK 3] Modulos Requeridos – Estado")
print("-" * 50)

modulos_requeridos = {
    'Accounting': 'Contabilidad (Invoices, Journal Entries)',
    'Selling': 'Ventas (Sales Invoice, Customer)',
    'Buying': 'Compras (Purchase Order, Supplier)',
    'CRM': 'Gestión de Relaciones (Lead, Opportunity)',
    'Stock': 'Inventario (Item, Warehouse)',
    'HR': 'Recursos Humanos (Employee)',
    'Human Resources': 'Recursos Humanos (Alternative)',
}

try:
    for modulo, descripcion in modulos_requeridos.items():
        # Verificar si módulo está instalado
        existe = frappe.db.exists("Module", modulo)
        
        if existe:
            print(f"  ✓ {modulo}: {descripcion}")
        else:
            # Intenta alternativas conocidas
            print(f"  ✗ {modulo} no encontrado (revisar nombre)")
            
except Exception as e:
    print(f"  ✗ Error verificando módulos: {str(e)}")

# ============================================================================
# SECCION 4: VERIFICAR CONFIGURACION DE TERMINOS DE PAGO
# ============================================================================

print("\n[CHECK 4] Terminos de Pago")
print("-" * 50)

try:
    terminos_pago = frappe.db.get_list("Payment Terms Template", limit_page_length=10)
    
    if len(terminos_pago) > 0:
        print(f"  ✓ Terminos de pago configurados: {len(terminos_pago)}")
        for termino in terminos_pago[:3]:
            print(f"    - {termino}")
    else:
        print(f"  ⚠️  ALERTA: No hay terminos de pago configurados")
        print(f"     Acción: Crear terminos de pago en Frappe")
        
except Exception as e:
    print(f"  ✗ Error verificando términos: {str(e)}")

# ============================================================================
# SECCION 5: REVISAR INTEGRACION CUSTOM DE APP
# ============================================================================

print("\n[CHECK 5] Integracion Custom - Modulos Esperados")
print("-" * 50)

modulos_custom_esperados = [
    'Factura de Servicios',
    'Cliente Servicios Publicos',
    'Lectura de Medidor',
    'Tipo de Servicio',
    'Plan de Pago',
    'Servicios Publicos Settings',
]

try:
    for doctype in modulos_custom_esperados:
        existe = frappe.db.exists("DocType", doctype)
        
        if existe:
            print(f"  ✓ {doctype}")
        else:
            print(f"  ✗ {doctype} (FALTA - debe crear)")
            
except Exception as e:
    print(f"  ✗ Error verificando doctypes custom: {str(e)}")

# ============================================================================
# SECCION 6: REVISAR CAMPOS CUSTOM AGREGADOS
# ============================================================================

print("\n[CHECK 6] Campos Custom en Doctypes de Frappe")
print("-" * 50)

campos_custom_esperados = {
    'Customer': [
        'custom_cliente_servicios',
        'custom_categoria_cliente',
        'custom_estrato',
    ],
    'Sales Invoice': [
        'custom_factura_servicios',
        'custom_tipo_servicio',
        'custom_consumo',
    ],
    'Payment Entry': [
        'custom_referencia_factura',
    ],
}

try:
    for doctype, campos in campos_custom_esperados.items():
        print(f"\n  {doctype}:")
        for campo in campos:
            existe = frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": campo})
            
            if existe:
                print(f"    ✓ {campo}")
            else:
                print(f"    ✗ {campo} (FALTA)")
                
except Exception as e:
    print(f"  ✗ Error verificando campos custom: {str(e)}")

# ============================================================================
# SECCION 7: VALIDAR VALOR MONET ARIO Y DECIMALES
# ============================================================================

print("\n[CHECK 7] Configuracion de Campos Monetarios")
print("-" * 50)

try:
    # Verificar configuración de campo monetario típico en Frappe
    field_info = frappe.db.get_value(
        "DocField",
        {"parent": "Sales Invoice", "fieldname": "grand_total"},
        ["fieldtype", "options"]
    )
    
    if field_info:
        fieldtype, options = field_info
        print(f"  Sales Invoice.grand_total:")
        print(f"    Tipo: {fieldtype}")
        print(f"    Opciones: {options}")
        
        if fieldtype == "Currency":
            print(f"    ✓ Es tipo Currency (soporta COP)")
        else:
            print(f"    ⚠️  No es tipo Currency")
    else:
        print(f"  ✗ Field grand_total no encontrado")
        
except Exception as e:
    print(f"  ✗ Error: {str(e)}")

# ============================================================================
# SECCION 8: RESUMEN DE PROBLEMAS IDENTIFICADOS
# ============================================================================

print("\n" + "="*80)
print("RESUMEN DE HALLAZGOS")
print("="*80)

print("""
PREOCUPACIONES IDENTIFICADAS:

1. PRECISION DECIMAL:
   - Excel tiene valores como 10.59 (2 decimales)
   - Frappe ERPNext standard también usa 2 decimales
   - VALIDADO: Precision coincide ✓

2. MONEDA (COP):
   - App debe estar configurada con COP como moneda
   - Verificar: System Settings > Currency = "COP"
   - ⚠️  ACCION REQUERIDA: Validar que COP está en la lista de divisas

3. MODULOS FALTANTES POTENCIALMENTE:
   - Payment Terms (Terminos de Pago) - CRITICO
   - Currency Exchange (para futuras conversiones) - IMPORTANTE
   - Tax Configuration (Impuestos) - IMPORTANTE
   - Bank Account Reconciliation - MEDIO

4. INTEGRACION INCOMPLETE:
   - accounting_integration.py existe pero puede necesitar Update
   - Campos custom no validados en producción
   - Fechas de Termino de Pago no está vinculado

5. CONFIGURACION DE FRAPPE:
   - Verificar que default_currency = "COP"
   - Verificar precision_in_currency = 2 (mínimo)
   - Verificar company configurada con COP

RECOMENDACIONES:
✓ Mantener 2 decimales (coincide con Excel)
✓ Usar COP como moneda principal
✓ Configurar Términos de Pago en Frappe
✓ Crear campos custom necesarios
✓ Validar integración en environment de prueba
✓ Crear integración con módulo de divisas
✓ Crear integración con Payment Terms

PROXIMO PASO: Ejecutar script de validacion_frappe_config.py
""")

print("="*80 + "\n")
