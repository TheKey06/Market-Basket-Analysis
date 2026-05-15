import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

st.set_page_config(layout="wide")


reglas_dir = Path(__file__).resolve().parents[2] / 'reglas'
df = pd.read_parquet(reglas_dir / 'segmento_medio' / 'Basket.parquet')
df_reglas = pd.read_csv(reglas_dir / 'segmento_medio' / 'reglas.csv', sep=';')

df= df.rename(columns={'margen_promeido':'margen_promedio'})
df['clientes']= df['cliente'].astype(object)

resumen = df.groupby('cluster').agg(
    nombre_cluster = ('nombre_cluster','first'),
    frecuencia = ('frecuencia','mean'),
    ticket_promedio = ('ticket_promedio','mean'),
    cl_value = ('cl_value','mean'),
    clientes = ('cliente','nunique'),
    linea_favorita = ('linea_favorita', 'first'),
    marca_favorita = ('marca_favorita','unique'),
    margen_promedio = ('margen_promedio','mean') 
)

# Muestra de la segmentacion de clientes en este segmento
st.markdown('#### Segmentacion de clientes en este segmento')

# Datos
clientes = len(df.groupby('cliente').count())
st.metric(label='Clientes del segmento', value=f'{clientes}', delta=f'{clientes}')

# Configuración
colores = ['#2ecc71', '#e74c3c', '#3498db']
variables = ['frecuencia', 'ticket_promedio', 'cl_value', 'clientes']
titulos = ['Frecuencia Promedio', 'Ticket Promedio', 'CL Value Promedio', 'clientes']

# Crear subplots
fig = make_subplots(
    rows=1, cols=4,
    subplot_titles=titulos,
    horizontal_spacing=0.08
)

for i, (var, titulo) in enumerate(zip(variables, titulos)):
    fig.add_trace(
        go.Bar(
            x=resumen.nombre_cluster,
            y=resumen[var],
            marker=dict(
                color=colores,
                line=dict(color='black', width=1)
            ),
            opacity=0.85,
            text=[f'{v:,.0f}' for v in resumen[var]],
            textposition='outside',
            textfont=dict(size=12, family='Arial Black'),
            showlegend=False
        ),
        row=1, col=i+1
    )

    # Configurar ejes de cada subplot
    fig.update_xaxes(
        title_text='Cluster',
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
        text='Comparación de Clusters - df_bajo',
        font=dict(size=16, family='Arial Black'),
        x=0.5,
        xanchor='center'
    ),
    height=500,
    width=1200,
    template='plotly_dark',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig, use_container_width=True)

array_titulos = resumen['nombre_cluster'].to_numpy()
array_titulos = np.append(array_titulos, 'Completo')

titulos = st.selectbox(
    'Selecciona el segmento:',
    array_titulos
)

if titulos == 'Completo':
    df_filtrado = df.copy()  # Todos los datos
else:
    df_filtrado = df[df['nombre_cluster'] == titulos]  # Solo el segmento elegido

# ---- Contar las líneas y marcas ----
# value_counts() ya agrupa y cuenta, no necesitas groupby antes
lineas = (
    df_filtrado['linea_favorita']
    .value_counts()
    .reset_index()
)
lineas.columns = ['linea_favorita', 'count']

marcas = (
    df_filtrado['marca_favorita']
    .value_counts()
    .reset_index()
)
marcas.columns = ['marca_favorita', 'count']

# ---- Calcular el porcentaje para mostrarlo en las barras ----
lineas['porcentaje'] = (lineas['count'] / lineas['count'].sum() * 100).round(2)
marcas['porcentaje'] = (marcas['count'] / marcas['count'].sum() * 100).round(2)

# ---- Ordenar de menor a mayor (para que la barra más grande quede arriba) ----
lineas = lineas.sort_values('count', ascending=True)
marcas = marcas.sort_values('count', ascending=True)

# ---- Gráfico de Barras Horizontales: LÍNEAS ----
fig1 = px.bar(
    lineas,
    x='count',
    y='linea_favorita',
    orientation='h',                          # Horizontal
    text=lineas['porcentaje'].apply(lambda x: f"{x}%"),  # Etiqueta con %
    title=f'Líneas vendidas en el segmento: {titulos}',
    labels={'count': 'Cantidad', 'linea_favorita': 'Línea'},
    color='count',
    color_continuous_scale='Reds'             # Escala de azules
)

fig1.update_traces(
    textposition='outside',                   # Texto fuera de la barra
    textfont=dict(size=12)
)

fig1.update_layout(
    template='plotly_dark',
    height=400 + (len(lineas) * 25),          # Altura dinámica según categorías
    showlegend=False,
    coloraxis_showscale=False,                # Ocultar barra de color
    xaxis=dict(title='Cantidad'),
    yaxis=dict(title=''),
    margin=dict(l=10, r=80)
)

# ---- Gráfico de Barras Horizontales: MARCAS ----
fig2 = px.bar(
    marcas,
    x='count',
    y='marca_favorita',
    orientation='h',
    text=marcas['porcentaje'].apply(lambda x: f"{x}%"),
    title=f'Marcas vendidas en el segmento: {titulos}',
    labels={'count': 'Cantidad', 'marca_favorita': 'Marca'},
    color='count',
    color_continuous_scale='Blues'           # Escala de verdes para diferenciar
)

fig2.update_traces(
    textposition='outside',
    textfont=dict(size=12)
)

fig2.update_layout(
    template='plotly_dark',
    height=400 + (len(marcas) * 25),
    showlegend=False,
    coloraxis_showscale=False,
    xaxis=dict(title='Cantidad'),
    yaxis=dict(title=''),
    margin=dict(l=10, r=80)
)

col1,col2 = st.columns([3,3])
with col1:
    st.markdown('### Marcas vendidas en el segmento')
    st.plotly_chart(fig2,use_container_width=True)
with col2:
    st.markdown('### Lineas vendidas en el segmento')
    st.plotly_chart(fig1)
    
    
    
## Algoritmo apriori
st.markdown('## Relacion de productos')
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