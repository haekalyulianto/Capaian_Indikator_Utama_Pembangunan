import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn import ensemble
from sklearn.metrics import mean_squared_error
import streamlit as st

def read_map(df_mapping, provinsi):
    f = open('indonesia.geojson')  
    indomap = json.load(f)
    f.close()

    provtemp = provinsi
    provtemp.append('INDONESIA')

    df_mapping['variabel'] = provtemp

    df = pd.DataFrame(
        {"Provinsi": pd.json_normalize(indomap["features"])["properties.state"]}
    ).assign(Columnnext=lambda d: d["Provinsi"].str.len())
    
    mappingprovinsi = pd.read_csv('mappingprovinsi.csv')

    dfnew = pd.DataFrame()

    for i in mappingprovinsi['mappingtarget']:
        df_mapping_temp = df_mapping.iloc[i]
        dfnew = dfnew.append(df_mapping_temp)

    dfnew = dfnew.reset_index(drop=True)
    dfnew = pd.concat([dfnew, mappingprovinsi['provinsi']], axis=1, join="inner")

    return dfnew, indomap

def plot_map(df, indomap, tahun):
    fig = go.Figure(
        data=go.Choropleth(
            geojson=indomap,
            locations=df["provinsi"],
            featureidkey="properties.state",
            z=df[int(tahun)],
            colorscale="YlOrRd",
            colorbar_title="Rentang",
        )
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    fig.data[0].colorbar.x=-0.05

    return fig

def prediction(dfprov):
    namakolom = dfprov.columns[0]

    # Tahap 1
    X = dfprov.iloc[:, 1:12]
    y = dfprov.iloc[:,0]
    
    X_train = X[:10]
    y_train = y[:10]
    X_test = X[10:]
    y_test = y[10:]

    returns = {}

    reg = ensemble.GradientBoostingRegressor(random_state=42)
    reg.fit(X_train, y_train)
    y_pred = reg.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)

    returns['MSE'] = mse
    returns['RMSE'] = rmse
    returns['y_pred'] = y_pred
    returns['y_test'] = y_test

    feature_importance = reg.feature_importances_
    importance_df = pd.DataFrame({'Fungsi Anggaran': X_train.columns,
                                'Keutamaan': feature_importance})
    importance_df.sort_values(by='Keutamaan', ascending=False, inplace=True)
    
    returns['importance_df'] = importance_df

    # Pilih 3 Fitur Utama
    feature=importance_df.iloc[:3,:1].T.values.tolist()
    flat_list = [item for sublist in feature for item in sublist]
    flat_list.append(namakolom)
    dfprov = dfprov[dfprov.columns.intersection(flat_list)]

    returns['dfprov'] = dfprov

    return returns

def is_feature_importance(temp):
    if temp > 0.5:
        return 'background-color: lightgreen'
    elif temp > 0.2 and temp < 0.5:
        return 'background-color: yellow'
    elif temp > 0.1 and temp < 0.2:
        return 'background-color: orange'
    else:
        return 'background-color: red'

def coba(value, data):                 #masih bug --> if else condition kebacanya kacau
  for index, row in data.iterrows():
    deviasi=0
    if row['batas_bawah'] != '' and row['batas_atas']=='':
      print(row['batas_bawah'])
      deviasi = row['batas_bawah'] * 5/100
      if value > row['batas_bawah'] and value <= row['batas_bawah']+deviasi:
        return 'background-color: yellow'
      elif value > row['batas_bawah'] and value > row['batas_bawah']+deviasi:
        return 'background-color: red'
      elif value < row['batas_bawah'] and value >= row['batas_bawah']-deviasi:
        return 'background-color: yellow'
      elif value < row['batas_bawah'] and value < row['batas_bawah']-deviasi:
        return 'background-color: red'
      elif value == row['batas_bawah']:
        return 'background-color: green'
    elif row['batas_bawah']!='' and row['batas_atas']!='':
      if value >= row['batas_bawah']:
        deviasi = row['batas_atas'] * 5/100
        if value <= row['batas_atas']:
          return 'background-color: green'
        elif value > row['batas_atas'] and value <= row['batas_atas']+deviasi:
          return 'background-color: yellow'
        elif value > row['batas_atas'] and value > row['batas_atas']+deviasi:
          return 'background-color: red'
      elif value <= row['batas_bawah']:
        deviasi = row['batas_bawah'] * 5/100
        if value >= row['batas_bawah']-deviasi:
          return 'background-color: yellow'
        elif value < row['batas_bawah']+deviasi:
          print(row['batas_bawah'],row['batas_bawah']-deviasi)
          return 'background-color: red'
    else:
      return 'background-color: white'

def is_target(temp_df, col) :                   #solusi 2 pake ini, tapi ga apply warna :') 
  for index, row in temp_df.iterrows():
    if row['batas_bawah'] != '' and row['batas_atas']=='':
      deviasi = row['batas_bawah'] * 5/100
      if row[col] > row['batas_bawah'] and row[col] <= row['batas_bawah']+deviasi:
        st.write( row['tahun'], ': ',row[col], '--> kuning')
      elif row[col] > row['batas_bawah'] and row[col] > row['batas_bawah']+deviasi:
        st.write( row['tahun'], ': ',row[col], '--> merah')
      elif row[col] < row['batas_bawah'] and row[col] >= row['batas_bawah']-deviasi:
        st.write( row['tahun'], ': ',row[col], '--> kuning')
      elif row[col] < row['batas_bawah'] and row[col] < row['batas_bawah']-deviasi:
        st.write( row['tahun'], ': ',row[col], '--> merah')
      elif row[col] == row['batas_bawah']:
        st.write( row['tahun'], ': ',row[col], '--> hijau')
    elif row['batas_bawah']!='' and row['batas_atas']!='':
      if row[col] >= row['batas_bawah']:
        deviasi = row['batas_atas'] * 5/100
        if row[col] <= row['batas_atas']:
          st.write( row['tahun'], ': ',row[col], '--> hijau')
        elif row[col] > row['batas_atas'] and row[col] <= row['batas_atas']+deviasi:
          st.write( row['tahun'], ': ',row[col], '--> kuning')
        elif row[col] > row['batas_atas'] and row[col] > row['batas_atas']+deviasi:
          st.write( row['tahun'], ': ',row[col], '--> merah')
      elif row[col] <= row['batas_bawah']:
        deviasi = row['batas_bawah'] * 5/100
        if row[col] >= row['batas_bawah']-deviasi:
          st.write( row['tahun'], ': ',row[col], '--> kuning')
        elif row[col] < row['batas_bawah']+deviasi:
          st.write( row['tahun'], ': ',row[col], '--> merah')
    else:
      st.write( row['tahun'], ': ',row[col], '--> putih')
