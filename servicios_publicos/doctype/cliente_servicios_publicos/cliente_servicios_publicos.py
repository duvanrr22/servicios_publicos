# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0

import frappe
import re
from frappe.model.document import Document


class ClienteServiciosPublicos(Document):
	"""Cliente de Servicios Públicos - Conforme a estándares Frappe Data Import"""
	
	def validate(self):
		"""
		Validación de datos antes de guardar/importar.
		Sigue los estándares Frappe Data Import para importación bulto.
		
		IMPORTANTE: Esta validación se ejecuta:
		1. Manualmente: cuando usuario hace click Save
		2. Importación: cuando se importa via Data Import tool
		3. API: cuando se crea via API/scripts
		"""
		
		# Validaciones básicas
		self._validar_campos_requeridos()
		self._validar_documento()
		self._validar_email()
		self._validar_categoria()
		self._validar_prestador_existe()
		self._validar_tipo_identificacion()
	
	def _validar_campos_requeridos(self):
		"""Validar que campos obligatorios están presentes"""
		campos_requeridos = {
			"nombre": "Nombre del cliente",
			"categoria": "Categoría",
			"documento": "Número de documento",
			"email": "Email",
			"prestador_de_servicios": "Prestador de servicios",
		}
		
		for campo, label in campos_requeridos.items():
			if not self.get(campo):
				frappe.throw(f"{label} es requerido y no puede estar vacío")
	
	def _validar_documento(self):
		"""
		Validar formato del documento según tipo de identificación.
		Conforme a estándares colombianos.
		"""
		documento = self.documento or ""
		tipo_id = self.tipo_identificacion or "CC"
		
		# Remover caracteres especiales
		documento = re.sub(r"[^\d]", "", documento)
		
		if not documento:
			frappe.throw("Número de documento no válido. Debe contener solo dígitos.")
		
		# Validar según tipo
		if tipo_id == "CC" and len(documento) not in [6, 7, 8, 9, 10]:
			frappe.throw("Cédula de Ciudadanía debe tener entre 6 y 10 dígitos")
		
		if tipo_id == "NIT" and len(documento) not in [8, 9]:
			frappe.throw("NIT debe tener 8 o 9 dígitos")
		
		if tipo_id == "CE" and len(documento) not in [6, 7, 8, 9]:
			frappe.throw("Cédula de Extranjería debe tener entre 6 y 9 dígitos")
		
		# Guardar documento normalizado
		self.documento = documento
	
	def _validar_email(self):
		"""Validar formato de email (conforme RFC 5322 simplified)"""
		email = self.email or ""
		
		# Regular expression básica para email
		patron_email = r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
		
		if not re.match(patron_email, email):
			frappe.throw(f"Email '{email}' no tiene formato válido. Formato requerido: usuario@dominio.com")
	
	def _validar_categoria(self):
		"""Validar que categoría es una de las válidas"""
		categorias_validas = ["Residencial", "Comercial", "Industrial", "Oficial"]
		
		if self.categoria not in categorias_validas:
			frappe.throw(
				f"Categoría '{self.categoria}' no válida. "
				f"Opciones válidas: {', '.join(categorias_validas)}"
			)
	
	def _validar_prestador_existe(self):
		"""Validar que prestador_de_servicios existe en BD"""
		if not self.prestador_de_servicios:
			frappe.throw("Prestador de servicios es requerido")
		
		if not frappe.db.exists("Prestador de Servicios", self.prestador_de_servicios):
			frappe.throw(
				f"Prestador de servicios '{self.prestador_de_servicios}' no encontrado. "
				f"Debe importar Prestadores ANTES de Clientes."
			)
	
	def _validar_tipo_identificacion(self):
		"""Validar que tipo_identificacion es válido"""
		tipos_validos = ["CC", "CE", "NIT", "Pasaporte"]
		
		if self.tipo_identificacion not in tipos_validos:
			frappe.throw(
				f"Tipo de identificación '{self.tipo_identificacion}' no válido. "
				f"Opciones: {', '.join(tipos_validos)}"
			)
	
	def before_insert(self):
		"""Generar código de cliente antes de insertar"""
		if not self.codigo_cliente:
			self.codigo_cliente = self.get_new_coding()
	
	def get_new_coding(self):
		"""
		Genera un código de cliente único.
		Formato: CLI000001, CLI000002, etc.
		NOTA: Para importación bulto, el usuario puede proporcionar el código directamente.
		"""
		last_code = frappe.db.sql(
			"SELECT MAX(CAST(SUBSTRING(codigo_cliente, 7) AS UNSIGNED)) FROM `tabCliente Servicios Públicos`"
		)
		if last_code[0][0]:
			new_code = "CLI" + str(last_code[0][0] + 1).zfill(6)
		else:
			new_code = "CLI000001"
		return new_code
