import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn import ensemble
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

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
            locations=df["provinsi"],  # Spatial coordinates
            featureidkey="properties.state",
            z=df[int(tahun)],  # Data to be color-coded
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

    # TAHAP 1
    X = dfprov.iloc[:, 1:12]
    y = dfprov.iloc[:,0]
    
    X_train = X[:10]
    y_train = y[:10]
    X_test = X[10:]
    y_test = y[10:]

    params1 = {
        "n_estimators": 1000,
        "learning_rate": 0.01,
        "loss": "squared_error",
    }

    returns = {}

    reg = ensemble.GradientBoostingRegressor(**params1)
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

    #select top 3 feature
    feature=importance_df.iloc[:3,:1].T.values.tolist()
    flat_list = [item for sublist in feature for item in sublist]
    flat_list.append(namakolom)
    dfprov = dfprov[dfprov.columns.intersection(flat_list)]

    returns['dfprov'] = dfprov

    # TAHAP 2
    X = dfprov.iloc[:, 1:10]
    y = dfprov[[namakolom]]

    X_train = X[:10]
    y_train = y[:10]
    X_test = X[10:]
    y_test = y[10:]

    regressor = LinearRegression()
    regressor.fit(X_train, y_train)

    #persamaan
    returns['regressor.intercept'] = regressor.intercept_
    returns['regressor.coef_'] = regressor.coef_

    y_pred = regressor.predict(X_test)
    returns['y_pred Tahap 2'] = y_pred
    returns['y_test Tahap 2'] = y_test

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)

    returns['mae Tahap 2'] = mae
    returns['mse Tahap 2'] = mse
    returns['rmse Tahap 2'] = rmse

    # TAHAP 3
    # select top 1 feature
    feature2=importance_df.iloc[:1,:1].T.values.tolist()
    flat_list2 = [item for sublist in feature2 for item in sublist]
    flat_list2.append(namakolom)
    dfprov = dfprov[dfprov.columns.intersection(flat_list2)]

    returns['dfprov2'] = dfprov

    X = dfprov.iloc[:, 1:10]
    y = dfprov[[namakolom]]

    X_train = X[:10]
    y_train = y[:10]
    X_test = X[10:]
    y_test = y[10:]

    regressor = LinearRegression()
    regressor.fit(X_train, y_train)

    #persamaan
    returns['regressor.intercept Tahap 3'] = regressor.intercept_
    returns['regressor.coef_ Tahap 3'] = regressor.coef_

    y_pred = regressor.predict(X_test)
    returns['y_pred Tahap 3'] = y_pred
    returns['y_test Tahap 3'] = y_test

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)

    returns['mae Tahap 3'] = mae
    returns['mse Tahap 3'] = mse
    returns['rmse Tahap 3'] = rmse

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

def is_target(value):
    if value > 6:
        return 'background-color: lightgreen' #Ini kudu diubah sih biar menyesuaikan target per indikatornya wkwk
