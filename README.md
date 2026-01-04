# Water Quality Monitoring System

Sistem Monitoring Kualitas Air Berbasis IoT dengan Prediksi Machine Learning dan Sistem Pakar

## 📁 Struktur File

```
.
├── app.py                  # Main application (entry point)
├── config.py              # Configuration & constants
├── utils.py               # Utility functions (Firebase, session state, etc.)
├── ui_components.py       # UI rendering components
├── styles.css             # External CSS styling
├── Machine_Learning.py    # ML model handler (CLEANED & ORGANIZED)
├── Sistem_Pakar.py        # Expert system (Fuzzy Logic)
├── water_potability_model.pkl  # Trained ML model
└── README.md              # Documentation
```

## 🎯 Komponen Utama

### 1. **app.py**
File utama aplikasi yang mengelola:
- Konfigurasi halaman Streamlit
- Sidebar untuk koneksi Firebase
- Loop utama untuk monitoring real-time
- Integrasi ML dan Expert System
- Auto-refresh setiap 3 detik

### 2. **config.py**
Berisi konstanta dan konfigurasi:
- `PAGE_CONFIG`: Konfigurasi halaman Streamlit
- `REFRESH_INTERVAL`: Interval auto-refresh (3000ms)
- `HISTORY_MAXLEN`: Panjang maksimal history chart (30 data points)
- `SVG_ICONS`: Icon library untuk UI
- `RECOMMENDATION_ICONS`: Icon untuk rekomendasi

### 3. **utils.py**
Fungsi utilitas untuk:
- `initialize_session_state()`: Inisialisasi state management
- `init_firebase()`: Koneksi ke Firebase
- `get_sensor_data_wib()`: Ambil data sensor dari Firebase
- `upload_status_to_firebase()`: Upload status ke Firebase
- `save_to_history()`: Simpan data ke node `sensor_history`
- `check_device_status()`: Cek status online ESP32
- `load_css()`: Load file CSS eksternal

### 4. **ui_components.py**
Komponen rendering UI:
- `create_plotly_chart()`: Chart untuk tren pH, TDS, NTU
- `render_device_status()`: Status online/offline ESP32
- `render_status_and_confidence()`: Status kualitas air + confidence level
- `render_decision_explanation()`: Penjelasan keputusan ML + ES
- `render_recommendations()`: Rekomendasi tindakan
- `render_pipeline()`: Visualisasi pipeline sistem
- `render_documentation()`: Dokumentasi teknis
- `render_welcome_screen()`: Welcome screen sebelum koneksi Firebase

### 5. **styles.css**
File CSS terpisah untuk styling:
- Global styles
- Header styling
- Metric cards
- Status cards
- Decision cards
- Pipeline visualization
- Tabs, dataframes, alerts
- Dark mode support

### 6. **Machine_Learning.py** ✨ (BARU - CLEANED & ORGANIZED)
Handler untuk model Machine Learning dengan struktur yang lebih baik:

**Class: `WaterQualityModel`**
- `__init__(model_path)`: Load model dari file
- `_load_model(model_path)`: Private method untuk loading model
- `_prepare_input(ph, tds, ntu)`: Prepare input data untuk prediksi
- `_get_prediction_probability(X)`: Get probability jika model support
- `predict(ph, tds, ntu)`: **Main method** untuk prediksi
- `predict_with_confidence(ph, tds, ntu)`: DEPRECATED (backward compatibility)
- `get_model_info()`: Get informasi tentang model

**Improvements:**
- ✅ Better code organization dengan private methods
- ✅ Comprehensive docstrings untuk setiap method
- ✅ Error handling yang lebih baik
- ✅ Separation of concerns (loading, preparing, predicting)
- ✅ Method untuk get model information
- ✅ Test function yang lebih informatif
- ✅ Clear deprecation warnings

**Input:**
- pH level (6.5-8.5 ideal)
- TDS (Total Dissolved Solids) in mg/L
- NTU (Turbidity)

**Output:**
- "Layak Minum" atau "Tidak Layak Minum"

**Note:** Confidence level dihitung oleh Expert System, bukan oleh ML model.

### 7. **Sistem_Pakar.py**
Sistem Pakar menggunakan Fuzzy Logic:
- 22 aturan inferensi (R1-R22)
- Fuzzifikasi parameter (pH, TDS, Kekeruhan)
- Inferensi fuzzy dengan operator MIN-MAX
- Defuzzifikasi menggunakan metode Centroid
- Hybrid decision dengan ML
- Perhitungan confidence level (0-100%)

## 🚀 Cara Menggunakan

### 1. Install Dependencies
```bash
pip install streamlit firebase-admin pandas plotly streamlit-autorefresh joblib scikit-learn
```

### 2. Jalankan Aplikasi
```bash
streamlit run app.py
```

### 3. Konfigurasi Firebase
1. Buka sidebar
2. Masukkan Firebase Database URL
3. Tentukan Database Path (contoh: `sensor`)
4. Upload Service Account JSON
5. Klik Connect

### 4. Monitoring Real-time
- Dashboard akan auto-refresh setiap 3 detik
- Data sensor ditampilkan dalam chart dan metric cards
- Status kualitas air dihitung secara parallel (ML + ES)
- Confidence level menunjukkan tingkat keyakinan sistem
- Semua data disimpan ke `sensor_history` untuk analisis historis

## 📊 Struktur Data Firebase

### Node Sensor (Input)
```json
{
  "sensor": {
    "ph": 7.2,
    "tds": 120.5,
    "ntu": 0.85,
    "timestamp": "14:30:25",
    "status": "Layak Minum"  // Di-update oleh sistem
  }
}
```

### Node History (Output)
```json
{
  "sensor_history": {
    "20260102": {
      "210032": {
        "ntu": 0.1,
        "ph": 7.18,
        "status": "Layak Minum",
        "tds": 103.3,
        "timestamp": "21:00:32"
      }
    }
  }
}
```

## 🎨 Fitur Utama

### ✅ Real-time Monitoring
- Auto-refresh setiap 3 detik
- Visualisasi chart untuk pH, TDS, NTU
- Metric cards dengan delta indicators
- Device status (online/offline ESP32)

### 🤖 Parallel Processing
- Machine Learning (Random Forest)
- Expert System (Fuzzy Logic)
- Hybrid decision logic
- Confidence level calculation

### 💾 Historical Data
- Automatic saving ke Firebase
- Struktur hierarkis (YYYYMMDD/HHMMSS)
- Anti-duplikasi dengan signature checking
- Data lengkap untuk analisis jangka panjang

### 📱 Responsive UI
- Dark mode support
- Clean dan professional design
- Modular components
- External CSS untuk easy customization

## 🧪 Testing Machine Learning Model

Untuk test ML model secara standalone:

```bash
python Machine_Learning.py
```

Output akan menampilkan:
- Model information (type, features, capabilities)
- Test cases dengan berbagai kondisi air
- Prediction results
- Debug information

## 🔧 Customization

### Mengubah Styling
Edit file `styles.css` untuk mengubah tampilan UI.

### Mengubah Interval Refresh
Edit `REFRESH_INTERVAL` di `config.py`.

### Menambah Aturan Expert System
Edit fungsi `fuzzy_inference()` di `Sistem_Pakar.py`.

### Mengubah Threshold Parameter
Edit fungsi fuzzifikasi di `Sistem_Pakar.py`.

### Retrain ML Model
1. Siapkan dataset dengan kolom: `ph`, `Solids`, `Turbidity`, `Potability`
2. Train model Random Forest
3. Save model: `joblib.dump(model, "water_potability_model.pkl")`
4. Replace file yang lama

## 📝 Catatan Penting

1. **Firebase Rules**: Pastikan read/write diizinkan untuk development
2. **Model File**: File `water_potability_model.pkl` harus ada di direktori yang sama
3. **CSS File**: File `styles.css` harus ada di direktori yang sama
4. **ESP32**: Pastikan ESP32 mengirim data dengan format yang benar
5. **Dependencies**: Install semua library yang dibutuhkan

## 🐛 Troubleshooting

### CSS tidak load
- Pastikan `styles.css` ada di direktori yang sama dengan `app.py`
- Check console untuk error messages

### Firebase tidak terkoneksi
- Verifikasi URL format: `https://...firebaseio.com/`
- Check Service Account JSON validity
- Verify Firebase Rules

### Data tidak tersimpan ke history
- Check Firebase write permissions
- Verify `sensor_history` path accessibility
- Check console logs untuk error messages

### ESP32 terdeteksi offline
- Verifikasi koneksi WiFi ESP32
- Check Firebase write permissions dari ESP32
- Pastikan ESP32 mengirim data setiap beberapa detik

### ML Model Error
- Pastikan file `water_potability_model.pkl` ada
- Check model compatibility dengan scikit-learn version
- Verify input data format (pH, TDS, NTU)

## 📦 File Dependencies

```
streamlit>=1.28.0
firebase-admin>=6.0.0
pandas>=2.0.0
plotly>=5.18.0
streamlit-autorefresh>=0.0.1
joblib>=1.3.0
scikit-learn>=1.3.0
numpy>=1.24.0
```

Save as `requirements.txt` dan install dengan:
```bash
pip install -r requirements.txt
```

## 🎓 Code Quality Improvements

### Machine_Learning.py
- ✅ **Better Organization**: Private methods untuk internal operations
- ✅ **Docstrings**: Comprehensive documentation untuk setiap method
- ✅ **Error Handling**: Proper try-catch dengan informative messages
- ✅ **Modularity**: Separated concerns (loading, preparing, predicting)
- ✅ **Testing**: Built-in test function dengan sample data
- ✅ **Type Hints**: Clear parameter and return types in docstrings

### Overall Structure
- ✅ **Separation of Concerns**: Each file has specific responsibility
- ✅ **Reusability**: Components can be reused in other projects
- ✅ **Maintainability**: Easy to update and debug
- ✅ **Scalability**: Easy to add new features
- ✅ **Documentation**: Comprehensive README and inline comments

## 📄 License

Copyright © 2026. All rights reserved.

---

**Created with ❤️ for IoT Water Quality Monitoring**
