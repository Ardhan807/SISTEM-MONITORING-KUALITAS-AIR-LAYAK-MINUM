"""
Water Quality Monitoring System - Main Application
IoT-based Water Quality Monitoring with Machine Learning and Expert System
"""

import streamlit as st
import re
from streamlit_autorefresh import st_autorefresh

# Import modules
from config import PAGE_CONFIG, REFRESH_INTERVAL
from utils import (
    initialize_session_state,
    init_firebase_from_secrets,
    load_firebase_config,
    get_sensor_data_wib,
    upload_status_to_firebase,
    save_to_history,
    check_device_status,
    check_device_status_by_timestamp,
    load_css
)
from ui_components import (
    create_plotly_chart,
    render_device_status,
    render_status_and_confidence,
    render_decision_explanation,
    render_recommendations,
    render_pipeline,
    render_documentation,
    render_welcome_screen
)
from Machine_Learning import WaterQualityModel
from Sistem_Pakar import evaluate_water_quality, get_recommendations


@st.cache_resource
def load_model():
    """Load ML model with caching"""
    return WaterQualityModel("water_potability_model.pkl")


def main():
        """Main application function"""
        # Page configuration
        st.set_page_config(**PAGE_CONFIG)
        
        # Load custom CSS
        load_css()
        
        # Initialize session state
        initialize_session_state()
        
        # Header
        st.markdown("<h1>SISTEM MONITORING KUALITAS AIR BERBASIS IOT DENGAN PREDIKSI MACHINE LEARNING DAN SISTEM PAKAR</h1>", unsafe_allow_html=True)
        st.markdown("""
            <p style='text-align: center; color: #666; font-size: 15px; margin-bottom: 5px;'>
            Pemantauan real-time dengan Machine Learning ⚡ Sistem Pakar (Parallel Processing)
            </p>
        """, unsafe_allow_html=True)
        st.divider()
        
        # Sidebar - System Info Only
        with st.sidebar:
            st.title("Informasi Sistem")
            
            st.info("""
            **Model ML:** Random Forest  
            **Aturan:** 22 Fuzzy Logic  
            **Mode:** Parallel Processing
            **Update:** Real-time (3s)
            **Firebase Upload:** Aktif
            **History Logging:** Aktif
            """)
            
            # Show current config status
            with st.expander("Status Koneksi"):
                config = load_firebase_config()
                if config["success"]:
                    st.success("✅ Konfigurasi OK")
                    st.text(f"Path: {config['db_path']}")
                else:
                    st.error("❌ Konfigurasi Error")
                    st.caption(config['error'])
            
            st.markdown("---")
        
        # Auto-connect to Firebase from secrets
        firebase_connected = False
        db_path = "sensor"  # default
        
        success, message, path = init_firebase_from_secrets()
        
        if success:
            firebase_connected = True
            db_path = path
            # Show connection status in sidebar
            with st.sidebar:
                st.success("🟢 Firebase Terhubung")
        else:
            st.error(f"⚠️ **Gagal Terhubung ke Firebase**")
            st.error(message)
            st.info("""
            **Setup yang diperlukan:**
            
            1. Buat file `.streamlit/secrets.toml` di root project
            
            2. Tambahkan konfigurasi berikut:
    ```toml
            [firebase]
            database_url = "https://your-project.firebaseio.com/"
            db_path = "sensor"
            service_account = '''
            {
            "type": "service_account",
            "project_id": "your-project-id",
            ...
            }
            '''
    ```
            
            3. Restart aplikasi
            
            **Pemecahan Masalah:**
            - Periksa Firebase Rules (allow read/write)
            - Verifikasi database_url
            - Verifikasi service_account JSON valid
            - Periksa koneksi internet
            """)
            return
        
        # Auto refresh
        st_autorefresh(interval=REFRESH_INTERVAL, key="refresh")
        
        # Main dashboard logic
        data, error = get_sensor_data_wib(db_path)
        
        if error:
            st.error(f"Error mengambil data: {error}")
            st.info("""
            **Pemecahan Masalah:**
            1. Periksa Firebase Rules (harus allow read/write)
            2. Verifikasi path database di secrets.toml
            3. Periksa koneksi internet
            """)
        
        elif not data:
            st.warning(f"⚠️ Tidak ada data di path: `{db_path}`")
            st.info("""
            **Kemungkinan Penyebab:**
            - ESP32 belum mengirim data pertama kali
            - Path database salah di secrets.toml
            - Sensor belum aktif
            
            Pastikan ESP32 terhubung ke WiFi dan Firebase.
            """)
        
        else:
            # ... (lanjutkan dengan kode dashboard Anda yang sudah ada)
            # Parse sensor data
            ph = float(data.get("ph", 0))
            tds = float(data.get("tds", 0))
            ntu = float(data.get("ntu", 0))
            timestamp = data.get("timestamp", "00:00:00")
            
            # Create a data signature from sensor values
            current_data_signature = f"{ph:.2f}|{tds:.1f}|{ntu:.2f}"
            
            # Check if data has changed (untuk tracking history)
            if st.session_state.last_timestamp is None:
                # Pertama kali masuk - simpan signature
                st.session_state.last_timestamp = current_data_signature
                st.session_state.no_update_count = 0
            elif current_data_signature == st.session_state.last_timestamp:
                # Data tidak berubah - increment counter
                st.session_state.no_update_count += 1
            else:
                # Data berubah - reset counter dan set flag bahwa sudah terima data baru
                st.session_state.last_timestamp = current_data_signature
                st.session_state.no_update_count = 0
                st.session_state.first_data_received = True
            
            # Check device status BERDASARKAN TIMESTAMP FIREBASE (universal untuk semua user)
            device_status = check_device_status_by_timestamp(timestamp)
            is_online = device_status["is_online"]
            status_message = device_status["message"]
            
            # Update history
            st.session_state.ph_hist.append(ph)    
            st.session_state.tds_hist.append(tds)
            st.session_state.ntu_hist.append(ntu)
            st.session_state.time_hist.append(timestamp)
            
            # 1. COMPACT DEVICE STATUS
            render_device_status(is_online, status_message, timestamp)
            
            # Show warning if offline
            if not is_online:
                seconds_ago = device_status.get("seconds_ago", 0)
                st.warning(f"⚠️ **ESP32 tidak mengirim data baru ke Firebase.** Data terakhir diterima {seconds_ago} detik yang lalu. Pastikan ESP32 terhubung ke WiFi dan Firebase.")
            
            # 2. CHARTS & TRENDS
            st.markdown("### Tren Historis")
            
            chart_col1, chart_col2, chart_col3 = st.columns(3)
            
            with chart_col1:
                fig_ph = create_plotly_chart(
                    st.session_state.ph_hist,
                    "pH Level Trend",
                    "#1f77b4",
                    "pH"
                )
                st.plotly_chart(fig_ph, use_container_width=True)
            
            with chart_col2:
                fig_tds = create_plotly_chart(
                    st.session_state.tds_hist,
                    "TDS Trend",
                    "#ff7f0e",
                    "TDS (ppm)"
                )
                st.plotly_chart(fig_tds, use_container_width=True)
            
            with chart_col3:
                fig_ntu = create_plotly_chart(
                    st.session_state.ntu_hist,
                    "Turbidity Trend",
                    "#2ca02c",
                    "NTU"
                )
                st.plotly_chart(fig_ntu, use_container_width=True)
            
            # 3. REAL-TIME METRICS
            st.markdown("### Data Sensor Real-time")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                ph_delta = ph - 7.0 if len(st.session_state.ph_hist) > 1 else None
                
                if ph_delta is not None and len(st.session_state.ph_hist) >= 2:
                    previous_ph = st.session_state.ph_hist[-2]
                    
                    # Cek apakah pH melewati nilai 7 (crossing)
                    crossed_neutral = (previous_ph < 7.0 and ph > 7.0) or (previous_ph > 7.0 and ph < 7.0)
                    
                    # Hitung jarak dari 7
                    current_distance = abs(ph - 7.0)
                    previous_distance = abs(previous_ph - 7.0)
                    
                    # Jika melewati 7 = merah
                    # Jika tidak melewati 7:
                    #   - mendekati 7 = hijau
                    #   - menjauhi 7 = merah
                    if crossed_neutral:
                        ph_delta_color = "inverse"  # merah (melewati 7)
                    elif current_distance < previous_distance:
                        ph_delta_color = "normal"   # hijau (mendekati 7)
                    else:
                        ph_delta_color = "inverse"  # merah (menjauhi 7)
                else:
                    ph_delta_color = "off"
                
                st.metric(
                    label="pH",
                    value=f"{ph:.2f}",
                    delta=f"{ph_delta:+.2f}" if ph_delta is not None else None,
                    delta_color=ph_delta_color
                )
            
            with col2:
                tds_delta_color = "inverse"
                tds_delta = tds - 900 if len(st.session_state.tds_hist) > 1 else None
                st.metric(
                    label="TDS",
                    value=f"{tds:.1f} ppm",
                    delta=f"{tds_delta:.1f}" if tds_delta is not None else None,
                    delta_color=tds_delta_color
                )

            with col3:
                ntu_delta_color = "inverse"
                ntu_delta = ntu - 25 if len(st.session_state.ntu_hist) > 1 else None
                st.metric(
                    label="Kekeruhan",
                    value=f"{ntu:.2f} NTU",
                    delta=f"{ntu_delta:.2f}" if ntu_delta is not None else None,
                    delta_color=ntu_delta_color
                )

            with col4:
                st.metric(
                    label="Update Terakhir",
                    value=timestamp
                )
            
            # 4. AI ANALYSIS & FINAL STATUS - PARALLEL PROCESSING
            model = load_model()
            
            # *** PARALLEL HYBRID WORKFLOW ***
            # Tahap 1: Machine Learning - berjalan independen
            ml_result = model.predict(ph, tds, ntu)
            
            # Tahap 2: Expert System - berjalan independen dengan ML result
            # ES akan menghitung confidence berdasarkan agreement dengan ML
            es_result, es_explanations, confidence, has_active_rules = evaluate_water_quality(ph, tds, ntu, ml_result)
            
            # Extract rule IDs
            rule_ids = []
            in_rules_section = False

            for exp in es_explanations:
                exp_stripped = exp.strip()
                
                if "✅ Aturan Aktif:" in exp_stripped:
                    in_rules_section = True
                    continue
                
                if in_rules_section:
                    if exp_stripped == "" or exp_stripped.startswith("Firing Strength:"):
                        break
                
                if in_rules_section and exp_stripped:
                    match = re.match(r'^(R\d+)\s*\(μ=', exp_stripped)
                    if match:
                        rule_ids.append(match.group(1))
            
            # Status final dari ES (sudah melalui hybrid_decision)
            status = es_result
            explanations = es_explanations
            
            # **UPLOAD STATUS TO FIREBASE**
            upload_status_to_firebase(db_path, status, confidence)
            
            # **SAVE TO HISTORY NODE**
            save_to_history(ph, tds, ntu, status, timestamp)
            
            # Status Card + Confidence
            st.markdown("### Status Kualitas Air")
            render_status_and_confidence(status, confidence)
            
            # Decision Explanation
            st.markdown("### Penjelasan Keputusan")
            render_decision_explanation(ml_result, es_result, status, explanations, rule_ids, has_active_rules)
            
            # Recommendations
            st.markdown("### Rekomendasi Tindakan")
            recommendations = get_recommendations(status, ph, tds, ntu)
            render_recommendations(recommendations)
            
            # System Pipeline
            render_pipeline(data, True, True)
            
            # Technical Documentation
            render_documentation()


if __name__ == "__main__":
    main()