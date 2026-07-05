# 🌐 NiNA Translate v 0.1

**Masaüstü ve Mobil uyumlu, harici bağımlılığı olmayan, gerçek zamanlı simultane çeviri uygulaması.**  
Mikrofon yardımıyla konuşmalarınızı dinler, anlık olarak yazıya döker, hedef dile çevirir ve sesli olarak okur.

---

## 🚀 Öne Çıkan Özellikler

* **📦 Sıfır Harici Bağımlılık (Zero Dependencies):** Flask veya harici Python kütüphanelerine ihtiyaç duymaz. Sadece standart Python kütüphaneleriyle çalışır.
* **🎙️ Gerçek Zamanlı Ses Karakteri Tespiti:** Mikrofon girişinden alınan ses perdesi (pitch) frekansını arka planda analiz ederek konuşanın **Erkek 🧑, Kadın 👩 veya Çocuk 🧒** olduğunu otomatik tespit eder.
* **🔊 Uyarlamalı Seslendirme (TTS):** Algılanan ses türüne göre seslendirmenin tonu (pitch) ve hızı (rate) otomatik ayarlanır (çocuk için yüksek ve canlı ton, erkek için daha kalın ton).
* **🎨 UI Ses Rozeti:** Arayüzde anlık olarak tespit edilen ses tipini gösteren şık, dinamik bir bildirim rozeti yer alır.
* **🌍 Çift Yönlü Dil Değiştirme:** Kaynak ve hedef diller arasındaki geçiş butonu (değiştirme tuşu) ile diller tek tıkla yer değiştirir.
* **📱 Mobil Erişim ve QR Kod:** Masaüstünde oluşturulan `Mobil-Çeviri-Bağlantısı.html` içerisindeki QR kod ile telefonunuzdan anında erişim sağlayabilirsiniz.
* **🔊 Mobil Uyumlu Sesli Okuma (TTS):** Mobil tarayıcılardaki ses engelleme politikalarını aşan ve iOS Safari kilitlenmelerini önleyen özel korumalı ses motoru.
* **🎨 Premium Arayüz ve Akıcı Animasyonlar:** HSL renk paletleri, parıldayan dinamik logo animasyonu, mikro etkileşimler ve durum bildirimleri içeren modern bir tasarıma sahiptir.
* **🎛️ Geniş Dil Desteği:** Türkçe, İngilizce, Almanca, Fransızca, İspanyolca, İtalyanca ve daha birçok dil arasında anlık çeviri seçeneği sunar.

---

## 📁 Proje Klasör Yapısı

```text
NiNA Translate v 0.1/
├── app.py                     ← Python backend (Gömülü HTTP Sunucusu + HTML/CSS/JS)
├── README.md                  ← Bu doküman (Kullanım kılavuzu)
├── start.bat                  ← Sunucuyu ve HTTPS tünelini başlatan ana betik
├── baslat.vbs                 ← start.bat'ı arka planda CMD penceresiz başlatan dosya
├── durdur.bat                 ← Sunucuyu ve SSH tünelini sonlandıran temizlik betiği
├── nina_red.ico               ← Uygulamanın kırmızı renkli simgesi (Kısayollar için)
├── python_run.log             ← Python sunucusunun çalışma günlükleri
├── tunnel.log                 ← localhost.run tünel günlükleri (Mobil bağlantı adresi buradadır)
└── tunnel.err                 ← Tünel hata günlükleri
```

---

## ⚙️ Kurulum ve Çalıştırma

Uygulamayı çalıştırmak için herhangi bir kurulum veya paket yüklemesi yapmanıza gerek yoktur. Bilgisayarınızda **Python 3** kurulu olması yeterlidir.

### 1. Başlatma
* Proje klasöründeki **`baslat.vbs`** dosyasına çift tıklayın.
* Arka planda çalışan eski işlemler otomatik olarak kapatılır, yeni sunucu ve HTTPS tüneli penceresiz (tamamen gizli) olarak başlatılır.
* Mobil erişim için masaüstünüzde otomatik olarak **`Mobil-Çeviri-Bağlantısı.html`** dosyası oluşturulacak ve tarayıcınızda açılacaktır.

### 2. Mobil Bağlantı
* Masaüstünüzde açılan veya oluşturulan dosyadaki **QR Kodu** telefonunuzun kamerasıyla taratarak uygulamayı telefonunuzda kullanmaya başlayabilirsiniz.
* Arayüz içerisindeki **"📱 Mobil"** butonuna tıklayarak da QR koda istediğiniz an ulaşabilirsiniz.

### 3. Durdurma
* Uygulamadan çıkmak istediğinizde klasördeki **`durdur.bat`** dosyasına çift tıklamanız yeterlidir.
* Tüm arka plan süreçleri temizlenir ve masaüstündeki geçici HTML dosyası otomatik olarak silinir.

---

## 🖥️ Tarayıcı Desteği ve Öneriler

> [!TIP]
> Çevirinin en yüksek doğrulukla yapılabilmesi için tarayıcı olarak **Google Chrome** veya **Microsoft Edge** kullanılması önerilir. Bu tarayıcılar Web Speech API (ses tanıma) teknolojisini tam olarak desteklemektedir.

> [!IMPORTANT]
> Mobil cihazlardan mikrofon erişimi sağlayabilmek için HTTPS bağlantısı zorunludur. Uygulama, `localhost.run` tüneli üzerinden güvenli HTTPS bağlantısını otomatik olarak sağlar.
