import streamlit as st
import pandas as pd

# Başlık
st.title("Üretim Planlama Programı")

# Açıklama
st.write("""
Bu program, üretim planlaması yapmak için iki Excel dosyasını (FY26 Kapasite ve FY26 Plan) okur ve analiz eder. 
Ayrıca modüller arasındaki bağımlılıkları gözetir ve boş hücreleri "üretilmiyor" olarak değerlendirir.
Süreler saat cinsinden hesaplanmıştır.
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
        # Plan dosyasını oku ve ilgili sütunları seç
        df_plan = pd.read_excel(uploaded_plan, usecols="A,C:N")
        st.success("FY26 Plan dosyası başarıyla yüklendi!")
        
        # Sütun adlarını güncelle
        df_plan.columns = [
            "cihaz_kodu", "Eylül 2025", "Ekim 2025", "Kasım 2025", "Aralık 2025", "Ocak 2026",
            "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026", "Haziran 2026", 
            "Temmuz 2026", "Ağustos 2026"
        ]

        # Plan dosyasını yazdır
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
            "gruplama_manyetik",
            "paketleme",
            "muhurleme"
        ]

        # Modüller arası bağımlılık kontrolü
        st.subheader("Modüller Arası Bağımlılık ve Boş Hücrelerin Dikkate Alınması")
        st.write("""
        Her modül, kendisinden önceki modülün işlemini tamamlamasını bekler. Boş hücreler, ilgili cihazın o modülde üretilmeyeceğini ifade eder.
        Tüm süreler saat cinsinden hesaplanmıştır.
        """)

        # Modüller için sıralı işlem hesaplaması
        for index, modul in enumerate(moduller):
            if modul in combined_data.columns:
                if index == 0:
                    # İlk modül herhangi bir bağımlılığa sahip değil
                    combined_data[f"{modul}_sure_saat"] = combined_data.apply(
                        lambda row: (
                            row["Eylül 2025"] / row[modul]
                            if pd.notna(row[modul]) and row[modul] != 0
                            else "Üretilmiyor"
                        ),
                        axis=1
                    )
                else:
                    # Sonraki modüller önceki modülün tamamlanmasını bekler ve boş hücreleri atlar
                    onceki_modul = moduller[index - 1]
                    combined_data[f"{modul}_sure_saat"] = combined_data.apply(
                        lambda row: (
                            row[f"{onceki_modul}_sure_saat"] + (row["Eylül 2025"] / row[modul])
                            if pd.notna(row[modul]) and row[modul] != 0 and row[f"{onceki_modul}_sure_saat"] != "Üretilmiyor"
                            else "Üretilmiyor"
                        ),
                        axis=1
                    )

                # Sonuçları yazdır
                st.write(f"**{modul}** modülü için işlem süreleri (saat cinsinden) (ilk 5 satır):")
                st.dataframe(combined_data[["cihaz_kodu", f"{modul}_sure_saat"]].head())

    except Exception as e:
        st.error(f"Analiz sırasında bir hata oluştu: {e}")
