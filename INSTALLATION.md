# Installation Guide - Water Quality Monitoring System

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Firebase account with Realtime Database
- ESP32 device (for IoT integration)

## 🚀 Installation Steps

### 1. Clone or Extract Project

Extract the ZIP file to your desired location:
```bash
cd /path/to/your/project
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

**Option A: Install from requirements.txt**
```bash
pip install -r requirements.txt
```

**Option B: Install manually**
```bash
pip install streamlit>=1.28.0
pip install firebase-admin>=6.2.0
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install plotly>=5.18.0
pip install scikit-learn>=1.3.0
pip install joblib>=1.3.0
pip install streamlit-autorefresh>=0.0.1
```

### 4. Verify Installation

Check if all packages are installed:
```bash
pip list
```

You should see:
- streamlit
- firebase-admin
- pandas
- numpy
- plotly
- scikit-learn
- joblib
- streamlit-autorefresh

### 5. Prepare Required Files

Ensure these files are in your project directory:
```
your_project/
├── app.py
├── config.py
├── utils.py
├── ui_components.py
├── styles.css
├── Machine_Learning.py
├── Sistem_Pakar.py
├── water_potability_model.pkl    ← ML model file
├── requirements.txt
└── README.md
```

### 6. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Enable **Realtime Database**
4. Go to **Project Settings** → **Service Accounts**
5. Click **Generate New Private Key**
6. Download the JSON file (keep it secure!)

### 7. Configure Firebase Rules

In Firebase Console, set these rules for development:
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

⚠️ **Note:** These rules are for development only. Use proper authentication in production.

### 8. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### 9. Configure in Application

1. Open the sidebar in the application
2. Enter Firebase Database URL: `https://your-project.firebaseio.com/`
3. Enter Database Path: `sensor` (or your preferred path)
4. Upload the Service Account JSON file
5. Click connect

## 🔧 Troubleshooting

### Issue: Module not found

**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Firebase connection failed

**Solution:**
- Check Firebase URL format: must start with `https://` and end with `/`
- Verify Service Account JSON is valid
- Check Firebase Rules allow read/write access
- Ensure internet connection is active

### Issue: Streamlit command not found

**Solution:**
```bash
# Add Python Scripts to PATH or use:
python -m streamlit run app.py
```

### Issue: Port already in use

**Solution:**
```bash
# Run on different port:
streamlit run app.py --server.port 8502
```

### Issue: CSS not loading

**Solution:**
- Ensure `styles.css` is in the same directory as `app.py`
- Check file permissions
- Restart the application

### Issue: ML model not found

**Solution:**
- Ensure `water_potability_model.pkl` is in the same directory
- Check file name matches exactly (case-sensitive)
- Verify file is not corrupted

## 📦 Version Compatibility

Tested with:
- Python 3.8, 3.9, 3.10, 3.11
- Streamlit 1.28.0 - 1.32.0
- Firebase Admin 6.2.0 - 6.4.0

## 🔄 Updating Dependencies

To update all packages to latest versions:
```bash
pip install --upgrade -r requirements.txt
```

To update specific package:
```bash
pip install --upgrade streamlit
```

## 🐳 Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t water-monitoring .
docker run -p 8501:8501 water-monitoring
```

## 📱 ESP32 Configuration

Ensure your ESP32 code sends data in this format:
```json
{
  "ph": 7.2,
  "tds": 120.5,
  "ntu": 0.85,
  "timestamp": "14:30:25"
}
```

To the Firebase path: `sensor/` (or your configured path)

## 🆘 Support

If you encounter issues:
1. Check the README.md for detailed documentation
2. Verify all files are present and named correctly
3. Check Python and package versions
4. Ensure Firebase is properly configured
5. Review the Troubleshooting section above

## ✅ Quick Test

After installation, test with these commands:

**Test Python:**
```bash
python --version
```

**Test Streamlit:**
```bash
streamlit --version
```

**Test Firebase Admin:**
```bash
python -c "import firebase_admin; print('Firebase Admin OK')"
```

**Test All Imports:**
```bash
python -c "import streamlit, firebase_admin, pandas, numpy, plotly, sklearn, joblib; print('All imports OK')"
```

If all tests pass, you're ready to go! 🎉

## 🔐 Security Notes

**For Production:**
1. Use environment variables for sensitive data
2. Implement proper Firebase authentication rules
3. Use HTTPS only
4. Secure your Service Account JSON file
5. Implement rate limiting
6. Add user authentication

**Example .env file:**
```
FIREBASE_URL=https://your-project.firebaseio.com/
FIREBASE_DB_PATH=sensor
```

Then use `python-dotenv` to load:
```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
firebase_url = os.getenv('FIREBASE_URL')
```

---

**Happy Monitoring! 💧**
