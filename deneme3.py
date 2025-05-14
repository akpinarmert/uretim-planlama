import streamlit as st
import pandas as pd

# Fonksiyonlar
def load_kapasite_file(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Kapasite")
        st.success("FY26 Kapasite dosyası başarıyla yüklendi!")
        return df
    except Exception as e:
        st.error(f"FY26 Kapasite dosyasını okurken bir hata oluştu: {e}")
        return None

def load_plan_file(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, usecols="A,C:N")
        df.columns = [
            "cihaz_kodu", "Eylül 2025", "Ekim 2025", "Kasım 2025", "Aralık 2025", "Ocak 2026",
            "Şubat 2026", "Mart 2026", "Nisan 2026", "Mayıs 2026", "Haziran 2026", 
            "Temmuz 2026", "Ağustos 2026"
        ]
        st.success("FY26 Plan dosyası başarıyla yüklendi!")
        return df
    except Exception as e:
        st.error(f"FY26 Plan dosyasını okurken bir hata oluştu: {e}")
        return None

def analyze_data(df_plan, df_kapasite):
    try:
        combined_data = pd.merge(df_plan, df_kapasite, on="cihaz_kodu", how="inner")
        
        # Modül sıralaması ve analiz
        moduller = [
            "bireysel_montaj",
            "on_ayar_kapama",
            "termik_ayar",
            "termik_test",
            "gruplama_manyetik",
            "paketleme",
            "muhurleme"
        ]
        
        for index, modul in enumerate(moduller):
            if modul in combined_data.columns:
                if index == 0:
                    combined_data[f"{modul}_sure_saat"] = combined_data.apply(
                        lambda row: (
                            row["Eylül 2025"] / row[modul]
                            if pd.notna(row[modul]) and row[modul] != 0
                            else "Üretilmiyor"
                        ),
                        axis=1
                    )
                else:
                    onceki_modul = moduller[index - 1]
                    combined_data[f"{modul}_sure_saat"] = combined_data.apply(
                        lambda row: (
                            row[f"{onceki_modul}_sure_saat"] + (row["Eylül 2025"] / row[modul])
                            if pd.notna(row[modul]) and row[modul] != 0 and row[f"{onceki_modul}_sure_saat"] != "Üretilmiyor"
                            else "Üretilmiyor"
                        ),
                        axis=1
                    )
        return combined_data
    except Exception as e:
        st.error(f"Analiz sırasında bir hata oluştu: {e}")
        return None

# Sayfa başlıkları ve yönlendirme
st.set_page_config(page_title="Üretim Planlama Dashboard", layout="wide")

# Sayfa seçimi
st.sidebar.title("Navigasyon")
page = st.sidebar.radio("Sayfa Seçimi", ["Dashboard", "Analiz"])

if page == "Dashboard":
    # Dashboard ekranı
    st.title("Üretim Planlama Dashboard")
    
    # Proje hedefleri
    st.subheader("Projenin Hedefleri")
    st.write("""
    - Tip bazlı minimum tip değişikliği ile optimize edilecek günlük üretim planlarının hazırlanması.
    - 2. vardiya operatör görev dağılımının yapılması.
    - Etkileşimli ve modüler bir üretim planlama arayüzü.
    """)
    
    # Dosya yükleme alanları
    st.header("Excel Dosyalarını Yükleyin")
    uploaded_kapasite = st.file_uploader("FY26 Kapasite dosyasını yükleyin (FPY26 Kapasite.xlsx)", type=["xlsx", "xls"])
    uploaded_plan = st.file_uploader("FY26 Plan dosyasını yükleyin (FPY26 Plan.xlsx)", type=["xlsx", "xls"])
    
elif page == "Analiz":
    # Analiz ekranı
    st.title("Üretim Planlama Analizi")
    st.subheader("Yüklenen Veriler ve Analiz Sonuçları")
    
    # Kapasite dosyasını yükleme ve gösterme
    if 'uploaded_kapasite' in locals() and uploaded_kapasite is not None:
        df_kapasite = load_kapasite_file(uploaded_kapasite)
        if df_kapasite is not None:
            st.write("FY26 Kapasite dosyasının ilk 5 satırı:")
            st.dataframe(df_kapasite.head())
    
    # Plan dosyasını yükleme ve gösterme
    if 'uploaded_plan' in locals() and uploaded_plan is not None:
        df_plan = load_plan_file(uploaded_plan)
        if df_plan is not None:
            st.write("FY26 Plan dosyasının ilk 5 satırı:")
            st.dataframe(df_plan.head())
    
    # Analiz ve sonuçların gösterimi
    if 'df_kapasite' in locals() and 'df_plan' in locals() and df_kapasite is not None and df_plan is not None:
        combined_data = analyze_data(df_plan, df_kapasite)
        if combined_data is not None:
            st.write("Birleştirilmiş veri seti (ilk 5 satır):")
            st.dataframe(combined_data.head())
            
            # Özet bilgiler
            st.subheader("Analiz Özeti")
            st.write("""
            - Tüm süreler saat cinsinden hesaplanmıştır.
            - Boş hücreler "Üretilmiyor" olarak değerlendirilmiştir.
            """)
