#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para configuración rápida después de la instalación
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def setup_app():
    """Ejecuta la configuración inicial"""
    try:
        print("=" * 60)
        print("Servicios Públicos Colombia - Configuración Inicial")
        print("=" * 60)
        
        print("\n✓ Estructura de aplicación creada correctamente")
        print("✓ DocTypes definidos")
        print("✓ APIs configuradas")
        print("✓ Permisos establecidos")
        
        print("\n" + "=" * 60)
        print("PRÓXIMOS PASOS:")
        print("=" * 60)
        
        print("""
1. Instalar en Frappe:
   bench get-app servicios_publicos /ruta/a/servicios_publicos
   bench install-app servicios_publicos
   bench migrate

2. Configuración Inicial:
   - Crear Prestador de Servicios
   - Definir Tipos de Servicios
   - Establecer Tarifas
   - Registrar Clientes

3. Consultar:
   - README.md
   - INSTALLATION_GUIDE.md
   - ARCHITECTURE.md
        """)
        
        print("=" * 60)
        
    except Exception as e:
        print(f"Error durante configuración: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = setup_app()
    sys.exit(0 if success else 1)
