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

# FY26 Plan dosyasını yükleme
import streamlit as st
import pandas as pd

# Dosya yükleme
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
        st.error(f"FY26 Plan dosyasını işlerken bir hata oluştu: {e}")
        # Veri analizi: Hangi cihaz kodundan hangi ayda kaç adet üretilmesi gerektiği
        st.subheader("Aylık Üretim Planı")
        for ay in df_plan.columns[1:]:  # Ay sütunları
            st.write(f"**{ay}** için üretim planı:")
            st.dataframe(df_plan[["cihaz_kodu", ay]].sort_values(by=ay, ascending=False).reset_index(drop=True))

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
                    combined_data[f"{modul}_sure"] = combined_data["Eylül 2025"] / combined_data[modul]
                else:
                    # Sonraki modüller önceki modülün tamamlanmasını bekler
                    onceki_modul = moduller[index - 1]
                    combined_data[f"{modul}_sure"] = (
                        combined_data[f"{onceki_modul}_sure"] + 
                        (combined_data["Eylül 2025"] / combined_data[modul])
                    )

                st.write(f"**{modul}** modülü için işlem süreleri (ilk 5 satır):")
                st.dataframe(combined_data[["cihaz_kodu", f"{modul}_sure"]].head())

    except Exception as e:
        st.error(f"Analiz sırasında bir hata oluştu: {e}")
