# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0
# API para integración y sincronización

import frappe
from frappe.utils import getdate
from servicios_publicos.integrations.accounting_integration import AccountingIntegration


@frappe.whitelist()
def sincronizar_cliente(cliente_name):
	"""API: Sincroniza un Cliente Servicios Públicos con Customer"""
	try:
		result = AccountingIntegration.sincronizar_cliente_a_customer(cliente_name)
		return result
	except Exception as e:
		frappe.throw(str(e))


@frappe.whitelist()
def sincronizar_factura(factura_name):
	"""API: Crea Sales Invoice y Journal Entry desde una Factura de Servicios"""
	try:
		settings = frappe.get_single("Servicios Publicos Settings")
		results = {}
		
		# Crear Sales Invoice
		if settings.auto_create_sales_invoice:
			results["sales_invoice"] = AccountingIntegration.crear_sales_invoice_desde_factura(factura_name)
		
		# Crear Journal Entry
		if settings.auto_create_journal_entry:
			results["journal_entry"] = AccountingIntegration.crear_journal_entry_desde_factura(factura_name)
		
		return results
	except Exception as e:
		frappe.throw(str(e))


@frappe.whitelist()
def sincronizar_pago(pago_name):
	"""API: Crea Payment Entry desde un Pago de Servicios"""
	try:
		result = AccountingIntegration.crear_payment_entry_desde_pago(pago_name)
		return result
	except Exception as e:
		frappe.throw(str(e))


@frappe.whitelist()
def obtener_estado_integracion(doctype_name, document_name):
	"""API: Obtiene el estado de integración de un documento"""
	try:
		doc = frappe.get_doc(doctype_name, document_name)
		
		estado = {
			"doctype": doctype_name,
			"document": document_name,
			"timestamp": getdate(),
		}
		
		# Verificar campos de integración según el tipo de documento
		if doctype_name == "Cliente Servicios Públicos":
			estado["customer_id"] = doc.get("customer_id", "")
			estado["sincronizado"] = bool(doc.get("customer_id"))
		
		elif doctype_name == "Factura de Servicios":
			estado["sales_invoice_id"] = doc.get("sales_invoice_id", "")
			estado["journal_entry_id"] = doc.get("journal_entry_id", "")
			estado["estado_factura"] = doc.get("estado_factura", "")
		
		elif doctype_name == "Pago de Servicios":
			estado["payment_entry_id"] = doc.get("payment_entry_id", "")
			estado["estado_pago"] = doc.get("estado_pago", "")
		
		return estado
		
	except Exception as e:
		frappe.throw(str(e))


@frappe.whitelist()
def obtener_estadisticas_integracion():
	"""API: Obtiene estadísticas de integración"""
	try:
		stats = {
			"clientes_totales": len(frappe.get_list("Cliente Servicios Públicos")),
			"clientes_sincronizados": len(frappe.get_list(
				"Cliente Servicios Públicos",
				filters={"customer_id": ["!=", ""]}
			)),
			"facturas_totales": len(frappe.get_list("Factura de Servicios")),
			"facturas_sincronizadas": len(frappe.get_list(
				"Factura de Servicios",
				filters={"sales_invoice_id": ["!=", ""]}
			)),
			"pagos_totales": len(frappe.get_list("Pago de Servicios")),
			"pagos_sincronizados": len(frappe.get_list(
				"Pago de Servicios",
				filters={"payment_entry_id": ["!=", ""]}
			)),
		}
		
		# Calcular porcentajes
		if stats["clientes_totales"] > 0:
			stats["porcentaje_clientes"] = round(
				(stats["clientes_sincronizados"] / stats["clientes_totales"]) * 100, 2
			)
		else:
			stats["porcentaje_clientes"] = 0
		
		if stats["facturas_totales"] > 0:
			stats["porcentaje_facturas"] = round(
				(stats["facturas_sincronizadas"] / stats["facturas_totales"]) * 100, 2
			)
		else:
			stats["porcentaje_facturas"] = 0
		
		if stats["pagos_totales"] > 0:
			stats["porcentaje_pagos"] = round(
				(stats["pagos_sincronizados"] / stats["pagos_totales"]) * 100, 2
			)
		else:
			stats["porcentaje_pagos"] = 0
		
		return stats
		
	except Exception as e:
		frappe.throw(str(e))
