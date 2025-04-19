#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("Compras_historicas.csv", parse_dates=["FechaCompra"])
    df["Año"] = df["FechaCompra"].dt.year
    df["Mes"] = df["FechaCompra"].dt.month
    return df

df = load_data()

st.title("📊 Dashboard de Compras Históricas")

# Filtros
st.sidebar.header("🔍 Filtros")

# Año
años = sorted(df["Año"].dropna().unique())
año_sel = st.sidebar.selectbox("Seleccionar Año", opciones := ["Todos"] + list(map(str, años)))

# Mes
meses = sorted(df["Mes"].dropna().unique())
mes_sel = st.sidebar.selectbox("Seleccionar Mes", opciones := ["Todos"] + list(map(str, meses)))

# Filtro por texto - Concepto
concepto_input = st.sidebar.text_input("Buscar por Concepto")

# Filtro por texto - Proveedor
proveedor_input = st.sidebar.text_input("Buscar por Proveedor")

# Aplicar filtros
df_filtrado = df.copy()

if año_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Año"] == int(año_sel)]

if mes_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Mes"] == int(mes_sel)]

if concepto_input:
    df_filtrado = df_filtrado[df_filtrado["Concepto"].str.contains(concepto_input, case=False, na=False)]

if proveedor_input:
    df_filtrado = df_filtrado[df_filtrado["Proveedor"].str.contains(proveedor_input, case=False, na=False)]

# Gráfico de compras por concepto
st.subheader("📈 Total de compras por Concepto")
grafico = df_filtrado.groupby("Concepto")["Monto"].sum().sort_values(ascending=False).head(10)
st.bar_chart(grafico)

# Mostrar tabla con scroll
st.subheader("📄 Compras filtradas")
st.dataframe(df_filtrado, height=500)

