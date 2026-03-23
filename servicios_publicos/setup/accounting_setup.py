# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0
# Script de inicialización para contabilidad

import frappe
from frappe.utils import getdate


def setup_company_and_accounting():
	"""
	Crea la estructura básica de Contabilidad:
	- Company
	- Chart of Accounts
	- Cost Centers
	- Fiscal Year
	"""
	
	print("\n=== INICIALIZANDO MÓDULO DE CONTABILIDAD ===\n")
	
	# 1. Crear Company
	print("1. Creando Empresa...")
	crear_company()
	
	# 2. Crear Chart of Accounts
	print("2. Creando Plan de Cuentas...")
	crear_chart_of_accounts()
	
	# 3. Crear Cost Centers
	print("3. Creando Centros de Costo...")
	crear_cost_centers()
	
	# 4. Crear Fiscal Year
	print("4. Creando Año Fiscal...")
	crear_fiscal_year()
	
	# 5. Crear Settings
	print("5. Creando Configuraciones...")
	crear_settings()
	
	print("\n✅ CONTABILIDAD INICIALIZADA CORRECTAMENTE\n")


def crear_company():
	"""Crea la Company (Empresa) principal"""
	
	company_name = "Servicios Públicos Colombia"
	
	# Verificar si ya existe
	if frappe.db.exists("Company", company_name):
		print(f"   ✓ Empresa '{company_name}' ya existe")
		return
	
	try:
		company = frappe.get_doc({
			"doctype": "Company",
			"company_name": company_name,
			"abbr": "SPC",
			"country": "Colombia",
			"default_currency": "COP",
			"company_type": "Individual",
			"creation": getdate(),
		})
		
		company.insert(ignore_permissions=True)
		print(f"   ✓ Empresa '{company_name}' creada exitosamente")
		
	except Exception as e:
		print(f"   ✗ Error creando empresa: {str(e)}")


def crear_chart_of_accounts():
	"""Crea el Plan de Cuentas (Chart of Accounts) para servicios públicos"""
	
	company = "Servicios Públicos Colombia"
	
	# Estructura de Cuentas según normas contables colombianas
	accounts = [
		# ACTIVO
		{"name": "10 - ACTIVO", "parent": None, "acc_type": "Asset", "is_group": 1},
		{"name": "1010 - Caja", "parent": "10 - ACTIVO", "acc_type": "Cash", "is_group": 0},
		{"name": "1020 - Bancos", "parent": "10 - ACTIVO", "acc_type": "Bank", "is_group": 0},
		{"name": "1030 - Clientes", "parent": "10 - ACTIVO", "acc_type": "Receivable", "is_group": 0},
		
		# PASIVO
		{"name": "20 - PASIVO", "parent": None, "acc_type": "Liability", "is_group": 1},
		{"name": "2010 - Proveedores", "parent": "20 - PASIVO", "acc_type": "Payable", "is_group": 0},
		
		# PATRIMONIO
		{"name": "30 - PATRIMONIO", "parent": None, "acc_type": "Equity", "is_group": 1},
		{"name": "3010 - Capital Social", "parent": "30 - PATRIMONIO", "acc_type": "Equity", "is_group": 0},
		
		# INGRESOS
		{"name": "40 - INGRESOS", "parent": None, "acc_type": "Income", "is_group": 1},
		{"name": "4010 - Ingresos por Agua", "parent": "40 - INGRESOS", "acc_type": "Income", "is_group": 0},
		{"name": "4020 - Ingresos por Luz", "parent": "40 - INGRESOS", "acc_type": "Income", "is_group": 0},
		{"name": "4030 - Ingresos por Gas", "parent": "40 - INGRESOS", "acc_type": "Income", "is_group": 0},
		{"name": "4040 - Ingresos por Datos", "parent": "40 - INGRESOS", "acc_type": "Income", "is_group": 0},
		{"name": "4090 - Ingresos por Servicios Públicos", "parent": "40 - INGRESOS", "acc_type": "Income", "is_group": 0},
		
		# GASTOS
		{"name": "50 - GASTOS OPERACIONALES", "parent": None, "acc_type": "Expense", "is_group": 1},
		{"name": "5010 - Gastos de Personal", "parent": "50 - GASTOS OPERACIONALES", "acc_type": "Expense", "is_group": 0},
		{"name": "5020 - Gastos de Servicios", "parent": "50 - GASTOS OPERACIONALES", "acc_type": "Expense", "is_group": 0},
		{"name": "5030 - Gastos de Mantenimiento", "parent": "50 - GASTOS OPERACIONALES", "acc_type": "Expense", "is_group": 0},
		
		# IMPUESTOS
		{"name": "60 - IMPUESTOS Y CONTRIBUCIONES", "parent": None, "acc_type": "Liability", "is_group": 1},
		{"name": "6010 - IVA por Pagar", "parent": "60 - IMPUESTOS Y CONTRIBUCIONES", "acc_type": "Liability", "is_group": 0},
	]
	
	created_count = 0
	for acc in accounts:
		# Verificar si ya existe
		if frappe.db.exists("Account", {"account_name": acc["name"], "company": company}):
			print(f"   ✓ Cuenta '{acc['name']}' ya existe")
			continue
		
		try:
			account = frappe.get_doc({
				"doctype": "Account",
				"account_name": acc["name"],
				"parent_account": acc["parent"],
				"company": company,
				"account_type": acc["acc_type"],
				"is_group": acc["is_group"],
			})
			
			account.insert(ignore_permissions=True)
			created_count += 1
			print(f"   ✓ Cuenta '{acc['name']}' creada")
			
		except Exception as e:
			print(f"   ✗ Error creando cuenta {acc['name']}: {str(e)}")
	
	if created_count > 0:
		print(f"\n   Total: {created_count} cuentas nuevas creadas")


def crear_cost_centers():
	"""Crea los Centros de Costo (Cost Centers)"""
	
	company = "Servicios Públicos Colombia"
	
	cost_centers = [
		{"name": "CC-001 - Agua", "description": "Centro de Costo - Servicio de Agua"},
		{"name": "CC-002 - Luz", "description": "Centro de Costo - Servicio de Electricidad"},
		{"name": "CC-003 - Gas", "description": "Centro de Costo - Servicio de Gas"},
		{"name": "CC-004 - Datos", "description": "Centro de Costo - Servicio de Datos"},
		{"name": "CC-005 - Administración", "description": "Centro de Costo - Administrativo"},
	]
	
	created_count = 0
	for cc in cost_centers:
		# Verificar si ya existe
		if frappe.db.exists("Cost Center", cc["name"]):
			print(f"   ✓ Centro de Costo '{cc['name']}' ya existe")
			continue
		
		try:
			cost_center = frappe.get_doc({
				"doctype": "Cost Center",
				"cost_center_name": cc["name"],
				"company": company,
				"disabled": 0,
			})
			
			cost_center.insert(ignore_permissions=True)
			created_count += 1
			print(f"   ✓ Centro de Costo '{cc['name']}' creado")
			
		except Exception as e:
			print(f"   ✗ Error creando cost center {cc['name']}: {str(e)}")
	
	if created_count > 0:
		print(f"\n   Total: {created_count} centros de costo nuevos creados")


def crear_fiscal_year():
	"""Crea el Año Fiscal (Fiscal Year)"""
	
	company = "Servicios Públicos Colombia"
	from datetime import date
	current_year = date.today().year
	
	fiscal_year_name = f"{current_year}"
	
	# Verificar si ya existe
	if frappe.db.exists("Fiscal Year", fiscal_year_name):
		print(f"   ✓ Año Fiscal '{fiscal_year_name}' ya existe")
		return
	
	try:
		fiscal_year = frappe.get_doc({
			"doctype": "Fiscal Year",
			"year": fiscal_year_name,
			"year_start_date": f"{current_year}-01-01",
			"year_end_date": f"{current_year}-12-31",
			"disabled": 0,
		})
		
		fiscal_year.insert(ignore_permissions=True)
		print(f"   ✓ Año Fiscal '{fiscal_year_name}' creado (01/01/{current_year} - 31/12/{current_year})")
		
	except Exception as e:
		print(f"   ✗ Error creando fiscal year: {str(e)}")


def crear_settings():
	"""Crea la configuración de Servicios Públicos"""
	
	if frappe.db.exists("Servicios Publicos Settings"):
		print("   ✓ Configuración de Servicios Públicos ya existe")
		return
	
	try:
		settings = frappe.get_doc({
			"doctype": "Servicios Publicos Settings",
			"default_company": "Servicios Públicos Colombia",
		})
		
		settings.insert(ignore_permissions=True)
		print("   ✓ Configuración de Servicios Públicos creada")
		
	except Exception as e:
		print(f"   ✗ Error creando settings: {str(e)}")


if __name__ == "__main__":
	setup_company_and_accounting()
