# Copyright (c) 2024, Servicios Públicos Colombia
# License: GPL-3.0
# Integración con módulo de Contabilidad de Frappe

import frappe
from frappe.utils import getdate
from frappe.stock.get_item_details import get_item_details


class AccountingIntegration:
	"""Clase para integración con módulos contables de Frappe"""
	
	@staticmethod
	def crear_sales_invoice_desde_factura(factura_sp):
		"""
		Crea una Sales Invoice (factura estándar Frappe) desde Factura de Servicios
		
		ACTUALIZADO: Incluye soporte para:
		- Moneda (COP)
		- Términos de Pago
		- Cálculo automático de fecha de vencimiento
		
		Args:
			factura_sp: Documento de tipo "Factura de Servicios"
		
		Returns:
			dict: Status de la creación
		"""
		try:
			# Obtener datos de la factura de servicios
			factura = frappe.get_doc("Factura de Servicios", factura_sp)
			cliente = frappe.get_doc("Cliente Servicios Públicos", factura.cliente)
			
			# Validar que exista el Customer estándar vinculado
			customer = frappe.db.get_value(
				"Customer",
				{"custom_cliente_servicios": cliente.name}
			)
			
			if not customer:
				frappe.throw(f"No existe Customer vinculado para {cliente.name}")
			
			# Obtener la empresa (asumiendo configuración en app_config.json)
			company = frappe.db.get_single_value("Servicios Publicos Settings", "default_company")
			if not company:
				frappe.throw("No se ha configurado la empresa por defecto en Servicios Públicos")
			
			# NUEVO: Obtener moneda (siempre COP para servicios públicos en Colombia)
			currency = frappe.db.get_single_value("System Settings", "currency") or "COP"
			
			# NUEVO: Obtener términos de pago según grupo de cliente
			payment_terms_template = AccountingIntegration._obtener_terminos_pago(cliente.name)
			
			# Crear Sales Invoice
			sales_invoice = frappe.get_doc({
				"doctype": "Sales Invoice",
				"naming_series": "ACC-SI-.YYYY.-",
				"customer": customer,
				"company": company,
				"currency": currency,  # NUEVO: Especificar moneda explícitamente
				"posting_date": factura.fecha_emision,
				"due_date": factura.fecha_vencimiento,
				"payment_terms_template": payment_terms_template,  # NUEVO: Asignar términos de pago
				"custom_factura_servicios": factura.name,
				"custom_tipo_servicio": factura.tipo_de_servicio,
				"items": [{
					"item_code": factura.tipo_de_servicio,  # El servicio es un Item
					"qty": 1,
					"uom": "Nos",
					"rate": factura.valor_consumo,
					"amount": factura.valor_consumo,
					"custom_consumo": factura.consumo_facturado,
					"custom_lectura_anterior": factura.lectura_anterior,
					"custom_lectura_actual": factura.lectura_actual,
				}],
				"taxes": AccountingIntegration._obtener_impuestos(
					factura.tipo_de_servicio,
					factura.valor_consumo,
					company
				),
				"remarks": f"Factura de {factura.tipo_de_servicio} - Período {factura.periodo_factura} - Términos: {payment_terms_template}"
			})
			
			sales_invoice.insert(ignore_permissions=True)
			
			# Actualizar factura de servicios con referencia a Sales Invoice
			factura.db_set({
				"sales_invoice_id": sales_invoice.name,
				"estado_factura": "Sincronizada",
				"moneda": currency,
				"terminos_pago": payment_terms_template
			})
			
			return {
				"status": "success",
				"sales_invoice": sales_invoice.name,
				"factura_servicios": factura.name,
				"currency": currency,
				"payment_terms": payment_terms_template
			}
			
		except Exception as e:
			frappe.log_error(
				f"Error creando Sales Invoice: {str(e)}",
				"AccountingIntegration.crear_sales_invoice_desde_factura"
			)
			return {"status": "error", "message": str(e)}
	
	@staticmethod
	def crear_journal_entry_desde_factura(factura_sp):
		"""
		Crea un Journal Entry (asiento contable) desde Factura de Servicios
		
		Args:
			factura_sp: Documento de tipo "Factura de Servicios"
		
		Returns:
			dict: Status de la creación
		"""
		try:
			factura = frappe.get_doc("Factura de Servicios", factura_sp)
			company = frappe.db.get_single_value("Servicios Publicos Settings", "default_company")
			
			if not company:
				frappe.throw("No se ha configurado la empresa por defecto")
			
			# Obtener cuentas contables del Chart of Accounts
			cuenta_ingresos = frappe.db.get_value(
				"Account",
				{"account_name": "Ingresos por Servicios Públicos", "company": company},
				"name"
			)
			
			cuenta_clientes = frappe.db.get_value(
				"Account",
				{"account_type": "Receivable", "company": company},
				"name"
			)
			
			if not cuenta_ingresos or not cuenta_clientes:
				frappe.throw("Cuentas contables no configuradas en Chart of Accounts")
			
			# Crear Journal Entry
			journal_entry = frappe.get_doc({
				"doctype": "Journal Entry",
				"naming_series": "ACC-JE-.YYYY.-",
				"company": company,
				"posting_date": factura.fecha_emision,
				"journal_entry_date": factura.fecha_emision,
				"custom_factura_servicios": factura.name,
				"voucher_type": "Journal Entry",
				"accounts": [
					{
						"account": cuenta_clientes,
						"debit": factura.valor_total,
						"party": frappe.db.get_value("Customer", {"custom_cliente_servicios": factura.cliente}, "name"),
						"party_type": "Customer",
						"description": f"Factura de {factura.tipo_de_servicio}",
					},
					{
						"account": cuenta_ingresos,
						"credit": factura.valor_total,
						"description": f"Ingreso por {factura.tipo_de_servicio}",
					}
				],
				"remarks": f"Asiento automático de Factura: {factura.name}"
			})
			
			journal_entry.insert(ignore_permissions=True)
			
			# Actualizar factura con referencia a Journal Entry
			factura.db_set({
				"journal_entry_id": journal_entry.name
			})
			
			return {
				"status": "success",
				"journal_entry": journal_entry.name,
				"factura_servicios": factura.name
			}
			
		except Exception as e:
			frappe.log_error(
				f"Error creando Journal Entry: {str(e)}",
				"AccountingIntegration.crear_journal_entry_desde_factura"
			)
			return {"status": "error", "message": str(e)}
	
	@staticmethod
	def crear_payment_entry_desde_pago(pago_sp):
		"""
		Crea un Payment Entry (pago estándar Frappe) desde Pago de Servicios
		
		Args:
			pago_sp: Documento de tipo "Pago de Servicios"
		
		Returns:
			dict: Status de la creación
		"""
		try:
			pago = frappe.get_doc("Pago de Servicios", pago_sp)
			factura = frappe.get_doc("Factura de Servicios", pago.factura_de_servicios)
			company = frappe.db.get_single_value("Servicios Publicos Settings", "default_company")
			
			# Obtener Sales Invoice y Customer
			sales_invoice = frappe.db.get_value(
				"Sales Invoice",
				{"custom_factura_servicios": factura.name}
			)
			
			customer = frappe.db.get_value(
				"Customer",
				{"custom_cliente_servicios": factura.cliente},
				"name"
			)
			
			if not sales_invoice or not customer:
				frappe.throw("No existe Sales Invoice o Customer vinculados")
			
			# Mapeo de métodos de pago a modo de pago Frappe
			metodo_pago_frappe = {
				"Efectivo": "Cash",
				"Transferencia Bancaria": "Bank Transfer",
				"Tarjeta Crédito": "Credit Card",
				"Tarjeta Débito": "Debit Card",
				"Cheque": "Cheque",
				"Otro": "Other"
			}
			
			# Crear Payment Entry
			payment_entry = frappe.get_doc({
				"doctype": "Payment Entry",
				"naming_series": "ACC-PE-.YYYY.-",
				"payment_type": "Receive",
				"company": company,
				"posting_date": pago.fecha_pago,
				"party_type": "Customer",
				"party": customer,
				"paid_to": frappe.db.get_single_value("Servicios Publicos Settings", "default_bank_account"),
				"paid_amount": pago.valor_pagado,
				"received_amount": pago.valor_pagado,
				"mode_of_payment": metodo_pago_frappe.get(pago.metodo_pago, "Other"),
				"custom_pago_servicios": pago.name,
				"reference_no": pago.numero_referencia,
				"reference_date": pago.fecha_pago,
				"remarks": f"Pago de factura {factura.nombre_factura}",
				"allocations": [{
					"against_doctype": "Sales Invoice",
					"against_name": sales_invoice,
					"amount": pago.valor_pagado,
				}]
			})
			
			payment_entry.insert(ignore_permissions=True)
			
			# Actualizar pago de servicios con referencia a Payment Entry
			pago.db_set({
				"payment_entry_id": payment_entry.name,
				"estado_pago": "Registrada"
			})
			
			return {
				"status": "success",
				"payment_entry": payment_entry.name,
				"pago_servicios": pago.name
			}
			
		except Exception as e:
			frappe.log_error(
				f"Error creando Payment Entry: {str(e)}",
				"AccountingIntegration.crear_payment_entry_desde_pago"
			)
			return {"status": "error", "message": str(e)}
	
	@staticmethod
	def _obtener_terminos_pago(cliente_id):
		"""
		Obtiene los términos de pago aplicables para un cliente.
		
		CASCADA DE BÚSQUEDA (respeta configuración de ERPNext):
		1. ¿Cliente tiene términos pre-configurados? → Usar esos
		2. ¿Su categoría tiene términos en nuestro mapeo? → Usar esos
		3. ¿El término configurado existe en Payment Terms Template? → Usar
		4. Fallback: "Neto 30" (default universal)
		
		Mapeo por categoría (editable en ERPNext):
		- Residencial: Neto 30 días
		- Comercial: Neto 30 días  
		- Industrial: Neto 60 días
		- Oficial: Neto 10 días
		
		Args:
			cliente_id: ID del Cliente de Servicios Públicos
		
		Returns:
			str: Nombre del Payment Terms Template configurado
		"""
		try:
			cliente = frappe.get_doc("Cliente Servicios Públicos", cliente_id)
			
			# CASCADA 1: ¿Cliente tiene término pre-configurado?
			if hasattr(cliente, 'termino_pago_preferido') and cliente.termino_pago_preferido:
				termino_preferido = cliente.termino_pago_preferido
				# Validar que exista
				if frappe.db.exists("Payment Terms Template", termino_preferido):
					print(f"  → Usando término preferido del cliente: {termino_preferido}")
					return termino_preferido
			
			# CASCADA 2: Mapeo por categoría
			terminos_mapping = {
				"Residencial": "Neto 30",
				"Comercial": "Neto 30",
				"Industrial": "Neto 60",
				"Oficial": "Neto 10",
			}
			
			categoria = getattr(cliente, 'categoria', 'Residencial') or "Residencial"
			termino_sugerido = terminos_mapping.get(categoria, "Neto 30")
			
			# CASCADA 3: Validar que el término sugerido existe
			if frappe.db.exists("Payment Terms Template", termino_sugerido):
				print(f"  → Usando término por categoría ({categoria}): {termino_sugerido}")
				return termino_sugerido
			
			# CASCADA 4: Fallback - Usar default universal
			print(f"  → Término {termino_sugerido} no existe, usando default: Neto 30")
			return "Neto 30"
			
		except Exception as e:
			frappe.log_error(
				f"Error obteniendo términos de pago para {cliente_id}: {str(e)}",
				"_obtener_terminos_pago"
			)
			return "Neto 30"  # Default si hay error
	
	@staticmethod
	def _obtener_impuestos(tipo_servicio, monto, company):
		"""
		Obtiene template de impuestos para un servicio
		
		Args:
			tipo_servicio: Tipo de servicio
			monto: Monto de la factura
			company: Empresa
		
		Returns:
			list: Lista de impuestos
		"""
		try:
			# Obtener template de impuestos
			template = frappe.db.get_value(
				"Sales Taxes and Charges Template",
				{"custom_tipo_servicio": tipo_servicio, "company": company},
				"name"
			)
			
			if template:
				template_doc = frappe.get_doc("Sales Taxes and Charges Template", template)
				return template_doc.taxes or []
			
			return []
			
		except Exception as e:
			frappe.log_error(f"Error obteniendo impuestos: {str(e)}")
			return []
	
	@staticmethod
	def sincronizar_cliente_a_customer(cliente_sp):
		"""
		Sincroniza un Cliente Servicios Públicos con un Customer estándar
		
		Args:
			cliente_sp: Documento de tipo "Cliente Servicios Públicos"
		
		Returns:
			dict: Status de la sincronización
		"""
		try:
			cliente = frappe.get_doc("Cliente Servicios Públicos", cliente_sp)
			
			# Verificar si ya existe Customer vinculado
			existing_customer = frappe.db.get_value(
				"Customer",
				{"custom_cliente_servicios": cliente.name}
			)
			
			if existing_customer:
				return {
					"status": "already_exists",
					"customer": existing_customer,
					"cliente_servicios": cliente.name
				}
			
			# Crear nuevo Customer
			customer = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": cliente.nombre_completo,
				"customer_type": "Individual",
				"customer_group": "Servicios Públicos",
				"territory": "Colombia",
				"custom_cliente_servicios": cliente.name,
				"custom_numero_identificacion": cliente.numero_identificacion,
				"custom_tipo_identificacion": cliente.tipo_identificacion,
			})
			
			customer.insert(ignore_permissions=True)
			
			# Actualizar Cliente Servicios Públicos con referencia
			cliente.db_set({
				"customer_id": customer.name
			})
			
			return {
				"status": "created",
				"customer": customer.name,
				"cliente_servicios": cliente.name
			}
			
		except Exception as e:
			frappe.log_error(
				f"Error sincronizando Cliente a Customer: {str(e)}",
				"AccountingIntegration.sincronizar_cliente_a_customer"
			)
			return {"status": "error", "message": str(e)}
