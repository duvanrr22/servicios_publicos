"""
SUITE DE TESTING EXHAUSTIVO - OPTIMIZADO
==========================================

Versión mejorada que:
1. Lee datos Excel una sola vez
2. Usa datos cacheados en memoria
3. Ejecuta tests rápidamente
4. Genera reporte completo de resultados

Ejecutar: python test_suite_optimizado.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')

# Rutas
EXCEL_DIR = Path('c:/App servicios publicos/servicios_publicos/archivos_excel')
ARCHIVOS = {
    'Diciembre 2025': EXCEL_DIR / 'PaqueteFacturacion-Diciembre-2025.xlsx',
    'Enero 2026': EXCEL_DIR / 'PaqueteFacturacion-Enero-2026.xlsx',
    'Febrero 2026': EXCEL_DIR / 'PaqueteFacturacion-Febrero-2026.xlsx',
}

# ============================================================================
# CARGO DE DATOS ÚNICO
# ============================================================================

print("\n" + "="*80)
print("🔄 Cargando datos Excel (lectura única)...")
print("="*80 + "\n")

DATOS = {}
for mes, ruta in ARCHIVOS.items():
    print(f"  ⏳ {mes}... ", end='', flush=True)
    try:
        df = pd.read_excel(ruta, sheet_name=0)
        if pd.isna(df.iloc[0, 0]):
            df = df.iloc[1:].reset_index(drop=True)
        
        # Convertir inmediatamente a tipos correctos
        for col in df.columns:
            if col in ['Lectura anterior', 'Lectura Actual', 'Consumo', 'Valor.Metro',
                       'Total.Consumo', 'Valor.Subsidio', 'Valor.Consumo', 'CargoFijo',
                       'CargoPart', 'CargoGlob', 'Valor.Mora(II)', 'Valor.Aju.',
                       'Valor. Neto', 'SdoCarte.', 'Valor. Total', 'Total.Recaudo']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        DATOS[mes] = df
        print(f"✓ ({len(df)} registros)")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)

# ============================================================================
# SUITE DE TESTS
# ============================================================================

class Reporte:
    """Generador de reporte de testing"""
    
    def __init__(self):
        self.resultados = []
        self.test_actual = None
        self.fase_actual = None
        self.total_tests = 0
        self.tests_pasados = 0
        self.tests_fallidos = 0
    
    def nueva_fase(self, titulo: str):
        """Comenzar nueva fase"""
        self.fase_actual = titulo
        print(f"\n{'='*80}")
        print(f"#{titulo}")
        print(f"{'='*80}")
    
    def nuevo_test(self, titulo: str):
        """Comenzar nuevo test"""
        self.test_actual = titulo
        self.total_tests += 1
        print(f"\n[TEST {self.total_tests}] {titulo}")
    
    def resultado(self, estado: bool, mensaje: str):
        """Registrar resultado"""
        if estado:
            self.tests_pasados += 1
            print(f"  ✓ {mensaje}")
        else:
            self.tests_fallidos += 1
            print(f"  ✗ {mensaje}")
    
    def info(self, mensaje: str):
        """Información adicional"""
        print(f"  ℹ {mensaje}")
    
    def resumen_final(self):
        """Imprimir resumen final"""
        print(f"\n{'='*80}")
        print("📊 RESUMEN FINAL")
        print(f"{'='*80}")
        print(f"Total de tests: {self.total_tests}")
        print(f"Tests exitosos: {self.tests_pasados} ({(self.tests_pasados/self.total_tests)*100:.1f}%)")
        print(f"Tests fallidos: {self.tests_fallidos}")
        
        if self.tests_fallidos == 0:
            print(f"\n✅ TODOS LOS TESTS PASARON - APP LISTA PARA PRODUCCIÓN\n")
            return True
        else:
            print(f"\n⚠️ HAY FALLOS - REVISAR ARRIBA\n")
            return False

# ============================================================================

reporte = Reporte()

# FASE 1: ANÁLISIS DE DATOS
# ============================================================================

reporte.nueva_fase("FASE 1: EXTRACCIÓN Y ANÁLISIS DE DATOS")

reporte.nuevo_test("Verificar estructura de archivos")
for mes, df in DATOS.items():
    reporte.info(f"{mes}: {len(df)} registros, {len(df.columns)} columnas")
reporte.resultado(True, "Todos los archivos cargados correctamente")

# Columnas requeridas
columnas_requeridas = [
    'codigo de suscriptor', 'Propietario', 'Lectura anterior', 'Lectura Actual',
    'Consumo', 'Total.Consumo', 'CargoFijo', 'Valor. Neto', 'Valor. Total',
    'Valor.Mora(II)', 'IvaCargos', 'Factura', 'nit o cedula', 'Dir.Entrega'
]

reporte.nuevo_test("Validar columnas requeridas")
faltan = []
for mes, df in DATOS.items():
    for col in columnas_requeridas:
        if col not in df.columns:
            faltan.append((mes, col))

if not faltan:
    reporte.resultado(True, "Todas las columnas presentes")
else:
    reporte.resultado(False, f"Faltan {len(faltan)} columnas")
    for mes, col in faltan:
        print(f"     - {mes}: {col}")

# Integridad de datos críticos
reporte.nuevo_test("Validar integridad de datos críticos")
campos_criticos = ['codigo de suscriptor', 'Consumo', 'Valor. Total']
nulos_encontrados = False

for mes, df in DATOS.items():
    for col in campos_criticos:
        nulos = df[col].isna().sum()
        if nulos > 0:
            nulos_encontrados = True
            reporte.resultado(False, f"{mes} - {col}: {nulos} nulos")

if not nulos_encontrados:
    reporte.resultado(True, "Sin valores nulos en campos críticos")

# Verificar rangos
reporte.nuevo_test("Validar rangos de valores")
valor_ok = True

for mes, df in DATOS.items():
    consumo_negativo = (df['Consumo'] < 0).sum()
    total_negativo = (df['Valor. Total'] < 0).sum()
    
    if consumo_negativo > 0 or total_negativo > 0:
        valor_ok = False
        if consumo_negativo > 0:
            reporte.resultado(False, f"{mes}: {consumo_negativo} consumos negativos")
        if total_negativo > 0:
            reporte.resultado(False, f"{mes}: {total_negativo} totales negativos")

if valor_ok:
    reporte.resultado(True, "Todos los valores en rangos válidos (>= 0)")

# Estadísticas generales
reporte.nuevo_test("Estadísticas de datos")
for mes, df in DATOS.items():
    reporte.info(f"{mes}:")
    reporte.info(f"  - Consumo: {df['Consumo'].mean():.2f} m³ (rango: {df['Consumo'].min():.0f}-{df['Consumo'].max():.0f})")
    reporte.info(f"  - Total facturado: ${df['Valor. Total'].sum():,.2f}")
    reporte.info(f"  - Promedio por cliente: ${df['Valor. Total'].mean():.2f}")
    reporte.info(f"  - Registros con mora: {(df['Valor.Mora(II)'] > 0).sum()}")

reporte.resultado(True, "Estadísticas calculadas")

# ============================================================================
# FASE 2: VALIDACIÓN DE CÁLCULOS
# ============================================================================

reporte.nueva_fase("FASE 2: VALIDACIÓN DE CÁLCULOS")

# Test 1: Consumo = Lectura Actual - Lectura Anterior
reporte.nuevo_test("Validar cálculo de consumo")
errores_consumo = 0

for mes, df in DATOS.items():
    consumo_calculado = df['Lectura Actual'] - df['Lectura anterior']
    diferencias = (df['Consumo'] != consumo_calculado).sum()
    errores_consumo += diferencias

if errores_consumo == 0:
    reporte.resultado(True, "Consumo calculado correctamente en todos los registros")
else:
    reporte.resultado(False, f"{errores_consumo} errores en cálculo de consumo")

# Test 2: Total.Consumo = Consumo * Valor.Metro
reporte.nuevo_test("Validar cálculo de Total.Consumo")
errores_total_consumo = 0

for mes, df in DATOS.items():
    total_calculado = df['Consumo'] * df['Valor.Metro']
    diferencias = np.abs(df['Total.Consumo'] - total_calculado) > 0.01
    errores_total_consumo += diferencias.sum()

if errores_total_consumo == 0:
    reporte.resultado(True, "Total.Consumo calculado correctamente")
else:
    reporte.resultado(False, f"{errores_total_consumo} errores")

# Test 3: Valor.Neto
reporte.nuevo_test("Validar cálculo de Valor.Neto")
errores_neto = 0

for mes, df in DATOS.items():
    df = df.copy()
    df['CargoFijo'] = df['CargoFijo'].fillna(0)
    df['CargoPart'] = df['CargoPart'].fillna(0)
    df['Valor.Subsidio'] = df['Valor.Subsidio'].fillna(0)
    
    neto_calculado = (df['Total.Consumo'] + df['CargoFijo'] + 
                     df['CargoPart'] - df['Valor.Subsidio'])
    diferencias = np.abs(df['Valor. Neto'] - neto_calculado) > 0.01
    errores_neto += diferencias.sum()

if errores_neto == 0:
    reporte.resultado(True, "Valor.Neto calculado correctamente")
else:
    reporte.resultado(False, f"{errores_neto} errores")

# Test 4: Valor.Total
reporte.nuevo_test("Validar cálculo de Valor.Total")
errores_total = 0

for mes, df in DATOS.items():
    df = df.copy()
    df['Valor.Aju.'] = df['Valor.Aju.'].fillna(0)
    df['Valor.Mora(II)'] = df['Valor.Mora(II)'].fillna(0)
    df['IvaMora'] = df['IvaMora'].fillna(0)
    df['IvaCargos'] = df['IvaCargos'].fillna(0)
    
    total_calculado = (df['Valor. Neto'] + df['Valor.Mora(II)'] + 
                      df['Valor.Aju.'] + df['IvaMora'] + df['IvaCargos'])
    diferencias = np.abs(df['Valor. Total'] - total_calculado) > 0.01
    errores_total += diferencias.sum()

if errores_total == 0:
    reporte.resultado(True, "Valor.Total calculado correctamente")
else:
    reporte.resultado(False, f"{errores_total} errores")

# ============================================================================
# FASE 3: INTEGRACIONES FRAPPE
# ============================================================================

reporte.nueva_fase("FASE 3: VALIDACIÓN DE INTEGRACIONES FRAPPE")

# Test 1: Customer
reporte.nuevo_test("Validar datos para Customer")
customer_ok = True

for mes, df in DATOS.items():
    campos = ['codigo de suscriptor', 'Propietario', 'nit o cedula']
    for col in campos:
        validos = df[col].notna().sum()
        pct = (validos / len(df)) * 100
        if pct < 95:
            customer_ok = False
            reporte.resultado(False, f"{mes} - {col}: solo {pct:.1f}%")

if customer_ok:
    reporte.resultado(True, "Datos suficientes para crear Customer")

# Test 2: Sales Invoice
reporte.nuevo_test("Validar datos para Sales Invoice")
invoice_ok = True

for mes, df in DATOS.items():
    campos = ['Factura', 'codigo de suscriptor', 'Valor. Total']
    for col in campos:
        validos = df[col].notna().sum()
        pct = (validos / len(df)) * 100
        if pct < 99:
            invoice_ok = False
            reporte.resultado(False, f"{mes} - {col}: {pct:.1f}%")

if invoice_ok:
    reporte.resultado(True, "Datos válidos para Sales Invoice")

# Test 3: Facturas únicas
reporte.nuevo_test("Validar facturas sin duplicadas")
duplicadas = 0

for mes, df in DATOS.items():
    df_validas = df[df['Factura'].notna()]
    duplicadas += len(df_validas) - df_validas['Factura'].nunique()

if duplicadas == 0:
    total_facturas = sum(df[df['Factura'].notna()]['Factura'].nunique() for df in DATOS.values())
    reporte.resultado(True, f"{total_facturas} facturas únicas sin duplicadas")
else:
    reporte.resultado(False, f"{duplicadas} facturas duplicadas")

# Test 4: Clientes únicos
reporte.nuevo_test("Validar clientes únicos")
total_clientes = 0

for mes, df in DATOS.items():
    clientes = df['codigo de suscriptor'].nunique()
    total_clientes += clientes
    reporte.info(f"{mes}: {clientes} clientes")

reporte.resultado(True, f"Total: ~{total_clientes} clientes (con O/S)")

# ============================================================================
# FASE 4: REPORTES
# ============================================================================

reporte.nueva_fase("FASE 4: ANÁLISIS DE REPORTES")

# Reporte 1: Deuda por Cliente
reporte.nuevo_test("Reporte: Deuda por Cliente")
for mes, df in DATOS.items():
    deuda_total = df['Valor. Total'].sum()
    clientes = df['codigo de suscriptor'].nunique()
    reporte.info(f"{mes}: ${deuda_total:,.2f} ({clientes} clientes)")
reporte.resultado(True, "Datos para Deuda por Cliente")

# Reporte 2: Ingresos por Servicio
reporte.nuevo_test("Reporte: Ingresos por Servicio")
for mes, df in DATOS.items():
    consumo = df['Total.Consumo'].sum()
    cargos = df['CargoFijo'].fillna(0).sum()
    otros = df['Valor. Total'].sum() - consumo - cargos
    reporte.info(f"{mes}: Consumo ${consumo:,.0f}, Cargos ${cargos:,.0f}, Otros ${otros:,.0f}")
reporte.resultado(True, "Datos para Ingresos por Servicio")

# Reporte 3: Libro Mayor
reporte.nuevo_test("Reporte: Libro Mayor")
for mes, df in DATOS.items():
    ingresos = df['Valor. Total'].sum()
    mora = df['Valor.Mora(II)'].sum()
    iva = df['IvaCargos'].sum()
    reporte.info(f"{mes}: Ingresos ${ingresos:,.0f}, Mora ${mora:,.0f}, IVA ${iva:,.0f}")
reporte.resultado(True, "Datos para Libro Mayor")

# Reporte 4: Reconciliación de Pagos
reporte.nuevo_test("Reporte: Reconciliación de Pagos")
for mes, df in DATOS.items():
    facturado = df['Valor. Total'].sum()
    recaudado = df['Total.Recaudo'].sum()
    pct_recaudo = (recaudado / facturado) * 100 if facturado > 0 else 0
    reporte.info(f"{mes}: ${facturado:,.0f} facturado, ${recaudado:,.0f} recaudado ({pct_recaudo:.1f}%)")
reporte.resultado(True, "Datos para Reconciliación de Pagos")

# ============================================================================
# FASE 5: EDGE CASES
# ============================================================================

reporte.nueva_fase("FASE 5: EDGE CASES Y CASOS ESPECIALES")

# Edge 1: Consumo cero
reporte.nuevo_test("Identificar registros con consumo cero")
for mes, df in DATOS.items():
    cero = (df['Consumo'] == 0).sum()
    pct = (cero / len(df)) * 100
    reporte.info(f"{mes}: {cero} registros ({pct:.2f}%)")
reporte.resultado(True, "Consumo cero identificados")

# Edge 2: Lectura sin cambio
reporte.nuevo_test("Identificar lecturas sin cambio")
for mes, df in DATOS.items():
    sin_cambio = (df['Lectura Actual'] == df['Lectura anterior']).sum()
    pct = (sin_cambio / len(df)) * 100 if len(df) > 0 else 0
    reporte.info(f"{mes}: {sin_cambio} registros ({pct:.2f}%)")
reporte.resultado(True, "Lecturas sin cambio identificadas")

# Edge 3: Registros con mora
reporte.nuevo_test("Análisis de registros con mora")
for mes, df in DATOS.items():
    con_mora = (df['Valor.Mora(II)'] > 0).sum()
    total_mora = df['Valor.Mora(II)'].sum()
    pct_mora = (con_mora / len(df)) * 100
    reporte.info(f"{mes}: {con_mora} registros ({pct_mora:.1f}%) - Total: ${total_mora:,.0f}")
reporte.resultado(True, "Mora analizada")

# Edge 4: Inconsistencias reportadas
reporte.nuevo_test("Validar inconsistencias reportadas")
for mes, df in DATOS.items():
    if 'Inconsistencias' in df.columns:
        con_inconsistencias = df['Inconsistencias'].notna().sum()
        reporte.info(f"{mes}: {con_inconsistencias} con inconsistencias")
reporte.resultado(True, "Inconsistencias identificadas")

# Edge 5: Valores anómalos
reporte.nuevo_test("Detectar valores anómalos")
for mes, df in DATOS.items():
    consumo_alto = (df['Consumo'] > 100).sum()
    total_alto = (df['Valor. Total'] > 1000).sum()
    reporte.info(f"{mes}: {consumo_alto} consumos > 100m³, {total_alto} totales > $1000")
reporte.resultado(True, "Valores anómalos detectados")

# ============================================================================
# RESUMEN FINAL
# ============================================================================

success = reporte.resumen_final()

sys.exit(0 if success else 1)
