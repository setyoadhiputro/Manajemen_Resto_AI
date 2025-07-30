# 🍽️ Sistem Manajemen Restoran AI

Sistem manajemen restoran yang dilengkapi dengan AI chatbot untuk membantu operasional restoran.

## ✨ Fitur Utama

### 📊 **Dashboard Interaktif**
- Metrics real-time (total menu, rata-rata harga, rating, pendapatan)
- Analisis laba rugi dan margin keuntungan
- Grafik trend pesanan dan distribusi kategori
- Visualisasi data yang informatif

### 🍽️ **Manajemen Menu**
- Daftar menu dengan search dan filter
- Kategori menu (Main Course, Appetizer, Beverage)
- Informasi harga dan rating
- Upload data menu via CSV

### 📦 **Manajemen Inventori**
- Status stok bahan baku real-time
- Alert untuk low stock dengan notifikasi email
- Prediksi kebutuhan inventori
- Upload data inventori via CSV
- Auto-update stok saat pembelian bahan baku

### 💰 **Manajemen Keuangan**
- Input biaya operasional dan pembelian bahan baku
- Perhitungan laba rugi otomatis
- Analisis margin keuntungan
- Tracking pengeluaran dan pendapatan
- Upload data keuangan via CSV

### 💬 **Analisis Review Customer**
- Analisis sentimen review pelanggan
- Metrics positive/negative reviews
- Data customer feedback
- Upload data review via CSV

### 🎯 **Rekomendasi Menu**
- Rekomendasi berdasarkan rating
- Rekomendasi berdasarkan harga
- Menu terpopuler
- Generate rekomendasi otomatis

### 📈 **Analisis Data**
- Performa menu terbaik
- Analisis pendapatan dan keuntungan
- Trend penjualan
- Prediksi demand

### 📤 **Upload Data**
- Upload file CSV untuk berbagai jenis data
- Import data menu, transaksi, inventori, review
- Upload data pembelian dan biaya operasional
- Validasi data otomatis

### ⚙️ **Pengaturan**
- Konfigurasi notifikasi email
- Pengaturan threshold stok rendah
- Konfigurasi SMTP untuk email
- Test email notifikasi
- Panduan troubleshooting email

### 🤖 **ChefAI Chatbot**
- AI-powered chatbot dengan OpenRouter API
- Chat history yang tersimpan
- Bantuan informasi menu, harga, dan tips manajemen
- Terintegrasi di sidebar aplikasi

## 🚀 Cara Menjalankan

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi
```bash
streamlit run app.py
```

### 3. Buka Browser
Kunjungi `http://localhost:8501` atau 'https://manajemenrestoai-zoev9xhjluevpzt7wuqr7q.streamlit.app/'

## 📁 Struktur File

```
├── app.py                   # Aplikasi utama
├── requirements.txt         # Dependencies Python
├── README.md               # Dokumentasi ini
├── models/                 # Model AI dan ML
│   ├── demand_forecast.py
│   ├── inventory_management.py
│   ├── menu_recommendation.py
│   └── sentiment_analysis.py
├── utils/                  # Utility functions
│   ├── data_generator.py
│   └── helpers.py
├── data/                   # Data aplikasi
│   ├── inventory.csv
│   ├── menu_items.csv
│   ├── customer_reviews.csv
│   ├── customer_preferences.csv
│   └── sample_orders.csv
└── .streamlit/            # Konfigurasi Streamlit
    └── config.toml
```

## 🤖 ChefAI Chatbot

### Fitur Chatbot:
- **AI Powered**: Menggunakan OpenRouter API dengan GPT-3.5-turbo
- **Chat History**: Menyimpan riwayat percakapan
- **Sidebar Integration**: Terintegrasi di sidebar aplikasi
- **Context Aware**: Memahami konteks percakapan

### Contoh Pertanyaan:
- "Apa saja menu yang tersedia?"
- "Berapa harga nasi goreng?"
- "Rekomendasikan menu untuk makan siang"
- "Tips mengelola inventori restoran"
- "Jam buka restoran kapan?"
- "Bagaimana cara menghitung margin keuntungan?"

## 💰 Fitur Keuangan

### Analisis Laba Rugi:
- **Total Revenue**: Total pendapatan dari penjualan
- **COGS (Cost of Goods Sold)**: Biaya pokok penjualan
- **Gross Profit**: Laba kotor
- **Operating Expenses**: Biaya operasional
- **Net Profit**: Laba bersih
- **Profit Margin**: Persentase keuntungan

### Input Biaya:
- **Biaya Operasional**: Sewa, listrik, gaji, dll
- **Pembelian Bahan Baku**: Auto-update inventori
- **Biaya Peralatan**: Investasi peralatan restoran

## 📧 Notifikasi Email

### Fitur Notifikasi:
- **Low Stock Alert**: Notifikasi otomatis saat stok rendah
- **Email Configuration**: Setup SMTP Gmail
- **Test Email**: Verifikasi konfigurasi email
- **Troubleshooting Guide**: Panduan mengatasi masalah email

### Setup Email:
1. Aktifkan 2-Factor Authentication di Gmail
2. Buat App Password khusus
3. Masukkan email dan App Password di halaman Pengaturan
4. Test email notifikasi

## 🔧 Konfigurasi

### API Configuration:
- **OpenRouter API Key**: Terintegrasi dalam aplikasi
- **Model**: GPT-3.5-turbo
- **Max Tokens**: 500
- **Temperature**: 0.7

### Email Configuration:
- **SMTP Server**: smtp.gmail.com
- **Port**: 587
- **Security**: TLS/SSL
- **Authentication**: Gmail App Password

### System Requirements:
- Python 3.8+
- Streamlit 1.28.0+
- Pandas, NumPy, Requests
- smtplib (built-in)

## 📊 Data Sample

Aplikasi menggunakan data sample untuk demonstrasi:
- **Menu**: 6 menu dengan harga dan rating
- **Orders**: 30 hari data pesanan
- **Inventory**: 5 bahan baku dengan status stok
- **Reviews**: 4 review customer dengan sentimen
- **Financial Data**: Sample data keuangan

## 🛠️ Troubleshooting

### Error Umum:
1. **Import Error**: Pastikan semua dependencies terinstall
2. **API Error**: Periksa koneksi internet dan API key
3. **Session Error**: Clear browser cache atau restart aplikasi
4. **Email Error**: Periksa konfigurasi SMTP dan App Password

### Debug Mode:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Troubleshooting Email:
1. Pastikan 2FA aktif di Gmail
2. Gunakan App Password, bukan password biasa
3. Periksa folder Spam
4. Pastikan koneksi internet stabil

## 📝 Pengembangan

### Menambah Fitur:
1. Edit file `app.py` untuk fitur baru
2. Test di local environment
3. Update dokumentasi jika diperlukan

### Customization:
- System prompt chatbot: Edit di fungsi `show_chef_ai_chatbot()`
- Data sample: Edit di fungsi `main()`
- UI styling: Edit CSS di `st.markdown()`
- Email template: Edit di fungsi `send_low_stock_email()`

## 📞 Support

Untuk bantuan atau pertanyaan:
1. Periksa dokumentasi ini
2. Lihat halaman Pengaturan untuk troubleshooting email
3. Test fitur email notifikasi
4. Periksa console browser untuk error JavaScript

## 📄 License

Proyek ini dibuat untuk pembelajaran dan demonstrasi sistem manajemen restoran dengan AI.

---

**Dibuat dengan ❤️ menggunakan Streamlit dan OpenRouter API** 
