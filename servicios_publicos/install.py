# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0

"""Instalación de la aplicación Servicios Públicos"""

import frappe
from frappe.custom.doctype.custom_field import create_custom_fields


def before_tests(config):
	"""Ejecutado antes de los tests"""
	pass


def after_install():
	"""Ejecutado después de instalar la aplicación"""
	create_module_workspace()
	create_custom_fields_and_validations()
	frappe.msgprint("Servicios Públicos instalado correctamente")


def create_module_workspace():
	"""Crea el workspace del módulo"""
	if not frappe.db.exists("Workspace", "Servicios Publicos"):
		ws = frappe.get_doc({
			"doctype": "Workspace",
			"name": "Servicios Publicos",
			"label": "Servicios Públicos",
			"for_user": "",
			"is_hidden": 0,
			"sidebar_items": []
		})
		ws.insert()


def create_custom_fields_and_validations():
	"""Crea campos personalizados y validaciones necesarias"""
	pass
