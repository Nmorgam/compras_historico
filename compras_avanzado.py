#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np

# Configuración
st.set_page_config(page_title="Dashboard de Compras Avanzado", layout="wide")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("Compras_historicas.csv", parse_dates=["FechaCompra"])
    df["Año"] = df["FechaCompra"].dt.year
    df["Mes"] = df["FechaCompra"].dt.month
    df["Trimestre"] = df["FechaCompra"].dt.to_period("Q")
    return df

df = load_data()

st.title("📊 Dashboard Avanzado de Compras Históricas")

# Filtros
st.sidebar.header("🔍 Filtros")

# Año y Mes
años = sorted(df["Año"].dropna().unique())
año_sel = st.sidebar.selectbox("Seleccionar Año", options=["Todos"] + list(map(str, años)))

meses = sorted(df["Mes"].dropna().unique())
mes_sel = st.sidebar.selectbox("Seleccionar Mes", options=["Todos"] + list(map(str, meses)))

# Rango de fechas separados
fecha_min = df["FechaCompra"].min()
fecha_max = df["FechaCompra"].max()
fecha_desde = st.sidebar.date_input("Desde", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
fecha_hasta = st.sidebar.date_input("Hasta", value=fecha_max, min_value=fecha_min, max_value=fecha_max)

# Búsqueda por texto
concepto_input = st.sidebar.text_input("Buscar por Concepto")
proveedor_input = st.sidebar.text_input("Buscar por Proveedor")

# Aplicar filtros
df_filtrado = df.copy()

if año_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Año"] == int(año_sel)]

if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Mes"] == int(mes_sel)]

df_filtrado = df_filtrado[(df_filtrado["FechaCompra"] >= pd.to_datetime(fecha_desde)) & 
                          (df_filtrado["FechaCompra"] <= pd.to_datetime(fecha_hasta))]

if concepto_input:
    df_filtrado = df_filtrado[df_filtrado["Concepto"].str.contains(concepto_input, case=False, na=False)]

if proveedor_input:
    df_filtrado = df_filtrado[df_filtrado["Proveedor"].str.contains(proveedor_input, case=False, na=False)]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Comprado", f"${df_filtrado['Monto'].sum():,.2f}")
col2.metric("Promedio por Compra", f"${df_filtrado['Monto'].mean():,.2f}")
col3.metric("Proveedores únicos", df_filtrado["Proveedor"].nunique())
col4.metric("Compras Totales", len(df_filtrado))

# Gráfico de evolución mensual corregido
st.subheader("📈 Evolución mensual de compras")
evolucion = df_filtrado.copy()
evolucion["MesFecha"] = evolucion["FechaCompra"].dt.to_period("M").dt.to_timestamp()
compras_mensuales = evolucion.groupby("MesFecha")["Monto"].sum().sort_index()
st.line_chart(compras_mensuales)

# Distribución por centro de costo
st.subheader("🏢 Distribución de gastos por Centro de Costo")
centros = df_filtrado.groupby("CentroCosto")["Monto"].sum().sort_values(ascending=False).head(10)
st.bar_chart(centros)

# Ranking de proveedores
st.subheader("🏆 Top 10 Proveedores por Monto Total")
top_prov = df_filtrado.groupby("Proveedor")["Monto"].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_prov)

# Gastos promedio por proveedor
st.subheader("💰 Gasto promedio por proveedor (Top 10)")
prom_prov = df_filtrado.groupby("Proveedor")["Monto"].mean().sort_values(ascending=False).head(10)
st.bar_chart(prom_prov)

# Análisis ABC
st.subheader("🔠 Análisis ABC de Proveedores")
abc = df_filtrado.groupby("Proveedor")["Monto"].sum().sort_values(ascending=False)
abc_total = abc.sum()
abc_cumsum = abc.cumsum() / abc_total

def abc_class(row):
    if row <= 0.8:
        return "A"
    elif row <= 0.95:
        return "B"
    else:
        return "C"

abc_df = abc_cumsum.reset_index()
abc_df.columns = ["Proveedor", "Acumulado"]
abc_df["Clasificación"] = abc_df["Acumulado"].apply(abc_class)
st.dataframe(abc_df)

# Outliers
st.subheader("🚨 Detección de Outliers por Monto")
threshold = df_filtrado["Monto"].mean() + 3 * df_filtrado["Monto"].std()
outliers = df_filtrado[df_filtrado["Monto"] > threshold]
st.write(f"Se detectaron {len(outliers)} compras con montos significativamente altos (z-score > 3).")
st.dataframe(outliers)

# Tabla con scroll
st.subheader("📄 Detalle de Compras Filtradas")
st.dataframe(df_filtrado, height=500)

