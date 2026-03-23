# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0

import frappe
from frappe.utils import getdate


@frappe.whitelist()
def obtener_deuda_cliente(cliente):
	"""API: Obtiene la deuda total de un cliente"""
	deuda = frappe.db.get_value(
		"Factura de Servicios",
		{
			"cliente": cliente,
			"estado_factura": ["in", ["Vencida", "Parcialmente Pagada"]]
		},
		"SUM(saldo_pendiente)"
	)
	return {
		"cliente": cliente,
		"deuda_total": deuda[0] if deuda else 0
	}


@frappe.whitelist()
def obtener_ultimas_lecturas(conexion_de_servicio, limite=3):
	"""API: Obtiene las últimas lecturas de una conexión"""
	lecturas = frappe.get_list(
		"Lectura de Medidor",
		filters={"conexion_de_servicio": conexion_de_servicio},
		fields=["name", "fecha_lectura", "lectura_actual", "consumo", "estado_lectura"],
		order_by="fecha_lectura desc",
		limit_page_length=limite
	)
	return lecturas


@frappe.whitelist()
def obtener_consumo_promedio(conexion_de_servicio, meses=3):
	"""API: Calcula el consumo promedio de los últimos meses"""
	lecturas = frappe.get_list(
		"Lectura de Medidor",
		filters={"conexion_de_servicio": conexion_de_servicio},
		fields=["consumo", "fecha_lectura"],
		order_by="fecha_lectura desc",
		limit_page_length=meses
	)
	
	if lecturas:
		consumo_total = sum([l['consumo'] for l in lecturas])
		consumo_promedio = consumo_total / len(lecturas)
	else:
		consumo_promedio = 0
	
	return {
		"conexion": conexion_de_servicio,
		"consumo_promedio": consumo_promedio,
		"periodo_meses": meses
	}


@frappe.whitelist()
def listar_reclamos_abiertos(prestador_de_servicios=None):
	"""API: Lista los reclamos abiertos no resueltos"""
	filters = {
		"estado_reclamo": ["in", ["Registrado", "En Análisis", "En Proceso"]]
	}
	
	if prestador_de_servicios:
		filters["prestador_de_servicios"] = prestador_de_servicios
	
	reclamos = frappe.get_list(
		"Reclamo de Servicios",
		filters=filters,
		fields=["name", "cliente", "asunto", "fecha_reclamo", "prioridad", "estado_reclamo"],
		order_by="prioridad desc, fecha_reclamo asc"
	)
	
	return reclamos


@frappe.whitelist()
def crear_factura_desde_lectura(numero_lectura):
	"""API: Crea una factura desde una lectura de medidor"""
	from servicios_publicos.utils.utils import FacuracionUtils
	
	lectura = frappe.get_doc("Lectura de Medidor", numero_lectura)
	conexion = frappe.get_doc("Conexion de Servicio", lectura.conexion_de_servicio)
	cliente = frappe.get_doc("Cliente Servicios Públicos", conexion.cliente)
	
	# Obtener tarifa vigente
	tarifa = FacuracionUtils.obtener_tarifa_vigente(
		lectura.tipo_de_servicio,
		cliente.categoria_cliente,
		getdate()
	)
	
	if not tarifa:
		frappe.throw("No hay tarifa vigente para este servicio y categoría de cliente")
	
	# Calcular valor
	valor_total = FacuracionUtils.calcular_valor_factura(lectura.consumo, tarifa['name'])
	
	# Crear factura
	factura = frappe.get_doc({
		"doctype": "Factura de Servicios",
		"conexion_de_servicio": lectura.conexion_de_servicio,
		"cliente": cliente.name,
		"prestador_de_servicios": conexion.prestador_de_servicios,
		"tipo_de_servicio": lectura.tipo_de_servicio,
		"periodo_factura": lectura.fecha_lectura,
		"fecha_emision": getdate(),
		"fecha_vencimiento": getdate() + frappe.utils.relativedelta(months=1),
		"lectura_anterior": lectura.lectura_anterior,
		"lectura_actual": lectura.lectura_actual,
		"consumo_facturado": lectura.consumo,
		"tarifa_aplicada": tarifa['name'],
		"valor_consumo": valor_total,
		"valor_total": valor_total,
		"estado_factura": "Emitida"
	})
	
	factura.insert()
	lectura.facturada = 1
	lectura.save()
	
	return {
		"status": "success",
		"factura": factura.name,
		"valor": valor_total
	}
