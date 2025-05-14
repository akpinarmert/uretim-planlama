import streamlit as st
import pandas as pd

# Fonksiyonlar
def load_kapasite_file(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Kapasite")
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
        return df
    except Exception as e:
        st.error(f"FY26 Plan dosyasını okurken bir hata oluştu: {e}")
        return None

def analyze_data(df_plan, df_kapasite, calisma_gunu, vardiyalar):
    try:
        combined_data = pd.merge(df_plan, df_kapasite, on="cihaz_kodu", how="inner")
        
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

        # Modül bazlı analiz sonuçları
        modül_sonuclari = {}

        for index, modul in enumerate(moduller):
            if modul in combined_data.columns:
                # Tip bazlı harcanacak süre (dakika cinsinden)
                combined_data[f"{modul}_sure_dakika"] = combined_data.apply(
                    lambda row: (
                        (row["Eylül 2025"] / row[modul]) * 60
                        if pd.notna(row[modul]) and row[modul] != 0
                        else 0
                    ),
                    axis=1
                )
                
                # Modülün toplam yıllık çalışma kapasitesi (dakika cinsinden)
                toplam_kapasite_dakika = calisma_gunu * vardiyalar[modul] * 8 * 60
                
                # Modülün toplam doluluk oranı
                toplam_harcanan_sure = combined_data[f"{modul}_sure_dakika"].sum()
                doluluk_orani = (toplam_harcanan_sure / toplam_kapasite_dakika) * 100
                
                # Analiz sonuçlarını kaydet
                modül_sonuclari[modul] = {
                    "toplam_harcanan_sure": toplam_harcanan_sure,
                    "toplam_kapasite_dakika": toplam_kapasite_dakika,
                    "doluluk_orani": doluluk_orani
                }
        
        return combined_data, modül_sonuclari
    except Exception as e:
        st.error(f"Analiz sırasında bir hata oluştu: {e}")
        return None, None

# Sayfa başlıkları ve yönlendirme
st.set_page_config(page_title="Üretim Planlama Dashboard", layout="wide")

# Yüklenen dosyaları saklamak için session_state kullanımı
if "df_kapasite" not in st.session_state:
    st.session_state.df_kapasite = None

if "df_plan" not in st.session_state:
    st.session_state.df_plan = None

if "combined_data" not in st.session_state:
    st.session_state.combined_data = None

if "modul_sonuclari" not in st.session_state:
    st.session_state.modul_sonuclari = None

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

    # Çalışma günü ve vardiya bilgileri
    st.sidebar.header("Çalışma Ayarları")
    calisma_gunu = st.sidebar.number_input("Yıllık Çalışma Günü", min_value=1, max_value=365, value=265)
    
    st.sidebar.subheader("Günlük Çalışılabilir Vardiya Sayıları")
    moduller = [
        "bireysel_montaj",
        "on_ayar_kapama",
        "termik_ayar",
        "termik_test",
        "gruplama_manyetik",
        "paketleme",
        "muhurleme"
    ]
    vardiyalar = {}
    for modul in moduller:
        vardiyalar[modul] = st.sidebar.number_input(f"{modul.capitalize()}", min_value=1, max_value=3, value=2 if modul != "muhurleme" else 1)

    # Dosya yükleme alanları
    st.header("Excel Dosyalarını Yükleyin")
    
    uploaded_kapasite = st.file_uploader("FY26 Kapasite dosyasını yükleyin (FPY26 Kapasite.xlsx)", type=["xlsx", "xls"])
    if uploaded_kapasite is not None:
        st.session_state.df_kapasite = load_kapasite_file(uploaded_kapasite)
        if st.session_state.df_kapasite is not None:
            st.write("FY26 Kapasite dosyasının ilk 5 satırı:")
            st.dataframe(st.session_state.df_kapasite.head())
    
    uploaded_plan = st.file_uploader("FY26 Plan dosyasını yükleyin (FPY26 Plan.xlsx)", type=["xlsx", "xls"])
    if uploaded_plan is not None:
        st.session_state.df_plan = load_plan_file(uploaded_plan)
        if st.session_state.df_plan is not None:
            st.write("FY26 Plan dosyasının ilk 5 satırı:")
            st.dataframe(st.session_state.df_plan.head())
    
    # Analiz durumunu kontrol et
    if st.session_state.df_kapasite is not None and st.session_state.df_plan is not None:
        st.session_state.combined_data, st.session_state.modul_sonuclari = analyze_data(
            st.session_state.df_plan, 
            st.session_state.df_kapasite, 
            calisma_gunu, 
            vardiyalar
        )
        st.success("Analiz tamamlandı! 'Analiz' sekmesinden sonuçları görüntüleyebilirsiniz.")

elif page == "Analiz":
    # Analiz ekranı
    st.title("Üretim Planlama Analizi")
    st.subheader("Modül Bazlı Harcanacak Süreler ve Doluluk Oranları")
    
    # Analiz sonuçlarını göster
    if st.session_state.modul_sonuclari is not None:
        for modul, sonuc in st.session_state.modul_sonuclari.items():
            st.subheader(f"{modul.capitalize()} Modülü")
            st.write(f"Toplam Harcanan Süre: {sonuc['toplam_harcanan_sure']:.2f} dakika")
            st.write(f"Toplam Kapasite: {sonuc['toplam_kapasite_dakika']:.2f} dakika")
            st.write(f"Doluluk Oranı: {sonuc['doluluk_orani']:.2f} %")
    else:
        st.warning("Lütfen önce Dashboard ekranından dosyalarınızı yükleyip analiz yapın.")
