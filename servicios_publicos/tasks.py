# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0
# Tareas Scheduladas

import frappe
from frappe.utils import getdate
from servicios_publicos.integrations.accounting_integration import AccountingIntegration


def sincronizar_clientes_con_customer():
	"""Sincroniza diariamente los Clientes Servicios Públicos con Customer de Frappe"""
	
	print("\n=== SINCRONIZACIÓN DE CLIENTES ===")
	
	try:
		# Obtener configuración
		settings = frappe.get_single("Servicios Publicos Settings")
		
		if not settings.sync_to_standard_frappe:
			print("Sincronización deshabilitada en configuración")
			return
		
		# Obtener clientes sin sincronizar
		clientes = frappe.get_all(
			"Cliente Servicios Públicos",
			filters={"customer_id": ""},
			fields=["name"]
		)
		
		sincronizados = 0
		errores = 0
		
		for cliente in clientes:
			try:
				result = AccountingIntegration.sincronizar_cliente_a_customer(cliente.name)
				if result["status"] in ["created", "already_exists"]:
					sincronizados += 1
				else:
					errores += 1
			except Exception as e:
				print(f"Error sincronizando {cliente.name}: {str(e)}")
				errores += 1
		
		print(f"✓ Sincronización completada: {sincronizados} clientes, {errores} errores")
		
	except Exception as e:
		frappe.log_error(
			f"Error en tarea sincronizar_clientes_con_customer: {str(e)}",
			"tasks.sincronizar_clientes_con_customer"
		)
		print(f"✗ Error: {str(e)}")


def sincronizar_pagos_pendientes():
	"""Sincroniza pagos pendientes cada hora"""
	
	print("\n=== SINCRONIZACIÓN DE PAGOS ===")
	
	try:
		settings = frappe.get_single("Servicios Publicos Settings")
		
		if not settings.sync_to_standard_frappe or not settings.auto_create_payment_entry:
			print("Sincronización de pagos deshabilitada")
			return
		
		# Obtener pagos sin sincronizar
		pagos = frappe.get_all(
			"Pago de Servicios",
			filters=[
				("estado_pago", "=", "Registrada"),
				("payment_entry_id", "=", "")
			],
			fields=["name"]
		)
		
		sincronizados = 0
		errores = 0
		
		for pago in pagos:
			try:
				result = AccountingIntegration.crear_payment_entry_desde_pago(pago.name)
				if result["status"] == "success":
					sincronizados += 1
				else:
					errores += 1
			except Exception as e:
				print(f"Error sincronizando pago {pago.name}: {str(e)}")
				errores += 1
		
		print(f"✓ Sincronización de pagos: {sincronizados} pagos, {errores} errores")
		
	except Exception as e:
		frappe.log_error(
			f"Error en tarea sincronizar_pagos_pendientes: {str(e)}",
			"tasks.sincronizar_pagos_pendientes"
		)
		print(f"✗ Error: {str(e)}")


def generar_reportes_diarios():
	"""Genera reportes diarios automáticos"""
	
	print("\n=== GENERACIÓN DE REPORTES DIARIOS ===")
	
	try:
		from servicios_publicos.reports.daily_summary import generar_resumen_diario
		
		result = generar_resumen_diario()
		print(f"✓ Reporte diario generado: {result}")
		
	except Exception as e:
		frappe.log_error(
			f"Error generando reportes diarios: {str(e)}",
			"tasks.generar_reportes_diarios"
		)
		print(f"✗ Error: {str(e)}")
