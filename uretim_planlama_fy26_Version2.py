import streamlit as st
import pandas as pd
from datetime import date, timedelta

# Başlık
st.title("FY26 Üretim Planlama ve Tip Değişikliği Optimizasyonu")

# Excel Dosyası Yükleme
kapasite_file = st.file_uploader("Kapasite Excel Dosyasını Yükleyin", type=["xlsx"])
aylik_plan_file = st.file_uploader("FY26 Aylık Üretim Planı Excel Dosyasını Yükleyin", type=["xlsx"])

if kapasite_file and aylik_plan_file:
    try:
        # Kapasite Verilerini Yükle
        kapasite_data = pd.read_excel(kapasite_file, sheet_name="Kapasite")
        moduller_data = pd.read_excel(kapasite_file, sheet_name="Modüller")
        
        # FY26 Aylık Üretim Planını Yükle
        aylik_plan_data = pd.read_excel(aylik_plan_file)

        # Çalışma Günü Ayarları
        st.sidebar.header("Çalışma Günü Ayarları")
        work_days = st.sidebar.number_input("Yıllık Çalışma Günü", min_value=1, max_value=365, value=265)

        # Günlük Üretim Hedefi
        daily_target = 1634  # Günlük üretim hedefi
        st.sidebar.header("Günlük Üretim Hedefi")
        st.sidebar.text(f"Günlük Üretim Hedefi: {daily_target} adet")

        # Tip Değişikliği Süresi (Dakika)
        tip_degisim_suresi = 5  # Tip değişikliği süresi sabit olarak 5 dakika
        st.sidebar.text(f"Tip Değişikliği Süresi: {tip_degisim_suresi} dakika")

        # FY26 Ay Seçimi
        aylar = [
            "Eylül 2025", "Ekim 2025", "Kasım 2025", "Aralık 2025", 
            "Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026", 
            "Mayıs 2026", "Haziran 2026", "Temmuz 2026", "Ağustos 2026"
        ]
        st.sidebar.header("FY26 Ay Seçimi")
        select_month = st.sidebar.selectbox("Planlama Yapılacak Ayı Seçin", aylar)

        # Seçilen Ay için Üretim Hedeflerini Al
        aylik_plan_data["Günlük Hedef"] = aylik_plan_data[select_month] / (work_days / 12)
        st.subheader(f"{select_month} Aylık Üretim Planı")
        st.dataframe(aylik_plan_data[["Ürün Kodu", "Ürün Tanımı", select_month, "Günlük Hedef"]])

        # Günlük Planlama
        st.header("Günlük Üretim Planı")
        selected_date = st.date_input("Planlama Tarihi Seçin", value=pd.Timestamp.today())

        # Tip Değişikliği Optimizasyonu
        st.header("Tip Değişikliği Optimizasyonu")
        daily_plan = []
        remaining_target = daily_target

        # Ürünleri, modüllerdeki üretim kapasitesine göre sıralayın
        sorted_products = aylik_plan_data.sort_values(by="Günlük Hedef", ascending=False)

        last_product_type = None
        total_changeover_time = 0

        for _, row in sorted_products.iterrows():
            if remaining_target <= 0:
                break

            cihaz_kodu = row["Ürün Kodu"]
            cihaz_tanimi = row["Ürün Tanımı"]
            gunluk_hedef = row["Günlük Hedef"]

            if gunluk_hedef <= 0:
                continue

            # Tip değişikliği kontrolü
            if last_product_type and last_product_type != cihaz_kodu:
                total_changeover_time += tip_degisim_suresi

            # Günlük üretim hedefinden eksilt
            produce_count = min(remaining_target, gunluk_hedef)
            remaining_target -= produce_count

            daily_plan.append({
                "Ürün Kodu": cihaz_kodu,
                "Ürün Tanımı": cihaz_tanimi,
                "Üretim Miktarı": produce_count
            })

            last_product_type = cihaz_kodu

        # Sonuçları Görüntüleme
        st.subheader("Günlük Üretim Planı ve Tip Değişikliği Süresi")
        daily_plan_df = pd.DataFrame(daily_plan)
        st.dataframe(daily_plan_df)

        st.text(f"Toplam Tip Değişikliği Süresi: {total_changeover_time} dakika")

    except Exception as e:
        st.error(f"Hata: {e}")

else:
    st.warning("Lütfen kapasite ve FY26 aylık üretim planı dosyalarını yükleyin.")