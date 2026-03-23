# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0

from frappe.model.document import Document


class LecturaDeMedidor(Document):
	"""Lectura de Medidor"""
	
	def before_save(self):
		"""Antes de guardar, calcular consumo"""
		if self.lectura_actual and self.lectura_anterior:
			self.consumo = self.lectura_actual - self.lectura_anterior
