from os import name
import pandas as pd
import streamlit as st
import json
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import util
import mapping

# Konfigurasi Halaman
st.set_page_config(page_title="Peta Indonesia", layout="wide")
st.title('Capaian Indikator Utama Pembangunan')

tab1, tab2 = st.tabs(["Pemrosesan Data", "Hasil"])
# Pemrosesan Data
#df = util.read_and_preprocess_data('IPM')
# =================================================================
with tab1:
    inputcol1, inputcol2 = st.columns(2)

    with inputcol1:
        tahun = st.selectbox('Tahun', ([str(x) for x in range(2010, 2022)]))

    with inputcol2:
        target = st.selectbox('Indikator', ('Indeks Pembangunan Manusia', 'Tingkat Kemiskinan', 'Rasio Gini', 'Laju Pertumbuhan Ekonomi', 'Tingkat Pengangguran Terbuka'))

    filetarget = 'Indeks Pembangunan Manusia.xlsx'
    column = ['IPM']

    if (target == 'Tingkat Kemiskinan'):
        filetarget = 'persentasemiskin.xlsx'
        column = ['Kemiskinan']
    elif (target == 'Rasio Gini'):
        filetarget = 'giniratio.xlsx'
        column = ['Gini']
    elif (target == 'Laju Pertumbuhan Ekonomi'):
        filetarget = 'Laju PDRB.xlsx'
        column = ['LPE']
    elif (target == 'Tingkat Pengangguran Terbuka'):
        filetarget = 'pengangguran.xlsx'
        column = ['TPT']

    exec('{} = pd.read_excel("{}")'.format(column[0], filetarget))
    provinsi=['ACEH','SUMATERA_UTARA','SUMATERA_BARAT','RIAU', 'JAMBI',	'SUMATERA_SELATAN',	'BENGKULU',	'LAMPUNG',	'BANGKA_BELITUNG',	'KEPRI',	'DKI_JAKARTA',	'JAWA_BARAT',	'JAWA_TENGAH',	'DI_YOGYAKARTA',	'JAWA_TIMUR',	'BANTEN',	'BALI',	'NTB',	'NTT',	'KALIMANTAN_BARAT',	'KALIMANTAN_TENGAH',	'KALIMANTAN_SELATAN',	'KALIMANTAN_TIMUR',	'KALIMANTAN_UTARA',	'SULAWESI_UTARA',	'SULAWESI_TENGAH',	'SULAWESI_SELATAN',	'SULAWESI_TENGGARA',	'GORONTALO',	'SULAWESI_BARAT',	'MALUKU',	'MALUKU_UTARA',	'PAPUA_BARAT',	'PAPUA']

    for x in provinsi:  
        exec('{} = pd.DataFrame(columns=column)'.format(x))

    countX=0
    countY=0

    #isi data target
    for i in provinsi:
        for j in column:
            exec('{}["{}"]={}.loc[{}:{},2010:2021].T'.format(i,j,j,countX,countY))
        #countX+=1
    countY+=1

    APBN = pd.read_csv('Peta APBN Data.csv', header=None)

    APBN[0][0] = 'Tahun'
    APBN.columns = APBN.iloc[0]
    APBN = APBN.iloc[1:]
    APBN = APBN.astype({"Tahun": int})
    APBN = APBN.astype({"Tahun": str})
    APBN = APBN.set_index('Tahun', drop=True)

    mappingprovinsiAPBN = mapping.mappingprovinsiAPBN

    # Pisah2 --> 11 fitur APBN
    for x in mappingprovinsiAPBN.keys():
        firstcol = (x-1)*11 # ini parameter yang diganti2 kalo ganti jumlah kolom
        lastcol = x*11 # ini parameter yang diganti2 kalo ganti jumlah kolom
        exec('{} = APBN.iloc[:, {}:{}]'.format(mappingprovinsiAPBN[x], firstcol, lastcol))
        exec('for col in {}.columns: {}[col] = {}[col].astype(int)'.format(mappingprovinsiAPBN[x],mappingprovinsiAPBN[x],mappingprovinsiAPBN[x]))
        #exec('for col in {}.columns: {}.loc[:, col] *= 1000000'.format(mappingprovinsiAPBN[x],mappingprovinsiAPBN[x],mappingprovinsiAPBN[x]))

    # Join2 --> kolom target dengan 11 fitur APBN
    for x in provinsi:
        exec('{}.index = {}.index.map(str)'.format(x, x))
        exec('{} = pd.concat([{}, {}APBN], axis=1, join="inner")'.format(x, x, x))
    # =================================================================

    # Pemrosesan Peta
    st.success('Data ' + target + ' per Provinsi')
    exec('df_mapping = {}'.format(column[0]))
    df, indomap = util.read_map(df_mapping, provinsi)
   
    col1, col2 = st.columns((4, 1))
    with col1:
        peta = util.plot_map(df, indomap, tahun)
        selected_points = plotly_events(peta)

        # Visualisasi Peta
        if(len(selected_points) > 0):
            idx = int(selected_points[0]['pointIndex'])

            name_provinsi = df.iloc[idx]['provinsi']
            selected_provinsi = df['variabel'].iloc[idx]

            #exec('st.write({})'.format(selected_provinsi))
            exec('results = util.prediction({})'.format(selected_provinsi))
    
    with col2:
        if 'name_provinsi' in locals():
            st.subheader('Provinsi ' + name_provinsi)
    
with tab2:
    if 'name_provinsi' in locals():
        st.subheader('Capaian ' + column[0] + ' pada Provinsi ' + name_provinsi)
    if 'results' in locals():
        st.success('Hasil Prediksi ' + column[0])
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write('Hasil Prediksi')
            st.write(results['y_test'])
        with col2:
            st.write('Data Real')
            st.write(results['y_pred'])
        col3.metric("Mean Square Error (MSE)", str('{:.2f}'.format(results['MSE'])))

        st.success('Seleksi Fitur')
        col1, col2 = st.columns(2)
        with col1:
            st.write('Feature Importance')
            st.write(results['importance_df'].style.applymap(util.is_feature_importance, subset=['importance']))
            #df.style.applymap(is_temp_valid, subset=['celsius_temperature'])
        with col2:
            st.write('Best Features')
            st.write(results['dfprov'].iloc[:, 1:])

        st.success('Hasil Prediksi dengan Best Features')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write('Hasil Prediksi')
            st.write(results['y_test Tahap 2'])
        with col2:
            st.write('Data Real')
            st.write(results['y_pred Tahap 2'])
        col3.metric("Mean Square Error (MSE)", str('{:.2f}'.format(results['mse Tahap 2'])))

        st.success('Simulasi Belanja Pemerintah Pusat Per Fungsi terhadadap Capaian ' + column[0])
        with st.form("my_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                f1 = st.number_input('Anggaran ' + results['dfprov'].columns[1])
            with col2:
                f2 = st.number_input('Anggaran ' + results['dfprov'].columns[2])
            with col3:
                f3 = st.number_input('Anggaran ' + results['dfprov'].columns[3])
                
            submitted = st.form_submit_button("Submit")
            if submitted:
                predictionresult = (f1*results['regressor.coef_'][0][0] + f2*results['regressor.coef_'][0][1] + f3*results['regressor.coef_'][0][2])
                st.metric('Prediksi Capaian ' +column[0]+':', str(predictionresult))
