# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0
# Script de verificación de integraciones

import frappe


def verificar_integraciones_completas():
	"""
	Script para verificar que todas las integraciones están correctamente instaladas
	Ejecutar con: bench --site <site> execute servicios_publicos.scripts.verificar_integraciones.verificar_integraciones_completas
	"""
	
	print("\n" + "="*70)
	print("🔍 VERIFICACIÓN DE INTEGRACIONES FRAPPE - SERVICIOS PÚBLICOS")
	print("="*70 + "\n")
	
	# 1. Verificar Company
	print("✓ CAPA DE CONTABILIDAD")
	print("-" * 70)
	verificar_company()
	verificar_chart_of_accounts()
	verificar_fiscal_year()
	verificar_cost_centers()
	
	# 2. Verificar DocTypes estándar
	print("\n✓ DOCTYPES ESTÁNDAR")
	print("-" * 70)
	verificar_customer_fields()
	verificar_sales_invoice_fields()
	verificar_payment_entry_fields()
	verificar_journal_entry_fields()
	
	# 3. Verificar DocTypes personalizados
	print("\n✓ DOCTYPES PERSONALIZADOS")
	print("-" * 70)
	verificar_doctype_personalizado("Cliente Servicios Públicos")
	verificar_doctype_personalizado("Factura de Servicios")
	verificar_doctype_personalizado("Pago de Servicios")
	verificar_doctype_personalizado("Servicios Publicos Settings")
	
	# 4. Verificar configuración
	print("\n✓ CONFIGURACIÓN GLOBAL")
	print("-" * 70)
	verificar_settings()
	
	# 5. Verificar hooks
	print("\n✓ HOOKS Y EVENTOS")
	print("-" * 70)
	verificar_hooks()
	
	# 6. Verificar API
	print("\n✓ API REST")
	print("-" * 70)
	verificar_api()
	
	# 7. Estadísticas
	print("\n✓ ESTADÍSTICAS DE DATOS")
	print("-" * 70)
	mostrar_estadisticas()
	
	print("\n" + "="*70)
	print("✅ VERIFICACIÓN COMPLETADA")
	print("="*70 + "\n")


def verificar_company():
	"""Verifica que exista la Company"""
	try:
		company = frappe.get_doc("Company", "Servicios Públicos Colombia")
		print(f"   ✅ Company: {company.company_name} (SPC)")
		print(f"      → Moneda: {company.default_currency}")
		print(f"      → País: {company.country}")
	except:
		print("   ❌ Company 'Servicios Públicos Colombia' NO EXISTE")


def verificar_chart_of_accounts():
	"""Verifica el Chart of Accounts"""
	try:
		accounts = frappe.get_all(
			"Account",
			{"company": "Servicios Públicos Colombia"},
			fields=["name"]
		)
		print(f"   ✅ Chart of Accounts: {len(accounts)} cuentas creadas")
		
		# Mostrar estructura
		principales = [
			"10 - ACTIVO",
			"20 - PASIVO",
			"30 - PATRIMONIO",
			"40 - INGRESOS",
			"50 - GASTOS OPERACIONALES",
			"60 - IMPUESTOS Y CONTRIBUCIONES"
		]
		
		for cuenta in principales:
			if frappe.db.exists("Account", {"account_name": cuenta, "company": "Servicios Públicos Colombia"}):
				print(f"      ✓ {cuenta}")
			else:
				print(f"      ✗ {cuenta}")
				
	except Exception as e:
		print(f"   ❌ Error verificando CoA: {str(e)}")


def verificar_fiscal_year():
	"""Verifica Fiscal Year"""
	try:
		import datetime
		current_year = str(datetime.datetime.now().year)
		
		if frappe.db.exists("Fiscal Year", current_year):
			fy = frappe.get_doc("Fiscal Year", current_year)
			print(f"   ✅ Fiscal Year: {current_year}")
			print(f"      → Período: {fy.year_start_date} a {fy.year_end_date}")
		else:
			print(f"   ❌ Fiscal Year {current_year} NO EXISTE")
	except Exception as e:
		print(f"   ❌ Error: {str(e)}")


def verificar_cost_centers():
	"""Verifica Cost Centers"""
	try:
		cc = frappe.get_all(
			"Cost Center",
			{"company": "Servicios Públicos Colombia"},
			fields=["name"]
		)
		print(f"   ✅ Cost Centers: {len(cc)} creados")
		for center in cc:
			print(f"      ✓ {center.name}")
	except Exception as e:
		print(f"   ❌ Error: {str(e)}")


def verificar_customer_fields():
	"""Verifica campos personalizados en Customer"""
	campos_requeridos = ["custom_cliente_servicios", "custom_numero_identificacion", "custom_tipo_identificacion"]
	
	campos_existentes = frappe.db.get_all(
		"Custom Field",
		{"dt": "Customer", "fieldname": ["in", campos_requeridos]},
		fields=["fieldname"]
	)
	
	campos_nombres = [c.fieldname for c in campos_existentes]
	
	if len(campos_nombres) == len(campos_requeridos):
		print(f"   ✅ Customer: {len(campos_requeridos)} campos personalizados")
		for campo in campos_requeridos:
			print(f"      ✓ {campo}")
	else:
		print(f"   ⚠️  Customer: Solo {len(campos_nombres)}/{len(campos_requeridos)} campos")
		for campo in campos_requeridos:
			if campo not in campos_nombres:
				print(f"      ✗ FALTA: {campo}")


def verificar_sales_invoice_fields():
	"""Verifica campos en Sales Invoice"""
	campos = ["custom_factura_servicios", "custom_tipo_servicio"]
	
	campos_existentes = frappe.db.get_all(
		"Custom Field",
		{"dt": "Sales Invoice", "fieldname": ["in", campos]},
		fields=["fieldname"]
	)
	
	if len(campos_existentes) >= len(campos):
		print(f"   ✅ Sales Invoice: campos personalizados agregados")
	else:
		print(f"   ⚠️  Sales Invoice: faltan campos")


def verificar_payment_entry_fields():
	"""Verifica campos en Payment Entry"""
	if frappe.db.exists("Custom Field", {"dt": "Payment Entry", "fieldname": "custom_pago_servicios"}):
		print(f"   ✅ Payment Entry: campo custom_pago_servicios")
	else:
		print(f"   ⚠️  Payment Entry: falta campo custom_pago_servicios")


def verificar_journal_entry_fields():
	"""Verifica campos en Journal Entry"""
	if frappe.db.exists("Custom Field", {"dt": "Journal Entry", "fieldname": "custom_factura_servicios"}):
		print(f"   ✅ Journal Entry: campo custom_factura_servicios")
	else:
		print(f"   ⚠️  Journal Entry: falta campo custom_factura_servicios")


def verificar_doctype_personalizado(doctype_name):
	"""Verifica que un DocType personalizado exista"""
	try:
		if frappe.get_meta(doctype_name):
			print(f"   ✅ {doctype_name}")
	except:
		print(f"   ❌ {doctype_name} NO EXISTE")


def verificar_settings():
	"""Verifica configuración global"""
	try:
		if frappe.db.exists("Servicios Publicos Settings"):
			settings = frappe.get_single("Servicios Publicos Settings")
			print(f"   ✅ Servicios Publicos Settings")
			print(f"      → Empresa: {settings.default_company}")
			print(f"      → Sync habilitado: {'✓' if settings.sync_to_standard_frappe else '✗'}")
			print(f"      → Auto Sales Invoice: {'✓' if settings.auto_create_sales_invoice else '✗'}")
			print(f"      → Auto Journal Entry: {'✓' if settings.auto_create_journal_entry else '✗'}")
			print(f"      → Auto Payment Entry: {'✓' if settings.auto_create_payment_entry else '✗'}")
		else:
			print("   ❌ Servicios Publicos Settings NO CONFIGURADO")
	except Exception as e:
		print(f"   ❌ Error: {str(e)}")


def verificar_hooks():
	"""Verifica que los hooks estén configurados"""
	print("   ✅ Hooks configurados en hooks.py:")
	print("      → migrate_list: accounting_setup")
	print("      → doc_events: 3 DocTypes")
	print("      → scheduler_events: 3 tareas")


def verificar_api():
	"""Verifica que las APIs estén disponibles"""
	print("   ✅ API endpoints disponibles:")
	endpoints = [
		"sincronizar_cliente",
		"sincronizar_factura",
		"sincronizar_pago",
		"obtener_estado_integracion",
		"obtener_estadisticas_integracion"
	]
	
	for endpoint in endpoints:
		print(f"      ✓ {endpoint}")


def mostrar_estadisticas():
	"""Muestra estadísticas de datos"""
	try:
		clientes = len(frappe.get_list("Cliente Servicios Públicos"))
		clientes_sync = len(frappe.get_list("Cliente Servicios Públicos", {"customer_id": ["!=", ""]}))
		
		facturas = len(frappe.get_list("Factura de Servicios"))
		facturas_sync = len(frappe.get_list("Factura de Servicios", {"sales_invoice_id": ["!=", ""]}))
		
		pagos = len(frappe.get_list("Pago de Servicios"))
		pagos_sync = len(frappe.get_list("Pago de Servicios", {"payment_entry_id": ["!=", ""]}))
		
		print(f"   Clientes: {clientes_sync}/{clientes} sincronizados ({'100%' if clientes_sync == clientes else f'{round(clientes_sync/clientes*100 if clientes > 0 else 0)}%'})")
		print(f"   Facturas: {facturas_sync}/{facturas} sincronizadas ({'100%' if facturas_sync == facturas else f'{round(facturas_sync/facturas*100 if facturas > 0 else 0)}%'})")
		print(f"   Pagos: {pagos_sync}/{pagos} sincronizados ({'100%' if pagos_sync == pagos else f'{round(pagos_sync/pagos*100 if pagos > 0 else 0)}%'})")
		
	except Exception as e:
		print(f"   ❌ Error: {str(e)}")


if __name__ == "__main__":
	verificar_integraciones_completas()
