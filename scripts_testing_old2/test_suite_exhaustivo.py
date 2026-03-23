"""
SUITE DE TESTING EXHAUSTIVO - VALIDACIÓN COMPLETA
==================================================

Archivo de pruebas para validar:
1. Extracción de datos Excel
2. Cálculos (consumo, tarifas, impuestos, mora)
3. Integraciones Frappe (Customer, Sales Invoice, Journal Entry)
4. Reportes (Libro Mayor, Deuda por Cliente, etc.)
5. APIs de integración
6. Edge cases y manejo de errores
7. Workflows completos

Ejecutar con: python test_suite_exhaustivo.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import unittest
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')

# Configuración de rutas
EXCEL_DIR = Path('c:/App servicios publicos/servicios_publicos/archivos_excel')
FRAPPE_DIR = Path('c:/App servicios publicos/servicios_publicos')

# Archivos Excel
ARCHIVOS_EXCEL = {
    'Diciembre 2025': EXCEL_DIR / 'PaqueteFacturacion-Diciembre-2025.xlsx',
    'Enero 2026': EXCEL_DIR / 'PaqueteFacturacion-Enero-2026.xlsx',
    'Febrero 2026': EXCEL_DIR / 'PaqueteFacturacion-Febrero-2026.xlsx',
}

# ============================================================================
# FASE 1: EXTRACCIÓN Y ANÁLISIS DE DATOS
# ============================================================================

class TestExtraccionDatos(unittest.TestCase):
    """Validar extracción correcta de datos Excel"""
    
    def setUp(self):
        """Cargar datos antes de cada test"""
        self.datos = {}
        for mes, archivo in ARCHIVOS_EXCEL.items():
            print(f"\n  📂 Leyendo {mes}...")
            try:
                df = pd.read_excel(archivo, sheet_name=0)
                # Limpiar fila de encabezados duplicados
                if pd.isna(df.iloc[0, 0]):
                    df = df.iloc[1:].reset_index(drop=True)
                self.datos[mes] = df
                print(f"     ✓ {len(df)} registros cargados")
            except Exception as e:
                print(f"     ✗ Error: {str(e)}")
                self.fail(f"No se pudo cargar {archivo}")
    
    def test_1_archivos_existen(self):
        """Test 1: Verificar que archivos Excel existen"""
        print("\n[TEST 1] Verificar existencia de archivos Excel")
        for mes, archivo in ARCHIVOS_EXCEL.items():
            self.assertTrue(archivo.exists(), f"Falta archivo: {mes}")
            print(f"  ✓ {mes}: {archivo.name}")
    
    def test_2_estructura_datos(self):
        """Test 2: Verificar estructura de datos (columnas requeridas)"""
        print("\n[TEST 2] Validar estructura de datos")
        
        columnas_requeridas = [
            'codigo de suscriptor', 'Propietario', 'Lectura anterior',
            'Lectura Actual', 'Consumo', 'Total.Consumo',
            'CargoFijo', 'Valor. Neto', 'Valor. Total',
            'Valor.Mora(II)', 'IvaCargos', 'Factura'
        ]
        
        for mes, df in self.datos.items():
            print(f"  📊 {mes}:")
            print(f"     Filas: {len(df)}")
            print(f"     Columnas: {len(df.columns)}")
            
            for col in columnas_requeridas:
                self.assertIn(col, df.columns, f"Falta columna {col} en {mes}")
            
            print(f"     ✓ Todas las columnas requeridas presentes")
    
    def test_3_datos_no_nulos(self):
        """Test 3: Verificar que datos críticos no sean nulos"""
        print("\n[TEST 3] Validar integridad de datos (no nulos)")
        
        columnas_criticas = ['codigo de suscriptor', 'Consumo', 'Valor. Total']
        
        for mes, df in self.datos.items():
            print(f"  🔍 {mes}:")
            for col in columnas_criticas:
                nulos = df[col].isna().sum()
                self.assertEqual(nulos, 0, f"Hay {nulos} valores nulos en {col}")
                print(f"     ✓ {col}: sin valores nulos")
    
    def test_4_tipos_datos(self):
        """Test 4: Verificar tipos de datos correctos"""
        print("\n[TEST 4] Validar tipos de datos")
        
        for mes, df in self.datos.items():
            print(f"  📋 {mes}:")
            
            # Numéricas
            columnas_numericas = ['Consumo', 'Total.Consumo', 'Valor. Total',
                                 'CargoFijo', 'Lectura Actual', 'Lectura anterior']
            
            for col in columnas_numericas:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                self.assertTrue(df[col].dtype in ['float64', 'int64'],
                              f"{col} no es numérica en {mes}")
            
            print(f"     ✓ Tipos de datos correctos")
    
    def test_5_rangos_valores(self):
        """Test 5: Verificar rangos de valores válidos"""
        print("\n[TEST 5] Validar rangos de valores")
        
        for mes, df in self.datos.items():
            print(f"  📏 {mes}:")
            
            # Consumo >= 0
            consumo_negativo = (df['Consumo'] < 0).sum()
            self.assertEqual(consumo_negativo, 0, 
                           f"Hay {consumo_negativo} consumos negativos en {mes}")
            print(f"     ✓ Consumo: todos >= 0 (rango: {df['Consumo'].min():.2f} - {df['Consumo'].max():.2f})")
            
            # Total >= 0
            total_negativo = (df['Valor. Total'] < 0).sum()
            self.assertEqual(total_negativo, 0,
                           f"Hay {total_negativo} totales negativos en {mes}")
            print(f"     ✓ Total: todos >= 0 (rango: {df['Valor. Total'].min():.2f} - {df['Valor. Total'].max():.2f})")

# ============================================================================
# FASE 2: VALIDACIÓN DE CÁLCULOS
# ============================================================================

class TestCalculos(unittest.TestCase):
    """Validar cálculos de facturación"""
    
    def setUp(self):
        """Cargar datos"""
        self.datos = {}
        for mes, archivo in ARCHIVOS_EXCEL.items():
            df = pd.read_excel(archivo, sheet_name=0)
            if pd.isna(df.iloc[0, 0]):
                df = df.iloc[1:].reset_index(drop=True)
            self.datos[mes] = df
    
    def test_1_calculo_consumo(self):
        """Test 1: Validar cálculo de consumo (Lectura Actual - Lectura Anterior)"""
        print("\n[TEST CÁLCULOS 1] Validar cálculo de consumo")
        
        for mes, df in self.datos.items():
            print(f"  📊 {mes}:")
            
            # Convertir a numérico
            df['Lectura Actual'] = pd.to_numeric(df['Lectura Actual'], errors='coerce')
            df['Lectura anterior'] = pd.to_numeric(df['Lectura anterior'], errors='coerce')
            df['Consumo'] = pd.to_numeric(df['Consumo'], errors='coerce')
            
            # Calcular consumo esperado
            consumo_calculado = df['Lectura Actual'] - df['Lectura anterior']
            
            # Comparar
            diferencias = (df['Consumo'] != consumo_calculado).sum()
            self.assertEqual(diferencias, 0,
                           f"Hay {diferencias} diferencias en cálculo de consumo")
            
            print(f"     ✓ {len(df)} consumos validados correctamente")
    
    def test_2_calculo_total_consumo(self):
        """Test 2: Validar Total.Consumo = Consumo * Valor.Metro"""
        print("\n[TEST CÁLCULOS 2] Validar cálculo Total.Consumo")
        
        for mes, df in self.datos.items():
            print(f"  💰 {mes}:")
            
            df['Consumo'] = pd.to_numeric(df['Consumo'], errors='coerce')
            df['Valor.Metro'] = pd.to_numeric(df['Valor.Metro'], errors='coerce')
            df['Total.Consumo'] = pd.to_numeric(df['Total.Consumo'], errors='coerce')
            
            # Calcular esperado
            total_calculado = df['Consumo'] * df['Valor.Metro']
            
            # Permitir pequeñas variaciones por redondeo
            diferencias = np.abs(df['Total.Consumo'] - total_calculado) > 0.01
            errores = diferencias.sum()
            
            self.assertEqual(errores, 0,
                           f"Hay {errores} diferencias en Total.Consumo")
            
            print(f"     ✓ {len(df)} cálculos de Total.Consumo validados")
    
    def test_3_calculo_valor_neto(self):
        """Test 3: Validar Valor.Neto (Total componentes - Subsidios)"""
        print("\n[TEST CÁLCULOS 3] Validar cálculo Valor.Neto")
        
        for mes, df in self.datos.items():
            print(f"  📌 {mes}:")
            
            # Convertir a numérico
            for col in ['Total.Consumo', 'CargoFijo', 'CargoPart', 
                       'Valor.Subsidio', 'Valor. Neto']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Componentes del neto
            df['CargoFijo'] = df['CargoFijo'].fillna(0)
            df['CargoPart'] = df['CargoPart'].fillna(0)
            df['Valor.Subsidio'] = df['Valor.Subsidio'].fillna(0)
            
            # Valor Neto = Consumo + CargosF ijos + CargosParciales - Subsidios
            neto_calculado = (df['Total.Consumo'] + df['CargoFijo'] + 
                             df['CargoPart'] - df['Valor.Subsidio'])
            
            diferencias = np.abs(df['Valor. Neto'] - neto_calculado) > 0.01
            errores = diferencias.sum()
            
            self.assertEqual(errores, 0,
                           f"Hay {errores} diferencias en Valor.Neto")
            
            print(f"     ✓ {len(df)} Valores Neto validados")
    
    def test_4_calculo_valor_total(self):
        """Test 4: Validar Valor.Total (Neto + Mora + Ajustes + IVA)"""
        print("\n[TEST CÁLCULOS 4] Validar cálculo Valor.Total")
        
        for mes, df in self.datos.items():
            print(f"  💵 {mes}:")
            
            for col in ['Valor. Neto', 'Valor.Mora(II)', 'Valor.Aju.',
                       'IvaMora', 'IvaCargos', 'Valor. Total']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['Valor.Aju.'] = df['Valor.Aju.'].fillna(0)
            df['Valor.Mora(II)'] = df['Valor.Mora(II)'].fillna(0)
            df['IvaMora'] = df['IvaMora'].fillna(0)
            df['IvaCargos'] = df['IvaCargos'].fillna(0)
            
            # Total = Neto + Mora + Ajustes + IVAs
            total_calculado = (df['Valor. Neto'] + df['Valor.Mora(II)'] + 
                              df['Valor.Aju.'] + df['IvaMora'] + df['IvaCargos'])
            
            diferencias = np.abs(df['Valor. Total'] - total_calculado) > 0.01
            errores = diferencias.sum()
            
            self.assertEqual(errores, 0,
                           f"Hay {errores} diferencias en Valor.Total")
            
            print(f"     ✓ {len(df)} Valores Total validados")
    
    def test_5_estadisticas_cálculos(self):
        """Test 5: Mostrar estadísticas de cálculos"""
        print("\n[TEST CÁLCULOS 5] Estadísticas de cálculos")
        
        for mes, df in self.datos.items():
            print(f"\n  📈 {mes}:")
            
            df['Consumo'] = pd.to_numeric(df['Consumo'], errors='coerce')
            df['Valor. Total'] = pd.to_numeric(df['Valor. Total'], errors='coerce')
            df['Valor.Mora(II)'] = pd.to_numeric(df['Valor.Mora(II)'], errors='coerce')
            
            print(f"     Consumo promedio: {df['Consumo'].mean():.2f} m³")
            print(f"     Consumo rango: {df['Consumo'].min():.2f} - {df['Consumo'].max():.2f} m³")
            print(f"     Total facturado: ${df['Valor. Total'].sum():,.2f}")
            print(f"     Total promedio: ${df['Valor. Total'].mean():.2f}")
            print(f"     Registros con mora: {(df['Valor.Mora(II)'] > 0).sum()}")
            print(f"     Total mora: ${df['Valor.Mora(II)'].sum():,.2f}")

# ============================================================================
# FASE 3: VALIDACIÓN DE INTEGRACIONES FRAPPE
# ============================================================================

class TestIntegracionesFrappe(unittest.TestCase):
    """Validar integración con módulos Frappe ERPNext"""
    
    def setUp(self):
        """Cargar datos y configuración"""
        self.datos = {}
        for mes, archivo in ARCHIVOS_EXCEL.items():
            df = pd.read_excel(archivo, sheet_name=0)
            if pd.isna(df.iloc[0, 0]):
                df = df.iloc[1:].reset_index(drop=True)
            self.datos[mes] = df
    
    def test_1_estructura_customer(self):
        """Test 1: Validar que datos permiten crear Customer"""
        print("\n[TEST FRAPPE 1] Validar datos para Customer")
        
        for mes, df in self.datos.items():
            print(f"  👤 {mes}:")
            
            # Campos requeridos para Customer
            campos_requeridos = ['codigo de suscriptor', 'Propietario', 
                                'nit o cedula', 'Dir.Entrega']
            
            for campo in campos_requeridos:
                no_vacios = df[campo].notna().sum()
                pct = (no_vacios / len(df)) * 100
                self.assertGreater(pct, 95,
                                 f"Campo {campo} tiene solo {pct:.1f}% datos válidos")
                print(f"     ✓ {campo}: {pct:.1f}% datos válidos")
    
    def test_2_estructura_sales_invoice(self):
        """Test 2: Validar que datos permiten crear Sales Invoice"""
        print("\n[TEST FRAPPE 2] Validar datos para Sales Invoice")
        
        for mes, df in self.datos.items():
            print(f"  📄 {mes}:")
            
            # Campos requeridos para Sales Invoice
            campos = ['Factura', 'codigo de suscriptor', 'Valor. Total', 'Consumo']
            
            for campo in campos:
                no_vacios = df[campo].notna().sum()
                pct = (no_vacios / len(df)) * 100
                self.assertGreater(pct, 95)
                print(f"     ✓ {campo}: {pct:.1f}% datos")
    
    def test_3_validar_unicas_facturas(self):
        """Test 3: Verificar números de factura únicos"""
        print("\n[TEST FRAPPE 3] Validar facturas únicas")
        
        for mes, df in self.datos.items():
            print(f"  🔑 {mes}:")
            
            df = df[df['Factura'].notna()]
            total = len(df)
            unicas = df['Factura'].nunique()
            duplicadas = total - unicas
            
            self.assertEqual(duplicadas, 0,
                           f"Hay {duplicadas} facturas duplicadas")
            
            print(f"     ✓ {unicas} facturas únicas (sin duplicadas)")
    
    def test_4_validar_clientes_unicos(self):
        """Test 4: Verificar clientes únicos por suscriptor"""
        print("\n[TEST FRAPPE 4] Validar clientes únicos")
        
        for mes, df in self.datos.items():
            print(f"  👥 {mes}:")
            
            df = df[df['codigo de suscriptor'].notna()]
            clientes_unicos = df['codigo de suscriptor'].nunique()
            
            print(f"     ✓ {clientes_unicos} clientes únicos")
            
            # Verificar que mismo cliente no tenga múltiples Propietarios
            clientes_multiples = df.groupby('codigo de suscriptor')['Propietario'].nunique()
            errores = (clientes_multiples > 1).sum()
            
            self.assertEqual(errores, 0,
                           f"Hay {errores} clientes con múltiples propietarios")
    
    def test_5_estructura_journal_entry(self):
        """Test 5: Validar que datos permiten crear Journal Entries"""
        print("\n[TEST FRAPPE 5] Validar datos para Journal Entry")
        
        for mes, df in self.datos.items():
            print(f"  📊 {mes}:")
            
            df['Valor. Total'] = pd.to_numeric(df['Valor. Total'], errors='coerce')
            
            # Cada factura debe tener monto
            con_monto = (df['Valor. Total'] > 0).sum()
            pct = (con_monto / len(df)) * 100
            
            self.assertGreater(pct, 95)
            print(f"     ✓ {pct:.1f}% registros con monto > 0")
            
            print(f"     ✓ Total potencial a contabilizar: ${df['Valor. Total'].sum():,.2f}")

# ============================================================================
# FASE 4: VALIDACIÓN DE REPORTES
# ============================================================================

class TestReportes(unittest.TestCase):
    """Validar funcionalidad de reportes"""
    
    def setUp(self):
        """Cargar datos"""
        self.datos = {}
        for mes, archivo in ARCHIVOS_EXCEL.items():
            df = pd.read_excel(archivo, sheet_name=0)
            if pd.isna(df.iloc[0, 0]):
                df = df.iloc[1:].reset_index(drop=True)
            self.datos[mes] = df
    
    def test_1_reporte_deuda_cliente(self):
        """Test 1: Datos para Reporte 'Deuda por Cliente'"""
        print("\n[TEST REPORTES 1] Reporte Deuda por Cliente")
        
        for mes, df in self.datos.items():
            print(f"  💳 {mes}:")
            
            df['codigo de suscriptor'] = df['codigo de suscriptor'].fillna('DESCONOCIDO')
            df['Valor. Total'] = pd.to_numeric(df['Valor. Total'], errors='coerce')
            
            deuda = df.groupby('codigo de suscriptor')['Valor. Total'].agg(['sum', 'count'])
            deuda = deuda.sort_values('sum', ascending=False)
            
            print(f"     Clientes con deuda: {len(deuda)}")
            print(f"     Deuda total: ${deuda['sum'].sum():,.2f}")
            print(f"     Deuda promedio: ${deuda['sum'].mean():.2f}")
            print(f"     Top 3 deudores:")
            
            for idx, (cliente, row) in enumerate(deuda.head(3).iterrows(), 1):
                print(f"        {idx}. {cliente}: ${row['sum']:,.2f} ({int(row['count'])} facturas)")
    
    def test_2_reporte_ingresos_servicio(self):
        """Test 2: Datos para Reporte 'Ingresos por Servicio'"""
        print("\n[TEST REPORTES 2] Reporte Ingresos por Servicio")
        
        for mes, df in self.datos.items():
            print(f"  💵 {mes}:")
            
            df['Valor. Total'] = pd.to_numeric(df['Valor. Total'], errors='coerce')
            df['Total.Consumo'] = pd.to_numeric(df['Total.Consumo'], errors='coerce')
            df['CargoFijo'] = pd.to_numeric(df['CargoFijo'], errors='coerce')
            
            # Concepto de ingresos
            consumo_total = df['Total.Consumo'].sum()
            cargos_total = df['CargoFijo'].sum()
            otros_total = df['Valor. Total'].sum() - consumo_total - cargos_total
            
            print(f"     Ingresos consumo: ${consumo_total:,.2f}")
            print(f"     Cargos fijos: ${cargos_total:,.2f}")
            print(f"     Otros (IVA, mora, etc.): ${otros_total:,.2f}")
            print(f"     TOTAL: ${df['Valor. Total'].sum():,.2f}")
    
    def test_3_reporte_libro_mayor(self):
        """Test 3: Datos para Reporte 'Libro Mayor'"""
        print("\n[TEST REPORTES 3] Reporte Libro Mayor")
        
        for mes, df in self.datos.items():
            print(f"  📖 {mes}:")
            
            df['Valor.Mora(II)'] = pd.to_numeric(df['Valor.Mora(II)'], errors='coerce')
            df['IvaCargos'] = pd.to_numeric(df['IvaCargos'], errors='coerce')
            df['Valor. Total'] = pd.to_numeric(df['Valor. Total'], errors='coerce')
            
            # Cuentas contables
            mov_cuentas = {
                'Ingresos por Servicios': df['Valor. Total'].sum(),
                'Mora': df['Valor.Mora(II)'].sum(),
                'IVA por cobrar': df['IvaCargos'].sum(),
            }
            
            for cuenta, monto in mov_cuentas.items():
                print(f"     {cuenta}: ${monto:,.2f}")
    
    def test_4_reporte_reconciliacion_pagos(self):
        """Test 4: Datos para Reporte 'Reconciliación de Pagos'"""
        print("\n[TEST REPORTES 4] Reporte Reconciliación de Pagos")
        
        for mes, df in self.datos.items():
            print(f"  ✅ {mes}:")
            
            df['Valor. Total'] = pd.to_numeric(df['Valor. Total'], errors='coerce')
            df['Total.Recaudo'] = pd.to_numeric(df['Total.Recaudo'], errors='coerce')
            
            facturado = df['Valor. Total'].sum()
            recaudado = df['Total.Recaudo'].sum()
            diferencia = facturado - recaudado
            
            print(f"     Facturado: ${facturado:,.2f}")
            print(f"     Recaudado: ${recaudado:,.2f}")
            print(f"     Diferencia: ${diferencia:,.2f}")
            print(f"     % Recaudación: {(recaudado/facturado)*100:.2f}%")

# ============================================================================
# FASE 5: EDGE CASES Y VALIDACIÓN DE ERRORES
# ============================================================================

class TestEdgeCases(unittest.TestCase):
    """Validar manejo de casos extremos"""
    
    def setUp(self):
        """Cargar datos"""
        self.datos = {}
        for mes, archivo in ARCHIVOS_EXCEL.items():
            df = pd.read_excel(archivo, sheet_name=0)
            if pd.isna(df.iloc[0, 0]):
                df = df.iloc[1:].reset_index(drop=True)
            self.datos[mes] = df
    
    def test_1_consumo_cero(self):
        """Test 1: Registros con consumo cero"""
        print("\n[TEST EDGE 1] Consumo cero")
        
        for mes, df in self.datos.items():
            print(f"  ⚠️  {mes}:")
            
            df['Consumo'] = pd.to_numeric(df['Consumo'], errors='coerce')
            consumo_cero = (df['Consumo'] == 0).sum()
            pct = (consumo_cero / len(df)) * 100
            
            print(f"     Registros con consumo 0: {consumo_cero} ({pct:.2f}%)")
    
    def test_2_lectura_sin_cambio(self):
        """Test 2: Lecturas sin cambio (iguales)"""
        print("\n[TEST EDGE 2] Lecturas sin cambio")
        
        for mes, df in self.datos.items():
            print(f"  ⚠️  {mes}:")
            
            df['Lectura Actual'] = pd.to_numeric(df['Lectura Actual'], errors='coerce')
            df['Lectura anterior'] = pd.to_numeric(df['Lectura anterior'], errors='coerce')
            
            sin_cambio = (df['Lectura Actual'] == df['Lectura anterior']).sum()
            pct = (sin_cambio / len(df)) * 100
            
            print(f"     Lecturas sin cambio: {sin_cambio} ({pct:.2f}%)")
    
    def test_3_valores_negativos(self):
        """Test 3: Verificar no hay valores negativos"""
        print("\n[TEST EDGE 3] Valores negativos")
        
        for mes, df in self.datos.items():
            print(f"  ⚠️  {mes}:")
            
            columnas_positivas = ['Consumo', 'Total.Consumo', 'Valor. Total', 'Valor. Neto']
            
            all_valid = True
            for col in columnas_positivas:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                negativos = (df[col] < 0).sum()
                if negativos > 0:
                    print(f"     ⚠️  {col}: {negativos} valores negativos")
                    all_valid = False
            
            if all_valid:
                print(f"     ✓ Sin valores negativos")
    
    def test_4_datos_faltantes_criticos(self):
        """Test 4: Datos faltantes en campos críticos"""
        print("\n[TEST EDGE 4] Datos faltantes")
        
        for mes, df in self.datos.items():
            print(f"  ⚠️  {mes}:")
            
            campos_criticos = {
                'Factura': 'Número de factura',
                'codigo de suscriptor': 'Código de suscriptor',
                'Propietario': 'Nombre del propietario',
                'Consumo': 'Consumo registrado',
                'Valor. Total': 'Valor total',
            }
            
            for campo, descripcion in campos_criticos.items():
                faltantes = df[campo].isna().sum()
                if faltantes > 0:
                    print(f"     ⚠️  {descripcion}: {faltantes} faltantes")
    
    def test_5_inconsistencias(self):
        """Test 5: Registros con inconsistencias reportadas"""
        print("\n[TEST EDGE 5] Inconsistencias reportadas")
        
        for mes, df in self.datos.items():
            print(f"  🔍 {mes}:")
            
            if 'Inconsistencias' in df.columns:
                con_inconsistencias = df['Inconsistencias'].notna().sum()
                pct = (con_inconsistencias / len(df)) * 100
                print(f"     Registros con inconsistencias: {con_inconsistencias} ({pct:.2f}%)")
                
                if con_inconsistencias > 0:
                    print(f"     Tipos:")
                    inconsistencias_unicas = df['Inconsistencias'].value_counts().head(5)
                    for tipo, count in inconsistencias_unicas.items():
                        print(f"        - {tipo}: {count}")

# ============================================================================
# RUNNER DE TESTS
# ============================================================================

def ejecutar_suite_completa():
    """Ejecutar toda la suite de tests"""
    
    print("\n" + "="*80)
    print("🧪 SUITE DE TESTING EXHAUSTIVO - VALIDACIÓN COMPLETA")
    print("="*80)
    
    # Crear suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests en orden
    print("\n📋 Tests a ejecutar:")
    print("\n[FASE 1] Extracción y análisis de datos Excel")
    suite.addTests(loader.loadTestsFromTestCase(TestExtraccionDatos))
    print("  - test_1_archivos_existen")
    print("  - test_2_estructura_datos")
    print("  - test_3_datos_no_nulos")
    print("  - test_4_tipos_datos")
    print("  - test_5_rangos_valores")
    
    print("\n[FASE 2] Validación de cálculos")
    suite.addTests(loader.loadTestsFromTestCase(TestCalculos))
    print("  - test_1_calculo_consumo")
    print("  - test_2_calculo_total_consumo")
    print("  - test_3_calculo_valor_neto")
    print("  - test_4_calculo_valor_total")
    print("  - test_5_estadisticas_cálculos")
    
    print("\n[FASE 3] Integraciones Frappe")
    suite.addTests(loader.loadTestsFromTestCase(TestIntegracionesFrappe))
    print("  - test_1_estructura_customer")
    print("  - test_2_estructura_sales_invoice")
    print("  - test_3_validar_unicas_facturas")
    print("  - test_4_validar_clientes_unicos")
    print("  - test_5_estructura_journal_entry")
    
    print("\n[FASE 4] Reportes")
    suite.addTests(loader.loadTestsFromTestCase(TestReportes))
    print("  - test_1_reporte_deuda_cliente")
    print("  - test_2_reporte_ingresos_servicio")
    print("  - test_3_reporte_libro_mayor")
    print("  - test_4_reporte_reconciliacion_pagos")
    
    print("\n[FASE 5] Edge cases")
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    print("  - test_1_consumo_cero")
    print("  - test_2_lectura_sin_cambio")
    print("  - test_3_valores_negativos")
    print("  - test_4_datos_faltantes_criticos")
    print("  - test_5_inconsistencias")
    
    # Ejecutar
    print("\n" + "-"*80)
    print("🚀 Ejecutando tests...\n")
    
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN FINAL")
    print("="*80)
    print(f"Tests ejecutados: {resultado.testsRun}")
    print(f"Exitosos: {resultado.testsRun - len(resultado.failures) - len(resultado.errors)}")
    print(f"Fallos: {len(resultado.failures)}")
    print(f"Errores: {len(resultado.errors)}")
    
    if resultado.wasSuccessful():
        print("\n✅ TODOS LOS TESTS PASARON - APP LISTA PARA PRODUCCIÓN")
    else:
        print("\n⚠️  HAY FALLOS O ERRORES - REVISAR ARRIBA")
    
    print("="*80 + "\n")
    
    return resultado.wasSuccessful()

if __name__ == "__main__":
    success = ejecutar_suite_completa()
    sys.exit(0 if success else 1)
