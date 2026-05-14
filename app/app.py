import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title='Dashboard',
    layout='wide'
)

st.sidebar.title("📊 TRONEX")

pg = st.navigation([
    st.Page('pages/inicio.py', title='General'),
    st.Page("pages/bajo.py", title='Segmento Bajo'),
    st.Page("pages/medio.py", title='Segmento Medio'),
    st.Page("pages/alto.py", title='Segmento Alto'),
    st.Page("pages/premium.py",title='Segmento premium'),
    st.Page("pages/vip_premium.py", title='Segmento Vip Premium'),
    st.Page("pages/outlier.py", title='Outliers'),
    st.Page("pages/nuevos.py", title='Nuevos'),
])

pg.run()
