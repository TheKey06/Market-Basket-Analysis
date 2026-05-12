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

st.subheader('Dashboard MBA - TRONEX')

pg = st.navigation([
    st.Page("pages/bajo.py"),
    st.Page("pages/medio.py"),
    st.Page("pages/alto.py"),
    st.Page("pages/premium.py"),
    st.Page("pages/vip_premium.py"),
    st.Page("pages/outlier.py")
])

pg.run()
