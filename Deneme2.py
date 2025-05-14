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

# Excel dosyasını yükleme
file_path = "FY26 Plan.xlsx"  # Dosya yolu
data = pd.read_excel(file_path, engine='openpyxl')

# Sütunları tanımlama
urun_kodlari = data.iloc[:, 0]  # A sütunu (Ürün kodları)
urun_tanimlari = data.iloc[:, 1]  # B sütunu (Ürün tanımları)
aylik_siparisler = data.iloc[:, 2:14]  # C-N sütunları (Aylık siparişler)

# Aylık siparişlerin temsil ettiği aylar
aylar = [
    "Eylül 2025", "Ekim 2025", "Kasım 2025", "Aralık 2025",
    "Ocak 2026", "Şubat 2026", "Mart 2026", "Nisan 2026",
    "Mayıs 2026", "Haziran 2026", "Temmuz 2026", "Ağustos 2026"
]
aylik_siparisler.columns = aylar

# Verileri kontrol etme
print("Ürün Kodları:")
print(urun_kodlari)

print("\nÜrün Tanımları:")
print(urun)(#)

