import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

print(os.getcwd())

df_reglas= pd.read_csv('../reglas/general.csv')
df_general = pd.read_parquet('../raw/Antioquia.parquet')

df_general['fechafactura'] = df_general['fechafactura'].dt.to_period('M') 

df_mensual = df_general.groupby(['tro_e_marca','lineatat', 'fechafactura']).agg({
    'montoventapesos':'sum',
    'cantidad':'sum',
    'porcentajedescuento':'mean',
    'margenpesos':'sum'
}).reset_index()

df_mensual = df_mensual[df_mensual['fechafactura'].dt.month!=pd.Timestamp.now().month]

df_mensual['fechafactura'] = df_mensual['fechafactura'].dt.to_timestamp()

# Select bos para obtener la metrica que se desea evaluar
marcas = df_general['tro_e_marca'].unique()
marcas = np.append(marcas, 'General')

metricas = st.selectbox(
    'Selecciona la marca',
    marcas
)

col1,col2,col3,col4 = st.columns([1,1,1,1])
# Filtrar según la selección
if metricas == 'General':
    # Agrupar todo sin filtrar por marca, pero separando por línea
    
    
    with col1:
        with st.container(border=True):
            st.metric(
        label='Promedio de ventas mensual',
        value=f"${df_mensual['montoventapesos'].mean():,.0f}"
        )
    with col2:
        with st.container(border=True):
            st.metric(
        label='Promedio de margen mensual',
        value=f"${df_mensual['margenpesos'].mean():,.0f}"
        )
        

              
    df_filtrado = df_mensual.groupby(['lineatat', 'fechafactura']).agg({
        'montoventapesos': 'sum',
        'cantidad': 'sum',
        'porcentajedescuento': 'mean',
        'margenpesos': 'sum'
    }).reset_index()
    
    df_pie =df_general.groupby('lineatat')['cantidad'].sum().reset_index()
    fig2 = px.pie(df_pie, values='cantidad',names='lineatat')
    
    fig = px.line(
        df_filtrado,
        x='fechafactura',
        y='montoventapesos',
        color='lineatat',
        title='Ventas por Línea - Todas las Marcas',
        labels={
            'fechafactura': 'Fecha',
            'montoventapesos': 'Monto Ventas ($)',
            'lineatat': 'Líneas'
        },
        markers=True
    )
    fig.update_traces(
    hovertemplate='<b>%{fullData.name}</b><br>' +
                  'Fecha: %{x|%b %Y}<br>' +
                  'Monto Ventas: $%{y:,.0f}<extra></extra>'
)


else:
    
    # Filtrar por la marca seleccionada
    df_filtrado = df_mensual[df_mensual['tro_e_marca'] == metricas]
    # Grafica de paster
    df_pie = df_general[df_general['tro_e_marca']==metricas].groupby('lineatat')['cantidad'].sum().reset_index()
    fig2 = px.pie(df_pie, values='cantidad',names='lineatat')
    with col1:
        with st.container(border=True):
            st.metric(
        label='Promedio de ventas mensual',
        value=f"${df_mensual[df_mensual['tro_e_marca']==metricas]['montoventapesos'].mean():,.0f}"
        )
    with col2:
        with st.container(border=True):
            st.metric(
        label='Promedio de margen mensual',
        value=f"${df_mensual[df_mensual['tro_e_marca']==metricas]['margenpesos'].mean():,.0f}"
        )
    
    # Grafica de lineas
    fig = px.line(
        df_filtrado,
        x='fechafactura',
        y='montoventapesos',
        color='lineatat',
        title=f'Ventas por Línea - {metricas}',
        labels={
            'fechafactura': 'Fecha',
            'montoventapesos': 'Monto Ventas ($)',
            'lineatat': 'Líneas'
        },
        markers=True
    )
    fig.update_traces(
    hovertemplate='<b>%{fullData.name}</b><br>' +
                  'Fecha: %{x|%b %Y}<br>' +
                  'Monto Ventas: $%{y:,.0f}<extra></extra>'
)


fig.update_layout(
    template='plotly_dark',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    height=500,
    legend=dict(
        orientation='h',
        x=0.5,
        xanchor='center',
        y=-0.2
    )
)
fig.update_xaxes(
    dtick='M2',
    tickformat='%b %Y',
    tickangle=90

)


col1,col2 = st.columns([1.2,2])
with col1:
    st.plotly_chart(fig2, use_container_width=True)
    
with col2:
    st.plotly_chart(fig, use_container_width=True)


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


