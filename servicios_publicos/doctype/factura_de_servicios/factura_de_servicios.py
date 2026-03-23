# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class FacturaDeServicios(Document):
	"""
	Factura de Servicios Públicos - DocType para gestionar facturación de servicios.
	Conforme a estándares Frappe Data Import para importación bulto.
	"""
	
	def validate(self):
		"""
		Validación principal ejecutada:
		1. Manualmente: cuando usuario hace click Save
		2. Importación: cuando se importa via Data Import tool
		3. API: cuando se crea via API/scripts
		
		IMPORTANTE: Frappe ejecuta validate() ANTES de guardar en ambos casos
		(manual e importación).
		"""
		
		# Validaciones básicas
		self._validar_campos_requeridos()
		self._validar_dependencias_existen()
		self._validar_fechas()
		self._validar_consumo()
		self._validar_montos()
		self._validar_estado()
		
		# Calcular campos derivados
		self._calcular_saldo_pendiente()
	
	def _validar_campos_requeridos(self):
		"""Validar que campos obligatorios están presentes"""
		campos_requeridos = {
			"numero_factura": "Número de factura",
			"cliente": "Cliente",
			"conexion_de_servicio": "Conexión de servicio",
			"tipo_de_servicio": "Tipo de servicio",
			"periodo_factura": "Período de factura",
			"fecha_emision": "Fecha de emisión",
			"fecha_vencimiento": "Fecha de vencimiento",
			"valor_total": "Valor total",
		}
		
		for campo, label in campos_requeridos.items():
			if not self.get(campo):
				frappe.throw(f"{label} es requerido: {campo}")
	
	def _validar_dependencias_existen(self):
		"""
		Validar que documentos referenciados (Link fields) existen en la BD.
		CRÍTICO para Data Import: prevenir "No matching records found" errors.
		"""
		
		# Validar Cliente existe
		if self.cliente:
			if not frappe.db.exists("Cliente Servicios Públicos", self.cliente):
				frappe.throw(
					f"Cliente '{self.cliente}' no encontrado. "
					f"Asegúrese de importar Clientes ANTES de Facturas."
				)
		
		# Validar Conexión existe
		if self.conexion_de_servicio:
			if not frappe.db.exists("Conexion de Servicio", self.conexion_de_servicio):
				frappe.throw(
					f"Conexión '{self.conexion_de_servicio}' no encontrada. "
					f"Asegúrese de importar Conexiones ANTES de Facturas."
				)
		
		# Validar Tipo de Servicio existe
		if self.tipo_de_servicio:
			if not frappe.db.exists("Tipo de Servicio", self.tipo_de_servicio):
				frappe.throw(
					f"Tipo de Servicio '{self.tipo_de_servicio}' no encontrado. "
					f"Asegúrese de importar Tipos ANTES de Facturas."
				)
		
		# Validar Prestador existe
		if self.prestador_de_servicios:
			if not frappe.db.exists("Prestador de Servicios", self.prestador_de_servicios):
				frappe.throw(
					f"Prestador '{self.prestador_de_servicios}' no encontrado."
				)
	
	def _validar_fechas(self):
		"""
		Validar que fechas sean válidas y coherentes.
		"""
		from frappe.utils import getdate
		
		try:
			fecha_emision = getdate(self.fecha_emision)
			fecha_vencimiento = getdate(self.fecha_vencimiento)
		except:
			frappe.throw("Formato de fecha inválido. Use YYYY-MM-DD")
		
		# Vencimiento debe ser DESPUÉS de emisión
		if fecha_vencimiento < fecha_emision:
			frappe.throw(
				f"Fecha de vencimiento ({self.fecha_vencimiento}) "
				f"debe ser DESPUÉS de fecha de emisión ({self.fecha_emision})"
			)
		
		# Vencimiento no debe ser más de 90 días después
		dias_diferencia = (fecha_vencimiento - fecha_emision).days
		if dias_diferencia > 90:
			frappe.throw(
				f"Vencimiento muy lejano ({dias_diferencia} días). "
				f"Máximo permitido: 90 días."
			)
	
	def _validar_consumo(self):
		"""Validar datos de consumo"""
		
		# Lectura actual debe ser >= lectura anterior
		lectura_anterior = self.lectura_anterior or 0
		lectura_actual = self.lectura_actual or 0
		
		if lectura_actual < lectura_anterior:
			frappe.throw(
				f"Lectura actual ({lectura_actual}) "
				f"no puede ser menor que lectura anterior ({lectura_anterior})"
			)
		
		# Consumo debe ser positivo o cero
		consumo = self.consumo_facturado or 0
		if consumo < 0:
			frappe.throw("Consumo facturado no puede ser negativo")
	
	def _validar_montos(self):
		"""Validar que montos sean válidos y positivos"""
		
		campos_montos = {
			"valor_consumo": "Valor del consumo",
			"impuestos": "Impuestos",
			"descuentos": "Descuentos",
			"valor_total": "Valor total",
		}
		
		for campo, label in campos_montos.items():
			valor = self.get(campo) or 0
			try:
				valor_float = float(valor)
				if valor_float < 0:
					frappe.throw(f"{label} no puede ser negativo: {valor}")
			except:
				frappe.throw(f"{label} debe ser un número válido: {valor}")
		
		# Validar que valor_total es razonable
		if float(self.valor_total or 0) == 0:
			frappe.throw("Valor total no puede ser cero")
		
		# Validar monto máximo (prevenir errores de digitación)
		if float(self.valor_total or 0) > 99999999:
			# Límite arbitrario but reasonable
			frappe.throw(
				f"Valor total muy alto ({self.valor_total}). "
				f"Verifique que la cifra sea correcta."
			)
	
	def _validar_estado(self):
		"""Validar que estado sea válido"""
		estados_validos = ["Abierta", "Pagada", "Cancelada", "Anulada"]
		
		estado = self.estado_factura or "Abierta"
		if estado not in estados_validos:
			frappe.throw(
				f"Estado '{estado}' no válido. "
				f"Opciones: {', '.join(estados_validos)}"
			)
	
	def _calcular_saldo_pendiente(self):
		"""Calcular saldo pendiente"""
		valor_total = float(self.valor_total or 0)
		valor_pagado = float(self.valor_pagado or 0)
		self.saldo_pendiente = valor_total - valor_pagado
	
	def before_save(self):
		"""
		Cálculos automáticos ANTES de guardar.
		Se ejecuta automáticamente después de validate().
		"""
		# Garantizar que saldo_pendiente está calculado
		self._calcular_saldo_pendiente()
	
	def on_submit(self):
		"""
		Validaciones adicionales al SUBMIT (no aplica para Data Import, 
		ya que Data Import no submits a menos que se especifique).
		
		Para Data Import: Este NO se ejecuta a menos que user marque
		"Submit After Import" en la interfaz Data Import.
		"""
		pass
