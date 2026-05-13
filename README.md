# YZTA_Hackathon - Yapay Zeka - 252. Grup
# 🌿 KoopPilot — Kooperatifler İçin Yapay Zeka Destekli İşletme Asistanı

> **Google Yapay Zeka ve Teknoloji Akademisi Hackathonu** | KOBİ AI Çözümleri

---

## 📌 Proje Hakkında

Küçük ölçekli işletmeler ve kadın kooperatifleri, günlük operasyonlarını büyük ölçüde manuel yöntemlerle yürütmektedir. Bir işletme sahibi günde ortalama 2-3 saatini yalnızca "siparişim nerede?", "bu ürün stokta var mı?" gibi rutin sorulara cevap vermekle geçirebilmektedir. Stok tükenmesi fark edildiğinde iş işten geçmiş, müşteri kaybedilmiş olabilmektedir.

**KoopPilot**, bu sorunu çözmek için geliştirilmiş yapay zeka destekli bir işletme yönetim asistanıdır. Sipariş takibi, stok yönetimi, kargo izleme ve günlük raporlama gibi tüm operasyonel süreçleri tek bir platformda birleştirerek işletme sahiplerinin zamandan tasarruf etmesini ve daha bilinçli kararlar almasını sağlar.

---

## 🎯 Hedef Kitle

- Günde 10-100 arası sipariş işleyen küçük ölçekli e-ticaret işletmeleri
- Tarım, gıda veya el sanatları alanında faaliyet gösteren üretici kooperatifleri
- Fiziksel mağaza ile online satışı birlikte yürüten karma yapılar
- 20-200 ürün yelpazesiyle çalışan bölgesel satış firmaları

---

## 🚀 Özellikler

### 🤖 AI İşletme Asistanı
Doğal dil ile işletmenizi yönetin. "Kaç kilo domates stoğum var?", "Bugün kaç sipariş geldi?", "Geciken kargo var mı?" gibi soruları yazmanız yeterli. Sistem ilgili araçları otomatik çağırarak anlık ve doğru cevap üretir.

### 📦 Sipariş Yönetimi
Tüm siparişleri tek ekranda görüntüleyin, durumlarını güncelleyin. Bekleyen, kargoya verilen, teslim edilen ve iptal edilen siparişler anlık olarak izlenir.

### 🏭 Stok & Envanter Takibi
Kritik stok eşiklerini belirleyin, sistem otomatik uyarı üretsin. Ürün bazında stok seviyelerini güncelleyin, hangi ürünlerin ne kadar kaldığını görsel progress bar'larla takip edin.

### 🚚 Kargo İzleme
Aktif gönderileri, tahmini teslimat tarihlerini ve gecikme risklerini tek panelde görüntüleyin.

### 📊 Raporlar & Analizler
Sipariş durum dağılımı, stok seviyeleri, gelir özeti ve kritik stok detayları gibi operasyonel verileri interaktif grafiklerle inceleyin.

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Dashboard                 │
│         (Kullanıcı Arayüzü — 8 Sayfa)               │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP (REST API)
┌─────────────────▼───────────────────────────────────┐
│                  FastAPI Backend                     │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │           AI Agent Orchestrator              │    │
│  │         (LangGraph ReAct Agent)              │    │
│  │                                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │    │
│  │  │  Sipariş │  │   Stok   │  │  Kargo   │  │    │
│  │  │  Tools   │  │  Tools   │  │  Tools   │  │    │
│  │  └──────────┘  └──────────┘  └──────────┘  │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌──────────────────┐  ┌───────────────────────┐    │
│  │  Conversation    │  │     SQLite DB          │    │
│  │  Memory (DB)     │  │  (Ürün/Sipariş/Müşteri)│   │
│  └──────────────────┘  └───────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji | Açıklama |
|--------|-----------|----------|
| **AI Modeli** | Gemini 2.5 Flash | Ana LLM; doğal dil anlama ve üretme |
| **Agent Framework** | LangGraph (ReAct) | Tool-calling agent mimarisi |
| **Backend** | FastAPI + Python 3.12 | REST API, async endpoint'ler |
| **Veritabanı** | SQLite + SQLModel | Sipariş, ürün, müşteri verileri |
| **Konuşma Hafızası** | SQLite + in-memory cache | Kullanıcı bazlı konuşma geçmişi |
| **Frontend** | Streamlit | Dashboard arayüzü |
| **Grafikler** | Plotly | İnteraktif raporlar |
| **Kimlik Doğrulama** | Bcrypt + session state | Kullanıcı girişi ve yetkilendirme |

---

## 🤖 Agent Mimarisi

KoopPilot'un kalbinde **LangGraph ReAct Agent** yer almaktadır. Agent, kullanıcıdan gelen doğal dil mesajını anlayarak hangi araçları (tools) kullanacağına karar verir ve işlemi tamamlayarak anlamlı bir yanıt üretir.

### Admin Agent Araçları

```python
# Stok araçları
check_inventory(product_name)     # Ürün stok sorgulama
low_stock_alert()                  # Kritik stok listesi
update_stock(product_name, amount) # Stok güncelleme
list_all_products()                # Tüm ürün listesi
create_product(...)                # Yeni ürün ekleme

# Sipariş araçları
get_order_status(order_id)         # Sipariş durumu sorgulama
list_orders(status, limit)         # Sipariş listeleme
update_order_status(id, status)    # Sipariş durumu güncelleme
get_daily_summary()                # Günlük iş özeti

# Kargo araçları
track_shipment(tracking_id)        # Kargo takip
get_delayed_shipments()            # Geciken kargolar
```

### Örnek Agent Akışı

```
Kullanıcı: "Domates stoğunu 500 kg yap"
    │
    ▼
Agent niyeti anlar → update_stock("Domates", "500") çağrılır
    │
    ▼
DB güncellenir → "Domates stoğu 500 kg olarak güncellendi ✓"
```

---

## 📁 Proje Yapısı

```
KoopPilot/
├── backend/
│   ├── agent/
│   │   ├── orchestrator.py      # LangGraph ReAct agent
│   │   ├── memory.py            # Konuşma hafızası yönetimi
│   │   └── tools/
│   │       ├── stock_tools.py   # Stok araçları
│   │       ├── order_tools.py   # Sipariş araçları
│   │       └── cargo_tools.py   # Kargo araçları
│   ├── api/
│   │   ├── chat.py              # AI chat endpoint'leri
│   │   ├── orders.py            # Sipariş API'si
│   │   └── stock.py             # Stok API'si
│   ├── database/
│   │   ├── connection.py        # DB bağlantısı
│   │   ├── models.py            # SQLModel modelleri
│   │   └── seed.py              # Örnek veri
│   └── main.py                  # FastAPI uygulama
│
└── dashboard/
    ├── pages/
    │   ├── 1_dashboard.py       # Ana dashboard
    │   ├── 2_orders.py          # Sipariş yönetimi
    │   ├── 3_stock.py           # Stok yönetimi
    │   ├── 4_cargo.py           # Kargo takibi
    │   ├── 5_ai_assistant.py    # AI asistan
    │   ├── 6_reports.py         # Raporlar
    │   └── 8_settings.py        # Ayarlar
    ├── utils/
    │   ├── styles.py            # Global stil sistemi
    │   ├── api_client.py        # Backend API istemcisi
    │   └── auth.py              # Kimlik doğrulama
    └── app.py                   # Giriş sayfası
```

---

## ⚙️ Kurulum & Çalıştırma

### Gereksinimler
- Python 3.12+
- Google AI API anahtarı (Gemini)

### Backend

```bash
cd backend
pip install -r requirements.txt

# .env dosyası oluşturun
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Veritabanını hazırlayın
python -c "from database.connection import create_db_and_tables; create_db_and_tables()"
python -c "from database.seed import seed; seed()"

# Backend'i başlatın
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Dashboard

```bash
cd dashboard
pip install -r requirements.txt

# Dashboard'u başlatın
streamlit run app.py --server.port 8501
```

### Demo Hesabı

```
E-posta : demo@kooppilot.com
Şifre   : demo123
```

---

## 💡 Demo Senaryoları

**1. Doğal Dil ile Stok Güncelleme**
> AI Asistan'a "Domates stoğunu 300 kg yap" yazın → Agent `update_stock` tool'unu çağırır → DB güncellenir → Onay mesajı gelir

**2. Anlık Stok Sorgusu**
> "Hangi ürünlerin stoğu kritik seviyede?" → Agent `low_stock_alert()` çağırır → Tüm kritik ürünler listelenir

**3. Günlük İş Özeti**
> "Bugünkü iş özetini ver" → Agent `get_daily_summary()` çağırır → Sipariş, gelir ve stok durumu tek mesajda özetlenir

**4. Sipariş Takibi**
> Siparişler sayfasında bekleyen siparişleri "Onayla" butonuyla kargoya ver, "Teslim" ile tamamla

---

## 👥 Ekip

**Google Yapay Zeka ve Teknoloji Akademisi — 252. Grup - Hackathon 2026**

