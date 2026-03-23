#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Análisis de Estructura Excel - Servicios Públicos
Inspecciona las columnas reales para adaptar el script principal
"""

import sys
from pathlib import Path
import pandas as pd

proyecto_path = Path(__file__).parent.parent
sys.path.insert(0, str(proyecto_path))

ruta_archivos = proyecto_path / "archivos_excel"
archivo = ruta_archivos / "PaqueteFacturacion-Diciembre-2025.xlsx"

# Cargar Excel
df = pd.read_excel(archivo)

print("="*100)
print("ANÁLISIS DE ESTRUCTURA - Primeras 3 filas del Excel")
print("="*100)
print(f"\nTotal de filas: {len(df)}")
print(f"Total de columnas: {len(df.columns)}\n")

print("COLUMNAS DETECTADAS:")
print("-"*100)
for i, col in enumerate(df.columns[:20], 1):  # Mostrar primeras 20 columnas
    print(f"{i:2}. {col}")

print("\n\nPRIMERAS FILAS DE DATOS:")
print("-"*100)
print(df.head(3).to_string())

print("\n\nTIPOS DE DATOS:")
print("-"*100)
print(df.dtypes)

print("\n\nTIPOS DE DATOS (detallado):")
print("-"*100)
for col in df.columns[:15]:
    valores_unicos = df[col].nunique()
    tipo = df[col].dtype
    print(f"{col}: {tipo} ({valores_unicos} valores únicos)")
