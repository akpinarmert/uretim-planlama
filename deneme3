import streamlit as st
import pandas as pd

# Başlık
st.title("Üretim Planlama Programı")

# Excel dosyalarını yükleme
st.header("Excel Dosyalarını Yükle")

# FY26 Kapasite dosyası yükleme
uploaded_kapasite = st.file_uploader("FY26 Kapasite dosyasını yükleyin", type=["xlsx", "xls"])
if uploaded_kapasite is not None:
    try:
        df_kapasite = pd.read_excel(uploaded_kapasite)
        st.success("FY26 Kapasite dosyası başarıyla yüklendi!")
        st.write("İçerik önizlemesi:")
        st.dataframe(df_kapasite)
    except Exception as e:
        st.error(f"FY26 Kapasite dosyasını okurken bir hata oluştu: {e}")

# FY26 Plan dosyası yükleme
uploaded_plan = st.file_uploader("FY26 Plan dosyasını yükleyin", type=["xlsx", "xls"])
if uploaded_plan is not None:
    try:
        df_plan = pd.read_excel(uploaded_plan)
        st.success("FY26 Plan dosyası başarıyla yüklendi!")
        st.write("İçerik önizlemesi:")
        st.dataframe(df_plan)
    except Exception as e:
        st.error(f"FY26 Plan dosyasını okurken bir hata oluştu: {e}")
