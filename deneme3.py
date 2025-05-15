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

def analyze_data(df_plan, df_kapasite, calisma_gunu, vardiyalar, max_operators):
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
                    "doluluk_orani": doluluk_orani,
                    "max_operators": max_operators[modul]
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

if "vardiyalar" not in st.session_state:
    st.session_state.vardiyalar = {
        "bireysel_montaj": 2,
        "on_ayar_kapama": 2,
        "termik_ayar": 2,
        "termik_test": 2,
        "gruplama_manyetik": 2,
        "paketleme": 2,
        "muhurleme": 1
    }

if "max_operators" not in st.session_state:
    st.session_state.max_operators = {
        "bireysel_montaj": 6,
        "on_ayar_kapama": 2,
        "termik_ayar": 1,
        "termik_test": 1,
        "gruplama_manyetik": 1,
        "paketleme": 1,
        "muhurleme": 1
    }

# Sayfa seçimi
st.sidebar.title("Navigasyon")
page = st.sidebar.radio("Sayfa Seçimi", ["Dashboard", "Analiz", "Takvim Tabanlı Planlama"])

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
    
    for modul in moduller:
        st.session_state.vardiyalar[modul] = st.sidebar.number_input(
            f"{modul.capitalize()} Vardiya", min_value=1, max_value=3, value=st.session_state.vardiyalar[modul]
        )
    
    st.sidebar.subheader("Modül Bazlı Maksimum Operatör Sayısı")
    for modul in moduller:
        st.session_state.max_operators[modul] = st.sidebar.number_input(
            f"{modul.capitalize()} Operatör", min_value=1, max_value=10, value=st.session_state.max_operators[modul]
        )

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
            st.session_state.vardiyalar, 
            st.session_state.max_operators
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
            st.write(f"Maksimum Operatör Sayısı: {sonuc['max_operators']}")
    else:
        st.warning("Lütfen önce Dashboard ekranından dosyalarınızı yükleyip analiz yapın.")
# Takvim Tabanlı Planlama
elif page == "Takvim Tabanlı Planlama":
    st.title("Takvim Tabanlı Günlük Üretim Planı")
    
    # Takvim seçim arayüzü
    st.subheader("Bir gün seçin:")
    import datetime
    baslangic_tarihi = datetime.date(2025, 9, 1)  # Eylül 2025 başlangıcı
    bitis_tarihi = datetime.date(2026, 8, 31)    # Ağustos 2026 sonu
    
    selected_date = st.date_input(
        "Gün Seçimi",
        value=baslangic_tarihi,
        min_value=baslangic_tarihi,
        max_value=bitis_tarihi
    )
    
    if selected_date:
        st.write(f"Seçilen Gün: {selected_date}")
        
        # Tarihi aya dönüştürme
        aylar = [
            "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]
        secilen_ay = f"{aylar[selected_date.month - 1]} {selected_date.year}"
        st.write(f"Seçilen ay: {secilen_ay}")
        
        # Plan dosyasından ayı seçme
        if st.session_state.df_plan is not None:
            if secilen_ay in st.session_state.df_plan.columns:
                st.write(f"'{secilen_ay}' sütunundan veriler çekiliyor...")
                
                # Ay verilerini çek
                plan_verileri = st.session_state.df_plan[["cihaz_kodu", secilen_ay]]
                
                # Günlük hedefleri hesapla
                toplam_calisma_gunu = 20  # Örneğin, her ayda 20 gün çalışıyoruz
                plan_verileri["günlük_hedef"] = plan_verileri[secilen_ay] / toplam_calisma_gunu
                
                # Optimizasyon için "cihaz_kodu" ve günlük hedefleri kullan
                from ortools.linear_solver import pywraplp

                # Optimizasyon Modeli
                solver = pywraplp.Solver.CreateSolver('SCIP')
                if not solver:
                    st.error("Optimizasyon kütüphanesi başlatılamadı.")
                
                # Cihaz tipleri ve üretim adetleri
                cihaz_tipleri = plan_verileri["cihaz_kodu"].tolist()
                günlük_hedefler = plan_verileri["günlük_hedef"].tolist()
                
                uretim_miktarlari = {tip: solver.IntVar(0, 1634, f"miktar_{tip}") for tip in cihaz_tipleri}
                
                # Tip değişimlerini kontrol etmek için boolean değişkenler
                # Boolean değişkenler oluştur
                uretiliyor_mu = {tip: solver.BoolVar(f"uretiliyor_mu_{tip}") for tip in cihaz_tipleri}

                # Boolean variables for tip_degisim
                tip_degisim = {tip: solver.BoolVar(f"tip_degisim_{tip}") for tip in cihaz_tipleri}

                for tip in cihaz_tipleri:
                    # Eğer üretim miktarı 1 veya daha büyükse, boolean değişken 1 olmalı
                    solver.Add(uretim_miktarlari[tip] >= 1 - 1634 * (1 - uretiliyor_mu[tip]))
                    solver.Add(uretim_miktarlari[tip] <= 1634 * uretiliyor_mu[tip])

                    # Tip değişikliği kısıtı: Eğer üretim miktarı 1 veya daha büyükse, tip_degisim[tip] değişkeni 1 olmalı
                    solver.Add(uretim_miktarlari[tip] >= 1).OnlyEnforceIf(tip_degisim[tip])
                    solver.Add(uretim_miktarlari[tip] == 0).OnlyEnforceIf(tip_degisim[tip].Not())

                # Amaç fonksiyonu: Tip değişikliklerini minimize et
                solver.Minimize(solver.Sum(tip_degisim[tip] for tip in cihaz_tipleri))  # Tip değişikliklerini minimize et

                # Kısıtlar
                toplam_uretim = solver.Sum(uretim_miktarlari[tip] for tip in cihaz_tipleri)
                solver.Add(toplam_uretim == 1634)  # Günlük toplam hedef
    
                    # Tip değişikliği kısıtı: bir cihaz tipi üretildiyse, "tip_degisim" değişkeni 1 olur
                    # Bu değişken bir BoolVar olduğu için doğruluğunu garanti ediyoruz
                    solver.Add(uretim_miktarlari[tip] >= 1).OnlyEnforceIf(tip_degisim[tip])
                    solver.Add(uretim_miktarlari[tip] == 0).OnlyEnforceIf(tip_degisim[tip].Not())
                
                # Çözümü çalıştır
                status = solver.Solve()
                if status == pywraplp.Solver.OPTIMAL:
                    st.success("Optimizasyon başarıyla tamamlandı!")
                    st.subheader("Günlük Üretim Planı")
                    for tip in cihaz_tipleri:
                        miktar = uretim_miktarlari[tip].solution_value()
                        if miktar > 0:
                            st.write(f"- Cihaz Tipi: {tip} | Adet: {int(miktar)}")
                    toplam_tip_degisim = sum(tip_degisim[tip].solution_value() for tip in cihaz_tipleri)
                    st.write(f"Tip Değişiklik Sayısı: {int(toplam_tip_degisim)}")
                else:
                    st.error("Optimizasyon için uygun bir çözüm bulunamadı.")
            else:
                st.warning(f"'{secilen_ay}' sütunu 'FY26 Plan' dosyasında bulunamadı.")
        else:
            st.warning("Lütfen önce Dashboard ekranından 'FY26 Plan' dosyasını yükleyin.")
