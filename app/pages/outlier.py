import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

reglas_dir = Path(__file__).resolve().parents[2] / 'reglas'
df = pd.read_parquet(reglas_dir / 'segmento_outlier' / 'Basket.parquet')
df_reglas = pd.read_csv(reglas_dir / 'segmento_outlier' / 'reglas.csv', sep=';')

df_dispersion = df.groupby('cliente').agg({
    'ticket_promedio': 'mean'
})

# Muestra de la segmentacion de clientes en este segmento
st.markdown('#### clientes en este segmento')

# Datos
resumen = df.groupby('cliente')[['frecuencia', 'ticket_promedio', 'cl_value']].mean().reset_index(drop=False)

resumen['cliente'] = resumen['cliente'].astype(object)

fig, ax = plt.subplots(figsize=(10, 6))

x = resumen['cliente'].astype(str).tolist()
y = resumen['frecuencia'].tolist()

ax.bar(x, y)

ax.set_title("Frecuencia por cliente")
ax.set_xlabel("Cliente")
ax.set_ylabel("Frecuencia")

plt.xticks(rotation=45)

st.pyplot(fig)



## Algoritmo apriori

# Crear combinaciones
df_reglas['antecedents_clean'] = df_reglas['antecedents'].str.replace(
    "frozenset\(\{|'\}?\)", "", regex=True
).str.replace("'", "")

df_reglas['consequents_clean'] = df_reglas['consequents'].str.replace(
    "frozenset\(\{|'\}?\)", "", regex=True
).str.replace("'", "")

# ---- Selector de métrica ----
metrica = st.selectbox(
    'Selecciona la métrica:',
    ['confidence', 'lift', 'support', 'conviction', 'leverage']
)

# ---- Crear matriz pivote ----
matriz = df_reglas.pivot_table(
    index='antecedents_clean',
    columns='consequents_clean',
    values=metrica,
    aggfunc='mean'
)

# ---- Formato de texto ----
if metrica in ['confidence', 'support']:
    text_matrix = matriz.map(lambda x: f"{x:.1%}" if pd.notna(x) else "")
else:
    text_matrix = matriz.map(lambda x: f"{x:.2f}" if pd.notna(x) else "")

# ---- Crear Heatmap ----
fig = go.Figure(data=go.Heatmap(
    z=matriz.values,
    x=matriz.columns.tolist(),
    y=matriz.index.tolist(),
    text=text_matrix.values,
    texttemplate="%{text}",
    textfont=dict(size=10),
    colorscale='RdYlGn',
    colorbar=dict(title=metrica.capitalize()),
    hoverongaps=False
))

fig.update_layout(
    title=dict(
        text=f'Mapa de Calor - {metrica.capitalize()}',
        font=dict(size=16, family='Arial Black')
    ),
    xaxis=dict(
        title='Consecuente',
        tickangle=90
    ),
    yaxis=dict(
        title='Antecedente',
        automargin=True
    ),
    height=600,
    width=900,
    template='plotly_white',
    margin=dict(l=200, b=150)
)

st.plotly_chart(fig, use_container_width=True)





