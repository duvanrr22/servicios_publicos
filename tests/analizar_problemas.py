"""
ANÁLISIS DETALLADO DE PROBLEMAS EN DATOS
=========================================

Identifica exactamente qué registros tienen problemas y por qué.
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
print("🔍 ANÁLISIS DETALLADO DE PROBLEMAS")
print("="*80)

for mes, ruta in ARCHIVOS.items():
    print(f"\n{'='*80}")
    print(f"📊 {mes}")
    print(f"{'='*80}")
    
    # Cargar datos
    df = pd.read_excel(ruta, sheet_name=0)
    if pd.isna(df.iloc[0, 0]):
        df = df.iloc[1:].reset_index(drop=True)
    
    # Convertir a numérico
    for col in ['Lectura anterior', 'Lectura Actual', 'Consumo', 'Valor.Metro',
                'Total.Consumo', 'Valor.Subsidio', 'Valor.Consumo', 'CargoFijo',
                'CargoPart', 'CargoGlob', 'Valor.Mora(II)', 'Valor.Aju.',
                'Valor. Neto', 'SdoCarte.', 'Valor. Total', 'Total.Recaudo']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # ========================================================
    # PROBLEMA 1: Valores nulos
    # ========================================================
    print("\n[PROBLEMA 1] Valores nulos en campos críticos")
    print("-" * 50)
    
    nulos_por_col = {}
    for col in ['codigo de suscriptor', 'Valor. Total', 'Consumo', 'Factura']:
        nulos = df[col].isna().sum()
        if nulos > 0:
            nulos_por_col[col] = nulos
            print(f"  {col}: {nulos} nulos")
            
            # Mostrar ejemplos
            ejemplos_idx = df[df[col].isna()].head(3).index.tolist()
            for idx in ejemplos_idx:
                print(f"    - Fila {idx+2}: {df.loc[idx, 'Factura']} | {df.loc[idx, 'Propietario']}")
    
    if not nulos_por_col:
        print("  ✓ Sin valores nulos en campos críticos")
    
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
            
            # Mostrar ejemplos
            ejemplos = df[df[col] < 0][['Factura', 'Propietario', col]].head(3)
            for idx, row in ejemplos.iterrows():
                print(f"    - {row['Factura']}: ${row[col]:.2f}")
    
    if not negativos_encontrados:
        print("  ✓ Sin valores negativos")
    
    # ========================================================
    # PROBLEMA 3: Errores de cálculo de Consumo
    # ========================================================
    print("\n[PROBLEMA 3] Errores en cálculo de Consumo")
    print("-" * 50)
    
    df['Consumo_Calculado'] = df['Lectura Actual'] - df['Lectura anterior']
    errores_consumo = df[df['Consumo'] != df['Consumo_Calculado']].copy()
    
    if len(errores_consumo) > 0:
        print(f"  {len(errores_consumo)} errores de cálculo de consumo")
        for idx, row in errores_consumo.head(3).iterrows():
            print(f"    - Factura {row['Factura']}:")
            print(f"      Lectura Anterior: {row['Lectura anterior']}")
            print(f"      Lectura Actual: {row['Lectura Actual']}")
            print(f"      Consumo Registrado: {row['Consumo']}")
            print(f"      Consumo Calculado: {row['Consumo_Calculado']}")
    else:
        print("  ✓ Sin errores en cálculo de consumo")
    
    # ========================================================
    # PROBLEMA 4: Errores en Total.Consumo
    # ========================================================
    print("\n[PROBLEMA 4] Errores en Total.Consumo")
    print("-" * 50)
    
    df['Total_Consumo_Calculado'] = df['Consumo'] * df['Valor.Metro']
    errores_total_consumo = df[np.abs(df['Total.Consumo'] - df['Total_Consumo_Calculado']) > 0.01].copy()
    
    if len(errores_total_consumo) > 0:
        print(f"  {len(errores_total_consumo)} errores")
        for idx, row in errores_total_consumo.head(3).iterrows():
            print(f"    - Factura {row['Factura']}:")
            print(f"      Consumo: {row['Consumo']} × Valor.Metro: {row['Valor.Metro']}")
            print(f"      Total.Consumo Registrado: {row['Total.Consumo']}")
            print(f"      Calculado: {row['Total_Consumo_Calculado']}")
            print(f"      Diferencia: {row['Total.Consumo'] - row['Total_Consumo_Calculado']:.2f}")
    else:
        print("  ✓ Sin errores en Total.Consumo")
    
    # ========================================================
    # PROBLEMA 5: Errores en Valor.Neto
    # ========================================================
    print("\n[PROBLEMA 5] Errores en Valor.Neto")
    print("-" * 50)
    
    df_copy = df.copy()
    df_copy['CargoFijo'] = df_copy['CargoFijo'].fillna(0)
    df_copy['CargoPart'] = df_copy['CargoPart'].fillna(0)
    df_copy['Valor.Subsidio'] = df_copy['Valor.Subsidio'].fillna(0)
    
    df_copy['Neto_Calculado'] = (df_copy['Total.Consumo'] + df_copy['CargoFijo'] + 
                                 df_copy['CargoPart'] - df_copy['Valor.Subsidio'])
    
    errores_neto = df_copy[np.abs(df_copy['Valor. Neto'] - df_copy['Neto_Calculado']) > 0.01].copy()
    
    if len(errores_neto) > 0:
        print(f"  {len(errores_neto)} errores")
        for idx, row in errores_neto.head(3).iterrows():
            consumo = row['Total.Consumo']
            cargo_fijo = row['CargoFijo']
            cargo_part = row['CargoPart']
            subsidio = row['Valor.Subsidio']
            calculado = row['Neto_Calculado']
            registrado = row['Valor. Neto']
            
            print(f"    - Factura {row['Factura']}:")
            print(f"      Total.Consumo: {consumo:.2f}")
            print(f"      + CargoFijo: {cargo_fijo:.2f}")
            print(f"      + CargoPart: {cargo_part:.2f}")
            print(f"      - Subsidio: {subsidio:.2f}")
            print(f"      = Neto Calculado: {calculado:.2f}")
            print(f"      Valor.Neto Registrado: {registrado:.2f}")
            print(f"      Diferencia: {registrado - calculado:.2f}")
    else:
        print("  ✓ Sin errores en Valor.Neto")
    
    # ========================================================
    # PROBLEMA 6: Errores en Valor.Total
    # ========================================================
    print("\n[PROBLEMA 6] Errores en Valor.Total")
    print("-" * 50)
    
    df_copy['Valor.Aju.'] = df_copy['Valor.Aju.'].fillna(0)
    df_copy['Valor.Mora(II)'] = df_copy['Valor.Mora(II)'].fillna(0)
    df_copy['IvaMora'] = df_copy['IvaMora'].fillna(0)
    df_copy['IvaCargos'] = df_copy['IvaCargos'].fillna(0)
    
    df_copy['Total_Calculado'] = (df_copy['Valor. Neto'] + df_copy['Valor.Mora(II)'] + 
                                  df_copy['Valor.Aju.'] + df_copy['IvaMora'] + df_copy['IvaCargos'])
    
    errores_total = df_copy[np.abs(df_copy['Valor. Total'] - df_copy['Total_Calculado']) > 0.01].copy()
    
    if len(errores_total) > 0:
        print(f"  {len(errores_total)} errores")
        for idx, row in errores_total.head(3).iterrows():
            neto = row['Valor. Neto']
            mora = row['Valor.Mora(II)']
            ajuste = row['Valor.Aju.']
            iva_mora = row['IvaMora']
            iva_cargos = row['IvaCargos']
            calculado = row['Total_Calculado']
            registrado = row['Valor. Total']
            
            print(f"    - Factura {row['Factura']}:")
            print(f"      Valor.Neto: {neto:.2f}")
            print(f"      + Mora: {mora:.2f}")
            print(f"      + Ajuste: {ajuste:.2f}")
            print(f"      + IVA Mora: {iva_mora:.2f}")
            print(f"      + IVA Cargos: {iva_cargos:.2f}")
            print(f"      = Total Calculado: {calculado:.2f}")
            print(f"      Valor.Total Registrado: {registrado:.2f}")
            print(f"      Diferencia: {registrado - calculado:.2f}")
    else:
        print("  ✓ Sin errores en Valor.Total")
    
    # ========================================================
    # RESUMEN
    # ========================================================
    print(f"\n📋 RESUMEN {mes}")
    print("-" * 50)
    print(f"  Total registros: {len(df)}")
    print(f"  Registros con algún problema: {len(errores_neto) + len(errores_total)}")
    print(f"  Tasa de error: {((len(errores_neto) + len(errores_total))/len(df))*100:.2f}%")

print("\n" + "="*80)
print("✓ Análisis completado")
print("="*80 + "\n")
