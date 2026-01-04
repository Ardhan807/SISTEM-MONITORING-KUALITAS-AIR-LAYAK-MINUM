"""
UI Components for Water Quality Monitoring System
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from config import RECOMMENDATION_ICONS
from utils import get_status_class


def create_plotly_chart(data, title: str, color: str, y_label: str):
    """Create Plotly chart for sensor data"""
    fig = go.Figure()
    
    # Convert color hex to rgba
    rgb = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    fill_color = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.1)'
    
    fig.add_trace(go.Scatter(
        y=list(data),
        mode='lines+markers',
        line=dict(color=color, width=2),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor=fill_color
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#333')),
        xaxis_title="Time",
        yaxis_title=y_label,
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig


def render_status_and_confidence(status: str, confidence: int):
    """Render status card and confidence box side by side"""
    status_class, status_text = get_status_class(status)
    
    st.markdown(f"""
        <div class="equal-height-wrapper">
            <div class="confidence-box">
                <div class="confidence-label-inline">Tingkat Keyakinan Untuk Diminum</div>
                <div class="confidence-value-inline">{confidence}%</div>
                <div class="confidence-bar-inline">
                    <div class="confidence-fill-inline" style="width: {confidence}%;"></div>
                </div>
            </div>
            <div class="status-box {status_class}">
                {status_text}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_device_status(is_online: bool, status_message: str, timestamp: str):
    """Render compact device status indicator"""
    if is_online:
        status_bg = "#333333"
        status_border = "#059669"
        status_dot = "#059669"
        status_text = "ESP32 Online"
        status_text_color = "#ffffff"
        status_icon = "✓"
        status_detail_color = "#e5e5e5"
    else:
        status_bg = "#333333"
        status_border = "#dc2626"
        status_dot = "#dc2626"
        status_text = "ESP32 Offline"
        status_text_color = "#ffffff"
        status_icon = "✗"
        status_detail_color = "#e5e5e5"
    
    st.markdown(f"""
        <div style='
            background: {status_bg};
            border: 2px solid {status_border};
            border-radius: 8px;
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        '>
            <div style='display: flex; align-items: center; gap: 10px;'>
                <div style='
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: {status_dot};
                    animation: pulse-device 2s ease-in-out infinite;
                    box-shadow: 0 0 8px {status_dot};
                '></div>
                 <span style='font-weight: 600; color: {status_text_color}; font-size: 14px;'>
                    {status_text}
                </span>
            </div>
            <div style='display: flex; align-items: center; gap: 15px; font-size: 13px; color: {status_detail_color};'>
                <span>{status_icon} {status_message}</span>
                <span>⏱{timestamp}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_decision_explanation(ml_result: str, es_result: str, final_status: str, 
                                explanations: list, rule_ids: list, has_active_rules: bool):
    """Render decision explanation card with parallel processing"""
    ml_result_clean = ml_result.strip()
    es_result_clean = es_result.strip()
    
    # Format ML result
    ml_summary = f"<b>Machine Learning:</b> memprediksi kualitas air → <b>{ml_result_clean}</b>"
    
    # Format Expert System result
    if has_active_rules:
        rules_html = "<ul style='margin-top:5px; margin-bottom:5px;'>"
        
        in_rules_section = False
        for exp in explanations:
            exp_stripped = exp.strip()
            
            if "✅ Aturan Aktif:" in exp_stripped:
                in_rules_section = True
                continue
            
            if in_rules_section:
                if exp_stripped == "" or exp_stripped.startswith("Firing Strength:"):
                    break
            
            if in_rules_section and exp_stripped:
                if re.match(r'^R\d+\s*\(μ=', exp_stripped):
                    rules_html += f"<li>{exp_stripped}</li>"
        
        rules_html += "</ul>"
        
        unique_rules = len(set(rule_ids))
        es_summary = f"<b>Sistem Pakar:</b> {unique_rules} aturan aktif → <b>{es_result_clean}</b>{rules_html}"
    else:
        es_summary = f"<b>Sistem Pakar:</b> ❌ tidak ada aturan yang aktif → <b>{es_result_clean}</b>"
    
    # Format final decision
    if ml_result_clean == final_status and es_result_clean == final_status:
        decision_icon = "✅"
        decision_text = "Kedua sistem setuju"
    elif ml_result_clean != es_result_clean:
        decision_icon = "⚖️"
        if final_status == "Layak Minum":
            decision_text = "Sistem Pakar lebih spesifik → menggunakan hasil Sistem Pakar"
        else:
            decision_text = "Prioritas keamanan → status lebih aman dipilih"
    else:
        decision_icon = "✅"
        decision_text = "Hasil konsisten"
    
    st.markdown(
        f"""
        <div class="decision-card">
            {ml_summary}<br><br>
            {es_summary}<br><br>
            <b>{decision_icon} Kesimpulan:</b> {decision_text} → <b>Status Final: {final_status}</b>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_recommendations(recommendations: list):
    """Render recommendations with icons"""
    rec_html = '<div class="decision-card">'
    
    for rec in recommendations:
        if rec.startswith("✅"):
            icon = RECOMMENDATION_ICONS["check"]
            text = rec.replace("✅ ", "")
            rec_html += f"<h4 style='margin-top:0; display:flex; align-items:center; gap:8px;'>{icon}<span>{text}</span></h4>"
        elif rec.startswith("⚠️"):
            icon = RECOMMENDATION_ICONS["warning"]
            text = rec.replace("⚠️ ", "")
            rec_html += f"<h4 style='margin-top:0; display:flex; align-items:center; gap:8px;'>{icon}<span>{text}</span></h4>"
        elif rec.startswith("❌"):
            icon = RECOMMENDATION_ICONS["error"]
            text = rec.replace("❌ ", "")
            rec_html += f"<h4 style='margin-top:0; display:flex; align-items:center; gap:8px;'>{icon}<span>{text}</span></h4>"
        else:
            rec_html += f"<p style='margin:5px 0;'>{rec}</p>"
    
    rec_html += '</div>'
    st.markdown(rec_html, unsafe_allow_html=True)


def render_pipeline(data, ml_active: bool, es_active: bool):
    """Render system intelligence pipeline with 4 steps"""
    st.markdown("### Pipeline Sistem")
    
    step1_active = True
    step2_active = data is not None
    step3_active = step2_active and ml_active
    step4_active = step2_active and es_active
    
    col_p1, col_arrow1, col_p2, col_arrow2, col_p3, col_arrow3, col_p4 = st.columns([2, 0.5, 2, 0.5, 2, 0.5, 2])
    
    with col_p1:
        active_class = "pipeline-active" if step1_active else ""
        st.markdown(f'<div class="pipeline-step {active_class}">Sensor IoT<br><span style="font-size:12px;opacity:0.8">ESP32</span></div>', unsafe_allow_html=True)
    
    with col_arrow1:
        st.markdown("<div style='text-align:center; color:#999; margin-top:30px; font-size:20px'>→</div>", unsafe_allow_html=True)
    
    with col_p2:
        active_class = "pipeline-active" if step2_active else ""
        st.markdown(f'<div class="pipeline-step {active_class}">Firebase<br><span style="font-size:12px;opacity:0.8">Database Realtime</span></div>', unsafe_allow_html=True)
    
    with col_arrow2:
        st.markdown("<div style='text-align:center; color:#999; margin-top:30px; font-size:20px'>→</div>", unsafe_allow_html=True)
    
    with col_p3:
        ml_class = "pipeline-active" if step3_active else ""
        st.markdown(f'<div class="pipeline-step {ml_class}">Model ML<br><span style="font-size:12px;opacity:0.8">Random Forest</span></div>', unsafe_allow_html=True)
    
    with col_arrow3:
        st.markdown("<div style='text-align:center; color:#999; margin-top:30px; font-size:20px'>→</div>", unsafe_allow_html=True)
    
    with col_p4:
        es_class = "pipeline-active" if step4_active else ""
        st.markdown(f'<div class="pipeline-step {es_class}">Sistem Pakar<br><span style="font-size:12px;opacity:0.8">Fuzzy Logic</span></div>', unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)


def render_documentation():
    """Render technical documentation"""
    with st.expander("Dokumentasi Teknis & Standar Klasifikasi", expanded=False):
        doc_tab1, doc_tab2, doc_tab3 = st.tabs([
            "📊 Parameter Kualitas Air",
            "⚖️ Aturan Inferensi Sistem Pakar",
            "🔬 Penjelasan Sistem"
        ])
        
        with doc_tab1:
            st.markdown("##### Ambang Batas Parameter (Standar WHO)")
            
            st.markdown("**Tabel 1: Klasifikasi Tingkat pH**")
            ph_df = pd.DataFrame({
                'Klasifikasi': ['Asam', 'Sedikit Asam', 'Netral', 'Sedikit Basa', 'Basa'],
                'Rentang': ['≤ 6.5', '6.6 - 6.9', '7.0', '7.1 - 8.5', '≥ 8.6'],
                'Penilaian': ['Tidak Layak', 'Cukup', 'Optimal', 'Cukup', 'Tidak Layak']
            })
            st.dataframe(ph_df, hide_index=True, use_container_width=True)
            
            st.markdown("**Tabel 2: Klasifikasi Total Padatan Terlarut (TDS)**")
            tds_df = pd.DataFrame({
                'Klasifikasi': ['Sempurna', 'Baik', 'Cukup', 'Buruk', 'Tidak Diterima'],
                'Rentang (mg/L)': ['≤ 300', '301 - 600', '601 - 900', '901 - 1199', '≥ 1200'],
                'Penilaian': ['Layak', 'Layak', 'Cukup Layak', 'Tidak Layak', 'Tidak Layak']
            })
            st.dataframe(tds_df, hide_index=True, use_container_width=True)
            
            st.markdown("**Tabel 3: Klasifikasi Kekeruhan**")
            turb_df = pd.DataFrame({
                'Klasifikasi': ['Sempurna', 'Baik', 'Cukup', 'Buruk', 'Tidak Diterima'],
                'Rentang (NTU)': ['≤ 1', '1.1 - 5', '5.1 - 25.0', '25.1 - 100', '≥ 100'],
                'Penilaian': ['Layak', 'Layak', 'Cukup Layak', 'Tidak Layak', 'Tidak Layak']
            })
            st.dataframe(turb_df, hide_index=True, use_container_width=True)
        
        with doc_tab2:
            st.markdown("##### Aturan Inferensi Logika Fuzzy (R1–R22)")
            
            st.markdown("**Kondisi Tidak Layak Minum**")
            st.markdown("""
            - **R1:** IF pH *Asam* (≤ 6.5) → STATUS *Tidak Layak Minum*  
            - **R2:** IF pH *Basa* (≥ 8.6) → STATUS *Tidak Layak Minum*  
            - **R3:** IF TDS *Buruk* (901 - 1199 mg/L) → STATUS *Tidak Layak Minum*  
            - **R4:** IF TDS *Tidak Diterima* (≥ 1200 mg/L) → STATUS *Tidak Layak Minum*  
            - **R5:** IF Kekeruhan *Buruk* (25.1 - 100 NTU) → STATUS *Tidak Layak Minum*  
            - **R6:** IF Kekeruhan *Tidak Diterima* (≥ 100 NTU) → STATUS *Tidak Layak Minum*  
            """)
            
            st.markdown("**Kondisi Cukup Layak Minum**")
            st.markdown("""
            - **R7:** IF pH *Sedikit Asam* AND TDS *Cukup* AND Kekeruhan *Cukup*  
            - **R8:** IF pH *Sedikit Basa* AND TDS *Cukup* AND Kekeruhan *Cukup*  
            - **R9:** IF pH *Netral* AND TDS *Cukup* AND Kekeruhan *Baik*  
            - **R10:** IF pH *Netral* AND TDS *Baik* AND Kekeruhan *Cukup*
            - **R11:** IF pH *Sedikit Asam* AND TDS *Baik* AND Kekeruhan *Baik*  
            - **R12:** IF pH *Sedikit Basa* AND TDS *Baik* AND Kekeruhan *Baik*
            - **R13:** IF pH *Sedikit Asam* AND TDS *Baik* AND Kekeruhan *Sempurna*
            - **R14:** IF pH *Sedikit Basa* AND TDS *Baik* AND Kekeruhan *Sempurna*
            - **R15:** IF pH *Sedikit Asam* AND TDS *Sempurna* AND Kekeruhan *Baik*
            - **R16:** IF pH *Sedikit Basa* AND TDS *Sempurna* AND Kekeruhan *Baik*                     
            """)
            
            st.markdown("**Kondisi Layak Minum**")
            st.markdown("""
            - **R17:** IF pH *Sedikit Asam* AND TDS *Sempurna* AND Kekeruhan *Sempurna*
            - **R18:** IF pH *Sedikit Basa* AND TDS *Sempurna* AND Kekeruhan *Sempurna*
            - **R19:** IF pH *Netral* AND TDS *Sempurna* AND Kekeruhan *Sempurna*  
            - **R20:** IF pH *Netral* AND TDS *Baik* AND Kekeruhan *Baik*   
            - **R21:** IF pH *Netral* AND TDS *Sempurna* AND Kekeruhan *Baik*  
            - **R22:** IF pH *Netral* AND TDS *Baik* AND Kekeruhan *Sempurna*  
            """)
            
            st.info(
                "**Catatan:** Aturan inferensi disusun berdasarkan standar WHO dan "
                "divalidasi oleh pakar menggunakan Logika Fuzzy untuk menangani ketidakpastian "
                "pengukuran parameter kualitas air."
            )
        
        with doc_tab3:
            st.markdown("##### Penjelasan Sistem")
            
            st.markdown("""
            **IOT → Machine Learning ⚡ Sistem Pakar (Parallel Processing)**
            
            Sistem ini menggunakan **pendekatan paralel** untuk meningkatkan 
            akurasi dan kepercayaan dalam evaluasi kualitas air:
            
            **Tahap 1: Analisis Paralel**
            - **Machine Learning (Random Forest)** dan **Sistem Pakar (Fuzzy Logic)** berjalan **bersamaan**
            - Kedua sistem menganalisis parameter yang sama secara **independen**
            - ML menggunakan pola dari 13.276 sampel historis
            - Sistem Pakar menggunakan 22 aturan berbasis standar WHO yang telah di validasi oleh pakar
            
            **Tahap 2: Kombinasi Hasil**
            - Jika **kedua sistem setuju** → gunakan hasil tersebut
            - Jika **hasil berbeda**:
              - **ML: Tidak Layak, Sistem Pakar: Layak** → Gunakan hasil Sistem Pakar (rule-based lebih spesifik)
              - **ML: Layak, Sistem Pakar: Tidak Layak** → Gunakan hasil Sistem Pakar (prioritas keamanan)
            
            **Keunggulan Pendekatan Parallel:**
            - **Redundansi**: Dua sistem independen meningkatkan reliabilitas
            - **Cross-Validation**: Hasil saling memvalidasi
            - **Fleksibilitas**: Dapat menangani edge cases dari kedua sisi
            - **Transparansi**: Semua hasil ditampilkan untuk audit
            - **Safety First**: Prioritas pada keamanan air minum
            
            **Penyimpanan Historis:**
            - Setiap pembacaan sensor disimpan ke Firebase node `sensor_history`
            - Data tersimpan dengan struktur: `sensor_history/YYYYMMDD/HHMMSS`
            - Mencegah duplikasi data dengan signature checking
            - Menyimpan 5 field: ntu, ph, status, tds, timestamp
            - Format timestamp: HH:MM:SS (dari sensor)
            """)
            
            st.markdown("**Diagram Alur Keputusan:**")
            st.code("""
                    
                                            ┌─────────────────────┐
                                            │    Sensor Data      │
                                            └──────────┬──────────┘
                                                       │
                                                       ▼
                                            ┌─────────────────────┐
                                            │    Firebase DB      │
                                            └────┬───────────┬────┘
                                                 │           │
                                                 ▼           ▼
                                    ┌─────────────────┐ ┌─────────────────┐
                                    │     ML Model    │ │  Sistem Pakar   │
                                    │ (Random Forest) │ │(22 Fuzzy Rules) │
                                    └────────┬────────┘ └───────┬─────────┘
                                             │                  │
                                             ▼                  ▼
                                        ┌──────────┐     ┌─────────────┐
                                        │ Prediksi │     │  Validasi   │
                                        └────┬─────┘     └──────┬──────┘
                                             │                  │
                                             └─────────┬────────┘
                                                       │
                                                       ▼
                                   ┌────────────────────────────────────────┐
                                   │  Final Decision (Status + Confidence)  │
                                   │      ↓ Upload to Firebase ↓            │
                                   │   ↓ Save to sensor_history ↓           │
                                   └────────────────────────────────────────┘
                    
                        """, language="text")


def render_welcome_screen():
    """Render welcome screen when Firebase is not connected"""
    st.markdown("""
    <div class="info-box">
        <h3>Konfigurasi Firebase Diperlukan</h3>
        <p>Konfigurasi Firebase melalui bilah samping untuk mengaktifkan pemantauan kualitas air secara real-time.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Langkah Setup Awal")
        st.markdown("""
        **1. Buat Proyek Firebase**  
        Buat proyek baru di Firebase Console.

        **2. Aktifkan Database Realtime**  
        Aktifkan Database Realtime dan salin URL Database
        """)
        
        st.code("https://nama-proyek.asia-southeast1.firebasedatabase.app/", language="text")
        
        st.markdown("""
        **3. Konfigurasi Akun Layanan**  
        Unduh JSON Akun Layanan dari Pengaturan Proyek.
                    
        **4. Tentukan Path Database**  
        Tentukan path atau node di Database Realtime yang akan digunakan untuk menyimpan dan mengambil data.
        """)
    
    with col2:
        st.subheader("Kemampuan Sistem")
        st.markdown("""
        **Pemantauan Real-time**  
        Akuisisi dan visualisasi data sensor otomatis setiap 3 detik.

        **Machine Learning**  
        Prediksi menggunakan algoritma Random Forest berdasarkan pH, TDS, dan kekeruhan.

        **Sistem Pakar**  
        Validasi prediksi menggunakan 22 aturan berdasarkan standar WHO dan pengetahuan pakar.
        
        **Confidence Level**  
        Tingkat keyakinan 0-100% untuk transparansi keputusan.
        
        **Device Status**  
        Status perangkat ESP32 secara real-time dalam tampilan kompak.
        
        **Firebase Upload**  
        Status final dan confidence otomatis diupload ke Firebase.
        
        **Historical Data**  
        Setiap pembacaan sensor disimpan ke `sensor_history` untuk analisis jangka panjang.
        """)
    
    st.divider()
    
    with st.expander("Aturan Akses Database Realtime", expanded=False):
        st.code("""
{
    "rules": {
        ".read": true,
        ".write": true
    }
}
        """, language="json")
        st.warning("⚠️ Konfigurasi untuk pengembangan saja. Gunakan autentikasi yang lebih ketat.")
    
    st.divider()
    
    st.subheader("Instruksi Penggunaan")
    
    steps = st.columns(5)
    
    step_data = [
        ("1", "URL Database", "Masukkan di bilah samping", "#ffffff", "#000000"),
        ("2", "Database Path", "Tentukan node di Firebase", "#e8e8e8", "#333333"),
        ("3", "Unggah JSON", "File Akun Layanan", "#ffffff", "#000000"),
        ("4", "Koneksi", "Terhubung otomatis", "#e8e8e8", "#333333"),
        ("5", "Pemantauan", "Dashboard real-time", "#ffffff", "#000000")
    ]
    
    for idx, (num, title, desc, bg, border) in enumerate(step_data):
        with steps[idx]:
            st.markdown(f"""
            <div style='text-align: center; padding: 12px; background: {bg}; border: 2px solid {border}; border-radius: 0px;'>
                <h3 style='margin-top: 0; color: #000000;'>{num}</h3>
                <p style='color: #1a1a1a; margin-bottom: 0;'>
                    <strong>{title}</strong><br>
                    <span style='font-size: 12px;'>{desc}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
