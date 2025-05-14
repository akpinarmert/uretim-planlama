import streamlit as st
import pandas as pd

# Streamlit başlığı
st.title("Üretim Planlama - 'FY26 Kapasite' Verileri Yükleme ve İşleme")

# GitHub URL'den dosyayı okuma
file_url = "https://raw.githubusercontent.com/akpinarmert/uretim-planlama/main/FY26%20Kapasite.xlsx"

try:
    # Sheet seçimi
    sheet_name = st.selectbox("Lütfen bir sheet seçin", ["Kapasite"])

    # Excel dosyasını okuma
    data = pd.read_excel(file_url, sheet_name=sheet_name)

    # Sütun adlarını temizleme
    data.columns = (
        data.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("ç", "c")
        .str.replace("ğ", "g")
        .str.replace("ı", "i")
        .str.replace("ö", "o")
        .str.replace("ş", "s")
        .str.replace("ü", "u")
    )

    # Boş hücreleri doldurma (üretim yapılmayan modüller için "0" yazıyoruz)
    data.fillna(0, inplace=True)

    # Temizlenmiş veriyi gösterme
    st.subheader("Temizlenmiş Veri:")
    st.dataframe(data)

    # Veri ile ilgili bilgi
    st.subheader("Veri Bilgisi:")
    st.write(data.describe())

except Exception as e:
    st.error(f"Veri yükleme veya işleme sırasında bir hata oluştu: {e}")
