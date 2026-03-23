# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0
# Reportes personalizados para Servicios Públicos integrados con Frappe

import frappe
from frappe import _
from frappe.utils import getdate, date_diff
from frappe.desk.query_report import QueryReport
import datetime


def generar_reporte_general_ledger_servicios():
	"""
	Reporte de Libro Mayor filtrado por tipo de servicio
	Mostrará todos los asientos contables de servicios públicos
	"""
	
	def execute(filters=None):
		"""
		Parámetros:
			- company: Empresa
			- from_date: Fecha inicial
			- to_date: Fecha final
			- tipo_servicio: Tipo de servicio a filtrar
		"""
		
		if not filters:
			filters = {}
		
		company = filters.get("company") or "Servicios Públicos Colombia"
		from_date = filters.get("from_date") or getdate("2026-01-01")
		to_date = filters.get("to_date") or getdate()
		tipo_servicio = filters.get("tipo_servicio")
		
		columns = [
			_("Fecha") + ":Date:80",
			_("Documento") + ":Link/Journal Entry:120",
			_("Cuenta") + ":Link/Account:150",
			_("Descripción") + ":Data:200",
			_("Débito") + ":Currency:100",
			_("Crédito") + ":Currency:100",
			_("Saldo") + ":Currency:100",
			_("Tipo") + ":Data:80",
		]
		
		# Consulta de GL Entry
		data = []
		
		gl_entries = frappe.get_list(
			"GL Entry",
			filters={
				"company": company,
				"posting_date": [">=", from_date],
				"posting_date": ["<=", to_date]
			},
			fields=["name", "posting_date", "account", "voucher_no", "debit", "credit", "remarks"],
			order_by="posting_date asc, account asc"
		)
		
		saldo = 0
		for entry in gl_entries:
			# Si hay filtro de tipo de servicio, filtrar por Journal Entry
			if tipo_servicio:
				je = frappe.get_doc("Journal Entry", entry.voucher_no)
				if je.get("custom_factura_servicios"):
					factura = frappe.get_doc("Factura de Servicios", je.custom_factura_servicios)
					if factura.tipo_de_servicio != tipo_servicio:
						continue
			
			saldo += (entry.debit or 0) - (entry.credit or 0)
			
			data.append([
				entry.posting_date,
				entry.voucher_no,
				entry.account,
				entry.remarks or "",
				entry.debit or 0,
				entry.credit or 0,
				saldo,
				"Débito" if entry.debit else "Crédito"
			])
		
		return columns, data
	
	return execute


def generar_reporte_deuda_por_cliente():
	"""
	Reporte de deuda por cliente
	Muestra todas las facturas pendientes y cantidad a cobrar
	"""
	
	def execute(filters=None):
		if not filters:
			filters = {}
		
		cliente = filters.get("cliente")
		servicio = filters.get("servicio")
		
		columns = [
			_("N° Factura") + ":Link/Factura de Servicios:150",
			_("Cliente") + ":Link/Cliente Servicios Públicos:150",
			_("Servicio") + ":Data:100",
			_("Fecha Emisión") + ":Date:80",
			_("Fecha Vencimiento") + ":Date:80",
			_("Monto") + ":Currency:100",
			_("Pagado") + ":Currency:100",
			_("Saldo") + ":Currency:100",
			_("Días Vencimiento") + ":Int:80",
			_("Estado") + ":Data:80",
		]
		
		filters_query = {
			"estado_factura": ["in", ["Vencida", "Parcialmente Pagada", "Emitida"]]
		}
		
		if cliente:
			filters_query["cliente"] = cliente
		if servicio:
			filters_query["tipo_de_servicio"] = servicio
		
		facturas = frappe.get_all(
			"Factura de Servicios",
			filters=filters_query,
			fields=[
				"name", "cliente", "tipo_de_servicio", "fecha_emision",
				"fecha_vencimiento", "valor_total", "valor_pagado",
				"saldo_pendiente", "estado_factura"
			]
		)
		
		data = []
		for factura in facturas:
			dias_vencimiento = date_diff(getdate(), factura.fecha_vencimiento)
			
			data.append([
				factura.name,
				factura.cliente,
				factura.tipo_de_servicio,
				factura.fecha_emision,
				factura.fecha_vencimiento,
				factura.valor_total,
				factura.valor_pagado,
				factura.saldo_pendiente,
				dias_vencimiento,
				factura.estado_factura
			])
		
		return columns, data
	
	return execute


def generar_reporte_ingresos_por_servicio():
	"""
	Reporte de ingresos por tipo de servicio
	Análisis de ingresos por categoría de servicio
	"""
	
	def execute(filters=None):
		if not filters:
			filters = {}
		
		from_date = filters.get("from_date") or getdate("2026-01-01")
		to_date = filters.get("to_date") or getdate()
		
		columns = [
			_("Servicio") + ":Link/Tipo de Servicio:150",
			_("Facturas Emitidas") + ":Int:100",
			_("Facturas Pagadas") + ":Int:100",
			_("Ingresos Totales") + ":Currency:120",
			_("Ingresos Cobrados") + ":Currency:120",
			_("Ingresos Pendientes") + ":Currency:120",
			_("% Recaudación") + ":Percent:80",
		]
		
		# Obtener tipos de servicio
		tipos_servicio = frappe.get_all("Tipo de Servicio", fields=["name", "nombre_servicio"])
		
		data = []
		
		for tipo in tipos_servicio:
			# Facturas por servicio
			facturas = frappe.get_all(
				"Factura de Servicios",
				filters={
					"tipo_de_servicio": tipo.name,
					"fecha_emision": [">=", from_date],
					"fecha_emision": ["<=", to_date]
				},
				fields=["valor_total", "valor_pagado", "saldo_pendiente"]
			)
			
			if len(facturas) == 0:
				continue
			
			facturas_emitidas = len(facturas)
			facturas_pagadas = len([f for f in facturas if f.saldo_pendiente == 0])
			
			ingresos_totales = sum([f.valor_total for f in facturas])
			ingresos_cobrados = sum([f.valor_pagado for f in facturas])
			ingresos_pendientes = sum([f.saldo_pendiente for f in facturas])
			
			porcentaje_recaudacion = (ingresos_cobrados / ingresos_totales * 100) if ingresos_totales > 0 else 0
			
			data.append([
				tipo.name,
				facturas_emitidas,
				facturas_pagadas,
				ingresos_totales,
				ingresos_cobrados,
				ingresos_pendientes,
				porcentaje_recaudacion
			])
		
		return columns, data
	
	return execute


def generar_reporte_reconciliacion_pagos():
	"""
	Reporte de reconciliación de pagos
	Compara Payment Entry con Pago de Servicios
	"""
	
	def execute(filters=None):
		if not filters:
			filters = {}
		
		from_date = filters.get("from_date") or getdate("2026-01-01")
		to_date = filters.get("to_date") or getdate()
		
		columns = [
			_("Pago Servicios") + ":Link/Pago de Servicios:150",
			_("Payment Entry") + ":Link/Payment Entry:150",
			_("Fecha") + ":Date:80",
			_("Cliente") + ":Data:150",
			_("Monto") + ":Currency:100",
			_("Estado") + ":Data:80",
			_("Reconciliado") + ":Check:50",
		]
		
		pagos_sp = frappe.get_all(
			"Pago de Servicios",
			filters={
				"fecha_pago": [">=", from_date],
				"fecha_pago": ["<=", to_date]
			},
			fields=["name", "cliente", "fecha_pago", "valor_pagado", "estado_pago", "payment_entry_id"]
		)
		
		data = []
		
		for pago in pagos_sp:
			reconciliado = bool(pago.payment_entry_id)
			
			data.append([
				pago.name,
				pago.payment_entry_id or "",
				pago.fecha_pago,
				frappe.get_value("Cliente Servicios Públicos", pago.cliente, "nombre_completo"),
				pago.valor_pagado,
				pago.estado_pago,
				1 if reconciliado else 0
			])
		
		return columns, data
	
	return execute
