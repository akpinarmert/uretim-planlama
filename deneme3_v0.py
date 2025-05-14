import streamlit as st
import pandas as pd

# Başlık
st.title("Üretim Planlama Programı")

# Açıklama
st.write("""
Bu program, üretim planlaması yapmak için iki Excel dosyasını (FY26 Kapasite ve FY26 Plan) okur ve analiz eder.
""")

# Dosya yükleme
st.header("Excel Dosyalarını Yükleyin")

# FY26 Kapasite dosyasını yükleme
uploaded_kapasite = st.file_uploader("FY26 Kapasite dosyasını yükleyin (FPY26 Kapasite.xlsx)", type=["xlsx", "xls"])
if uploaded_kapasite is not None:
    try:
        # "Kapasite" sayfasını oku
        df_kapasite = pd.read_excel(uploaded_kapasite, sheet_name="Kapasite")
        st.success("FY26 Kapasite dosyası başarıyla yüklendi!")
        st.write("Kapasite dosyasının ilk 5 satırı:")
        st.dataframe(df_kapasite.head())

        # Sütun tanımları
        st.subheader("FY26 Kapasite Sütun Tanımları")
        st.write("""
        - **cihaz_kodu**: A sütunu, cihazların kodlarını içerir.
        - **cihaz_tanimi**: B sütunu, cihazların tanımlarını içerir.
        - **yillik_siparis**: C sütunu, yıllık sipariş miktarlarını içerir.
        - **Modüller**: D'den J'ye kadar olan sütunlar, üretim hattındaki modülleri ve kapasitelerini içerir:
            - bireysel_montaj
            - on_ayar_kapama
            - termik_ayar
            - termik_test
            - gruplama__manyetik
            - paketleme
            - muhurleme
        """)

        # Modülleri ve kapasitelerini hesaplama
        st.subheader("Modül Kapasiteleri ve Yıllık Siparişler")
        moduller = [
            "bireysel_montaj",
            "on_ayar_kapama",
            "termik_ayar",
            "termik_test",
            "gruplama__manyetik",
            "paketleme",
            "muhurleme"
        ]

        for modul in moduller:
            if modul in df_kapasite.columns:
                st.write(f"**{modul}** modülündeki kapasite (ilk 5 satır):")
                st.dataframe(df_kapasite[["cihaz_kodu", modul]].head())

    except Exception as e:
        st.error(f"FY26 Kapasite dosyasını okurken bir hata oluştu: {e}")

# FY26 Plan dosyasını yükleme
uploaded_plan = st.file_uploader("FY26 Plan dosyasını yükleyin (FPY26 Plan.xlsx)", type=["xlsx", "xls"])
if uploaded_plan is not None:
    try:
        # FY26 Plan dosyasını oku
        df_plan = pd.read_excel(uploaded_plan)
        st.success("FY26 Plan dosyası başarıyla yüklendi!")
        st.write("Plan dosyasının ilk 5 satırı:")
        st.dataframe(df_plan.head())

        st.subheader("FY26 Plan Sütun Tanımları")
        st.write("""
        - **cihaz_kodu**: Üretilecek cihaz kodu.
        - **Aylık Üretim Planı**: Her cihaz kodu için aylık üretim miktarını içerir.
        """)
    except Exception as e:
        st.error(f"FY26 Plan dosyasını okurken bir hata oluştu: {e}")

# İki dosyanın analiz edilmesi
if uploaded_kapasite is not None and uploaded_plan is not None:
    st.header("Analiz")
    st.write("""
    Yüklenen iki dosya üzerinden analiz yapılacaktır. Bu analiz, cihaz kodlarına göre üretim planlaması
    ve modül kapasitelerinin değerlendirilmesini içerir.
    """)

    try:
        # Verileri birleştirme
        combined_data = pd.merge(
            df_plan,
            df_kapasite,
            on="cihaz_kodu",
            how="inner"
        )

        st.write("Birleştirilmiş veri seti (ilk 5 satır):")
        st.dataframe(combined_data.head())

        # Analiz: Aylık hedef ve kapasite karşılaştırması
        st.subheader("Aylık Hedef ve Kapasite Karşılaştırması")
        for modul in moduller:
            if modul in combined_data.columns:
                combined_data[f"{modul}_ihtiyac"] = combined_data["Aylık Üretim Planı"] / combined_data[modul]
                st.write(f"**{modul}** modülü için ihtiyaç (ilk 5 satır):")
                st.dataframe(combined_data[["cihaz_kodu", "Aylık Üretim Planı", modul, f"{modul}_ihtiyac"]].head())

    except Exception as e:
        st.error(f"Analiz sırasında bir hata oluştu: {e}")
