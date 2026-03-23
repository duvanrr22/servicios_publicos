# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0

import frappe
from frappe.model.document import Document


class Item(Document):
	"""
	Item personalizado para Servicios Públicos
	Extiende la funcionalidad del Item estándar de Frappe
	"""
	
	def validate(self):
		"""Validaciones personalizadas"""
		if not self.item_name:
			self.item_name = self.item_code
	
	def on_update(self):
		"""Al actualizar un Item, sincronizar con Tipo de Servicio si aplica"""
		# Si el item está vinculado a un Tipo de Servicio, actualizar datos
		if hasattr(self, 'custom_tipo_servicio') and self.custom_tipo_servicio:
			tipo_servicio = frappe.get_doc("Tipo de Servicio", self.custom_tipo_servicio)
			if tipo_servicio:
				tipo_servicio.item_id = self.name
				tipo_servicio.db_update()
