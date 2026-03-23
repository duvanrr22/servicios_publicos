# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0

import frappe
from frappe import _


class FacuracionUtils:
	"""Utilidades para facturación automática"""
	
	@staticmethod
	def calcular_consumo(lectura_actual, lectura_anterior):
		"""Calcula el consumo entre dos lecturas"""
		if lectura_actual and lectura_anterior:
			return lectura_actual - lectura_anterior
		return 0
	
	@staticmethod
	def obtener_tarifa_vigente(tipo_servicio, categoria_cliente, fecha):
		"""
		Obtiene la tarifa vigente para un servicio y categoría
		
		Args:
			tipo_servicio: Tipo de Servicio
			categoria_cliente: Categoría del cliente
			fecha: Fecha para verificar vigencia
		
		Returns:
			DocType Tarifa Servicios o None
		"""
		tarifa = frappe.db.get_list(
			"Tarifa Servicios",
			filters={
				"tipo_de_servicio": tipo_servicio,
				"categoria_cliente": categoria_cliente,
				"estado": "Activa",
				"fecha_vigencia": ["<=", fecha]
			},
			fields=["name", "valor_tarifa", "valor_fijo_factura"],
			order_by="fecha_vigencia desc",
			limit_page_length=1
		)
		
		return tarifa[0] if tarifa else None
	
	@staticmethod
	def calcular_valor_factura(consumo, tarifa_doc):
		"""
		Calcula el valor total de la factura
		
		Args:
			consumo: Consumo registrado
			tarifa_doc: Documento de Tarifa
		
		Returns:
			Valor total calculado
		"""
		if not tarifa_doc:
			return 0
		
		tarifa = frappe.get_doc("Tarifa Servicios", tarifa_doc)
		valor = (consumo * tarifa.valor_tarifa) + (tarifa.valor_fijo_factura or 0)
		
		# Aplicar sobretasa si corresponde
		if tarifa.aplica_sobretasa and consumo >= tarifa.rango_sobretasa_minimo:
			valor = valor * (1 + (tarifa.valor_sobretasa / 100))
		
		return valor


class ClientesUtils:
	"""Utilidades para gestión de clientes"""
	
	@staticmethod
	def generar_codigo_cliente():
		"""Genera un código único para cliente"""
		import frappe
		last_code = frappe.db.sql(
			"SELECT MAX(CAST(SUBSTRING(codigo_cliente, 4) AS UNSIGNED)) "
			"FROM `tabCliente Servicios Públicos` WHERE codigo_cliente LIKE 'CLI%'"
		)
		if last_code[0][0]:
			new_code = "CLI" + str(last_code[0][0] + 1).zfill(6)
		else:
			new_code = "CLI000001"
		return new_code
	
	@staticmethod
	def obtener_deuda_cliente(cliente):
		"""
		Obtiene la deuda total de un cliente
		
		Args:
			cliente: Nombre del cliente
		
		Returns:
			Valor total de deuda
		"""
		deuda = frappe.db.get_value(
			"Factura de Servicios",
			{
				"cliente": cliente,
				"estado_factura": ["in", ["Vencida", "Parcialmente Pagada"]]
			},
			"SUM(saldo_pendiente)"
		)
		return deuda[0] if deuda else 0


class ReportesUtils:
	"""Utilidades para generación de reportes"""
	
	@staticmethod
	def consumo_por_periodo(tipo_servicio, prestador, fecha_inicio, fecha_fin):
		"""
		Genera reporte de consumo por período
		
		Args:
			tipo_servicio: Tipo de servicio a reportar
			prestador: Prestador de servicio
			fecha_inicio: Fecha inicio del período
			fecha_fin: Fecha fin del período
		
		Returns:
			Lista de lecturas agrupadas
		"""
		lecturas = frappe.get_list(
			"Lectura de Medidor",
			filters={
				"tipo_de_servicio": tipo_servicio,
				"prestador_de_servicios": prestador,
				"fecha_lectura": [">=", fecha_inicio],
				"fecha_lectura": ["<=", fecha_fin]
			},
			fields=["conexion_de_servicio", "consumo", "fecha_lectura"],
			order_by="conexion_de_servicio, fecha_lectura"
		)
		return lecturas
	
	@staticmethod
	def morosidad_por_cliente():
		"""Obtiene el reporte de morosidad por cliente"""
		clientes_morosos = frappe.db.sql("""
			SELECT 
				c.name,
				c.nombre_completo,
				c.numero_identificacion,
				SUM(f.saldo_pendiente) as deuda_total,
				MAX(f.fecha_vencimiento) as ultimo_vencimiento
			FROM `tabCliente Servicios Públicos` c
			LEFT JOIN `tabFactura de Servicios` f ON c.name = f.cliente
			WHERE f.estado_factura IN ('Vencida', 'Parcialmente Pagada')
			GROUP BY c.name
			ORDER BY deuda_total DESC
		""", as_dict=True)
		
		return clientes_morosos
