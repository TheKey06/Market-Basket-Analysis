import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
# para las cartas

def comportamiento_marca(df):

    media_monto = df['montoventapesos'].mean()
    media_frecuencia = df['frecuencia'].mean()
    media_margen = df['margenpesos'].mean()

    # Definir las categorías y los valores
    categorias = ['Monto Venta', 'Frecuencia', 'Margen']
    valores = [media_monto, media_frecuencia, media_margen]

    # IMPORTANTE: cerrar el radar (repetir el primer valor al final)
    categorias_cerrado = categorias + [categorias[0]]
    valores_cerrado = valores + [valores[0]]

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
        r=valores_cerrado,
        theta=categorias_cerrado,
        fill='toself',
        fillcolor='rgba(255, 100, 50, 0.3)',
        line=dict(color='rgb(255, 100, 50)', width=2),
        marker=dict(size=8),
        name='Media General'
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor='gray'
            ),
            angularaxis=dict(
                gridcolor='gray'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        title='Radar - Medias Generales',
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    # En Streamlit
    return fig_radar

    
    


