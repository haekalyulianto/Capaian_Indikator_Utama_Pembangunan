import pandas as pd
import streamlit as st
from streamlit_plotly_events import plotly_events
import util
import mapping
from sklearn import ensemble
from sklearn.multioutput import MultiOutputRegressor

def changeprov():
    indexgantiprov = df['provinsi'].loc[lambda x: x==st.session_state.state_name_provinsi].index[0]
    st.session_state.selectboxchanged = 1
    st.session_state.index_provinsi = indexgantiprov

    #st.write(st.session_state['state_name_provinsi'])
    if 'selected_points' in locals():
        selected_points.append({'pointIndex' : indexgantiprov})
        #selected_points[0]['pointIndex'] = indexgantiprov
        idx = int(selected_points[0]['pointIndex'])
    else:
        selected_points = [{'pointIndex': indexgantiprov}, {'pointIndex': indexgantiprov}]
        idx = int(selected_points[0]['pointIndex'])

if 'selectboxchanged' not in st.session_state:
    st.session_state['selectboxchanged'] = 0

# Konfigurasi Halaman
st.set_page_config(page_title="Peta Indonesia", layout="wide")
st.title('Capaian Indikator Utama Pembangunan di Indonesia')

tab1, tab2, tab3 = st.tabs(["1. Visualisasi Data", "2. Prediksi Data", "3. Simulasi"])

# Pemrosesan Data
with tab1:
    inputcol1, inputcol2 = st.columns(2)

    with inputcol1:
        tahun = st.selectbox('Tahun', ([str(x) for x in range(2021, 2009, -1)]))

    with inputcol2:
        target = st.selectbox('Indikator', ('Indeks Pembangunan Manusia', 'Tingkat Kemiskinan', 'Rasio Gini', 'Laju Pertumbuhan Ekonomi', 'Tingkat Pengangguran Terbuka'), key=0)

    filetarget = 'Indeks Pembangunan Manusia.xlsx'
    sasaran = 'IPM.xlsx'
    
    column = ['IPM']
    flag='IPM'

    if (target == 'Tingkat Kemiskinan'):
        filetarget = 'persentasemiskin.xlsx'
        sasaran = 'TK.xlsx'
        column = ['Kemiskinan']
        flag='Kemiskinan'
    elif (target == 'Rasio Gini'):
        filetarget = 'giniratio.xlsx'
        sasaran = 'GINI.xlsx'
        column = ['Gini']
        flag='Gini'
    elif (target == 'Laju Pertumbuhan Ekonomi'):
        filetarget = 'Laju PDRB.xlsx'
        sasaran = 'LPE.xlsx'
        column = ['LPE']
        flag='LPE'
    elif (target == 'Tingkat Pengangguran Terbuka'):
        filetarget = 'pengangguran.xlsx'
        sasaran = 'TPT.xlsx'
        column = ['TPT']
        flag='TPT'

    exec('{} = pd.read_excel("{}")'.format(column[0], filetarget))

    filesasaran = pd.read_excel(sasaran).sort_values(by='tahun').reset_index().drop('index', axis=1)
    filesasaran.fillna("", inplace = True)

    provinsi=['ACEH','SUMATERA_UTARA','SUMATERA_BARAT','RIAU', 'JAMBI',	'SUMATERA_SELATAN',	'BENGKULU',	'LAMPUNG',	'BANGKA_BELITUNG',	'KEPRI',	'DKI_JAKARTA',	'JAWA_BARAT',	'JAWA_TENGAH',	'DI_YOGYAKARTA',	'JAWA_TIMUR',	'BANTEN',	'BALI',	'NTB',	'NTT',	'KALIMANTAN_BARAT',	'KALIMANTAN_TENGAH',	'KALIMANTAN_SELATAN',	'KALIMANTAN_TIMUR',	'KALIMANTAN_UTARA',	'SULAWESI_UTARA',	'SULAWESI_TENGAH',	'SULAWESI_SELATAN',	'SULAWESI_TENGGARA',	'GORONTALO',	'SULAWESI_BARAT',	'MALUKU',	'MALUKU_UTARA',	'PAPUA_BARAT',	'PAPUA']

    for x in provinsi:  
        exec('{} = pd.DataFrame(columns=column)'.format(x))

    countX=0
    countY=0

    for i in provinsi:
        for j in column:
            exec('{}["{}"]={}.loc[{}:{},2010:2021].T'.format(i,j,j,countX,countY))
        countX+=1
        countY+=1

    APBN = pd.read_csv('Peta APBN Data.csv', header=None)

    APBN[0][0] = 'Tahun'
    APBN.columns = APBN.iloc[0]
    APBN = APBN.iloc[1:]
    APBN = APBN.astype({"Tahun": int})
    APBN = APBN.astype({"Tahun": str})
    APBN = APBN.set_index('Tahun', drop=True)

    mappingprovinsiAPBN = mapping.mappingprovinsiAPBN

    # Pisah - Pisah --> 11 fitur APBN Per Fungsi
    for x in mappingprovinsiAPBN.keys():
        firstcol = (x-1)*11 # Jumlah parameter
        lastcol = x*11 
        exec('{} = APBN.iloc[:, {}:{}]'.format(mappingprovinsiAPBN[x], firstcol, lastcol))
        exec('for col in {}.columns: {}[col] = {}[col].astype(int)'.format(mappingprovinsiAPBN[x],mappingprovinsiAPBN[x],mappingprovinsiAPBN[x]))

    # Join Join --> Kolom target dengan 11 fitur APBN Per Fungsi
    for x in provinsi:
        exec('{}.index = {}.index.map(str)'.format(x, x))
        exec('{} = pd.concat([{}, {}APBN], axis=1, join="inner")'.format(x, x, x))

    # Pemrosesan Peta
    st.success('Data ' + target + ' per Provinsi')
    exec('df_mapping = {}'.format(column[0]))
    df, indomap = util.read_map(df_mapping, provinsi)
   
    col1, col2 = st.columns((4, 1))
    with col1:
        do_refresh = st.button('Refresh')
        peta = util.plot_map(df, indomap, tahun)

        selected_points = plotly_events(peta)
        
        if (st.session_state.selectboxchanged == 1):
            selected_points.append({'pointIndex' : -1})

        if ('ever_clicked' in st.session_state):
            selected_points.append({'pointIndex' : -1})

        # Visualisasi Peta
        if (len(selected_points) > 0):
            st.session_state.ever_clicked = 1
            idx = int(selected_points[0]['pointIndex'])

            if (st.session_state.selectboxchanged == 1):
                idx = st.session_state.index_provinsi
                st.session_state.selectboxchanged = 0

            if (selected_points[0]['pointIndex'] == -1):
                idx = st.session_state.index_provinsi

            name_provinsi = df.iloc[idx]['provinsi']
            st.session_state['state_name_provinsi'] = name_provinsi
            selected_provinsi = df['variabel'].iloc[idx]
            exec('results = util.prediction({})'.format(selected_provinsi))
    
    with col2:
        st.selectbox('Provinsi', (df['provinsi']), key='state_name_provinsi' , on_change=changeprov)
        if 'selected_provinsi' in locals():
            exec('temp_df={}[[column[0]]].reset_index().drop("index", axis=1)'.format(selected_provinsi))
            temp_df=pd.concat([temp_df, filesasaran], axis=1)

            util.is_target(temp_df, flag)
   
    col1, col2 = st.columns((4,1))
    with col1:
        with st.expander("Keterangan Rentang"):
            st.write('Semakin rendah Tingkat Pengangguran Terbuka, Tingkat Kemiskinan, dan Rasio Gini berarti semakin baik')
    with col2:    
        with st.expander("Keterangan Indikator"):
            st.write('🟥 Masih jauh dari target dalam RKP (>5% deviasi dari nilai target)')
            st.write('🟨 Mendekati target dalam RKP (5% deviasi dari nilai target)')  
            st.write('🟩 Sudah memenuhi target dalam RKP (>= atau <=)')    
            st.write('⬜ Target belum tersedia dalam RKP pada tahun tersebut') 
        
with tab2:
    if 'results' not in locals():
        st.warning('Silakan Pilih Provinsi pada Peta')
   
    if 'name_provinsi' in locals():
        st.subheader('Prediksi ' + target + ' pada Provinsi ' + name_provinsi)
    
    if 'results' in locals():
        st.success('Hasil Prediksi ' + target)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write('')
        with col2:
            st.write('Data Asli')
            st.write(results['y_test'])
        with col3:
            st.write('Hasil Prediksi')
            st.write(results['y_pred'])
        col4.metric("Root Mean Squared Error (RMSE)", str('{:.3f}'.format(results['RMSE'])))
        with col5:
            st.write('')
        
        with st.expander("Keterangan Hasil Prediksi"):
                st.write('Dilakukan pelatihan terhadap model pada data historis tahun 2010-2019 dan dilakukan pengujian pada data tahun 2020-2021')
                st.write('Semakin rendah hasil Root Mean Squared Error (RMSE) berarti semakin baik')

        st.success('Analisis Fungsi Anggaran Utama dalam Memprediksi ' + target)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write('')
        with col2:
            st.write('Tingkat Keutamaan Fungsi Anggaran')
            st.write(results['importance_df'].style.applymap(util.is_feature_importance, subset=['Keutamaan']))
        with col3:
            st.write('3 Fungsi Anggaran Utama')
            st.write(results['dfprov'].iloc[:, 1:])
        with col4:
            st.write('')

        col1, col2 = st.columns(2)
        with col1:
            with st.expander("Keterangan Tingkat Keutamaan"):    
                st.write('🟩 Tingkat keutamaan >= 0.5')
                st.write('🟨 0.2 =< Tingkat keutamaan < 0.5')  
                st.write('🟧 0.1 =< Tingkat keutamaan < 0.2')    
                st.write('🟥 Tingkat keutamaan < 0.1')    
        with col2:
            with st.expander("Keterangan Fungsi Anggaran"):
                    st.write('Data Fungsi Anggaran dalam Miliar Rupiah')
        
with tab3:
    if 'results' not in locals():
        st.warning('Silakan Pilih Provinsi pada Peta')
    
    if 'results' in locals():
        st.subheader('Simulasi Belanja Pemerintah Per Fungsi terhadap Capaian ' + target + ' pada Provinsi ' + name_provinsi)

        st.success('Simulasi ' + target + ' yang Akan Dicapai Berdasarkan 3 Fungsi Anggaran Utama yang Dikeluarkan' )   

        f1val = results['dfprov'].iloc[-1:, 1:][results['dfprov'].iloc[-1:, 1:].columns[0]].iloc[0]
        f2val = results['dfprov'].iloc[-1:, 1:][results['dfprov'].iloc[-1:, 1:].columns[1]].iloc[0]
        f3val = results['dfprov'].iloc[-1:, 1:][results['dfprov'].iloc[-1:, 1:].columns[2]].iloc[0]

        with st.form("form_1"):
            col1, col2, col3 = st.columns(3)
            with col1:
                f1 = st.number_input('Anggaran ' + results['dfprov'].columns[1] + ' (Dalam Milyar Rupiah)', value=f1val)
            with col2:
                f2 = st.number_input('Anggaran ' + results['dfprov'].columns[2] + ' (Dalam Milyar Rupiah)', value=f2val)
            with col3:
                f3 = st.number_input('Anggaran ' + results['dfprov'].columns[3] + ' (Dalam Milyar Rupiah)', value=f3val)
                
            submitted = st.form_submit_button("Hitung")
            if submitted:

                X = results['dfprov'].iloc[:, 1:4]
                y = results['dfprov'][[results['dfprov'].columns[0]]]

                X_train = X[:12]
                y_train = y[:12]
                
                regressor = ensemble.GradientBoostingRegressor(random_state=0)
                regressor.fit(X_train, y_train)
                
                y_pred = regressor.predict([[f1, f2, f3]])

                st.metric('Prediksi Capaian ' +target+':', str('{:.3f}'.format(y_pred[0])))
        
        st.success('Simulasi Fungsi Anggaran Utama yang Perlu Dikeluarkan untuk Mencapai ' + target + ' yang Diinginkan')
        with st.form("form_2"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write('')
            with col2:
                f1 = st.number_input('Capaian ' + target + ' yang Diinginkan', value=results['y_test'].iloc[-1:].iloc[0])
            with col3:
                st.write('')
                
            submitted = st.form_submit_button("Hitung")
            if submitted:
                
                X = results['dfprov'].iloc[:, 1:4]
                y = results['dfprov'][[results['dfprov'].columns[0]]]

                y_train = X[:12]
                X_train = y[:12]
                
                regressor = MultiOutputRegressor(ensemble.GradientBoostingRegressor(random_state=0))
                regressor.fit(X_train, y_train)
                
                y_pred = regressor.predict([[f1]])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric('Prediksi Anggaran  ' + X.columns[0] +' (Dalam Miliar Rupiah): ', str('{:.3f}'.format(float(y_pred[:,0:1]))))
                with col2:
                    st.metric('Prediksi Anggaran  ' + X.columns[1] +' (Dalam Miliar Rupiah): ', str('{:.3f}'.format(float(y_pred[:,1:2]))))
                with col3:
                    st.metric('Prediksi Anggaran  ' + X.columns[2] +' (Dalam Miliar Rupiah): ', str('{:.3f}'.format(float(y_pred[:,2:3]))))
