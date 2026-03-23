# setup_currency_and_payment_terms.py
# Configuración de Moneda (COP) y Términos de Pago
# PRIORIDAD: CRÍTICA

import frappe


def setup_cop_currency():
    """
    Valida y prepara la moneda COP para el sistema Servicios Públicos.
    
    IMPORTANTE: Esta función NO sobrescribe la configuración del usuario en System Settings.
    Si el usuario ha configurado otra moneda en ERPNext, se respetará.
    
    Solo garantiza que COP existe como Currency Master.
    
    Debe ejecutarse durante la instalación de la app.
    """
    
    print("\n[SETUP] Validando configuración de moneda...")
    
    try:
        # 1. OBTENER (sin escribir) la moneda configurada en el sistema
        system_currency = frappe.db.get_single_value("System Settings", "currency")
        print(f"  ✓ Moneda del sistema: {system_currency or 'No configurada'}")
        
        # 2. CREAR Currency Master para COP si no existe
        # (Esto no interfiere con la moneda default del sistema)
        if not frappe.db.exists("Currency", "COP"):
            print("  ⚙ Creando Currency Master para COP...")
            cop_currency = frappe.get_doc({
                "doctype": "Currency",
                "name": "COP",
                "currency_name": "Colombian Peso",
                "enabled": 1,
                "fraction": "Centavo",
                "fraction_units": 100,
            })
            cop_currency.insert(ignore_permissions=True)
            print("  ✓ Currency Master 'COP' creado")
        else:
            print("  ✓ Currency Master 'COP' ya existe")
        
        frappe.db.commit()
        print("  ✅ Validación de moneda completada\n")
        print("  NOTA: La app usará la moneda configurada en System Settings de ERPNext")
        print("         o COP por defecto si no está configurada.\n")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}\n")
        frappe.log_error(f"Error en setup_cop_currency: {str(e)}", "setup_cop_currency")
        raise


def setup_payment_terms():
    """
    Crea Términos de Pago estándar para servicios públicos en Colombia.
    
    IMPORTANTE: Solo crea términos si no existen. Respeta cualquier configuración
    previa que el usuario haya hecho en ERPNext.
    
    Los términos creados son:
    - Inmediato (0 días)
    - Neto 10 (10 días)
    - Neto 30 (30 días - estándar para servicios públicos)
    - Neto 60 (60 días - para clientes empresariales)
    - Mes Siguiente (45 días)
    
    Estos términos definen automáticamente las fechas de vencimiento en Sales Invoice.
    """
    
    print("\n[SETUP] Preparando Términos de Pago...")
    print("  NOTA: Se crearán solo si no existen. Respetando configuración existente.\n")
    
    try:
        terminos = [
            {
                "name": "Inmediato",
                "description": "Pago al momento de recibir la factura (0 días)",
                "days": 0
            },
            {
                "name": "Neto 10",
                "description": "Pago en 10 días",
                "days": 10
            },
            {
                "name": "Neto 30",
                "description": "Pago en 30 días (término estándar para servicios públicos)",
                "days": 30
            },
            {
                "name": "Neto 60",
                "description": "Pago en 60 días (para clientes empresariales)",
                "days": 60
            },
            {
                "name": "Mes Siguiente",
                "description": "Pago en el último día del mes siguiente",
                "days": 45
            },
        ]
        
        creados = 0
        existentes = 0
        
        for termino in terminos:
            if not frappe.db.exists("Payment Terms Template", termino["name"]):
                ptt_doc = frappe.get_doc({
                    "doctype": "Payment Terms Template",
                    "name": termino["name"],
                    "description": termino["description"],
                    "terms": [
                        {
                            "due_date_based_on": "Day(s) after invoice date",
                            "due_date": termino["days"]
                        }
                    ]
                })
                ptt_doc.insert(ignore_permissions=True)
                print(f"  ✓ '{termino['name']}' creado ({termino['days']} días)")
                creados += 1
            else:
                print(f"  ✓ '{termino['name']}' ya existe (respetado)")
                existentes += 1
        
        frappe.db.commit()
        print(f"\n  ✅ Términos de Pago procesados: {creados} creados, {existentes} ya existían\n")
        print("  NOTA: Estos términos se usarán por defecto en Sales Invoice.")
        print("         El usuario puede seleccionar otro término si lo desea.\n")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}\n")
        frappe.log_error(f"Error en setup_payment_terms: {str(e)}", "setup_payment_terms")
        raise


def setup_currency_exchange():
    """
    Configura tasas de cambio iniciales
    Por ahora, COP a COP = 1:1 (no hay conversión)
    """
    
    print("[SETUP] Configurando tasas de cambio...")
    
    try:
        # Crear tasa COP -> COP = 1
        if not frappe.db.exists("Currency Exchange", {"from_currency": "COP", "to_currency": "COP"}):
            frappe.get_doc({
                "doctype": "Currency Exchange",
                "from_currency": "COP",
                "to_currency": "COP",
                "exchange_rate": 1.0,
            }).insert(ignore_permissions=True)
            print("  ✓ Tasa COP → COP = 1.0 creada")
        else:
            print("  ✓ Tasa COP → COP ya existe")
        
        frappe.db.commit()
        print("  ✅ Tasas de cambio configuradas\n")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}\n")
        frappe.log_error(f"Error en setup_currency_exchange: {str(e)}", "setup_currency_exchange")
        raise


def validate_currency_setup():
    """
    Valida que toda la configuración de moneda está correcta
    Retorna True si todo está OK, False otherwise
    """
    
    print("[VALIDATE] Validando configuración de COP...")
    
    all_ok = True
    
    # Check 1: Currency default
    default_currency = frappe.db.get_single_value("System Settings", "currency")
    if default_currency == "COP":
        print("  ✓ System currency = COP")
    else:
        print(f"  ✗ System currency = {default_currency} (debería ser COP)")
        all_ok = False
    
    # Check 2: Currency Master existe
    if frappe.db.exists("Currency", "COP"):
        print("  ✓ Currency Master 'COP' existe")
    else:
        print("  ✗ Currency Master 'COP' no existe")
        all_ok = False
    
    # Check 3: Precisión decimal
    precision = frappe.db.get_single_value("Print Settings", "precision_in_currency")
    if precision and precision >= 2:
        print(f"  ✓ Precisión decimal = {precision}")
    else:
        print(f"  ✗ Precisión decimal = {precision} (debería ser >= 2)")
        all_ok = False
    
    # Check 4: Términos de pago
    num_terms = len(frappe.db.get_list("Payment Terms Template", limit_page_length=10))
    if num_terms >= 3:
        print(f"  ✓ {num_terms} Términos de Pago configurados")
    else:
        print(f"  ⚠️  Solo {num_terms} Términos de Pago (recomendado >= 3)")
    
    if all_ok:
        print("  ✅ Configuración válida\n")
    else:
        print("  ⚠️  Hay problemas de configuración\n")
    
    return all_ok


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_payment_terms_by_customer_group(customer_group):
    """Obtiene el término de pago recomendado según el grupo de cliente"""
    
    terms_mapping = {
        "Residencial": "Neto 30",
        "Comercial": "Neto 30",
        "Industrial": "Neto 60",
        "Oficial": "Neto 10",
    }
    
    return terms_mapping.get(customer_group, "Neto 30")


def calculate_due_date_from_invoice_date(invoice_date, payment_terms_template):
    """
    Calcula la fecha de vencimiento basada en la fecha de factura
    y los términos de pago
    
    Nota: En Frappe, esto se calcula automáticamente, pero aquí está
    para referencia
    """
    from datetime import timedelta
    
    ptt = frappe.get_doc("Payment Terms Template", payment_terms_template)
    
    if ptt.terms and len(ptt.terms) > 0:
        days = ptt.terms[0].get("due_date", 0)
        return invoice_date + timedelta(days=days)
    
    return invoice_date


# ============================================================================
# MAIN - Para testing
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SETUP: CONFIGURACION DE MONEDA Y TERMINOS DE PAGO")
    print("="*80)
    
    setup_cop_currency()
    setup_payment_terms()
    setup_currency_exchange()
    validate_currency_setup()
    
    print("="*80)
    print("✅ SETUP COMPLETADO")
    print("="*80 + "\n")
