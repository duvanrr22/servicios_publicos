# add_custom_fields_payment_entry.py
# Agrega campos custom a Payment Entry para mejor auditoría y trazabilidad
# Migración: Este archivo debe ejecutarse después de currency_and_payment_terms_setup.py

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


def add_payment_entry_custom_fields():
    """
    Agrega campos custom a Payment Entry para:
    1. Registrar la moneda original de la factura
    2. Auditar términos de pago aplicados
    3. Rastrear cálculos de vencimiento
    """
    
    print("\n[MIGRATION] Agregando campos custom a Payment Entry...")
    
    try:
        custom_fields = {
            "Payment Entry": [
                {
                    "fieldname": "custom_moneda_factura",
                    "label": "Moneda Original",
                    "fieldtype": "Link",
                    "options": "Currency",
                    "read_only": 1,
                    "help": "Moneda en que se emitió la factura original (normalmente COP)",
                    "insert_after": "reference_date",
                    "hidden": 0,
                },
                {
                    "fieldname": "custom_section_terminos",
                    "label": "Información de Términos de Pago",
                    "fieldtype": "Section Break",
                    "insert_after": "custom_moneda_factura",
                },
                {
                    "fieldname": "custom_termino_pago_aplicado",
                    "label": "Término de Pago Aplicado",
                    "fieldtype": "Link",
                    "options": "Payment Terms Template",
                    "read_only": 1,
                    "help": "Término de pago que aplica a esta factura",
                    "insert_after": "custom_section_terminos",
                },
                {
                    "fieldname": "custom_dias_vencimiento",
                    "label": "Días para Vencimiento",
                    "fieldtype": "Int",
                    "read_only": 1,
                    "help": "Cantidad de días configurados en el término de pago",
                    "insert_after": "custom_termino_pago_aplicado",
                },
                {
                    "fieldname": "custom_fecha_factura_original",
                    "label": "Fecha Factura Original",
                    "fieldtype": "Date",
                    "read_only": 1,
                    "help": "Fecha en que se emitió la factura original",
                    "insert_after": "custom_dias_vencimiento",
                },
                {
                    "fieldname": "custom_fecha_vencimiento_calculada",
                    "label": "Fecha Vencimiento Calculada",
                    "fieldtype": "Date",
                    "read_only": 1,
                    "help": "Fecha de vencimiento calculada según términos de pago",
                    "insert_after": "custom_fecha_factura_original",
                },
                {
                    "fieldname": "custom_dias_mora",
                    "label": "Días de Mora",
                    "fieldtype": "Int",
                    "read_only": 1,
                    "help": "Días que lleva vencida la factura (si está atrasada)",
                    "insert_after": "custom_fecha_vencimiento_calculada",
                },
                {
                    "fieldname": "custom_column_auditoria",
                    "label": "Auditoría y Trazabilidad",
                    "fieldtype": "Column Break",
                    "insert_after": "custom_dias_mora",
                },
                {
                    "fieldname": "custom_referencia_factura_original",
                    "label": "Referencia Factura Original",
                    "fieldtype": "Link",
                    "options": "Sales Invoice",
                    "read_only": 1,
                    "help": "Enlace a la Sales Invoice original en Frappe",
                    "insert_after": "custom_column_auditoria",
                },
                {
                    "fieldname": "custom_factura_servicios_id",
                    "label": "ID Factura Servicios (Externa)",
                    "fieldtype": "Data",
                    "read_only": 1,
                    "help": "ID de la factura en el sistema externo de servicios públicos",
                    "insert_after": "custom_referencia_factura_original",
                },
            ]
        }
        
        # Crear los campos
        create_custom_field(custom_fields, update=True)
        
        frappe.db.commit()
        print("  ✅ Campos custom agregados a Payment Entry\n")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}\n")
        frappe.log_error(f"Error en add_payment_entry_custom_fields: {str(e)}", 
                        "add_payment_entry_custom_fields")
        raise


def verify_payment_entry_fields():
    """Verifica que los campos custom se hayan creado correctamente"""
    
    print("[VERIFY] Validando campos custom en Payment Entry...")
    
    expected_fields = [
        "custom_moneda_factura",
        "custom_termino_pago_aplicado",
        "custom_dias_vencimiento",
        "custom_fecha_factura_original",
        "custom_fecha_vencimiento_calculada",
        "custom_dias_mora",
        "custom_referencia_factura_original",
        "custom_factura_servicios_id",
    ]
    
    try:
        all_exist = True
        for field in expected_fields:
            field_exists = frappe.db.exists(
                "Custom Field",
                {"dt": "Payment Entry", "fieldname": field}
            )
            
            if field_exists:
                print(f"  ✓ {field}")
            else:
                print(f"  ✗ {field} (NO EXISTE)")
                all_exist = False
        
        if all_exist:
            print("  ✅ Todos los campos están presentes\n")
        else:
            print("  ⚠️  Faltan algunos campos\n")
        
        return all_exist
        
    except Exception as e:
        print(f"  ✗ Error en validación: {str(e)}\n")
        return False


# Función para poblar campos cuando se crea Payment Entry
def populate_payment_entry_fields(payment_entry_doc):
    """
    Hook para ser llamado cuando se crea un Payment Entry
    Llena automáticamente los campos custom con datos de la factura
    
    Uso: Agregar al hooks.py
    """
    
    try:
        # Obtener la factura original referenciada
        if payment_entry_doc.references and len(payment_entry_doc.references) > 0:
            ref = payment_entry_doc.references[0]
            
            if ref.reference_doctype == "Sales Invoice":
                sales_invoice = frappe.get_doc("Sales Invoice", ref.reference_name)
                
                # Poblar moneda
                payment_entry_doc.custom_moneda_factura = sales_invoice.currency or "COP"
                
                # Poblar términos si existen
                if hasattr(sales_invoice, 'payment_terms_template'):
                    payment_entry_doc.custom_termino_pago_aplicado = sales_invoice.payment_terms_template
                
                # Poblar fechas
                payment_entry_doc.custom_fecha_factura_original = sales_invoice.posting_date
                payment_entry_doc.custom_fecha_vencimiento_calculada = sales_invoice.due_date
                
                # Calcular días de mora si está atrasada
                from datetime import datetime
                if sales_invoice.due_date:
                    dias_mora = (datetime.now().date() - sales_invoice.due_date).days
                    if dias_mora > 0:
                        payment_entry_doc.custom_dias_mora = dias_mora
                
                # Referencia de factura original
                payment_entry_doc.custom_referencia_factura_original = ref.reference_name
                
                # ID de factura Services si está disponible
                if hasattr(sales_invoice, 'custom_factura_servicios'):
                    payment_entry_doc.custom_factura_servicios_id = sales_invoice.custom_factura_servicios
        
    except Exception as e:
        frappe.log_error(f"Error poblando fields: {str(e)}", 
                        "populate_payment_entry_fields")


# ============================================================================
# MAIN - Para testing
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MIGRATION: CAMPOS CUSTOM PARA PAYMENT ENTRY")
    print("="*80)
    
    add_payment_entry_custom_fields()
    verify_payment_entry_fields()
    
    print("="*80)
    print("✅ MIGRATION COMPLETADA")
    print("="*80 + "\n")
