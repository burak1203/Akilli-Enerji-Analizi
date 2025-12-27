# ⚡ Türkiye Enerji Piyasası Analiz Platformu & Akıllı Enerji Asistanı

<img width="1918" height="917" alt="1" src="https://github.com/user-attachments/assets/4d35acdd-3ed6-41ed-8243-d83406a16b34" />


> **"Veriyi sadece analiz etme, eyleme dönüştür."**

Bu proje, Türkiye'nin gerçek zamanlı elektrik üretim ve tüketim verilerini analiz ederek, kullanıcılara **en çevreci ve ekonomik elektrik tüketim saatlerini** öneren bir veri bilimi ve sosyal sorumluluk platformudur. Python ve Streamlit kullanılarak geliştirilmiştir.

## 🎯 Projenin Amacı
Enerji tüketiminin yoğun olduğu saatlerde fosil yakıt (Doğalgaz, Kömür) kullanımı artmaktadır. Bu proje:
1.  **EPİAŞ** verilerini kullanarak üretim kaynaklarını analiz eder.
2.  Yenilenebilir enerji (Güneş, Rüzgar) oranının en yüksek olduğu saatleri tespit eder.
3.  Kullanıcıya **"Çamaşır makinesini şimdi çalıştır"** veya **"Akşamı bekle"** gibi somut öneriler sunarak karbon ayak izini düşürmeyi hedefler (Demand Side Management).

## 📊 Temel Özellikler

### 1. Dinamik Veri Görselleştirme
Kullanıcılar istedikleri tarih aralığını seçerek Türkiye'nin enerji üretim profilini inceleyebilir. Üretim kaynakları (Doğalgaz, Barajlı, Rüzgar, Güneş vb.) ve Tüketim eğrisi (Kırmızı Çizgi) üst üste bindirilerek arz-talep dengesi gösterilir.

<img width="1918" height="907" alt="2" src="https://github.com/user-attachments/assets/7b2d1bf1-5586-4c68-8356-8986899bc2ad" />

### 2. Akıllı Enerji Asistanı (Smart Assistant)
Projenin en yenilikçi kısmı olan bu modül, seçilen tarih aralığındaki verileri işleyerek **"Günün En Temiz Saatini"** hesaplar.
* **Algoritma:** Güneş, Rüzgar, Barajlı ve Jeotermal kaynakların toplam üretime oranını saatlik bazda hesaplar.
* **Sosyal Sorumluluk:** Kullanıcıya "Durum: KRİTİK" veya "Durum: MÜKEMMEL" şeklinde geri bildirim vererek davranış değişikliği yaratır.

<img width="1918" height="915" alt="3" src="https://github.com/user-attachments/assets/aa201a36-0297-496d-823f-6047d40f7537" />


### 3. Detaylı Veri İnceleme
Şeffaflık ilkesi gereği, analizde kullanılan ham veriler filtrelenmiş bir tablo halinde sunulur.

<img width="1918" height="905" alt="4" src="https://github.com/user-attachments/assets/bd5eb603-1213-4b4a-9e47-739c70de287b" />


---

## 🛠️ Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

### Gereksinimler
* Python 3.8 veya üzeri
* Git

### 1. Projeyi Klonlayın
```bash
git clone [https://github.com/burak1203/Akilli-Enerji-Analizi.git](https://github.com/burak1203/Akilli-Enerji-Analizi.git)
cd Akilli-Enerji-Analizi
```
### Adım 2: Gerekli Kütüphaneleri Yükleyin
Projenin çalışması için gerekli olan `pandas`, `streamlit`, `matplotlib` gibi kütüphaneleri tek komutla yükleyin:

```bash
pip install -r requirements.txt
```
### Adım 3: Uygulamayı Başlatın
Kurulum tamamlandıktan sonra Streamlit arayüzünü başlatmak için şu komutu çalıştırın:

```bash
streamlit run app.py
```
Bu komutu yazdıktan sonra tarayıcınız otomatik olarak açılacak ve uygulama şu adreste çalışacaktır: 👉 http://localhost:8501

### Kullanılan Teknolojiler
* **Python**
* **Streamlit**
* **Pandas**
* **Matplotlib** & **Seaborn**

### 📁 Proje Klasör Yapısı
* ├── data/                  # Ham CSV dosyaları (EPİAŞ verileri burada bulunur)
* ├── app.py                 # Ana uygulama dosyası (Kaynak kodlar)
* ├── requirements.txt       # Kütüphane bağımlılıkları
* └── README.md              # Proje dökümantasyonu
