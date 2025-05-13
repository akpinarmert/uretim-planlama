import streamlit as st
import pandas as pd


# Veri yükleme ve sütun başlıklarını temizleme
def load_and_clean_data(file_path, sheet_name):
    try:
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        data.columns = (
            data.columns.str.strip()
            .str.replace("\xa0", " ")
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("ç", "c")
            .str.replace("ğ", "g")
            .str.replace("ı", "i")
            .str.replace("ö", "o")
            .str.replace("ş", "s")
            .str.replace("ü", "u")
        )
        return data
    except Exception as e:
        st.error(f"Veri yükleme hatası: {e}")
        return None


# Aylık üretim planını hesaplama
def calculate_monthly_plan(plan_data, selected_month, work_days):
    try:
        if selected_month not in plan_data.columns:
            st.error(f"Seçilen ay ({selected_month}) bulunamadı.")
            return None
        plan_data["gunluk_hedef"] = plan_data[selected_month] / (work_days / 12)
        plan_data["kalan_hedef"] = plan_data[selected_month]
        return plan_data
    except Exception as e:
        st.error(f"Aylık planlama hatası: {e}")
        return None


# Günlük üretim planını oluşturma
def generate_daily_plan(plan_data, daily_target, tip_degisim_suresi):
    daily_plan = []
    remaining_target = daily_target
    sorted_products = plan_data.sort_values(by="kalan_hedef", ascending=False)

    last_product_type = None
    total_changeover_time = 0

    for _, row in sorted_products.iterrows():
        if remaining_target <= 0:
            break

        cihaz_kodu = row["urun_kodu"]
        cihaz_tanimi = row["urun_tanimi"]
        kalan_hedef = row["kalan_hedef"]

        if kalan_hedef <= 0:
            continue

        # Tip değişikliği kontrolü
        if last_product_type and last_product_type != cihaz_kodu:
            total_changeover_time += tip_degisim_suresi

        # Üretim miktarını hesapla
        produce_count = min(remaining_target, kalan_hedef)
        remaining_target -= produce_count
        plan_data.loc[_, "kalan_hedef"] -= produce_count

        daily_plan.append({
            "Ürün Kodu": cihaz_kodu,
            "Ürün Tanımı": cihaz_tanimi,
            "Üretim Miktarı": produce_count
        })

        last_product_type = cihaz_kodu

    return pd.DataFrame(daily_plan), total_changeover_time


# 2. vardiya planını oluşturma
def generate_second_shift_plan(moduller_data):
    second_shift_plan = []

    for _, modül in moduller_data.iterrows():
        max_operator = modül["calisabilir_operator_sayisi"]
        daily_goal = modül["gunluk_istenen_uretim_(pol)"]
        shifts_available = modül["calisabilir_vardiya_sayisi"]

        if shifts_available > 1:
            second_shift_goal = daily_goal / shifts_available
            operator_time = (second_shift_goal / max_operator) * 60  # dakika cinsinden
            second_shift_plan.append({
                "Modül": modül["moduller"],
                "Gerekli Operatör Sayısı": max_operator,
                "2. Vardiya Üretim Hedefi": second_shift_goal,
                "Operatör Başına Çalışma Süresi (dk)": operator_time,
            })

    return pd.DataFrame(second_shift_plan)


# Ana uygulama fonksiyonu
def main():
    # Başlık
    st.title("FY26 Üretim Planlama ve Tip Değişikliği Optimizasyonu")

    # Dosya yükleme
    kapasite_file = st.file_uploader("Kapasite Excel Dosyasını Yükleyin", type=["xlsx"])
    aylik_plan_file = st.file_uploader("FY26 Aylık Üretim Planı Excel Dosyasını Yükleyin", type=["xlsx"])

    if kapasite_file and aylik_plan_file:
        # Veri yükleme
        moduller_data = load_and_clean_data(kapasite_file, "Modüller")
        aylik_plan_data = load_and_clean_data(aylik_plan_file, "FY26 Plan")

        if moduller_data is not None and aylik_plan_data is not None:
            # Çalışma günü
            work_days = st.sidebar.number_input("Yıllık Çalışma Günü", min_value=1, max_value=365, value=265)

            # Aylık planlama
            st.sidebar.header("FY26 Ay Seçimi")
            select_month = st.sidebar.selectbox("Planlama Yapılacak Ayı Seçin", aylik_plan_data.columns)
            aylik_plan_data = calculate_monthly_plan(aylik_plan_data, select_month, work_days)

            if aylik_plan_data is not None:
                st.subheader(f"{select_month.capitalize()} Aylık Üretim Planı")
                st.dataframe(aylik_plan_data)

                # Günlük planlama
                daily_target = 1634
                tip_degisim_suresi = 5
                daily_plan, total_changeover_time = generate_daily_plan(aylik_plan_data, daily_target, tip_degisim_suresi)
                st.subheader("Günlük Üretim Planı ve Tip Değişikliği Süresi")
                st.dataframe(daily_plan)
                st.text(f"Toplam Tip Değişikliği Süresi: {total_changeover_time} dakika")

                # 2. vardiya planı
                second_shift_plan = generate_second_shift_plan(moduller_data)
                st.subheader("2. Vardiya Planı")
                st.dataframe(second_shift_plan)


if __name__ == "__main__":
    main()
