import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os


print(os.getcwd())

df_reglas= pd.read_csv('../reglas/general.csv')


df_reglas['antecedents_clean'] = df_reglas['antecedents'].str.replace(
    "frozenset\(\{|'\}?\)", "", regex=True
).str.replace("'", "")

df_reglas['consequents_clean'] = df_reglas['consequents'].str.replace(
    "frozenset\(\{|'\}?\)", "", regex=True
).str.replace("'", "")

st.markdown('## Relaciones de productos a nivel general')

metrica = st.selectbox(
    'Selecciona la metrica que quieres evaluar',
    ['support','confidence','conviction','lift','leverage']
)

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
        tickangle=45
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


