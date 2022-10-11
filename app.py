import pandas as pd
import streamlit as st
import json
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

import util

# Konfigurasi Halaman
st.set_page_config(page_title="Peta Indonesia", layout="wide")

st.header('Peta Indeks Pembangunan Manusia per Provinsi')
df_metric = pd.read_csv('data.csv')
df, indomap = util.read_map(df_metric)

peta = util.plot_map(df, indomap)
selected_points = plotly_events(peta)

if(len(selected_points) > 0):
    idx = int(selected_points[0]['pointIndex'])

    st.success(df.iloc[idx]['provinsi'])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("IPM", str(df.loc[df['provinsi'] == df.iloc[idx]['provinsi']]['ipm'].iloc[0]))
    col2.metric("a", str(df.loc[df['provinsi'] == df.iloc[idx]['provinsi']]['a'].iloc[0]))
    col3.metric("b", str(df.loc[df['provinsi'] == df.iloc[idx]['provinsi']]['b'].iloc[0]))
    col4.metric("c", str(df.loc[df['provinsi'] == df.iloc[idx]['provinsi']]['c'].iloc[0]))
