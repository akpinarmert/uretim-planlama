import streamlit as st
import pandas as pd

# Başlık
st.title("Üretim Planlama Programı")

# Açıklama
st.write("""
Bu program, üretim planlaması yapmak için iki Excel dosyasını (FY26 Kapasite ve FY26 Plan) okur ve analiz eder. 
Ayrıca modüller arasındaki bağımlılıkları gözetir.
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

    except Exception as e:
        st.error(f"FY26 Plan dosyasını okurken bir hata oluştu: {e}")

# Analiz
if uploaded_kapasite is not None and uploaded_plan is not None:
    st.header("Modül Bağımlılıklarına Göre Üretim Planı Analizi")

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

        # Modül sıralaması
        moduller = [
            "bireysel_montaj",
            "on_ayar_kapama",
            "termik_ayar",
            "termik_test",
            "gruplama__manyetik",
            "paketleme",
            "muhurleme"
        ]

        # Modüller arası bağımlılık kontrolü
        st.subheader("Modüller Arası Bağımlılık")
        st.write("""
        Her modül, kendisinden önceki modülün işlemini tamamlamasını bekler. 
        Bu nedenle, üretim planı modüller arasındaki bu bağımlılıkları gözeterek oluşturulur.
        """)

        # Modüller için sıralı işlem hesaplaması
        for index, modul in enumerate(moduller):
            if modul in combined_data.columns:
                if index == 0:
                    # İlk modül herhangi bir bağımlılığa sahip değil
                    combined_data[f"{modul}_sure"] = combined_data["Aylık Üretim Planı"] / combined_data[modul]
                else:
                    # Sonraki modüller önceki modülün tamamlanmasını bekler
                    onceki_modul = moduller[index - 1]
                    combined_data[f"{modul}_sure"] = (
                        combined_data[f"{onceki_modul}_sure"] + 
                        (combined_data["Aylık Üretim Planı"] / combined_data[modul])
                    )

                st.write(f"**{modul}** modülü için işlem süreleri (ilk 5 satır):")
                st.dataframe(combined_data[["cihaz_kodu", f"{modul}_sure"]].head())

    except Exception as e:
        st.error(f"Analiz sırasında bir hata oluştu: {e}")
