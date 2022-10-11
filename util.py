import json
import pandas as pd
import plotly.graph_objects as go

def read_map(df_metric):
    f = open('indonesia.geojson')  
    indomap = json.load(f)
    f.close()

    df = pd.DataFrame(
        {"Provinsi": pd.json_normalize(indomap["features"])["properties.state"]}
    ).assign(Columnnext=lambda d: d["Provinsi"].str.len())
    
    dfnew = pd.DataFrame()

    for i in range (len(df)):
        df_metric_temp = df_metric.loc[df_metric['provinsi'] == df['Provinsi'].iloc[i]]
        dfnew = dfnew.append(df_metric_temp)
    
    print(dfnew)

    return dfnew, indomap

def plot_map(df, indomap):
    fig = go.Figure(
        data=go.Choropleth(
            geojson=indomap,
            locations=df["provinsi"],  # Spatial coordinates
            featureidkey="properties.state",
            z=df["ipm"],  # Data to be color-coded
            colorscale="YlOrRd",
            colorbar_title="ABCBRO",
        )
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(autosize=False, width=1300, height=800)
    fig.data[0].colorbar.x=-0.05

    return fig