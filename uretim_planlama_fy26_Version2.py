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

        # Sütun başlıklarını temizle
        aylik_plan_data.columns = (
            aylik_plan_data.columns.str.strip()
            .str.replace("\xa0", " ")
            .str.lower()
        )
        moduller_data.columns = (
            moduller_data.columns.str.strip()
            .str.replace("\xa0", " ")
            .str.lower()
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
            # Aylık Planlama
            aylik_plan_data["günlük hedef"] = aylik_plan_data[select_month] / (work_days / 12)
            aylik_plan_data["kalan hedef"] = aylik_plan_data[select_month]

            # Günlük Planlama
            st.header("Günlük Üretim Planı")
            selected_date = st.date_input("Planlama Tarihi Seçin", value=pd.Timestamp.today())

            # 1. Vardiya Hesaplaması
            moduller_data["1. vardiyada üretim"] = moduller_data["c sütunu"] * moduller_data["d sütunu"]
            moduller_data["kalan üretim"] = moduller_data["c sütunu"] - moduller_data["1. vardiyada üretim"]

            # 2. Vardiya Planlaması
            st.header("2. Vardiya Planı")
            second_shift_plan = []

            for _, modül in moduller_data.iterrows():
                kalan_uretim = modül["kalan üretim"]
                max_operator = modül["b sütunu"]

                # 2. vardiyadaki operatörlerin iş dağılımını hesapla
                if kalan_uretim > 0:
                    operator_time = (kalan_uretim / max_operator) * 60  # dakika cinsinden
                    second_shift_plan.append({
                        "Modül": modül["a sütunu"],
                        "Gerekli Operatör Sayısı": max_operator,
                        "Operatör Başına Çalışma Süresi (dk)": operator_time
                    })

            # 2. vardiya planını göster
            second_shift_df = pd.DataFrame(second_shift_plan)
            st.dataframe(second_shift_df)

    except Exception as e:
        st.error(f"Hata: {e}")

else:
    st.warning("Lütfen kapasite ve FY26 aylık üretim planı dosyalarını yükleyin.")
