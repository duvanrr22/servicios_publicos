# validar_integracion_hooks.py
# Script para validar que la integración en hooks.py es correcta

import os
import sys


def validar_hooks():
    """
    Valida que hooks.py contiene las integraciones necesarias
    """
    
    print("\n" + "="*60)
    print("VALIDACIÓN DE INTEGRACIÓN EN hooks.py")
    print("="*60 + "\n")
    
    # Obtener ruta de hooks.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    hooks_path = os.path.join(current_dir, "hooks.py")
    
    if not os.path.exists(hooks_path):
        print("✗ ERROR: No se encontró hooks.py")
        return False
    
    print(f"✓ Archivo encontrado: {hooks_path}\n")
    
    # Leer contenido
    with open(hooks_path, 'r', encoding='utf-8') as f:
        hooks_content = f.read()
    
    # Validaciones
    validaciones = {
        "after_app_install": "after_app_install = [\n\t\"servicios_publicos.setup.currency_and_payment_terms_setup.setup_cop_currency\"",
        "setup_payment_terms": "\"servicios_publicos.setup.currency_and_payment_terms_setup.setup_payment_terms\"",
        "validate_currency_setup": "\"servicios_publicos.setup.currency_and_payment_terms_setup.validate_currency_setup\"",
        "migrations": "migrations = {",
        "add_custom_fields_payment_entry": "\"add_custom_fields_payment_entry\"",
    }
    
    todas_ok = True
    
    print("VALIDACIONES:\n")
    for nombre, patron in validaciones.items():
        if patron in hooks_content:
            print(f"✓ {nombre}")
        else:
            print(f"✗ FALTA: {nombre}")
            todas_ok = False
    
    print("\n" + "="*60)
    
    if todas_ok:
        print("✅ TODAS LAS INTEGRACIONES ESTÁN CORRECTAS\n")
        print("El archivo hooks.py contiene:")
        print("  • after_app_install con setup_cop_currency")
        print("  • after_app_install con setup_payment_terms")
        print("  • after_app_install con validate_currency_setup")
        print("  • migrations con add_custom_fields_payment_entry")
        print("\n✅ Listo para ejecutar 'bench migrate' o instalar la app\n")
    else:
        print("❌ ALGUNAS INTEGRACIONES FALTAN\n")
        print("Se encontraron los siguientes problemas:")
        for nombre, patron in validaciones.items():
            if patron not in hooks_content:
                print(f"  • {nombre} - No se encontró el patrón")
        print("\nPor favor, revisa hooks.py manualmente\n")
    
    print("="*60 + "\n")
    
    # Mostrar resumen
    print("RESUMEN DE INTEGRACIÓN:\n")
    print("1. SETUP FUNCTIONS (after_app_install):")
    print("   Estas se ejecutarán AUTOMÁTICAMENTE al instalar la app\n")
    
    if "after_app_install" in hooks_content:
        # Extraer contenido
        inicio = hooks_content.find("after_app_install = [")
        fin = hooks_content.find("]", inicio) + 1
        if inicio > -1:
            section = hooks_content[inicio:fin]
            # Mostrar líneas formateadas
            for line in section.split("\n"):
                if "setup_" in line or "validate_" in line:
                    # Extraer nombre de función
                    if "setup_cop_currency" in line:
                        print("   ✓ setup_cop_currency() - Configura COP y precisión decimal")
                    elif "setup_payment_terms" in line:
                        print("   ✓ setup_payment_terms() - Crea 5 términos de pago")
                    elif "validate_currency_setup" in line:
                        print("   ✓ validate_currency_setup() - Valida la configuración")
    
    print("\n2. MIGRATIONS (bench migrate):")
    print("   Estas se ejecutarán cuando se ejecute 'bench migrate'\n")
    
    if "migrations" in hooks_content:
        # Extraer contenido
        inicio = hooks_content.find("migrations = {")
        fin = hooks_content.find("}", inicio) + 1
        if inicio > -1:
            section = hooks_content[inicio:fin]
            if "add_custom_fields_payment_entry" in section:
                print("   ✓ add_custom_fields_payment_entry - Agrega 8 campos custom")
    
    print("\n3. FILES REQUERIDOS:\n")
    
    # Validar archivos
    archivos_requeridos = {
        "setup/currency_and_payment_terms_setup.py": "Configuración de COP y Términos de Pago",
        "migrations/add_custom_fields_payment_entry.py": "Custom fields para Payment Entry",
        "integrations/accounting_integration.py": "Integración actualizada con soporte COP",
    }
    
    for ruta, descripcion in archivos_requeridos.items():
        path_completa = os.path.join(current_dir, ruta)
        if os.path.exists(path_completa):
            print(f"   ✓ {ruta}")
            print(f"     → {descripcion}")
        else:
            print(f"   ✗ FALTA: {ruta}")
            print(f"     → {descripcion}")
            todas_ok = False
    
    print("\n" + "="*60 + "\n")
    
    return todas_ok


if __name__ == "__main__":
    resultado = validar_hooks()
    sys.exit(0 if resultado else 1)
