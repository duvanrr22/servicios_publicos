from frappe import __version__ as frappe_version
app_name = "servicios_publicos"
app_title = "Servicios Públicos Colombia"
app_publisher = "Sistema Servicios Públicos"
app_description = "Aplicación para gestión de servicios públicos en Colombia"
app_email = "admin@serviciospublicos.local"
app_license = "GPL-3.0"
app_version = "1.0.0"

# Branding y Logo - Synapse Servicios Publicos
app_color = "#1b9e8f"
app_font_color = "#ffffff"
app_logo = "servicios_publicos/public/synapse_logo.png"
app_icon = "servicios_publicos/public/synapse_logo.png"
tagline = "Agua • Luz • Gas • Datos"
tagline_color = "#1b9e8f"

# Router
app_include_css = [
    "/assets/servicios_publicos/css/servicios_publicos.css"
]
app_include_js = [
    "/assets/servicios_publicos/js/servicios_publicos.js"
]

# Includes in <head>
# ---------------

# Include app javascript in the frontend
# web_include_js = "/assets/servicios_publicos/js/servicios_publicos.js"

# include app css in the frontend
# web_include_css = "/assets/servicios_publicos/css/servicios_publicos.css"

# include custom scss in every page where app is loaded
# app_include_css = "/assets/servicios_publicos/css/servicios_publicos.scss"

# include js, css files in header of web template
# web_include_css = "/assets/servicios_publicos/css/servicios_publicos.css"
# web_include_js = "/assets/servicios_publicos/js/servicios_publicos.js"

# include js in page
# page_js = {"page1" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"DocType" : "public/js/doctype.js"}
# doctype_list_js = {"DocType" : "public/js/doctype_list.js"}
# doctype_tree_js = {"DocType" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"DocType" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override the default home page)
# home_page = "login"

# page_order before
# page_order_before = {
# 	"page1": ["page2", "page3"]
# }

# Socket.io
# ---------------
# if app needs to emit socket events in real time to frontend based on db change, register "realtime_log" doctype

# Fixtures
# --------

# Sync on Migrate
# ---------------
# Functions that are run during `bench migrate` command, function should return True on success or False on failure
migrate_list = [
	"servicios_publicos.setup.accounting_setup.setup_company_and_accounting"
]

# App Installation Hooks
# ----------------------
# Functions that are run after app installation
after_app_install = [
	"servicios_publicos.setup.currency_and_payment_terms_setup.setup_cop_currency",
	"servicios_publicos.setup.currency_and_payment_terms_setup.setup_payment_terms",
	"servicios_publicos.setup.currency_and_payment_terms_setup.validate_currency_setup",
]

# Database Migrations
# -------------------
# Custom migrations for the app
migrations = {
	"servicios_publicos": [
		"add_custom_fields_payment_entry",
	]
}

# Features to Include
# -------------------

# fixture exclusion
# exclude_fixtures = ["Custom Field"]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"servicios_publicos.auth.validate"
# ]

# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype_1}",
        "filter_by": "{filter_field}",
        "redact_fields": ["{field_1}", "{field_2}"],
        "depends_on": "{depends_on_doctype}",
    },
]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes
# class_overrides = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Cliente Servicios Públicos": {
		"on_update": "servicios_publicos.integrations.accounting_integration.AccountingIntegration.sincronizar_cliente_a_customer"
	},
	"Factura de Servicios": {
		"on_submit": [
			"servicios_publicos.integrations.accounting_integration.AccountingIntegration.crear_sales_invoice_desde_factura",
			"servicios_publicos.integrations.accounting_integration.AccountingIntegration.crear_journal_entry_desde_factura"
		]
	},
	"Pago de Servicios": {
		"on_submit": "servicios_publicos.integrations.accounting_integration.AccountingIntegration.crear_payment_entry_desde_pago"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"servicios_publicos.tasks.sincronizar_clientes_con_customer",
		"servicios_publicos.tasks.generar_reportes_diarios"
	],
	"hourly": [
		"servicios_publicos.tasks.sincronizar_pagos_pendientes"
	]
}

# Testing
# -------

before_tests = "servicios_publicos.install.before_tests"

# Overrides
# ----------

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_trash": "method",
# 		"before_validate": "method",
# 	},
# }

# Whitelisted methods
# ------------------

# Global Report Settings
# -----------------------

# Uncomment this lines to define default filters, columns and so on for report
# report_user_settings = {
# 	"Report Name": {
# 		"columns": ["Field1", "Field2", "Field3"],
# 	}
# }

# Desk Notifications
# -------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "servicios_publicos.notifications.get_notification_config"

# Permissions on Desk
# --------------------

# set_desk_icons_by_module_section = True

# Assistants
# ----------
# Defines a list of AI Prompts to be used in the app

# assistant = [
# 	{
# 		"doctype": "Contract",
# 		"fieldname": "expected_value",
# 		"description": "Estimates the value of the contract based on the contract notes.",
# 	},
# ]
