# Servicios Públicos Colombia - Minimal Hooks (Frappe-compliant)
# Este archivo es una versión minimalista y segura que evita errores de build

from frappe import __version__ as frappe_version

app_name = "servicios_publicos"
app_title = "Servicios Públicos Colombia"
app_publisher = "Sistema Servicios Públicos"
app_description = "Aplicación para gestión de servicios públicos en Colombia"
app_email = "admin@serviciospublicos.local"
app_license = "GPL-3.0"
app_version = "1.0.0"

# Branding
app_color = "#1b9e8f"
app_font_color = "#ffffff"
app_logo = "servicios_publicos/public/synapse_logo.png"
app_icon = "servicios_publicos/public/synapse_logo.png"
tagline = "Agua • Luz • Gas • Datos"

# Assets - Minimal (solo rutas que existen)
app_include_css = [
	"servicios_publicos/public/css/servicios_publicos.css"
]
app_include_js = [
	"servicios_publicos/public/js/servicios_publicos.js"
]

# Migrations - Solo las funciones que existen
# migrate_list = []  # Comentado hasta verificar que existan

# App Installation Hooks - Solo las funciones que existen
# after_app_install = []  # Comentado hasta verificar que existan

# Features (debe estar vacío o con valores válidos)
# No poner placeholders como {doctype_1}

# Scheduler Events - Opcional, comentado por ahora
# scheduler_events = {}

# DocType Custom Scripts - Opcional
# doctype_js = {}
# doctype_css = {}

# Document Events - SOLO si los módulos existen
# doc_events = {}
