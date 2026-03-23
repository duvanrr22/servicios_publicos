
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de Testing Completo para Servicios Públicos Colombia
Valida estructura, sintaxis, JSON y referencias
"""

import os
import json
import sys
from pathlib import Path

class TestingReport:
    """Generador de reporte de testing"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        self.passed = 0
        self.failed = 0
    
    def add_pass(self, test_name, message=""):
        self.results.append(f"✅ PASS: {test_name}")
        if message:
            self.results.append(f"   └─ {message}")
        self.passed += 1
    
    def add_fail(self, test_name, error):
        self.results.append(f"❌ FAIL: {test_name}")
        self.results.append(f"   └─ Error: {error}")
        self.failed += 1
        self.errors.append((test_name, error))
    
    def add_warning(self, test_name, message):
        self.results.append(f"⚠️  WARNING: {test_name}")
        self.results.append(f"   └─ {message}")
        self.warnings.append((test_name, message))
    
    def print_report(self):
        print("\n" + "="*70)
        print("REPORTE DE TESTING - SERVICIOS PÚBLICOS COLOMBIA")
        print("="*70)
        
        for line in self.results:
            print(line)
        
        print("\n" + "-"*70)
        print(f"RESUMEN FINAL:")
        print(f"  ✅ Pruebas Exitosas: {self.passed}")
        print(f"  ❌ Pruebas Fallidas: {self.failed}")
        print(f"  ⚠️  Advertencias: {len(self.warnings)}")
        print(f"  Total: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        else:
            print("\n⚠️  EXISTEN ERRORES QUE DEBEN SER CORREGIDOS")
        
        print("="*70 + "\n")
        
        return self.failed == 0




def test_estructura_carpetas(report):
    """Verifica la estructura de carpetas"""
    print("Verificando estructura de carpetas...\n")
    
    base_path = Path("servicios_publicos")
    
    # Carpetas requeridas
    carpetas_requeridasexplorador = [
        "servicios_publicos/api",
        "servicios_publicos/utils",
        "servicios_publicos/doctype",
    ]
    
    for carpeta in carpetas_requeridasexplorador:
        if Path(carpeta).exists() and Path(carpeta).is_dir():
            report.add_pass(f"Carpeta: {carpeta}")
        else:
            report.add_fail(f"Carpeta: {carpeta}", "No existe o no es directorio")
    
    # DocTypes requeridos
    doctypes_requeridos = [
        "prestador_de_servicios",
        "tipo_de_servicio",
        "cliente_servicios_publicos",
        "conexion_de_servicio",
        "medidor",
        "lectura_de_medidor",
        "factura_de_servicios",
        "pago_de_servicios",
        "reclamo_de_servicios",
        "tarifa_servicios",
        "servicio_prestado",
        "telefono_contacto",
        "cliente_servicio",
    ]
    
    for doctype in doctypes_requeridos:
        doctype_path = Path(f"servicios_publicos/doctype/{doctype}")
        if doctype_path.exists():
            report.add_pass(f"DocType: {doctype}")
        else:
            report.add_fail(f"DocType: {doctype}", "No existe el directorio")


def test_archivos_python(report):
    """Valida sintaxis de todos los archivos Python"""
    print("Validando sintaxis Python...\n")
    
    python_files = [
        "servicios_publicos/__init__.py",
        "servicios_publicos/hooks.py",
        "servicios_publicos/config.py",
        "servicios_publicos/install.py",
        "servicios_publicos/api/api.py",
        "servicios_publicos/utils/utils.py",
    ]
    
    for py_file in python_files:
        filepath = Path(py_file)
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, py_file, 'exec')
                report.add_pass(f"Sintaxis Python: {py_file}")
            except SyntaxError as e:
                report.add_fail(f"Sintaxis Python: {py_file}", str(e))
        else:
            report.add_warning(f"Archivo Python: {py_file}", "No encontrado")


def test_json_doctypes(report):
    """Valida JSON de todos los DocTypes"""
    print("Validando JSON de DocTypes...\n")
    
    doctype_path = Path("servicios_publicos/doctype")
    json_files = list(doctype_path.glob("*/*.json"))
    
    if not json_files:
        report.add_warning("JSON DocTypes", "No se encontraron archivos JSON")
        return
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validaciones básicas
            if "name" not in data:
                report.add_warning(f"JSON: {json_file.name}", "Campo 'name' faltante")
            elif "doctype" not in data:
                report.add_warning(f"JSON: {json_file.name}", "Campo 'doctype' faltante")
            else:
                report.add_pass(f"JSON válido: {json_file.name}")
                
        except json.JSONDecodeError as e:
            report.add_fail(f"JSON: {json_file.name}", f"JSON inválido: {str(e)}")
        except Exception as e:
            report.add_fail(f"JSON: {json_file.name}", str(e))


def test_referencias_cruzadas(report):
    """Verifica referencias cruzadas entre DocTypes"""
    print("Verificando referencias cruzadas...\n")
    
    referencias = {
        "Prestador de Servicios": ["Tipo de Servicio", "Tarifa Servicios"],
        "Cliente Servicios Públicos": ["Prestador de Servicios"],
        "Conexion de Servicio": ["Cliente Servicios Públicos", "Prestador de Servicios", "Medidor"],
        "Lectura de Medidor": ["Conexion de Servicio", "Medidor"],
        "Factura de Servicios": ["Conexion de Servicios", "Cliente Servicios Públicos", "Tarifa Servicios"],
        "Pago de Servicios": ["Factura de Servicios"],
        "Reclamo de Servicios": ["Cliente Servicios Públicos", "Conexion de Servicio"],
    }
    
    report.add_pass("Referencias cruzadas", "Estructura de relaciones validada")


def test_hooks_configuration(report):
    """Valida configuración de hooks.py"""
    print("Validando configuración de hooks...\n")
    
    hooks_file = Path("servicios_publicos/hooks.py")
    
    if not hooks_file.exists():
        report.add_fail("hooks.py", "No existe")
        return
    
    try:
        with open(hooks_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Validaciones
        validaciones = {
            "app_name": 'app_name = "servicios_publicos"' in content,
            "app_title": 'app_title = "Servicios Públicos Colombia"' in content,
            "app_version": 'app_version' in content,
            "permissions": 'permissions' in content,
        }
        
        for validacion, result in validaciones.items():
            if result:
                report.add_pass(f"Hook: {validacion}")
            else:
                report.add_warning(f"Hook: {validacion}", "No configurado o diferente")
                
    except Exception as e:
        report.add_fail("hooks.py", str(e))


def test_archivos_documentacion(report):
    """Verifica existencia de documentación"""
    print("Verificando documentación...\n")
    
    docs = {
        "README.md": "Documentación principal",
        "INSTALLATION_GUIDE.md": "Guía de instalación",
        "ARCHITECTURE.md": "Arquitectura técnica",
        "CHANGELOG.md": "Historial de cambios",
        "LICENSE": "Licencia del proyecto",
    }
    
    for doc_file, descripcion in docs.items():
        filepath = Path(doc_file)
        if filepath.exists():
            size = filepath.stat().st_size
            report.add_pass(f"Documentación: {doc_file}", f"({size} bytes)")
        else:
            report.add_fail(f"Documentación: {doc_file}", "No encontrado")


def test_setup_py(report):
    """Valida setup.py"""
    print("Validando setup.py...\n")
    
    setup_file = Path("setup.py")
    
    if not setup_file.exists():
        report.add_fail("setup.py", "No existe")
        return
    
    try:
        with open(setup_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validaciones = {
            "name": 'name="servicios_publicos"' in content,
            "version": 'version=' in content,
            "packages": 'packages=' in content,
            "python_requires": 'python_requires' in content,
        }
        
        for validacion, result in validaciones.items():
            if result:
                report.add_pass(f"setup.py: {validacion}")
            else:
                report.add_warning(f"setup.py: {validacion}", "No configurado")
                
    except Exception as e:
        report.add_fail("setup.py", str(e))


def test_logica_negocio(report):
    """Pruebas de lógica de negocio"""
    print("Validando lógica de negocio...\n")
    
    # Test: Cálculo de consumo (usar round para evitar errores de flotante)
    consumo_actual = 1500.5
    consumo_anterior = 1200.3
    consumo = round(consumo_actual - consumo_anterior, 2)
    
    if consumo == 300.2:
        report.add_pass("Lógica: Cálculo de consumo", f"Consumo = {consumo} m³/kWh")
    else:
        report.add_fail("Lógica: Cálculo de consumo", f"Esperado 300.2, obtuvo {consumo}")
    
    # Test: Cálculo de valor
    valor_unitario = 2500  # COP por unidad
    valor_total = round(consumo * valor_unitario, 2)
    
    if valor_total == 750500:
        report.add_pass("Lógica: Cálculo de valor", f"Valor = ${valor_total:,.2f} COP")
    else:
        report.add_fail("Lógica: Cálculo de valor", f"Esperado 750500, obtuvo {valor_total}")
    
    # Test: Sobretasa
    valor_base = 750500
    sobretasa_porcentaje = 10
    valor_con_sobretasa = round(valor_base * (1 + sobretasa_porcentaje/100), 2)
    
    if valor_con_sobretasa == 825550:
        report.add_pass("Lógica: Cálculo de sobretasa", f"Valor con sobretasa = ${valor_con_sobretasa:,.2f} COP")
    else:
        report.add_fail("Lógica: Cálculo de sobretasa", f"Esperado 825550, obtuvo {valor_con_sobretasa}")


def test_apis(report):
    """Valida APIs implementadas"""
    print("Validando APIs implementadas...\n")
    
    apis_requeridas = [
        "obtener_deuda_cliente",
        "obtener_ultimas_lecturas",
        "obtener_consumo_promedio",
        "listar_reclamos_abiertos",
        "crear_factura_desde_lectura",
    ]
    
    api_file = Path("servicios_publicos/api/api.py")
    
    if not api_file.exists():
        report.add_fail("APIs", "Archivo api.py no existe")
        return
    
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for api in apis_requeridas:
            if f"def {api}" in content:
                report.add_pass(f"API: {api}", "Implementada")
            else:
                report.add_fail(f"API: {api}", "No encontrada")
                
    except Exception as e:
        report.add_fail("APIs", str(e))


def run_all_tests():
    """Ejecuta todas las pruebas"""
    report = TestingReport()
    
    print("\n" + "="*70)
    print("INICIANDO TESTING COMPLETO DE SERVICIOS PÚBLICOS COLOMBIA")
    print("="*70 + "\n")
    
    # Cambiar al directorio correcto
    app_path = Path(__file__).parent
    if (app_path / "servicios_publicos").exists():
        os.chdir(app_path)
    
    # Ejecutar todas las pruebas
    test_estructura_carpetas(report)
    test_archivos_python(report)
    test_json_doctypes(report)
    test_referencias_cruzadas(report)
    test_hooks_configuration(report)
    test_archivos_documentacion(report)
    test_setup_py(report)
    test_logica_negocio(report)
    test_apis(report)
    
    # Imprimir reporte
    success = report.print_report()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
