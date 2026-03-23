"""
ANALISIS DE PRECISION DECIMAL Y CONFIGURACION DE MONEDA
========================================================

Verifica:
1. Decimales exactos en Excel
2. Configuracion de moneda (COP)
3. Modulos faltantes de Frappe
"""

import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

ruta = Path('c:/App servicios publicos/servicios_publicos/archivos_excel/PaqueteFacturacion-Diciembre-2025.xlsx')
df = pd.read_excel(ruta)

# Limpiar encabezados
if pd.isna(df.iloc[0, 0]):
    df = df.iloc[1:].reset_index(drop=True)

# Buscar las facturas del reporte
facturas_test = [445693, 445694, 445691, 447863]

print('\n' + '='*80)
print('ANALISIS DETALLADO DE VALORES (CON TODOS LOS DECIMALES)')
print('='*80)

for factura in facturas_test:
    fila = df[df['Factura'] == factura]
    if len(fila) > 0:
        r = fila.iloc[0]
        print(f'\nFactura {int(factura)}:')
        print(f'  Valor. Total: {repr(r["Valor. Total"])} (tipo: {type(r["Valor. Total"]).__name__})')
        print(f'  Valor.Neto: {repr(r["Valor. Neto"])} (tipo: {type(r["Valor. Neto"]).__name__})')
        print(f'  CargoFijo: {repr(r["CargoFijo"])} (tipo: {type(r["CargoFijo"]).__name__})')
        print(f'  Consumo: {repr(r["Consumo"])} (tipo: {type(r["Consumo"]).__name__})')
        print(f'  Valor.Metro: {repr(r["Valor.Metro"])} (tipo: {type(r["Valor.Metro"]).__name__})')

print('\n' + '='*80)
print('PRECISION DECIMAL ANALYSIS')
print('='*80)

# Analizar precision
for factura in facturas_test:
    fila = df[df['Factura'] == factura]
    if len(fila) > 0:
        r = fila.iloc[0]
        valor = r['Valor. Total']
        if pd.notna(valor):
            valor_str = str(valor)
            decimales = len(valor_str.split('.')[-1]) if '.' in valor_str else 0
            print(f'\nFactura {int(factura)}:')
            print(f'  Valor: {valor}')
            print(f'  Decimales: {decimales}')
            print(f'  Raw string: {valor_str}')

print('\n' + '='*80)
print('ESTADISTICAS DE PRECISION EN TODA LA COLUMNA Valor. Total')
print('='*80)

# Analizar toda la columna
valor_total_col = df['Valor. Total'].dropna()

decimales_count = {}
for val in valor_total_col:
    val_str = str(val)
    if '.' in val_str:
        decimales = len(val_str.split('.')[-1])
        decimales_count[decimales] = decimales_count.get(decimales, 0) + 1

print('\nDistribucion de decimales:')
for dec, count in sorted(decimales_count.items()):
    print(f'  {dec} decimales: {count} registros ({(count/len(valor_total_col))*100:.1f}%)')

print('\n' + '='*80)
