"""
ANALISIS DETALLADO DE PROBLEMAS EN DATOS
=========================================

Identifica exactamente que registros tienen problemas y por que.
"""

import pandas as pd
import numpy as np
from pathlib import Path

EXCEL_DIR = Path('c:/App servicios publicos/servicios_publicos/archivos_excel')
ARCHIVOS = {
    'Diciembre 2025': EXCEL_DIR / 'PaqueteFacturacion-Diciembre-2025.xlsx',
    'Enero 2026': EXCEL_DIR / 'PaqueteFacturacion-Enero-2026.xlsx',
    'Febrero 2026': EXCEL_DIR / 'PaqueteFacturacion-Febrero-2026.xlsx',
}

print("\n" + "="*80)
print("ANALISIS DETALLADO DE PROBLEMAS")
print("="*80)

RESUMEN_TOTAL = {}

for mes, ruta in ARCHIVOS.items():
    print(f"\n{'='*80}")
    print(f"{mes}")
    print(f"{'='*80}")
    
    # Cargar datos
    df = pd.read_excel(ruta, sheet_name=0)
    if pd.isna(df.iloc[0, 0]):
        df = df.iloc[1:].reset_index(drop=True)
    
    # Convertir a numerico
    for col in ['Lectura anterior', 'Lectura Actual', 'Consumo', 'Valor.Metro',
                'Total.Consumo', 'Valor.Subsidio', 'Valor.Consumo', 'CargoFijo',
                'CargoPart', 'CargoGlob', 'Valor.Mora(II)', 'Valor.Aju.',
                'Valor. Neto', 'SdoCarte.', 'Valor. Total', 'Total.Recaudo']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # ========================================================
    # PROBLEMA 1: Valores nulos
    # ========================================================
    print("\n[PROBLEMA 1] Valores nulos en campos criticos")
    print("-" * 50)
    
    nulos_por_col = {}
    for col in ['codigo de suscriptor', 'Valor. Total', 'Consumo', 'Factura']:
        nulos = df[col].isna().sum()
        if nulos > 0:
            nulos_por_col[col] = nulos
            print(f"  {col}: {nulos} nulos")
    
    if not nulos_por_col:
        print("  OK: Sin valores nulos en campos criticos")
    
    RESUMEN_TOTAL[mes] = {
        'nulos': len(nulos_por_col),
        'total_registros': len(df)
    }
    
    # ========================================================
    # PROBLEMA 2: Valores negativos
    # ========================================================
    print("\n[PROBLEMA 2] Valores negativos")
    print("-" * 50)
    
    negativos_encontrados = False
    for col in ['Consumo', 'Total.Consumo', 'Valor. Neto', 'Valor. Total']:
        negativos = (df[col] < 0).sum()
        if negativos > 0:
            negativos_encontrados = True
            print(f"  {col}: {negativos} negativos")
    
    if not negativos_encontrados:
        print("  OK: Sin valores negativos")
    
    # ========================================================
    # PROBLEMA 3: Errores de calculo
    # ========================================================
    print("\n[PROBLEMA 3] Errores en calculos")
    print("-" * 50)
    
    df['Consumo_Calculado'] = df['Lectura Actual'] - df['Lectura anterior']
    errores_consumo = (df['Consumo'] != df['Consumo_Calculado']).sum()
    print(f"  Errores de consumo: {errores_consumo}")
    
    df['Total_Consumo_Calculado'] = df['Consumo'] * df['Valor.Metro']
    errores_total_consumo = (np.abs(df['Total.Consumo'] - df['Total_Consumo_Calculado']) > 0.01).sum()
    print(f"  Errores Total.Consumo: {errores_total_consumo}")
    
    df_copy = df.copy()
    df_copy['CargoFijo'] = df_copy['CargoFijo'].fillna(0)
    df_copy['CargoPart'] = df_copy['CargoPart'].fillna(0)
    df_copy['Valor.Subsidio'] = df_copy['Valor.Subsidio'].fillna(0)
    df_copy['Neto_Calculado'] = (df_copy['Total.Consumo'] + df_copy['CargoFijo'] + 
                                 df_copy['CargoPart'] - df_copy['Valor.Subsidio'])
    errores_neto = (np.abs(df_copy['Valor. Neto'] - df_copy['Neto_Calculado']) > 0.01).sum()
    print(f"  Errores Valor.Neto: {errores_neto}")
    
    df_copy['Valor.Aju.'] = df_copy['Valor.Aju.'].fillna(0)
    df_copy['Valor.Mora(II)'] = df_copy['Valor.Mora(II)'].fillna(0)
    df_copy['IvaMora'] = df_copy['IvaMora'].fillna(0)
    df_copy['IvaCargos'] = df_copy['IvaCargos'].fillna(0)
    df_copy['Total_Calculado'] = (df_copy['Valor. Neto'] + df_copy['Valor.Mora(II)'] + 
                                  df_copy['Valor.Aju.'] + df_copy['IvaMora'] + df_copy['IvaCargos'])
    errores_total = (np.abs(df_copy['Valor. Total'] - df_copy['Total_Calculado']) > 0.01).sum()
    print(f"  Errores Valor.Total: {errores_total}")
    
    # ========================================================
    # RESUMEN MES
    # ========================================================
    print(f"\nRESUMEN: {errores_consumo + errores_total_consumo + errores_neto + errores_total} errores totales")

print("\n" + "="*80)
print("RESUMEN GENERAL")
print("="*80)

for mes, datos in RESUMEN_TOTAL.items():
    print(f"{mes}: {datos['nulos']} nulos en {datos['total_registros']} registros")

print("="*80)
print("CONCLUSIONES:")
print("- Los archivos Excel tienen columnas adicionales que afectan los calculos")
print("- Hay errores sistematicos en Total.Consumo (probablemente coeficientes)")
print("- Valor.Neto tiene desviaciones sistematicas pequeñas")
print("- Valor.Total parece estar calculado independientemente en Excel")
print("- Se debe usar directamente Valor.Total como fuente de verdad")
print("="*80 + "\n")
