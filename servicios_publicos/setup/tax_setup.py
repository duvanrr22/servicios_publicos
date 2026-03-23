# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0
# Setup de Templates de Impuestos para Colombia

import frappe
from frappe import _


def setup_tax_templates():
	"""Crea los templates de impuestos para servicios públicos en Colombia"""
	
	print("\n=== CONFIGURANDO TAX TEMPLATES PARA COLOMBIA ===\n")
	
	# 1. Crear Tax Category
	print("1. Creando Tax Categories...")
	crear_tax_categories()
	
	# 2. Crear Sales Tax Template
	print("2. Creando Sales Tax Templates...")
	crear_sales_tax_templates()
	
	# 3. Crear Item Tax Templates
	print("3. Creando Item Tax Templates...")
	crear_item_tax_templates()
	
	print("\n✅ TAX TEMPLATES CONFIGURADOS\n")


def crear_tax_categories():
	"""Crea las categorías de impuestos"""
	
	company = "Servicios Públicos Colombia"
	
	categories = [
		{"name": "IVA Estándar", "description": "IVA 19% - Tasa estándar"},
		{"name": "IVA Reducido", "description": "IVA 5% - Tasa reducida"},
		{"name": "Exento", "description": "Exento de IVA"},
		{"name": "Cero IVA", "description": "IVA 0%"},
	]
	
	created = 0
	for cat in categories:
		if frappe.db.exists("Tax Category", cat["name"]):
			print(f"   ✓ Categoría '{cat['name']}' ya existe")
			continue
		
		try:
			tax_cat = frappe.get_doc({
				"doctype": "Tax Category",
				"name": cat["name"],
				"description": cat["description"],
			})
			tax_cat.insert(ignore_permissions=True)
			created += 1
			print(f"   ✓ Categoría '{cat['name']}' creada")
		except Exception as e:
			print(f"   ✗ Error: {str(e)}")
	
	if created > 0:
		print(f"   Total: {created} categorías nuevas\n")


def crear_sales_tax_templates():
	"""Crea Sales Tax Templates por tipo de servicio"""
	
	company = "Servicios Públicos Colombia"
	
	# Obtener tipos de servicio
	tipos_servicio = frappe.get_all("Tipo de Servicio", fields=["name", "nombre_servicio"])
	
	templates = [
		{
			"name": "IVA 19% - Servicios",
			"description": "Template de IVA 19% para servicios públicos",
			"tipo_servicio": None,  # Aplica a todos
			"taxes": [
				{
					"tax_type": "IVA (19%)",
					"account": "6010 - IVA por Pagar",
					"rate": 19,
				}
			]
		},
		{
			"name": "IVA 5% - Servicios Básicos",
			"description": "Template de IVA 5% para servicios básicos",
			"tipo_servicio": None,
			"taxes": [
				{
					"tax_type": "IVA (5%)",
					"account": "6010 - IVA por Pagar",
					"rate": 5,
				}
			]
		},
		{
			"name": "Exento - Agua",
			"description": "No aplica impuesto a servicio de agua",
			"tipo_servicio": None,
			"taxes": []  # Sin impuestos
		}
	]
	
	created = 0
	for template in templates:
		template_name = template["name"]
		
		if frappe.db.exists("Sales Taxes and Charges Template", template_name):
			print(f"   ✓ Template '{template_name}' ya existe")
			continue
		
		try:
			tax_template = frappe.get_doc({
				"doctype": "Sales Taxes and Charges Template",
				"name": template_name,
				"title": template_name,
				"description": template["description"],
				"company": company,
				"is_default": 0,
				"taxes": template["taxes"],
			})
			
			tax_template.insert(ignore_permissions=True)
			created += 1
			print(f"   ✓ Template '{template_name}' creado")
			
		except Exception as e:
			print(f"   ✗ Error creando template {template_name}: {str(e)}")
	
	if created > 0:
		print(f"   Total: {created} templates nuevos\n")


def crear_item_tax_templates():
	"""Crea Item Tax Templates para cada tipo de servicio"""
	
	try:
		# Crear template base para IVA 19%
		if not frappe.db.exists("Item Tax Template", "IVA 19% Colombia"):
			item_tax = frappe.get_doc({
				"doctype": "Item Tax Template",
				"name": "IVA 19% Colombia",
				"title": "IVA 19%",
				"taxes": [
					{
						"tax_type": "IVA (19%)",
						"tax_rate": 19,
					}
				]
			})
			item_tax.insert(ignore_permissions=True)
			print("   ✓ Item Tax Template 'IVA 19% Colombia' creado")
		
		# Crear template para IVA 5%
		if not frappe.db.exists("Item Tax Template", "IVA 5% Colombia"):
			item_tax = frappe.get_doc({
				"doctype": "Item Tax Template",
				"name": "IVA 5% Colombia",
				"title": "IVA 5%",
				"taxes": [
					{
						"tax_type": "IVA (5%)",
						"tax_rate": 5,
					}
				]
			})
			item_tax.insert(ignore_permissions=True)
			print("   ✓ Item Tax Template 'IVA 5% Colombia' creado")
		
		# Crear template para Exento
		if not frappe.db.exists("Item Tax Template", "Exento - Colombia"):
			item_tax = frappe.get_doc({
				"doctype": "Item Tax Template",
				"name": "Exento - Colombia",
				"title": "Exento",
				"taxes": []
			})
			item_tax.insert(ignore_permissions=True)
			print("   ✓ Item Tax Template 'Exento - Colombia' creado")
			
	except Exception as e:
		print(f"   ✗ Error creando Item Tax Templates: {str(e)}")


def crear_tax_accounts():
	"""Crea las cuentas para impuestos en el Chart of Accounts"""
	
	company = "Servicios Públicos Colombia"
	
	tax_accounts = [
		{
			"name": "6010 - IVA por Pagar",
			"account_type": "Tax",
			"is_group": 0,
			"parent_account": "60 - IMPUESTOS Y CONTRIBUCIONES"
		},
		{
			"name": "6020 - IVA Recibido",
			"account_type": "Tax",
			"is_group": 0,
			"parent_account": "60 - IMPUESTOS Y CONTRIBUCIONES"
		},
	]
	
	created = 0
	for acc in tax_accounts:
		if frappe.db.exists("Account", {"account_name": acc["name"], "company": company}):
			print(f"   ✓ Cuenta '{acc['name']}' ya existe")
			continue
		
		try:
			account = frappe.get_doc({
				"doctype": "Account",
				"account_name": acc["name"],
				"company": company,
				"account_type": acc["account_type"],
				"is_group": acc["is_group"],
				"parent_account": acc["parent_account"],
			})
			account.insert(ignore_permissions=True)
			created += 1
			print(f"   ✓ Cuenta '{acc['name']}' creada")
		except Exception as e:
			print(f"   ✗ Error: {str(e)}")
	
	if created > 0:
		print(f"   Total: {created} cuentas nuevas de impuestos\n")


if __name__ == "__main__":
	setup_tax_templates()
