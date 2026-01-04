"""
Utility functions for Water Quality Monitoring System
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import json
import tempfile
from collections import deque
from datetime import datetime
from config import HISTORY_MAXLEN


def initialize_session_state():
    """Initialize session state variables"""
    if "ph_hist" not in st.session_state:
        st.session_state.ph_hist = deque(maxlen=HISTORY_MAXLEN)
    if "tds_hist" not in st.session_state:
        st.session_state.tds_hist = deque(maxlen=HISTORY_MAXLEN)
    if "ntu_hist" not in st.session_state:
        st.session_state.ntu_hist = deque(maxlen=HISTORY_MAXLEN)
    if "time_hist" not in st.session_state:
        st.session_state.time_hist = deque(maxlen=HISTORY_MAXLEN)
    if "last_timestamp" not in st.session_state:
        st.session_state.last_timestamp = None
    if "no_update_count" not in st.session_state:
        st.session_state.no_update_count = 0
    if "last_saved_signature" not in st.session_state:
        st.session_state.last_saved_signature = None
    if "first_data_received" not in st.session_state:
        st.session_state.first_data_received = False  # Flag untuk tracking apakah sudah pernah terima data baru


def load_firebase_config():
    """Load Firebase configuration from Streamlit secrets"""
    try:
        firebase_url = st.secrets["firebase"]["database_url"]
        db_path = st.secrets["firebase"]["db_path"]
        service_account_json = st.secrets["firebase"]["service_account"]
        
        # Parse service account JSON string
        service_account_dict = json.loads(service_account_json)
        
        return {
            "firebase_url": firebase_url,
            "db_path": db_path,
            "service_account": service_account_dict,
            "success": True,
            "error": None
        }
    except KeyError as e:
        return {
            "firebase_url": None,
            "db_path": "sensor",
            "service_account": None,
            "success": False,
            "error": f"Missing key in secrets: {str(e)}"
        }
    except json.JSONDecodeError as e:
        return {
            "firebase_url": None,
            "db_path": "sensor",
            "service_account": None,
            "success": False,
            "error": f"Invalid JSON in service_account: {str(e)}"
        }
    except Exception as e:
        return {
            "firebase_url": None,
            "db_path": "sensor",
            "service_account": None,
            "success": False,
            "error": str(e)
        }


def init_firebase_from_secrets():
    """Initialize Firebase using secrets configuration"""
    config = load_firebase_config()
    
    if not config["success"]:
        return False, f"Error loading secrets: {config['error']}", None
    
    try:
        # Delete existing app if any
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
        
        # Initialize Firebase with service account dict
        cred = credentials.Certificate(config["service_account"])
        firebase_admin.initialize_app(
            cred,
            {
                'databaseURL': config["firebase_url"],
                'databaseAuthVariableOverride': {
                    'uid': 'streamlit-app'
                }
            }   
        )
        return True, "✅ Firebase connected", config["db_path"]
    except Exception as e:
        return False, f"❌ Error: {str(e)}", None


def init_firebase(key_file, db_url: str) -> tuple:
    """Initialize Firebase with proper error handling (legacy function)"""
    try:
        key_file.seek(0)
        key_dict = json.load(key_file)
        
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
        
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(
            cred,
            {
                'databaseURL': db_url,
                'databaseAuthVariableOverride': {
                    'uid': 'streamlit-app'
                }
            }   
        )
        return True, "✅ Firebase connected"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def get_sensor_data_wib(path: str) -> tuple:
    """Fetch data from Firebase and ensure WIB timestamp"""
    try:
        ref = db.reference(path)
        data = ref.get()

        if not data:
            return None, "Tidak ada data"

        ph = float(data.get("ph", 0))
        tds = float(data.get("tds", 0))
        ntu = float(data.get("ntu", 0))

        # Get timestamp directly from Firebase (no conversion)
        timestamp = data.get("timestamp", "00:00:00")

        return {
            "ph": ph,
            "tds": tds,
            "ntu": ntu,
            "timestamp": timestamp
        }, None

    except Exception as e:
        return None, str(e)


def upload_status_to_firebase(sensor_path: str, status: str, confidence: int):
    """Upload final status and confidence to sensor node in Firebase"""
    try:
        ref = db.reference(sensor_path)
        
        # Update only status field in the sensor node
        ref.update({
            "status": status
        })
    except Exception as e:
        st.sidebar.error(f"❌ Error uploading status: {str(e)}")


def save_to_history(ph: float, tds: float, ntu: float, status: str, timestamp: str):
    """
    Save sensor data and status to Firebase sensor_history node
    
    Structure: sensor_history/YYYYMMDD/HHMMSS
    
    Data saved:
    {
        "ntu": 0.1,
        "ph": 7.18,
        "status": "Layak Minum",
        "tds": 103.3,
        "timestamp": "21:00:32"
    }
    
    Args:
        ph: pH value
        tds: TDS value in mg/L
        ntu: Turbidity value in NTU
        status: Water quality status (Layak/Cukup Layak/Tidak Layak Minum)
        timestamp: Timestamp from sensor (HH:MM:SS format)
    """
    try:
        # Create data signature to avoid duplicates
        data_signature = f"{ph:.2f}|{tds:.1f}|{ntu:.2f}|{status}"
        
        # Check if this exact data was already saved
        if st.session_state.last_saved_signature == data_signature:
            return  # Skip duplicate save
        
        # Generate unique key based on current datetime
        now = datetime.now()
        date_key = now.strftime("%Y%m%d")  # YYYYMMDD format
        time_key = now.strftime("%H%M%S")  # HHMMSS format
        
        # Create history entry with ONLY 5 required fields
        history_entry = {
            "ntu": round(ntu, 2),
            "ph": round(ph, 2),
            "status": status,
            "tds": round(tds, 1),
            "timestamp": timestamp  # Time from sensor (HH:MM:SS)
        }
        
        # Save to Firebase under sensor_history/YYYYMMDD/HHMMSS
        history_ref = db.reference(f"sensor_history/{date_key}/{time_key}")
        history_ref.set(history_entry)
        
        # Update last saved signature
        st.session_state.last_saved_signature = data_signature
        
        print(f"✅ History saved: sensor_history/{date_key}/{time_key}")
        
    except Exception as e:
        print(f"❌ Error saving to history: {str(e)}")
        # Don't show error to user, just log it


def check_device_status_by_timestamp(firebase_timestamp: str) -> dict:
    """
    Check if device is online based on Firebase timestamp (universal untuk semua user)
    
    Args:
        firebase_timestamp: Timestamp dari Firebase dalam format "HH:MM:SS"
    
    Returns:
        dict: {
            "is_online": bool,
            "message": str,
            "seconds_ago": int
        }
    
    LOGIKA:
    - Bandingkan timestamp Firebase dengan waktu sekarang
    - Jika selisih > 15 detik → OFFLINE
    - Jika selisih <= 15 detik → ONLINE
    """
    try:
        from datetime import datetime, timedelta
        
        # Parse timestamp dari Firebase (format: "HH:MM:SS")
        now = datetime.now()
        
        # Parse jam, menit, detik dari timestamp
        time_parts = firebase_timestamp.split(":")
        firebase_hour = int(time_parts[0])
        firebase_minute = int(time_parts[1])
        firebase_second = int(time_parts[2])
        
        # Buat datetime object untuk timestamp Firebase (hari ini)
        firebase_time = now.replace(
            hour=firebase_hour,
            minute=firebase_minute,
            second=firebase_second,
            microsecond=0
        )
        
        # Hitung selisih waktu
        time_diff = now - firebase_time
        seconds_ago = int(time_diff.total_seconds())
        
        # Handle kasus timestamp Firebase lebih besar (belum update hari ini)
        # Misal: sekarang 00:05, timestamp 23:59 (kemarin)
        if seconds_ago < 0:
            # Timestamp kemarin, pasti offline
            seconds_ago = 86400 + seconds_ago  # 24 jam + selisih negatif
        
        # Tentukan status berdasarkan selisih waktu
        threshold = 15  # seconds
        
        if seconds_ago <= threshold:
            return {
                "is_online": True,
                "message": f"Online ({seconds_ago}s yang lalu)",
                "seconds_ago": seconds_ago
            }
        else:
            return {
                "is_online": False,
                "message": f"Offline ({seconds_ago}s yang lalu)",
                "seconds_ago": seconds_ago
            }
    
    except Exception as e:
        # Jika error parsing, anggap offline
        return {
            "is_online": False,
            "message": f"Error parsing timestamp: {str(e)}",
            "seconds_ago": 999
        }


def check_device_status(no_update_count, first_data_received) -> dict:
    """
    Check if device is online based on whether sensor data is updating
    
    LOGIKA:
    1. Jika belum pernah terima data baru (first_data_received = False) → OFFLINE
    2. Jika sudah pernah terima data baru:
       - no_update_count < 5 → ONLINE
       - no_update_count >= 5 (15 detik) → OFFLINE
    
    CATATAN: Fungsi ini untuk backward compatibility.
    Gunakan check_device_status_by_timestamp() untuk status yang lebih akurat.
    """
    max_no_update_checks = 5  # 5 checks x 3 seconds = 15 seconds
    
    # Jika belum pernah terima data baru sejak aplikasi dibuka
    if not first_data_received:
        return {
            "is_online": False,
            "message": "Menunggu data pertama..."
        }
    
    # Jika sudah pernah terima data, cek apakah masih update
    if no_update_count >= max_no_update_checks:
        return {
            "is_online": False,
            "message": f"Tidak ada data baru ({no_update_count * 3}s)"
        }
    else:
        return {
            "is_online": True,
            "message": "Menerima data baru"
        }


def get_status_class(status: str) -> tuple:
    """Get CSS class and text for status"""
    if status == "Layak Minum":
        return "status-safe-full", "LAYAK UNTUK MINUM"
    elif status == "Cukup Layak Minum":
        return "status-moderate-full", "CUKUP LAYAK UNTUK MINUM <br> (Baca rekomendasi tindakan)"
    else:
        return "status-unsafe-full", "TIDAK LAYAK MINUM"


def load_css():
    """Load external CSS file"""
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ styles.css tidak ditemukan. Menggunakan styling default.")