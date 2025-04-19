#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import yfinance as yf
import datetime

st.set_page_config(page_title="Stock Price App", layout="centered")

st.title("📈 Simple Stock Price App")

st.markdown("""
Este panel muestra los precios de cierre y el volumen histórico de acciones.
Usa el panel lateral para seleccionar el ticker y el rango de fechas.
""")

# Sidebar inputs
st.sidebar.header("Configuración")

# Ticker input
ticker = st.sidebar.text_input("Símbolo de la acción (ej. AAPL, GOOGL, MSFT):", value='GOOGL')

# Year range input
today = datetime.date.today()
start_year = st.sidebar.slider("Año de inicio", min_value=2000, max_value=today.year - 1, value=2015)
end_year = st.sidebar.slider("Año de fin", min_value=start_year, max_value=today.year, value=today.year)

start_date = datetime.date(start_year, 1, 1)
end_date = datetime.date(end_year, 12, 31)

# Load data
st.subheader(f"Datos históricos de {ticker.upper()} desde {start_date} hasta {end_date}")

try:
    ticker_data = yf.Ticker(ticker)
    ticker_df = ticker_data.history(start=start_date, end=end_date)

    if ticker_df.empty:
        st.warning("No se encontraron datos para ese rango de fechas o ticker.")
    else:
        st.line_chart(ticker_df.Close, use_container_width=True)
        st.line_chart(ticker_df.Volume, use_container_width=True)

        st.dataframe(ticker_df[['Open', 'High', 'Low', 'Close', 'Volume']].round(2))

except Exception as e:
    st.error(f"Error al obtener los datos: {e}")

