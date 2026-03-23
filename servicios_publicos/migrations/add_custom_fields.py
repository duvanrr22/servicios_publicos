# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0
# Script de migración para agregar campos personalizados

import frappe
from frappe import _


def ejecutar():
	"""
	Ejecuta las migraciones necesarias:
	- Agrega campos personalizados a DocTypes estándar
	- Crea vinculaciones entre DocTypes personalizados y estándar
	"""
	
	print("\n=== EJECUTANDO MIGRACIÓN DE INTEGRACIONES ===\n")
	
	# 1. Agregar campos a Customer
	print("1. Agregando campos personalizados a Customer...")
	agregar_campos_customer()
	
	# 2. Agregar campos a Sales Invoice
	print("2. Agregando campos personalizados a Sales Invoice...")
	agregar_campos_sales_invoice()
	
	# 3. Agregar campos a Payment Entry
	print("3. Agregando campos personalizados a Payment Entry...")
	agregar_campos_payment_entry()
	
	# 4. Agregar campos a Journal Entry
	print("4. Agregando campos personalizados a Journal Entry...")
	agregar_campos_journal_entry()
	
	# 5. Agregar campos a Sales Invoice Item
	print("5. Agregando campos personalizados a Sales Invoice Item...")
	agregar_campos_sales_invoice_item()
	
	print("\n✅ MIGRACIÓN COMPLETADA\n")


def agregar_campos_customer():
	"""Agrega campos para vincular con Cliente Servicios Públicos"""
	
	campos = [
		{
			"fieldname": "custom_cliente_servicios",
			"label": "Cliente Servicios Públicos",
			"fieldtype": "Link",
			"options": "Cliente Servicios Públicos",
			"translatable": 0,
		},
		{
			"fieldname": "custom_numero_identificacion",
			"label": "Número de Identificación",
			"fieldtype": "Data",
			"translatable": 0,
		},
		{
			"fieldname": "custom_tipo_identificacion",
			"label": "Tipo de Identificación",
			"fieldtype": "Select",
			"options": "Cédula de Ciudadanía (CC)\nCédula de Extranjería (CE)\nNIT\nPasaporte",
			"translatable": 0,
		},
	]
	
	agregar_campos_a_doctype("Customer", campos, "servicios_publicos")


def agregar_campos_sales_invoice():
	"""Agrega campos para vincular con Factura de Servicios"""
	
	campos = [
		{
			"fieldname": "custom_factura_servicios",
			"label": "Factura Servicios Públicos",
			"fieldtype": "Link",
			"options": "Factura de Servicios",
			"translatable": 0,
		},
		{
			"fieldname": "custom_tipo_servicio",
			"label": "Tipo de Servicio",
			"fieldtype": "Link",
			"options": "Tipo de Servicio",
			"translatable": 0,
		},
	]
	
	agregar_campos_a_doctype("Sales Invoice", campos, "servicios_publicos")


def agregar_campos_payment_entry():
	"""Agrega campos para vincular con Pago de Servicios"""
	
	campos = [
		{
			"fieldname": "custom_pago_servicios",
			"label": "Pago Servicios Públicos",
			"fieldtype": "Link",
			"options": "Pago de Servicios",
			"translatable": 0,
		},
	]
	
	agregar_campos_a_doctype("Payment Entry", campos, "servicios_publicos")


def agregar_campos_journal_entry():
	"""Agrega campos para vincular con Factura de Servicios"""
	
	campos = [
		{
			"fieldname": "custom_factura_servicios",
			"label": "Factura Servicios Públicos",
			"fieldtype": "Link",
			"options": "Factura de Servicios",
			"translatable": 0,
		},
	]
	
	agregar_campos_a_doctype("Journal Entry", campos, "servicios_publicos")


def agregar_campos_sales_invoice_item():
	"""Agrega campos para detalles de consumo"""
	
	campos = [
		{
			"fieldname": "custom_consumo",
			"label": "Consumo",
			"fieldtype": "Float",
			"precision": "2",
			"translatable": 0,
		},
		{
			"fieldname": "custom_lectura_anterior",
			"label": "Lectura Anterior",
			"fieldtype": "Float",
			"precision": "2",
			"translatable": 0,
		},
		{
			"fieldname": "custom_lectura_actual",
			"label": "Lectura Actual",
			"fieldtype": "Float",
			"precision": "2",
			"translatable": 0,
		},
	]
	
	agregar_campos_a_doctype("Sales Invoice Item", campos, "servicios_publicos")


def agregar_campos_a_doctype(doctype_name, campos, modulo):
	"""
	Función genérica para agregar campos a un DocType
	
	Args:
		doctype_name: Nombre del DocType
		campos: Lista de campos a agregar
		modulo: Módulo al que pertenecen
	"""
	
	try:
		for campo in campos:
			# Verificar si el campo ya existe
			if frappe.db.exists("Custom Field", {
				"dt": doctype_name,
				"fieldname": campo["fieldname"]
			}):
				print(f"   ✓ Campo '{campo['fieldname']}' ya existe en {doctype_name}")
				continue
			
			# Crear campo personalizado
			custom_field = frappe.get_doc({
				"doctype": "Custom Field",
				"dt": doctype_name,
				"fieldname": campo["fieldname"],
				"label": campo["label"],
				"fieldtype": campo["fieldtype"],
				"options": campo.get("options", ""),
				"precision": campo.get("precision", ""),
				"translatable": campo.get("translatable", 0),
				"insert_after": "amended_from" if doctype_name == "Customer" else None,
			})
			
			custom_field.insert(ignore_permissions=True)
			print(f"   ✓ Campo '{campo['fieldname']}' agregado a {doctype_name}")
		
	except Exception as e:
		print(f"   ✗ Error agregando campos a {doctype_name}: {str(e)}")
		frappe.log_error(f"Error en migración: {str(e)}", "migrations.add_custom_fields")
