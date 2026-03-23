# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0

"""Configuración inicial para la aplicación"""

import frappe
from frappe.custom.doctype.custom_field import create_custom_fields


def setup_colombia_defaults():
	"""Establece configuraciones por defecto para Colombia"""
	
	# Crear tipos de documentos de identidad
	identity_types = ["Cédula de Ciudadanía (CC)", "Cédula de Extranjería (CE)", "NIT", "Pasaporte"]
	
	for identity_type in identity_types:
		if not frappe.db.exists("Tipo de Identificacion", identity_type):
			frappe.get_doc({
				"doctype": "Tipo de Identificacion",
				"name": identity_type
			}).insert()
	
	# Crear categorías de clientes
	categories = ["Residencial", "Comercial", "Industrial", "Oficial"]
	
	for category in categories:
		if not frappe.db.exists("Categoria Cliente", category):
			frappe.get_doc({
				"doctype": "Categoria Cliente",
				"name": category
			}).insert()


def create_demo_data():
	"""Crea datos de demostración"""
	
	# Crear tipos de servicios demo
	servicios_demo = [
		{
			"nombre": "Agua Potable",
			"codigo": "AP",
			"unidad_medida": "m³",
			"icono": "💧",
			"color": "#0099FF"
		},
		{
			"nombre": "Energía Eléctrica",
			"codigo": "EE",
			"unidad_medida": "kWh",
			"icono": "⚡",
			"color": "#FFD700"
		},
		{
			"nombre": "Gas Natural",
			"codigo": "GN",
			"unidad_medida": "m³",
			"icono": "🔥",
			"color": "#FF6347"
		}
	]
	
	for servicio in servicios_demo:
		if not frappe.db.exists("Tipo de Servicio", servicio["nombre"]):
			frappe.get_doc({
				"doctype": "Tipo de Servicio",
				"nombre": servicio["nombre"],
				"codigo": servicio["codigo"],
				"unidad_medida": servicio["unidad_medida"],
				"icono": servicio["icono"],
				"color": servicio["color"],
				"estado": "Activo"
			}).insert()
