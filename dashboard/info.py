"""
info.py — KoopPilot Dashboard Backend Gereksinimleri.

Bu dosya, dashboard ve Telegram bot sisteminin tam işlevsel olabilmesi için
backend'e eklenmesi gereken endpoint'leri, modelleri ve yapılandırmaları
dokümante eder.

Her bölüm, hangi dashboard/bot özelliğinin bu gereksinimi tetiklediğini,
önerilen endpoint yapısını ve model şemasını belirtir.
"""

# ==========================================================================
# 1. AUTH (Kimlik Doğrulama) Endpoint'leri
# ==========================================================================
#
# ŞU AN: Dashboard, local SQLite ile demo auth kullanıyor (dashboard/utils/auth.py).
# ÜRETİM İÇİN: Backend'e aşağıdaki endpoint'ler eklenmeli.
#
# POST /auth/register
# -------------------
# Body: {
#     "business_name": str,
#     "email": str,
#     "password": str
# }
# Response: {
#     "id": int,
#     "business_name": str,
#     "email": str,
#     "token": str  (JWT)
# }
# Açıklama: İşletme kaydı. SHA-256+salt veya bcrypt ile şifre hash'leme.
#
# POST /auth/login
# ----------------
# Body: { "email": str, "password": str }
# Response: { "token": str, "user": {...} }
# Açıklama: JWT token döndüren login endpoint'i.
#
# POST /auth/reset-password
# -------------------------
# Body: { "email": str }
# Response: { "message": str }
# Açıklama: E-posta ile parola sıfırlama token'ı gönderir.
#
# POST /auth/reset-password/confirm
# ----------------------------------
# Body: { "token": str, "new_password": str }
# Response: { "message": str }
#
# GEREKLİ MODEL (database/models.py):
# class User(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     business_name: str
#     email: str = Field(unique=True)
#     password_hash: str
#     salt: str
#     phone: str = ""
#     telegram_bot_token: str = ""
#     telegram_customer_bot_token: str = ""
#     instagram_url: str = ""
#     whatsapp_url: str = ""
#     created_at: datetime
#     updated_at: datetime


# ==========================================================================
# 2. ÜRÜN EKLEME Endpoint'i
# ==========================================================================
#
# ŞU AN: Backend'de sadece GET /stock ve PATCH /stock/{id} var.
# EKSİK: Yeni ürün ekleme ve silme.
#
# POST /stock
# -----------
# Body: {
#     "name": str,
#     "stock_amount": int,
#     "critical_threshold": int,
#     "unit": str,
#     "price": float
# }
# Response: Product (yeni oluşturulan ürün)
#
# DELETE /stock/{product_id}
# -------------------------
# Response: { "message": "Ürün silindi", "id": int }
#
# Dashboard'da buton mevcut ancak backend desteği bekliyor.
# Bkz: dashboard/pages/3_🛒_Urun_Stok.py


# ==========================================================================
# 3. KARGO TAKİP NUMARASI ATAMA Endpoint'i
# ==========================================================================
#
# ŞU AN: Sipariş durumu PATCH ile güncellenebilir ama kargo takip no atanamaz.
#
# PATCH /orders/{order_id}/tracking
# ---------------------------------
# Body: { "cargo_tracking_id": str }
# Response: Order (güncellenmiş sipariş)
#
# Dashboard'da form mevcut ancak backend desteği bekliyor.
# Bkz: dashboard/pages/4_🚚_Kargo_Takibi.py


# ==========================================================================
# 4. TOPLU DASHBOARD İSTATİSTİK Endpoint'i (Opsiyonel)
# ==========================================================================
#
# ŞU AN: Dashboard, birden fazla endpoint çağırarak KPI verisi topluyor.
# OPTİMİZASYON: Tek bir endpoint ile tüm KPI'ları döndürmek daha verimli.
#
# GET /stats/dashboard
# --------------------
# Response: {
#     "today_orders": int,
#     "today_revenue": float,
#     "total_orders": int,
#     "critical_stock_count": int,
#     "shipped_count": int,
#     "pending_count": int,
#     "delay_count": int,
#     "total_products": int,
#     "status_distribution": { "pending": int, ... },
#     "total_revenue": float
# }


# ==========================================================================
# 5. TELEGRAM BOT YAPILANDIRMASI
# ==========================================================================
#
# ŞU AN: Bot token'ları dashboard local SQLite'ta saklanıyor.
# ÜRETİM İÇİN: Backend'de saklanmalı.
#
# PATCH /settings/telegram
# ------------------------
# Body: {
#     "admin_bot_token": str,
#     "customer_bot_token": str
# }
# Response: { "message": "Telegram ayarları güncellendi" }
#
# GET /settings/telegram
# ----------------------
# Response: {
#     "admin_bot_active": bool,
#     "customer_bot_active": bool,
#     "admin_bot_token_set": bool,
#     "customer_bot_token_set": bool
# }


# ==========================================================================
# 6. MÜŞTERİ BOTU İÇİN GEREKLİ AGENT GÜNCELLEMELERİ
# ==========================================================================
#
# ŞU AN: Müşteri agent'ı customer_id bazlı çalışıyor.
# TELEGRAM BOTU İÇİN: Telegram user_id → customer_id eşleştirmesi gerekli.
#
# GEREKLİ:
# 1. Customer modeline `telegram_user_id` alanı eklenmeli
# 2. Müşteri botunda /start komutu ile telefon no veya sipariş no
#    üzerinden müşteri eşleştirmesi yapılmalı
# 3. Eşleştirme sonrası tüm sorgular otomatik customer_id ile çalışmalı
#
# ÖNERİLEN ENDPOINT:
# POST /customers/link-telegram
# Body: { "telegram_user_id": int, "phone": str | "order_id": int }
# Response: { "customer_id": int, "name": str }


# ==========================================================================
# 7. SİPARİŞ OLUŞTURMA Endpoint'i
# ==========================================================================
#
# ŞU AN: Backend'de sipariş listeleme ve durum güncelleme var ama oluşturma yok.
#
# POST /orders
# ------------
# Body: {
#     "customer_id": int,
#     "items": [{ "product_id": int, "quantity": int }],
#     "channel": str  (web | telegram | whatsapp)
# }
# Response: Order (yeni oluşturulan sipariş)
#
# Bu endpoint hem dashboard'dan hem de Telegram botundan kullanılabilir.


# ==========================================================================
# 8. ÜRÜN SATIŞTAN KALDIRMA
# ==========================================================================
#
# Admin bot özelliği: "Domates'i satıştan kaldır" gibi komutlar.
#
# PATCH /stock/{product_id}/visibility
# Body: { "active": bool }
# Response: Product
#
# GEREKLİ MODEL GÜNCELLEMESİ:
# Product modeline `active: bool = True` alanı eklenmeli.


# ==========================================================================
# 9. DÖNEMSEL SATIŞ KARŞILAŞTIRMA
# ==========================================================================
#
# Admin bot özelliği: "Bu dönem geçen döneme göre ne kadar sattık?"
#
# GET /stats/comparison
# Params: period=week|month|quarter
# Response: {
#     "current_period": { "orders": int, "revenue": float, "top_products": [...] },
#     "previous_period": { "orders": int, "revenue": float, "top_products": [...] },
#     "growth_pct": float,
#     "trending_up": [str],    # Satışı artan ürünler
#     "trending_down": [str],  # Satışı azalan ürünler
# }


# ==========================================================================
# ÖZET: ÖNCELİK SIRASI
# ==========================================================================
#
# Yüksek Öncelik:
# 1. POST /stock (ürün ekleme)
# 2. POST /orders (sipariş oluşturma)
# 3. PATCH /orders/{id}/tracking (kargo takip no)
# 4. Customer telegram_user_id eşleştirme
#
# Orta Öncelik:
# 5. Auth endpoint'leri (register, login, reset)
# 6. DELETE /stock/{id} (ürün silme)
# 7. PATCH /stock/{id}/visibility (satıştan kaldırma)
#
# Düşük Öncelik (Optimizasyon):
# 8. GET /stats/dashboard (toplu KPI)
# 9. GET /stats/comparison (dönemsel karşılaştırma)
# 10. Telegram bot ayarları backend'e taşıma
