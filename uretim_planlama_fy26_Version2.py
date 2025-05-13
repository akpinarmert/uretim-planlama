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
        moduller_data = pd.read_excel(kapasite_file, sheet_name="Modüller")

        # Sütun başlıklarını normalize et
        moduller_data.columns = (
            moduller_data.columns.str.strip()  # Başındaki/sonundaki boşlukları kaldır
            .str.replace("\xa0", " ")  # Görünmez boşluk karakterlerini normal boşlukla değiştir
            .str.lower()  # Küçük harfe çevir
            .str.replace(" ", "_")  # Boşlukları alt çizgiyle değiştir
            .str.replace("ç", "c")
            .str.replace("ğ", "g")
            .str.replace("ı", "i")
            .str.replace("ö", "o")
            .str.replace("ş", "s")
            .str.replace("ü", "u")
        )
        
        # Beklenen sütun başlıklarını kontrol et
        expected_columns = [
            "moduller", 
            "calisabilir_operator_sayisi", 
            "yillik_calisma_gunu", 
            "gunluk_istenen_uretim_(pol)", 
            "calisabilir_vardiya_sayisi"
        ]
        missing_columns = [col for col in expected_columns if col not in moduller_data.columns]
        
        if missing_columns:
            st.error(f"Excel dosyasındaki sütun başlıkları beklenen formatta değil. Eksik sütunlar: {missing_columns}")
        else:
            st.success("Excel dosyası başarıyla yüklendi ve sütun başlıkları doğrulandı.")
            
            # Modüller ve üretim hedeflerini göster
            st.subheader("Modüller ve Üretim Hedefleri")
            st.dataframe(moduller_data)

            # 2. vardiya planını oluştur
            st.subheader("2. Vardiya Planı")
            second_shift_plan = []

            for _, modül in moduller_data.iterrows():
                max_operator = modül["calisabilir_operator_sayisi"]
                daily_goal = modül["gunluk_istenen_uretim_(pol)"]
                shifts_available = modül["calisabilir_vardiya_sayisi"]
                
                # 2. vardiyada yapılacak üretim miktarını hesapla
                if shifts_available > 1:  # En az 2 vardiya çalışabilen modüller
                    second_shift_goal = daily_goal / shifts_available
                    operator_time = (second_shift_goal / max_operator) * 60  # dakika cinsinden
                    second_shift_plan.append({
                        "Modül": modül["moduller"],
                        "Gerekli Operatör Sayısı": max_operator,
                        "2. Vardiya Üretim Hedefi": second_shift_goal,
                        "Operatör Başına Çalışma Süresi (dk)": operator_time
                    })

            # 2. vardiya planını göster
            second_shift_df = pd.DataFrame(second_shift_plan)
            st.dataframe(second_shift_df)

    except Exception as e:
        st.error(f"Hata: {e}")

else:
    st.warning("Lütfen kapasite ve FY26 aylık üretim planı dosyalarını yükleyin.")
