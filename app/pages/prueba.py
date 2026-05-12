import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

reglas_dir = Path(__file__).resolve().parents[2] / 'reglas'
df = pd.read_parquet(reglas_dir / 'segmento_bajo' / 'Basket.parquet')


print(df.info())



