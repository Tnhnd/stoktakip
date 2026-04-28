# 📦 Oto Stok Yönetim Sistemi

Bu proje, otomotiv yedek parça dükkanları için geliştirilmiş, modern arayüzlü bir stok ve borç takip yazılımıdır. 
Python ile geliştirilen uygulama, karmaşık marka/model hiyerarşilerini yönetebilmekte ve güvenli veritabanı yedeği alabilmektedir.

## 🚀 Öne Çıkan Özellikler

* **Dinamik Stok Yönetimi:** Barkod, OEM ve Raf bilgisi ile detaylı parça kaydı.
* **Hiyerarşik Araç Seçimi:** `all.json` dosyası üzerinden Marka -> Model -> Versiyon şeklinde filtrelenmiş seçim sistemi.
* **Cari (Borç) Takibi:** Müşteri bazlı veresiye satış yönetimi ve parça parça tahsilat imkanı.
* **Gelişmiş Raporlama:** Günlük bazda ciro, kâr analizi ve geçmiş işlem dökümleri.
* **İade Yönetimi:** Nakit veya veresiye satışların stoklara otomatik geri dönmesini sağlayan iade modülü.
* **Güvenlik:** SQLite veritabanı için her kapanışta otomatik tarihli yedekleme sistemi.

## 🛠️ Teknik Altyapı

* **Dil:** Python 3.12
* **Arayüz:** CustomTkinter (Modern ve dinamik UI bileşenleri)
* **Veritabanı:** SQLite3
* **Paketleme:** PyInstaller

## 📸 Ekran Görüntüsü

<img width="1919" height="1031" alt="image" src="https://github.com/user-attachments/assets/d57e87e0-8c0a-4407-acd8-f323cb1e6ed9" />


## 🛠️ Kurulum ve Çalıştırma

1. Python 3.12+ yüklü olduğundan emin olun.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install customtkinter darkdetect
