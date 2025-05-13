import streamlit as st
import pandas as pd

# Başlık
st.title("Üretim Planlama Programı")

# Excel Yükleme
uploaded_file = st.file_uploader("Excel Dosyasını Yükle")
if uploaded_file:
    try:
        kapasite_data = pd.read_excel(uploaded_file, sheet_name="Kapasite")
        moduller_data = pd.read_excel(uploaded_file, sheet_name="Modüller")
        st.success("Excel dosyası başarıyla yüklendi.")
    except Exception as e:
        st.error(f"Hata: {str(e)}")

# Yıllık Çalışma Günü
yillik_calisma_gunu = st.number_input("Yıllık Çalışma Günü", min_value=1, max_value=365, value=265)

# Plan Oluştur
if st.button("Plan Oluştur"):
    try:
        toplam_uretim_gun = yillik_calisma_gunu
        plan = []
        for _, row in kapasite_data.iterrows():
            cihaz_kodu = row["Cihaz Kodu"]
            cihaz_tanimi = row["Cihaz Tanımı"]
            yillik_siparis = row["Yıllık Sipariş"]
            gunluk_hedef = round(yillik_siparis / toplam_uretim_gun)
            plan.append({
                "Cihaz Kodu": cihaz_kodu,
                "Cihaz Tanımı": cihaz_tanimi,
                "Yıllık Sipariş": yillik_siparis,
                "Günlük Hedef": gunluk_hedef,
            })
        st.dataframe(pd.DataFrame(plan))
    except Exception as e:
        st.error(f"Hata: {str(e)}")