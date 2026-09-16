# 🎬 JODO - After Effects Automation with Claude

Otomatik video analizi ve After Effects speed ramp montaj sistemi. Claude Vision API kullanarak videoları analiz edip, otomatik olarak montaj kurar.

## ✨ Özellikler

- 🎥 **Video Analizi** - Claude Vision ile sahne tespiti
- 🎯 **Scene Detection** - Aksiyon/Diyalog/Doğa sahneleri otomatik tanıma
- 🎵 **Beat Detection** - Müzik ritmine senkronizasyon
- ⚡ **Speed Ramp** - Dinamik hız değişiklikleri
- 🎨 **Transitions** - Otomatik geçiş efektleri
- 📝 **Titles/Graphics** - Başlık ve grafik ekleme
- 🔄 **Batch Processing** - Çok video aynı anda işleme
- 🤖 **Full Automation** - Baştan sona otomatik

## 🛠️ Teknoloji Stack

- **Python 3.10+** - Ana backend
- **Claude AI (Vision + API)** - Video analizi
- **Adobe After Effects** - Montaj ve render
- **ExtendScript (JSX)** - After Effects otomasyon
- **OpenCV** - Video işleme
- **FFmpeg** - Video encoding

## 📋 Kurulum

```bash
# Repository klonla
git clone https://github.com/hasimaygun/jodo-aftereffects.git
cd jodo-aftereffects

# Python dependencies kur
pip install -r requirements.txt

# Konfigürasyonu düzenle
cp config.example.json config.json
# config.json'da API anahtarlarını ekle
```

## 🚀 Kullanım

```bash
# Tek video işle
python main.py --input video.mp4 --output output/

# Klasördeki tüm videoları işle
python main.py --batch videos/ --output renders/

# Konfigürasyonla başla
python main.py --config config.json --input video.mp4
```

## 📁 Proje Yapısı

```
jodo-aftereffects/
├── main.py                 # Ana Python script
├── video_analyzer.py       # Claude Vision analizi
├── ae_controller.py        # After Effects kontrol
├── montage_composer.py     # Montaj oluşturma
├── config.json            # Konfigürasyon
├── ae_scripts/
│   └── automation.jsx     # After Effects ExtendScript
├── templates/
│   └── project_template.aep
├── requirements.txt       # Python dependencies
└── README.md
```

## 🎯 İş Akışı

1. **Video Analizi**
   - Claude Vision video çerçeveleri analiz eder
   - Sahne türlerini belirler (aksiyon/diyalog/doğa)
   - Beat/ritim tespiti yapar

2. **Montaj Planı**
   - Speed ramp noktaları belirler
   - Transition yerlerini hesaplar
   - Timing ayarlaması yapar

3. **After Effects Otomasyon**
   - Yeni proje oluşturur
   - Videoyu import eder
   - Speed ramp efektlerini uygular
   - Transitionları ekler
   - Titilleri ve grafikleri yerleştirir

4. **Render & Export**
   - Başarılı render için ayarları konfigüre eder
   - Video'yu export eder
   - Metadata ekler

## 🔑 API Anahtarları

`config.json`'da şunları ayarlayın:

```json
{
  "anthropic_api_key": "your-claude-api-key",
  "video_analysis": {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096
  },
  "after_effects": {
    "path": "C:\\Program Files\\Adobe\\Adobe After Effects 2024\\Support Files\\AfterFX.exe",
    "timeout": 3600
  },
  "output": {
    "format": "mp4",
    "quality": "high",
    "fps": 30
  }
}
```

## 📝 Lisans

MIT License - Bkz. LICENSE dosyası

## 🤝 Katkıda Bulunun

Pull requestler açıkça memnun edilir! 🎉

---

**Hazır mı? Başlayalım!** 🚀