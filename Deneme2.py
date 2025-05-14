import streamlit as st
import pandas as pd

# Streamlit başlığı
st.title("Üretim Planlama - 'FY26 Kapasite' Verileri Yükleme ve İşleme")

# GitHub URL'den dosyayı okuma
file_url = "https://raw.githubusercontent.com/akpinarmert/uretim-planlama/main/FY26%20Kapasite.xlsx"

try:
    # Sheet seçimi
    sheet_name = st.selectbox("Lütfen bir sheet seçin", ["Kapasite"])

    # Excel dosyasını okuma
    data = pd.read_excel(file_url, sheet_name=sheet_name)

    # Sütun adlarını temizleme
    data.columns = (
        data.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("ç", "c")
        .str.replace("ğ", "g")
        .str.replace("ı", "i")
        .str.replace("ö", "o")
        .str.replace("ş", "s")
        .str.replace("ü", "u")
    )

    # Boş hücreleri doldurma (üretim yapılmayan modüller için "0" yazıyoruz)
    data.fillna(0, inplace=True)

    # Temizlenmiş veriyi gösterme
    st.subheader("Temizlenmiş Veri:")
    st.dataframe(data)

    # Veri ile ilgili bilgi
    st.subheader("Veri Bilgisi:")
    st.write(data.describe())

except Exception as e:
    st.error(f"Veri yükleme veya işleme sırasında bir hata oluştu: {e}")

import networkx as nx
import matplotlib.pyplot as plt

# Modüller ve bağımlılıkları
modules = [
    ("Bireysel Montaj", "Ön Ayar ve Kapama"),
    ("Ön Ayar ve Kapama", "Termik Ayar"),
    ("Termik Ayar", "Termik Test"),
    ("Termik Test", "Gruplama ve Manyetik"),
    ("Gruplama ve Manyetik", "Paketleme"),
    ("Paketleme", "Mühürleme"),
]

# Grafik oluşturma
G = nx.DiGraph()  # Yönlü bir grafik (Directed Graph)
G.add_edges_from(modules)

# Grafik görselleştirme
plt.figure(figsize=(10, 6))
nx.draw_networkx(G, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold", arrowsize=20)
plt.title("Üretim Süreci Bağımlılık Zinciri")

# Streamlit'te grafiği göster
st.pyplot(plt)

import pandas as pd

try:
    # Excel dosyasını yükleme
    data = pd.read_excel(file_path, engine='openpyxl')

    # Excel'in boş olup olmadığını kontrol etme
    if data.empty:
        print("Uyarı: Excel dosyası boş!")
    else:
        print("Excel dosyası başarıyla yüklendi ve boş değil.")
        print(data.head())  # İlk 5 satırı göster
except FileNotFoundError:
    print("HATA: Dosya bulunamadı! Lütfen dosya yolunu kontrol edin.")
except Exception as e:
    print(f"HATA: {e}")
# Sütunları tanımlama
cihaz_kodu = data.iloc[:, 0]  # A sütunu (Ürün kodları)
urun_tanimlari = data.iloc[:, 1]  # B sütunu (Ürün tanımları)
aylik_siparisler = data.iloc[:, 2:14]  # C-N sütunları (Aylık siparişler)

# Sütunları tanımlama
cihaz_kodu = data.iloc[:, 0]  # A sütunu
urun_tanimlari = data.iloc[:, 1]  # B sütunu
aylik_siparisler = data.iloc[:, 2:14]  # C-N sütunları (Aylık siparişler)

# Aylık siparişlerin temsil ettiği aylar
aylar = [
    "Eylül 2025", "Ekim 2025", "Kasım 2025", "Aralık 2025",
    "Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026",
    "Mayıs 2026", "Haziran 2026", "Temmuz 2026", "Ağustos 2026"
]

# Kodunuzu buraya ekleyin:
try:
    # Sütun ve aylar uzunluğunu kontrol et
    if len(aylik_siparisler.columns) != len(aylar):
        print("Uyarı: Sütun sayısı ve ay listesi uzunluğu eşleşmiyor.")
        aylar = aylar[:len(aylik_siparisler.columns)]  # Fazlalıkları kırp
        while len(aylar) < len(aylik_siparisler.columns):
            aylar.append(f"Ekstra-{len(aylar)+1}")  # Eksikleri doldur

    # Sütun isimlerini yeniden ata
    aylik_siparisler.columns = aylar
    print("Sütun isimleri başarıyla atandı!")

except ValueError as e:
    print(f"Hata: {e}")

# Verileri kontrol etme (isteğe bağlı)
print(aylik_siparisler.head())  # Güncellenmiş DataFrame'i kontrol edin
