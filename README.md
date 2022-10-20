# Analisis Prediktif Capaian Indikator Utama Pembangunan

## Link Deployment
https://capaian-indikator-utama-pembangunan.streamlitapp.com/

## Deskripsi Teknologi
Untuk mengembangkan dashboard, digunakan **Bahasa Pemrograman Python** dengan **Library Streamlit** serta library lain yang didefinisikan pada file *requirements.txt*. 

## Metode
Untuk melakukan prediksi dan pengembangan simulasi belanja pemerintah per fungsi dan capaian indikator utama pembangunan di Indonesia, digunakan metode **Gradient Boost Tree**. Pemilihan metode ini didasari pada hasil RMSE terendah dari metode berikut:
1. Gradient Boost Tree
2. Linear Regression
3. Support Vector Regression
4. Long Short Term Memory

## Struktur
Di repositori ini, terdapat 2 jenis file, yaitu **File Data** dan **File Kode**

### A. File Data
**File Data** adalah file-file yang digunakan sebagai dataset untuk Dashboard yang dikembangkan. Berikut adalah penjelasan dari data yang digunakan.

#### 1. Data Historis Tahun 2010-2022
Sumber: https://bps.go.id
1. Indeks Pembangunan Manusia (*Indeks Pembangunan Manusia.xlsx*)
2. Laju Pertumbuhan Ekonomi (*Laju PDRB.xlsx*)
3. Tingkat Pengangguran Terbuka (*pengangguran.xlsx*)
4. Persentase Tingkat Kemiskinan (*persentasemiskin.xlsx*)
5. Rasio Gini (*giniratio.xlsx*)

#### 2. Sasaran Rencana Kerja Pemerintah Tahun 2010-2022
Sumber: https://bappenas.go.id
1. Target Indeks Pembangunan Manusia (*IPM.xlsx*)
2. Target Laju Pertumbuhan Ekonomi (*LPE.xlsx*)
3. Target Tingkat Pengangguran Terbuka (*TPT.xlsx*)
4. Target Persentase Tingkat Kemiskinan (*TK.xlsx*)
5. Target Rasio Gini (*GINI.xlsx*)

#### 3. Belanja Pemerintah per Fungsi per Provinsi Tahun 2010-2021
Sumber: https://peta.data-apbn.kemenkeu.go.id  
Belanja Pemerintah per Fungsi per Provinsi (*Peta APBN Data.csv*)

#### 4. Peta Indonesia
Sumber: https://github.com/superpikar/indonesia-geojson
1. Koordinat Peta Indonesia per Provinsi (*indonesia.geojson*)
2. Mapping Data Provinsi di Peta dengan Data Provinsi dari BPS dan Kemenkeu (*mappingprovinsi.csv*)

### B. File Kode
**File Kode** adalah file-file yang digunakan untuk mengembangkan Dashboard. Berikut adalah penjabaran dari file kode.
1. Main Program (*app.py*)
2. Utilization Function (*util.py*)
3. List mapping provinsi dengan data belanja pemerintah per fungsi per provinsi (*mapping.py*)
4. Program untuk mengakuisisi data (*Proses Akuisisi.ipynb*)
5. Requirement Dependencies (*requirements.txt*)

## Authors
Haekal Rizky Yulianto  
Kurniandha Sukma Yunastrian  
Safira Vanillia Putri
