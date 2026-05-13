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
df= df.rename(columns={'margen_promeido':'margen_promedio'})

# Muestra de la segmentacion de clientes en este segmento
st.markdown('#### clientes en este segmento')

# Datos
resumen = df.groupby('cliente').agg(
    nombre = ('nombrecliente', 'first'),
    frecuencia = ('frecuencia','mean'),
    ticket_promedio = ('ticket_promedio','mean'),
    cl_value = ('cl_value','mean'),
    linea_favorita = ('linea_favorita', 'first'),
    marca_favorita = ('marca_favorita','unique'),
    margen_promedio = ('margen_promedio','mean'),
    productos = ('referencia', 'unique'),
    cantidad =('cantidad','sum')
).reset_index()

resumen['cliente'] = resumen['cliente'].astype(str)

variables = ['frecuencia', 'ticket_promedio', 'cl_value', 'clientes']
titulos = ['Frecuencia Promedio', 'Ticket Promedio', 'CL Value Promedio']


######### Primer Grafico

# Crear subplots
fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=titulos,
    horizontal_spacing=None
)
variables = ['frecuencia', 'ticket_promedio', 'cl_value']
titulos = ['Frecuencia Promedio', 'Ticket Promedio', 'Customer Life Time Value']

for i, (var, titulo) in enumerate(zip(variables, titulos)):
    fig.add_trace(
        go.Bar(
            x=resumen['cliente'],
            y=resumen[var],
            marker=dict(
                line=dict(color='black', width=1)
            ),
            opacity=1,
            text=[f'{v:,.0f}' for v in resumen[var]],
            textposition='outside',
            textfont=dict(size=12, family='Arial Black'),
            showlegend=False
        ),
        row=1, col=i+1
    )

    # Configurar ejes de cada subplot
    fig.update_xaxes(
        title_text='Cliente',
        title_font=dict(size=12),
        row=1, col=i+1
    )
    fig.update_yaxes(
        title_text=var,
        title_font=dict(size=12),
        separatethousands=True,
        row=1, col=i+1
    )

# Configuración general
fig.update_layout(
    title=dict(
        text='Comparación de clientes outliers',
        font=dict(size=16, family='Arial Black'),
        x=0.5,
        xanchor='center'
    ),
    template='plotly_dark',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig, width='stretch')


####### Segundo grafico

# marca favoritas

marcas = df.groupby('marca_favorita')['marca_favorita'].value_counts().reset_index()
fig2 = px.pie(marcas, values='count', names='marca_favorita')

st.markdown('### Marcas vendidas en el segmento')
st.plotly_chart(fig2,use_container_width=True)



## Filtro por cliente
nombres = resumen['cliente'].astype(str) + ' - ' + resumen['nombre']

metrica = st.selectbox(
    'Selecciona el cliente:',
    nombres
)

# Extraer el código del cliente desde la selección
cliente_seleccionado = metrica.split(' - ')[0].strip()

# Filtrar el dataframe por ese cliente
df_filtrado = df[df['cliente'].astype(str) == cliente_seleccionado]

# Gráfico de referencias (productos)
referencias = df_filtrado.groupby('referencia')['cantidad'].sum().reset_index()
fig3 = px.bar(
    referencias,
    y='referencia',
    x='cantidad',
    orientation='h',
    title='Referencias compradas por el cliente'
)

st.plotly_chart(fig3, use_container_width=True)

col1,col2 = st.columns([2,1.5])


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





