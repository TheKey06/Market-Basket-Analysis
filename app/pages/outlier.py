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

fig = plt.figure(figsize=(10, 6), dpi=80)
violin=plt.violinplot(df_dispersion['ticket_promedio'], showmeans=True, showmedians=True)

for pc in violin['bodies']:
    pc.set_facecolor("#D18D7F")
    pc.set_edgecolor('#D18D7F')
    pc.set_alpha(0.7)
violin['cmeans'].set_color('#D92E0D')
violin['cmeans'].set_linewidth(2)
violin['cmedians'].set_color('#D92E0D')
violin['cmedians'].set_linewidth(2)  
violin['cbars'].set_color('#D92E0D')
violin['cbars'].set_linewidth(2)
violin['cmaxes'].set_color('#D92E0D')
violin['cmaxes'].set_linewidth(2)
violin['cmins'].set_color('#D92E0D')
violin['cmins'].set_linewidth(2)
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x,_: f'{x:,.0f}'))
plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda x,_: f'{x:,.0f}'))
jitter = np.random.uniform(0.7, 1.3, size=len(df_dispersion))
plt.scatter(jitter, 
            df_dispersion['ticket_promedio'], 
            alpha=0.3, 
            s=10, 
            color='#D92E0D')
plt.title('Distribución del ticket promedio en el Segmento Outlier')

# Use a robust path relative to this file: app/pages/vip_premium.py -> parents[2] = repo root
st.markdown('### Distribución inicial de clientes en el segmento VIP Premium')
col1,col2 = st.columns([0.4,2])
with col1:
        
        st.metric(label='Clientes del segmento', value=f'{len(df_dispersion):,}', delta=f'{len(df_dispersion):,}')
with col2:
    st.pyplot(fig)



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
combinaciones = []
for i, row in df_reglas.iterrows():
    ant = row['antecedents'].replace("frozenset({", "").replace("})", "").replace("'", "")
    con = row['consequents'].replace("frozenset({", "").replace("})", "").replace("'", "")
    combinaciones.append(f"{ant} → {con}")

df_reglas['combinacion'] = combinaciones

# Selector de métrica
metrica = st.selectbox(
    'Selecciona la métrica:',
    ['confidence', 'lift', 'support', 'conviction', 'leverage']
)

# Ordenar por la métrica seleccionada
df_ordenado = df_reglas.sort_values(by=metrica, ascending=True)

# Formato del texto según la métrica
if metrica in ['confidence', 'support']:
    textos = [f"{v:.1%}" for v in df_ordenado[metrica]]
    tick_format = '.0%'
else:
    textos = [f"{v:.2f}" for v in df_ordenado[metrica]]
    tick_format = '.2f'

# Crear gráfica
fig = go.Figure()

fig.add_trace(go.Bar(
    y=df_ordenado['combinacion'],
    x=df_ordenado[metrica],
    orientation='h',
    marker=dict(
        color=df_ordenado[metrica],
        colorscale='RdYlGn',
        line=dict(color='black', width=1),
        colorbar=dict(title=metrica.capitalize())
    ),
    text=textos,
    textposition='outside',
    textfont=dict(size=12, family='Arial Black')
))

fig.update_layout(
    title=dict(
        text=f'Reglas de Asociación - {metrica.capitalize()}',
        font=dict(size=16, family='Arial Black')
    ),
    xaxis=dict(
        title=metrica.capitalize(),
        tickformat=tick_format,
        range=[0, max(df_ordenado[metrica]) * 1.15]
    ),
    yaxis=dict(
        title='',
        automargin=True
    ),
    height=400,
    width=900,
    template='plotly_white',
    margin=dict(l=250)
)

st.plotly_chart(fig,width='stretch')





