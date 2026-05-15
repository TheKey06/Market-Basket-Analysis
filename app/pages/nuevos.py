import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

pd.set_option('display.float_format', '{:,.2f}'.format)

st.markdown('## Cliente nuevos', text_alignment='center')

df_nuevos = pd.read_csv('../processed/clientes_nuevos.csv', sep=';', low_memory=False)
df_reglas = pd.read_csv('../reglas/nuevos/reglas.csv', sep=';')

df_nuevos= df_nuevos.groupby('cliente').agg(
    nombre = ('nombrecliente','first'),
    ticket_promedio = ('montoventapesos','mean'),
    margen_promedio = ('margenpesos','mean'),
    recencia= ('recencia', 'first'),
    descuento = ('porcentajedescuento','max'),
    linea_ingreso = ('linea_favorita','first'),
    marca_ingreso = ('marca_favorita','first')
)

linea = df_nuevos.groupby('linea_ingreso')['linea_ingreso'].value_counts().reset_index()
fig1 = px.pie(linea, values='count', names='linea_ingreso')
fig1.update_layout(
    height =500,
    width = 900  
)
marcas = df_nuevos.groupby('marca_ingreso')['marca_ingreso'].value_counts().reset_index()
fig2 = px.pie(marcas, values='count', names='marca_ingreso')
fig2.update_layout(
    height =500,
    width = 900
    
    
)
col1,col2 = st.columns([2,2])

with col1:
    st.markdown('### Lineas vendidas', )
    st.plotly_chart(fig1,use_container_width=True)

with col2:
    st.markdown('### Marcas vendidas')
    st.plotly_chart(fig2,use_container_width=True)


st.markdown('## Relacion de productos')
df_reglas['antecedents_clean'] = df_reglas['antecedents'].str.replace(
    "frozenset\(\{|'\}?\)", "", regex=True
).str.replace("'", "")

df_reglas['consequents_clean'] = df_reglas['consequents'].str.replace(
    "frozenset\(\{|'\}?\)", "", regex=True
).str.replace("'", "")

col1,col2= st.columns([1,1])

with col1:
 # ---- Selector de métrica ----
    metrica = st.selectbox(
        'Selecciona la métrica:',
        ['confidence', 'lift', 'support', 'conviction', 'leverage']
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