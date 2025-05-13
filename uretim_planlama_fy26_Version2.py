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

        # Sütun başlıklarını temizle (boşlukları ve özel karakterleri gider)
        aylik_plan_data.columns = (
            aylik_plan_data.columns.str.strip()  # Başındaki/sonundaki boşlukları kaldır
            .str.replace("\xa0", " ")  # Görünmez boşluk karakterlerini normal boşlukla değiştir
            .str.lower()  # Küçük harfe çevir
        )

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
            "eylül 2025", "ekim 2025", "kasım 2025", "aralık 2025", 
            "ocak 2026", "şubat 2026", "mart 2026", "nisan 2026", 
            "mayıs 2026", "haziran 2026", "temmuz 2026", "ağustos 2026"
        ]
        st.sidebar.header("FY26 Ay Seçimi")
        select_month = st.sidebar.selectbox("Planlama Yapılacak Ayı Seçin", aylar)

        # Seçilen Ay için Üretim Hedeflerini Al
        if select_month not in aylik_plan_data.columns:
            st.error(f"Seçilen ay ({select_month}) Excel dosyasında bulunamadı. Mevcut sütunlar: {list(aylik_plan_data.columns)}")
        else:
            # Günlük hedefi hesapla
            aylik_plan_data["günlük hedef"] = aylik_plan_data[select_month] / (work_days / 12)
            st.subheader(f"{select_month.capitalize()} Aylık Üretim Planı")
            st.dataframe(aylik_plan_data[["ürün kodu", "ürün tanımı", select_month, "günlük hedef"]])

            # Günlük Planlama
            st.header("Günlük Üretim Planı")
            selected_date = st.date_input("Planlama Tarihi Seçin", value=pd.Timestamp.today())

            # Tip Değişikliği Optimizasyonu
            st.header("Tip Değişikliği Optimizasyonu")
            daily_plan = []
            remaining_target = daily_target

            # Ürünleri, günlük hedefe göre sıralayın
            sorted_products = aylik_plan_data.sort_values(by="günlük hedef", ascending=False)

            last_product_type = None
            total_changeover_time = 0

            for _, row in sorted_products.iterrows():
                if remaining_target <= 0:
                    break

                cihaz_kodu = row["ürün kodu"]
                cihaz_tanimi = row["ürün tanımı"]
                gunluk_hedef = row["günlük hedef"]

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
