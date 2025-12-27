import streamlit as st
import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Enerji Analiz Platformu", layout="wide")

st.title("⚡ Türkiye Enerji Piyasası Analiz Platformu")
st.markdown("Bu proje, **gerçek zamanlı üretim ve tüketim verilerini** analiz ederek enerji farkındalığı oluşturmak amacıyla geliştirilmiştir.")

# --- 1. VERİ YÜKLEME VE TEMİZLEME FONKSİYONU ---
# @st.cache_data dekoratörü, veriyi her seferinde tekrar yüklemesini engeller, hızı artırır.
@st.cache_data
def verileri_yukle():
    dosya_yolu = "data/"
    params = {'sep': ';', 'decimal': ',', 'encoding': 'utf-8'}
    
    # ÜRETİM VERİLERİ
    dosyalar_uretim = glob.glob(os.path.join(dosya_yolu, "Gercek_Zamanli_Uretim*.csv"))
    dfs = [pd.read_csv(f, **params) for f in dosyalar_uretim]
    df_uretim = pd.concat(dfs, ignore_index=True)
    df_uretim['TarihSaat'] = pd.to_datetime(df_uretim['Tarih'] + ' ' + df_uretim['Saat'], format='%d.%m.%Y %H:%M')
    
    # TÜKETİM VERİLERİ
    dosyalar_tuketim = glob.glob(os.path.join(dosya_yolu, "*Gercek_Zamanli_Tuketim*.csv"))
    dfs_t = [pd.read_csv(f, **params) for f in dosyalar_tuketim]
    df_tuketim = pd.concat(dfs_t, ignore_index=True)
    
    # Sütun adı düzeltme ve birleştirme hazırlığı
    df_tuketim['TarihSaat'] = pd.to_datetime(df_tuketim['Tarih'] + ' ' + df_tuketim['Saat'], format='%d.%m.%Y %H:%M')
    
    # Tüketim verisi temizliği (String -> Float dönüşümü)
    col_tuketim = 'Tüketim' if 'Tüketim' in df_tuketim.columns else df_tuketim.columns[2]
    df_tuketim = df_tuketim.rename(columns={col_tuketim: 'Tuketim'})
    
    df_tuketim['Tuketim'] = df_tuketim['Tuketim'].astype(str)
    df_tuketim['Tuketim'] = df_tuketim['Tuketim'].str.replace('.', '', regex=False)
    df_tuketim['Tuketim'] = df_tuketim['Tuketim'].str.replace(',', '.')
    df_tuketim['Tuketim'] = pd.to_numeric(df_tuketim['Tuketim'])
    
    # BİRLEŞTİRME
    df_final = pd.merge(df_uretim, df_tuketim[['TarihSaat', 'Tuketim']], on='TarihSaat', how='inner')
    df_final = df_final.sort_values('TarihSaat').drop_duplicates(subset=['TarihSaat'])
    
    return df_final

# Verileri yükle (Ekrana 'Yükleniyor...' yazar)
with st.spinner('Veriler EPİAŞ kaynaklarından yükleniyor...'):
    df = verileri_yukle()

# --- 2. YAN MENÜ (SIDEBAR) ---
st.sidebar.header("Filtreleme Seçenekleri")

# Tarih Seçimi
min_date = df['TarihSaat'].min().date()
max_date = df['TarihSaat'].max().date()

baslangic_tarihi = st.sidebar.date_input("Başlangıç Tarihi", min_date)
bitis_tarihi = st.sidebar.date_input("Bitiş Tarihi", min_date + pd.Timedelta(days=7)) # Varsayılan 1 hafta

# Kaynak Seçimi
tum_kaynaklar = ['Doğal Gaz', 'Barajlı', 'Linyit', 'Rüzgar', 'Güneş', 'İthal Kömür', 'Jeotermal']
secilen_kaynaklar = st.sidebar.multiselect("Grafikte Gösterilecek Kaynaklar", tum_kaynaklar, default=['Doğal Gaz', 'Barajlı', 'Rüzgar', 'Güneş'])

# --- 3. FİLTRELEME VE AKILLI ÖRNEKLEME (RESAMPLING) ---
maske = (df['TarihSaat'].dt.date >= baslangic_tarihi) & (df['TarihSaat'].dt.date <= bitis_tarihi)
df_filtered = df.loc[maske].copy() # Kopyasını alıyoruz ki orjinali bozulmasın

# Tarih aralığını hesapla
gun_farki = (bitis_tarihi - baslangic_tarihi).days + 1

grafik_basligi = ""

# Eğer 30 günden fazla veri seçildiyse SAATLİK yerine GÜNLÜK ORTALAMA al
if gun_farki > 30:
    st.info(f"📅 Seçilen aralık geniş ({gun_farki} gün). Grafik daha anlaşılır olsun diye **Günlük Ortalamalar** gösteriliyor.")
    # Veriyi gün bazında (D) tekrar örnekle ve ortalamasını al
    df_chart = df_filtered.set_index('TarihSaat').resample('D').mean(numeric_only=True).reset_index()
    grafik_basligi = "Günlük Ortalama"
else:
    st.success(f"📅 Seçilen aralık kısa ({gun_farki} gün). **Saatlik Detaylı Veriler** gösteriliyor.")
    df_chart = df_filtered
    grafik_basligi = "Saatlik"

# --- 4. GRAFİK ÇİZİMİ ---
st.subheader(f"📊 {baslangic_tarihi} - {bitis_tarihi} Arası {grafik_basligi} Analiz")

if not df_chart.empty:
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Renk paleti
    renk_map = {'Doğal Gaz': 'gray', 'Barajlı': 'blue', 'Linyit': 'black', 'Rüzgar': 'green', 'Güneş': 'orange', 'İthal Kömür': 'brown', 'Jeotermal': 'purple'}
    secilen_renkler = [renk_map.get(k, 'gray') for k in secilen_kaynaklar]

    # Stackplot
    ax.stackplot(df_chart['TarihSaat'], 
                 [df_chart[k] for k in secilen_kaynaklar],
                 labels=secilen_kaynaklar,
                 colors=secilen_renkler,
                 alpha=0.8)
    
    # Tüketim Çizgisi
    ax.plot(df_chart['TarihSaat'], df_chart['Tuketim'], color='red', linewidth=2, linestyle='--', label='TOPLAM TÜKETİM')
    
# --- EKSEN AYARI ---
    
    if gun_farki <= 1:
        # Her 2 saatte bir yaz (02:00, 04:00, 06:00...)
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
    elif gun_farki <= 10:
        # Her 6 saatte bir yaz (Sabah, Öğlen, Akşam)
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
        
    elif gun_farki <= 40:
        # Sadece günleri yaz (01.01, 02.01, 03.01...)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        
    else:
        # 5 günde bir tarih at (Grafik boğulmasın)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))

    ax.set_ylabel("MWh (Ortalama)")
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Yazıların birbirine girmemesi için 90 derece dik yazdıralım
    plt.xticks(rotation=90, fontsize=10) 
    
    st.pyplot(fig)
    
    # --- 5. İSTATİSTİKLER ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Tüketim", f"{df_filtered['Tuketim'].sum():,.0f} MWh")
    
    gunes_payi = (df_filtered['Güneş'].sum() / df_filtered['Toplam'].sum()) * 100
    col2.metric("Güneş Enerjisi Payı", f"%{gunes_payi:.2f}")
    
    ruzgar_payi = (df_filtered['Rüzgar'].sum() / df_filtered['Toplam'].sum()) * 100
    col3.metric("Rüzgar Enerjisi Payı", f"%{ruzgar_payi:.2f}")

# --- 5.1 GELİŞMİŞ SOSYAL SORUMLULUK VE SAATLİK ANALİZ MODÜLÜ ---
    st.markdown("---")
    st.subheader("🌍 Akıllı Enerji Asistanı: Ne Zaman Tüketmeli?")
    
    # 1. ADIM: Saatlik Verimliliği Hesapla
    # Veriyi saatlere göre grupla (00:00'dan 23:00'a kadar ortalamaları al)
    df_filtered['Saat'] = df_filtered['TarihSaat'].dt.hour
    
    # Temiz kaynakların toplamı (Barajlı + Rüzgar + Güneş + Jeotermal)
    # Not: Veri setinde sütun adları tam eşleşmeli, hata alırsan kontrol et
    temiz_kaynaklar = ['Güneş', 'Rüzgar', 'Barajlı', 'Jeotermal']
    mevcut_temizler = [k for k in temiz_kaynaklar if k in df_filtered.columns]
    
    df_filtered['Temiz_Uretim'] = df_filtered[mevcut_temizler].sum(axis=1)
    df_filtered['Temiz_Payi'] = (df_filtered['Temiz_Uretim'] / df_filtered['Toplam']) * 100
    
    # Her saatin ortalama temiz enerji payını bul
    saatlik_ozet = df_filtered.groupby('Saat')['Temiz_Payi'].mean()
    
    # En verimli saati bul
    en_iyi_saat = saatlik_ozet.idxmax()
    en_yuksek_pay = saatlik_ozet.max()
    
# 2. ADIM: Durum Kartı (Dinamik ve Hatasız)
    col_karnesi, col_grafik = st.columns([1, 2])
    
    with col_karnesi:
        # Başlık Mantığı: Tek günse "Bugün", çok günse "Genel Ortalamaya Göre" diyelim
        baslik_prefix = "Günün" if gun_farki <= 1 else "Bu Dönemin Ortalama"
        st.info(f"🕒 **{baslik_prefix} En Temiz Saati:** {en_iyi_saat}:00")
        
        # HATA DÜZELTME: Aşağıdaki satırlara 'f' harfi eklendi, artık {en_iyi_saat} düzgün çalışacak.
        if en_yuksek_pay > 60:
            st.success(f"✅ **Durum: MÜKEMMEL**\n\nEnerjimizin çoğu yenilenebilir kaynaklardan! Tüketimi **{en_iyi_saat}:00** civarına denk getirmek harika olur.")
        elif en_yuksek_pay > 40:
            st.warning(f"⚠️ **Durum: ORTA**\n\nFosil yakıtlar devrede ama temiz enerji de var. Tüketimi **{en_iyi_saat}:00** civarına kaydırın.")
        else:
            st.error(f"⛔ **Durum: KRİTİK**\n\nSistem fosil yakıt ağırlıklı çalışıyor. **{en_iyi_saat}:00** saati, kötünün iyisi diyebileceğimiz tek zaman.")
            
        st.metric("Temiz Enerji Payı (Ortalama)", f"%{en_yuksek_pay:.1f}")
        
        # Çoklu gün seçimi için ek açıklama
        if gun_farki > 1:
            st.caption(f"ℹ️ Not: Seçilen {gun_farki} günün genel ortalamasına bakılarak, **alışkanlık oluşturmanız** için en uygun saat önerilmiştir.")

    # 3. ADIM: Saatlik Verimlilik Grafiği (Bar Chart)
    with col_grafik:
        st.write("📊 **Günün Saatlerine Göre Temiz Enerji Oranı**")
        
        # Renkli Bar Chart Oluşturma
        fig_bar, ax_bar = plt.subplots(figsize=(10, 4))
        
        # Renkleri değere göre ayarla (Yeşil > Sarı > Kırmızı)
        renkler = ['#ff4b4b' if x < 30 else '#ffa500' if x < 50 else '#4caf50' for x in saatlik_ozet.values]
        
        bars = ax_bar.bar(saatlik_ozet.index, saatlik_ozet.values, color=renkler)
        
        ax_bar.set_xlabel("Saat (00:00 - 23:00)")
        ax_bar.set_ylabel("Temiz Enerji Payı (%)")
        ax_bar.set_xticks(range(0, 24, 2)) # 2 saatte bir yaz
        ax_bar.grid(axis='y', alpha=0.3)
        
        # Ortalamayı çizgi olarak ekle
        ortalama_hat = saatlik_ozet.mean()
        ax_bar.axhline(ortalama_hat, color='gray', linestyle='--', linewidth=1, label=f'Ortalama (%{ortalama_hat:.1f})')
        ax_bar.legend()
        
        st.pyplot(fig_bar)

    # 4. ADIM: Detaylı Açıklama
    with st.expander("ℹ️ Bu Grafik Ne Anlatıyor?"):
        st.write("""
        **Yeşil Çubuklar:** Elektriğin en temiz olduğu saatlerdir. Çamaşır, bulaşık, ütü gibi işlerinizi bu saatlere denk getirirseniz doğayı korursunuz.
        **Kırmızı Çubuklar:** Doğalgaz ve Kömür kullanımının arttığı saatlerdir. Tasarruf yapılması gereken zamanlardır.
        """)

# --- 6. HAM VERİ GÖSTERİMİ ---
if st.checkbox("Ham Verileri Göster"):
    st.dataframe(df_filtered)