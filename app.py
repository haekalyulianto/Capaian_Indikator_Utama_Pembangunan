from asyncio import Transport
import pandas as pd
import streamlit as st
from streamlit_plotly_events import plotly_events
import util
import mapping
from sklearn import ensemble
from sklearn.multioutput import MultiOutputRegressor
from collections import Counter
from streamlit_card import card

def changeprov():
    indexgantiprov = df['provinsi'].loc[lambda x: x==st.session_state.state_name_provinsi].index[0]
    st.session_state.selectboxchanged = 1
    st.session_state.index_provinsi = indexgantiprov

    if 'selected_points' in locals():
        selected_points.append({'pointIndex' : indexgantiprov})
        idx = int(selected_points[0]['pointIndex'])
    else:
        selected_points = [{'pointIndex': indexgantiprov}, {'pointIndex': indexgantiprov}]
        idx = int(selected_points[0]['pointIndex'])

def changetarget():
    if ('ever_clicked' in st.session_state):
        del st.session_state['ever_clicked']

if 'selectboxchanged' not in st.session_state:
    st.session_state['selectboxchanged'] = 0

st.set_page_config(page_title="Capaian Indikator Utama Pembangunan di Indonesia", layout="wide")
st.title('Capaian Indikator Utama Pembangunan di Indonesia')

tab1, tab2, tab3, tab4 = st.tabs(["1. Visualisasi Data", "2. Prediksi Data", "3. Simulasi Satu Indikator", "4. Simulasi Seluruh Indikator"])

with tab1:
    inputcol1, inputcol2 = st.columns(2)

    with inputcol1:
        tahun = st.selectbox('Tahun', ([str(x) for x in range(2021, 2009, -1)]))

    with inputcol2:
        target = st.selectbox('Indikator', ('Indeks Pembangunan Manusia', 'Tingkat Kemiskinan', 'Rasio Gini', 'Laju Pertumbuhan Ekonomi', 'Tingkat Pengangguran Terbuka'), key=0, on_change=changetarget)

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
    
    column.append("Inflasi")
    column.append("KFD")

    Inflasi = pd.read_excel('Inflasi.xlsx')
    KFD = pd.read_excel('KFD.xlsx')

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

    for x in mappingprovinsiAPBN.keys():
        firstcol = (x-1)*11 
        lastcol = x*11 
        exec('{} = APBN.iloc[:, {}:{}]'.format(mappingprovinsiAPBN[x], firstcol, lastcol))
        exec('for col in {}.columns: {}[col] = {}[col].astype(int)'.format(mappingprovinsiAPBN[x],mappingprovinsiAPBN[x],mappingprovinsiAPBN[x]))

    for x in provinsi:
        exec('{}.index = {}.index.map(str)'.format(x, x))
        exec('{} = pd.concat([{}, {}APBN], axis=1, join="inner")'.format(x, x, x))

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

    resultsallcompiled = []
    if (len(selected_points) > 0):
            
        targets = ['Indeks Pembangunan Manusia', 'Tingkat Kemiskinan', 'Rasio Gini', 'Laju Pertumbuhan Ekonomi', 'Tingkat Pengangguran Terbuka']
        filetargets = ['Indeks Pembangunan Manusia.xlsx', 'persentasemiskin.xlsx', 'giniratio.xlsx', 'Laju PDRB.xlsx', 'pengangguran.xlsx']
        sasarans = ['IPM.xlsx', 'TK.xlsx', 'GINI.xlsx', 'LPE.xlsx', 'TPT.xlsx']
        columns = [['IPM'], ['Kemiskinan'], ['Gini'], ['LPE'], ['TPT']]

        for k in range(len(columns)):
            columns[k].append("Inflasi")
            columns[k].append("KFD")

        for i in range(len(targets)):
            target2 = targets[i]
            filetarget2 = filetargets[i]
            sasaran2 = sasarans[i]
            column2 = columns[i]

            exec('{} = pd.read_excel("{}")'.format(column2[0], filetarget2))

            filesasaran = pd.read_excel(sasaran2).sort_values(by='tahun').reset_index().drop('index', axis=1)
            filesasaran.fillna("", inplace = True)

            provinsi=['ACEH','SUMATERA_UTARA','SUMATERA_BARAT','RIAU', 'JAMBI',	'SUMATERA_SELATAN',	'BENGKULU',	'LAMPUNG',	'BANGKA_BELITUNG',	'KEPRI',	'DKI_JAKARTA',	'JAWA_BARAT',	'JAWA_TENGAH',	'DI_YOGYAKARTA',	'JAWA_TIMUR',	'BANTEN',	'BALI',	'NTB',	'NTT',	'KALIMANTAN_BARAT',	'KALIMANTAN_TENGAH',	'KALIMANTAN_SELATAN',	'KALIMANTAN_TIMUR',	'KALIMANTAN_UTARA',	'SULAWESI_UTARA',	'SULAWESI_TENGAH',	'SULAWESI_SELATAN',	'SULAWESI_TENGGARA',	'GORONTALO',	'SULAWESI_BARAT',	'MALUKU',	'MALUKU_UTARA',	'PAPUA_BARAT',	'PAPUA']

            for x in provinsi:  
                exec('{} = pd.DataFrame(columns=column2)'.format(x))

            countX=0
            countY=0

            for i in provinsi:
                for j in column2:
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

            for x in mappingprovinsiAPBN.keys():
                firstcol = (x-1)*11
                lastcol = x*11 
                exec('{} = APBN.iloc[:, {}:{}]'.format(mappingprovinsiAPBN[x], firstcol, lastcol))
                exec('for col in {}.columns: {}[col] = {}[col].astype(int)'.format(mappingprovinsiAPBN[x],mappingprovinsiAPBN[x],mappingprovinsiAPBN[x]))

            for x in provinsi:
                exec('{}.index = {}.index.map(str)'.format(x, x))
                exec('{} = pd.concat([{}, {}APBN], axis=1, join="inner")'.format(x, x, x))

            exec('df_mapping = {}'.format(column2[0]))
            df, indomap = util.read_map(df_mapping, provinsi)
            selected_provinsi = df['variabel'].iloc[idx]
            exec('resultsall = util.prediction({})'.format(selected_provinsi))
            resultsallcompiled.append(resultsall)
   
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
            results['importance_df'].drop(results['importance_df']
            [(results['importance_df']['Fungsi Anggaran'] == 'Inflasi') | (results['importance_df']['Fungsi Anggaran'] == 'KFD')].index, inplace=True)
            
            st.write(results['importance_df'].style.applymap(util.is_feature_importance, subset=['Keutamaan']))
        with col3:
            st.write('Fungsi Anggaran Utama')
            st.write(results['dfprovakhir'].iloc[:, 1:])

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
                    st.write('Fungsi anggaran utama didapat dari feature importance')
                    st.write('Fungsi anggaran dalam miliar rupiah')

        targets = ['Indeks Pembangunan Manusia', 'Tingkat Kemiskinan', 'Rasio Gini', 'Laju Pertumbuhan Ekonomi', 'Tingkat Pengangguran Terbuka']
        features1 = []
        features2 = []
        features3 = []
        listsemua = []
        for i in range (len(resultsallcompiled)):
            resultsallcompiled[i]['importance_df'].drop(resultsallcompiled[i]['importance_df']
            [(resultsallcompiled[i]['importance_df']['Fungsi Anggaran'] == 'Inflasi') | (resultsallcompiled[i]['importance_df']['Fungsi Anggaran'] == 'KFD')].index, inplace=True)
            
            features1.append(resultsallcompiled[i]['importance_df']['Fungsi Anggaran'].iloc[0])
            features2.append(resultsallcompiled[i]['importance_df']['Fungsi Anggaran'].iloc[1])
            features3.append(resultsallcompiled[i]['importance_df']['Fungsi Anggaran'].iloc[2])

            listsemua.append(resultsallcompiled[i]['importance_df']['Fungsi Anggaran'].iloc[0])
            listsemua.append(resultsallcompiled[i]['importance_df']['Fungsi Anggaran'].iloc[1])
            listsemua.append(resultsallcompiled[i]['importance_df']['Fungsi Anggaran'].iloc[2])

        dfalltarget = pd.DataFrame({'Target': targets, 'Anggaran Utama 1': features1, 'Anggaran Utama 2': features2, 'Anggaran Utama 3': features3})

        listcountsemua = []

        counterresults = Counter(listsemua)
        for key in counterresults.keys():
            listcountsemua.append((key,counterresults[key]))
        sorted_by_second = sorted(listcountsemua, key=lambda tup: tup[1], reverse=True)

        dfalltargettop3 = resultsallcompiled[0]['dfprovawal'][[sorted_by_second[0][0], sorted_by_second[1][0], sorted_by_second[2][0]]]
        
        for i in range(len(resultsallcompiled)):
            dfalltargettop3[targets[i]] = resultsallcompiled[i]['dfprov'][[resultsallcompiled[i]['dfprov'].columns[0]]]

        st.success('Analisis Fungsi Anggaran Utama dalam Memprediksi Seluruh 5 Indikator Utama Pembangunan')

        lsa = []
        lsb = []
        for i in range(len(sorted_by_second)):
            lsa.append(sorted_by_second[i][0])
            lsb.append(sorted_by_second[i][1]/15)

        dftop3counts = pd.DataFrame({'Fungsi Anggaran':lsa, 'Keutamaan': lsb})

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write('')
        with col2:
            st.write('Tingkat Keutamaan Fungsi Anggaran')
            st.write(dftop3counts.style.applymap(util.is_feature_importance, subset=['Keutamaan']))
        with col3:
            st.write('Fungsi Anggaran Utama')
            st.write(dfalltargettop3.iloc[:, :3])
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
                    st.write('Fungsi anggaran utama didapat dari kesamaan fungsi anggaran utama pada seluruh 5 indikator utama pembangunan')
        
with tab3:
    if 'results' not in locals():
        st.warning('Silakan Pilih Provinsi pada Peta')
    
    if 'results' in locals():
        st.subheader('Simulasi Belanja Pemerintah Per Fungsi terhadap Capaian ' + target + ' pada Provinsi ' + name_provinsi)

        st.success('Simulasi ' + target + ' yang Akan Dicapai Berdasarkan Fungsi Anggaran Utama yang Dikeluarkan' )   

        dflima = results['dfprovakhir'].copy()
        dflima['Inflasi'] = results['dfprovawal']['Inflasi']
        dflima['KFD'] = results['dfprovawal']['KFD']

        f1val = results['dfprovakhir'].iloc[-1:, 1:][results['dfprovakhir'].iloc[-1:, 1:].columns[0]].iloc[0]
        f2val = results['dfprovakhir'].iloc[-1:, 1:][results['dfprovakhir'].iloc[-1:, 1:].columns[1]].iloc[0]
        f3val = results['dfprovakhir'].iloc[-1:, 1:][results['dfprovakhir'].iloc[-1:, 1:].columns[2]].iloc[0]
        f4val = results['dfprovawal'].iloc[-1:, 1:][results['dfprovawal'].iloc[-1:, 1:].columns[0]].iloc[0]
        f5val = results['dfprovawal'].iloc[-1:, 1:][results['dfprovawal'].iloc[-1:, 1:].columns[1]].iloc[0]
    
        with st.form("form_1"):
            st.info('Faktor Anggaran')
            col1, col2, col3 = st.columns(3)
            
            with col1:
                f1 = st.number_input('Anggaran ' + results['dfprovakhir'].columns[1] + ' (Dalam Milyar Rupiah)', value=f1val)
            with col2:
                f2 = st.number_input('Anggaran ' + results['dfprovakhir'].columns[2] + ' (Dalam Milyar Rupiah)', value=f2val)
            with col3:
                f3 = st.number_input('Anggaran ' + results['dfprovakhir'].columns[3] + ' (Dalam Milyar Rupiah)', value=f3val)

            st.info('Faktor Lainnya')
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write('')
            with col2:
                f4 = st.number_input('Faktor Inflasi', value=f4val)
            with col3:
                f5 = st.number_input('Faktor Kapasitas Fiskal Daerah', value=f5val)
            with col4:
                st.write('')

            submitted = st.form_submit_button("Hitung")
            if submitted:
                
                X = dflima.iloc[:, 1:6]
                y = results['dfprov'][[results['dfprov'].columns[0]]]

                X_train = X[:12]
                y_train = y[:12]
                
                regressor = ensemble.GradientBoostingRegressor(random_state=0)
                regressor.fit(X_train, y_train)
                
                y_pred = regressor.predict([[f1, f2, f3, f4, f5]])

                st.metric('Prediksi Capaian ' +target+':', str('{:.3f}'.format(y_pred[0])))
                
                if (target == 'Indeks Pembangunan Manusia'):
                    if y_pred[0] >= 73.41:
                        st.warning('Sudah Mencapai Target RKP')
                    else:
                        st.error('Belum Mencapai Target RKP')
                elif (target == 'Tingkat Kemiskinan'):
                    if y_pred[0] <= 8.5:
                        st.warning('Sudah Mencapai Target RKP')
                    else:
                        st.error('Belum Mencapai Target RKP')
                elif (target == 'Rasio Gini'):
                    if y_pred[0] <= 0.376:
                        st.warning('Sudah Mencapai Target RKP')
                    else:
                        st.error('Belum Mencapai Target RKP')
                elif (target == 'Laju Pertumbuhan Ekonomi'):
                    if y_pred[0] >= 5.2 and y_pred[0] <= 5.5:
                        st.warning('Sudah Mencapai Target RKP')
                    else:
                        st.error('Belum Mencapai Target RKP')
                else:
                    if y_pred[0] <= 6.3:
                        st.warning('Sudah Mencapai Target RKP')
                    else:
                        st.error('Belum Mencapai Target RKP')
        
        st.success('Simulasi Fungsi Anggaran Utama yang Perlu Dikeluarkan untuk Mencapai ' + target + ' yang Diinginkan')
        with st.form("form_2"):
            st.info('Faktor Anggaran')
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write('')
            with col2:
                f1 = st.number_input('Capaian ' + target + ' yang Diinginkan', value=results['y_test'].iloc[-1:].iloc[0])
            with col3:
                if (target == 'Indeks Pembangunan Manusia'):
                    st.markdown('<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous"><p style="background-color: rgb(220, 137, 40); color: rgb(250, 250, 250); font-size: 34px; border-radius: 7px; padding-left: 12px; padding-top: 6px; padding-bottom: 6px; line-height: 27px;"><span style="color: rgb(0, 0, 0)">73.41 - 73.46</span><br><span style="font-size: 18px; margin-top: 0px; color: white; line-height: 5px;">Target Indeks Pembangunan Manusia pada RKP Tahun 2022</span></p>', unsafe_allow_html=True)
                elif (target == 'Tingkat Kemiskinan'):
                    st.markdown('<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous"><p style="background-color: rgb(220, 137, 40); color: rgb(250, 250, 250); font-size: 34px; border-radius: 7px; padding-left: 12px; padding-top: 6px; padding-bottom: 6px; line-height: 27px;"><span style="color: rgb(0, 0, 0)">8.50 - 9.00</span><br><span style="font-size: 18px; margin-top: 0px; color: white; line-height: 5px;">Target Tingkat Kemiskinan pada RKP Tahun 2022</span></p>', unsafe_allow_html=True)
                elif (target == 'Rasio Gini'):
                    st.markdown('<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous"><p style="background-color: rgb(220, 137, 40); color: rgb(250, 250, 250); font-size: 34px; border-radius: 7px; padding-left: 12px; padding-top: 6px; padding-bottom: 6px; line-height: 27px;"><span style="color: rgb(0, 0, 0)">0.376 - 0.378</span><br><span style="font-size: 18px; margin-top: 0px; color: white; line-height: 5px;">Target Rasio Gini pada RKP Tahun 2022</span></p>', unsafe_allow_html=True)
                elif (target == 'Laju Pertumbuhan Ekonomi'):
                    st.markdown('<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous"><p style="background-color: rgb(220, 137, 40); color: rgb(250, 250, 250); font-size: 34px; border-radius: 7px; padding-left: 12px; padding-top: 6px; padding-bottom: 6px; line-height: 27px;"><span style="color: rgb(0, 0, 0)">5.20 - 5.50</span><br><span style="font-size: 18px; margin-top: 0px; color: white; line-height: 5px;">Target Laju Pertumbuhan Ekonomi pada RKP Tahun 2022</span></p>', unsafe_allow_html=True)
                else:
                    st.markdown('<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous"><p style="background-color: rgb(220, 137, 40); color: rgb(250, 250, 250); font-size: 34px; border-radius: 7px; padding-left: 12px; padding-top: 6px; padding-bottom: 6px; line-height: 27px;"><span style="color: rgb(0, 0, 0)">5.50 - 6.30</span><br><span style="font-size: 18px; margin-top: 0px; color: white; line-height: 5px;">Target Tingkat Pengangguran Terbuka pada RKP Tahun 2022</span></p>', unsafe_allow_html=True)
            with col4:
                st.write('')
            
            st.info('Faktor Lainnya')
            col1, col2, col3, col4 = st.columns(4)  
            with col1:
                st.write('')
            with col2:
                f2 = st.number_input('Faktor Inflasi', value=f4val)
            with col3:
                f3 = st.number_input('Faktor Kapasitas Fiskal Daerah', value=f5val)
            with col4:
                st.write('')
                
            submitted = st.form_submit_button("Hitung")
            if submitted:
                X = dflima.iloc[:, 1:4]
                y = results['dfprovawal'][[results['dfprovawal'].columns[0], 'Inflasi', 'KFD']]

                y_train = X[:12]
                X_train = y[:12]
                
                regressor = MultiOutputRegressor(ensemble.GradientBoostingRegressor(random_state=0))
                regressor.fit(X_train, y_train)
                
                y_pred = regressor.predict([[f1,f2,f3]])
                    
                percentage1 = ((float(y_pred[:,0:1])-f1val)/f1val)*100
                percentage2 = ((float(y_pred[:,1:2])-f2val)/f2val)*100
                percentage3 = ((float(y_pred[:,2:3])-f3val)/f3val)*100

                st.warning('Anggaran Saat Ini')
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric('Anggaran ' + X.columns[0] + ' Saat Ini (Dalam Miliar Rupiah): ', str(f1val))
                with col2:
                    st.metric('Anggaran ' + X.columns[1] + ' Saat Ini (Dalam Miliar Rupiah): ', str(f2val))
                with col3:
                    st.metric('Anggaran ' + X.columns[2] + ' Saat Ini (Dalam Miliar Rupiah): ', str(f3val))

                st.warning('Prediksi Anggaran yang Perlu Dikeluarkan')
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric('Prediksi Anggaran  ' + X.columns[0] +' (Dalam Miliar Rupiah): ', str('{:.3f}'.format(float(y_pred[:,0:1]))), str('{:.3f}'.format(percentage1)) + '%', delta_color="inverse")
                with col2:
                    st.metric('Prediksi Anggaran  ' + X.columns[1] +' (Dalam Miliar Rupiah): ', str('{:.3f}'.format(float(y_pred[:,1:2]))), str('{:.3f}'.format(percentage2)) + '%', delta_color="inverse")
                with col3:
                    st.metric('Prediksi Anggaran  ' + X.columns[2] +' (Dalam Miliar Rupiah): ', str('{:.3f}'.format(float(y_pred[:,2:3]))), str('{:.3f}'.format(percentage3)) + '%', delta_color="inverse")

with tab4:
    if 'results' not in locals():
        st.warning('Silakan Pilih Provinsi pada Peta')
    
    if 'results' in locals():
        st.subheader('Simulasi Belanja Pemerintah Per Fungsi terhadap Seluruh Indikator Utama Pembangunan pada Provinsi ' + name_provinsi)
        with st.form("form_3"):
            st.info('Faktor Anggaran')
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.write('Capaian ' + targets[0] + ' yang Diinginkan: ')
                f1 = st.number_input('', value=73.46, label_visibility='collapsed')
                st.write('Target ' + targets[0] + ' RKP Tahun 2022: 73.46')
            with col2:
                st.write('Capaian ' + targets[1] + ' yang Diinginkan: ')
                f2 = st.number_input('', value=9.0, label_visibility='collapsed')
                st.write('Target ' + targets[1] + ' RKP Tahun 2022: 9.0')
            with col3:
                st.write('Capaian ' + targets[2] + ' yang Diinginkan: ')
                f3 = st.number_input('', value=0.378, label_visibility='collapsed')
                st.write('Target ' + targets[2] + ' RKP Tahun 2022: 0.378')
            with col4:
                st.write('Capaian ' + targets[3] + ' yang Diinginkan: ')
                f4 = st.number_input('', value=5.5, label_visibility='collapsed')
                st.write('Target ' + targets[3] + ' RKP Tahun 2022: 5.5')
            with col5:
                st.write('Capaian ' + targets[4] + ' yang Diinginkan: ')
                f5 = st.number_input('', value=6.3, label_visibility='collapsed')
                st.write('Target ' + targets[4] + ' RKP Tahun 2022: 6.3')

            st.info('Faktor Eksternal')
            col1, col2, col3, col4 = st.columns(4)  
            with col1:
                st.write('')
            with col2:
                f6 = st.number_input('Faktor Inflasi', value=f4val)
            with col3:
                f7 = st.number_input('Faktor Kapasitas Fiskal Daerah', value=f5val)
            with col4:
                st.write('')
                
            f1val = dfalltargettop3.iloc[:, 0:1].iloc[len(dfalltargettop3)-1].iloc[0]
            f2val = dfalltargettop3.iloc[:, 1:2].iloc[len(dfalltargettop3)-1].iloc[0]
            f3val = dfalltargettop3.iloc[:, 2:3].iloc[len(dfalltargettop3)-1].iloc[0]

            submitted = st.form_submit_button("Hitung")
            if submitted:
                dfalltargettop3['Inflasi'] = dflima['Inflasi'] 
                dfalltargettop3['KFD'] = dflima['KFD'] 
                X = dfalltargettop3.iloc[:, 3:10]
                y = dfalltargettop3.iloc[:, 0:3]
                
                X_train = X[:12]
                y_train = y[:12]
                
                regressor = MultiOutputRegressor(ensemble.GradientBoostingRegressor(random_state=0))
                regressor.fit(X_train, y_train)
                
                y_pred = regressor.predict([[f1, f2, f3, f4, f5, f6, f7]])
                    
                percentage1 = ((float(y_pred[:,0:1])-f1val)/f1val)*100
                percentage2 = ((float(y_pred[:,1:2])-f2val)/f2val)*100
                percentage3 = ((float(y_pred[:,2:3])-f3val)/f3val)*100

                st.warning('Anggaran Saat Ini')
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric('Anggaran ' + dfalltargettop3.columns[0] + ' Saat Ini (Dalam Miliar Rupiah): ', str(f1val))
                with col2:
                    st.metric('Anggaran ' + dfalltargettop3.columns[1] + ' Saat Ini (Dalam Miliar Rupiah): ', str(f2val))
                with col3:
                    st.metric('Anggaran ' + dfalltargettop3.columns[2] + ' Saat Ini (Dalam Miliar Rupiah): ', str(f3val))

                st.warning('Prediksi Anggaran yang Perlu Dikeluarkan')
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric('Prediksi Anggaran ' + dfalltargettop3.columns[0] + ' (Dalam Miliar Rupiah): ', str('{:.3f}'.format(float(y_pred[:,0:1]))), str('{:.3f}'.format(percentage1)) + '%', delta_color="inverse")
                with col2:
                    st.metric('Prediksi Anggaran ' + dfalltargettop3.columns[1] + ' (Dalam Miliar Rupiah): ', str('{:.3f}'.format(float(y_pred[:,1:2]))), str('{:.3f}'.format(percentage2)) + '%', delta_color="inverse")
                with col3:
                    st.metric('Prediksi Anggaran ' + dfalltargettop3.columns[2] + ' (Dalam Miliar Rupiah): ', str('{:.3f}'.format(float(y_pred[:,2:3]))), str('{:.3f}'.format(percentage3)) + '%', delta_color="inverse")
